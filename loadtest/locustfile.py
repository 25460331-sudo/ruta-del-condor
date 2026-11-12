"""Práctica 3.4 — Jugadores y espectadores simulados con Locust.

Jugador:  pide un servidor al allocator de Agones (como haría el matchmaker), se conecta por WebSocket,
          manda su posición 20 veces por segundo y mide el RTT con un ping por segundo.
Espectador: descarga segmentos HLS de 2 s desde S3/CloudFront y marca rebuffering si tarda más de 2 s.

Variables de entorno:
  ALLOCATOR_URL   https://<host-del-allocator>/gameserverallocation   (jugadores)
  CERT, KEY, CA   rutas a client.crt / client.key / ca.crt            (por defecto en la carpeta actual)
  VERIFY_TLS      "0" para no verificar el certificado en el laboratorio
  GAME_WS         ws://host:puerto   (alternativa sin allocator: UNA sola sala de 8 jugadores)
"""
import json, math, os, random, time, uuid

import requests
from gevent.lock import Semaphore
from locust import HttpUser, User, constant, constant_pacing, events, task
from websocket import create_connection

ALLOCATOR = os.environ.get("ALLOCATOR_URL", "")
DIRECTO = os.environ.get("GAME_WS", "")
PEDIDO = {"namespace": "default", "gameServerSelectors": [{"matchLabels": {"agones.dev/fleet": "condor-fleet"}}]}
CERTS = {"cert": (os.environ.get("CERT", "client.crt"), os.environ.get("KEY", "client.key"))}
CERTS["verify"] = os.environ.get("CA", "ca.crt") if os.environ.get("VERIFY_TLS", "1") != "0" else False
JUGADORES_POR_SALA = 8


def medir(nombre, inicio, error=None):
    events.request.fire(request_type="WS", name=nombre, response_time=(time.perf_counter() - inicio) * 1000,
                        response_length=0, exception=error)


class Jugador(User):                                   # 20 mensajes por segundo
    wait_time = constant(0.05)
    sala = {"addr": None, "cupo": 0}                   # mini-matchmaker compartido entre todos los jugadores
    candado = Semaphore()

    def pedir_servidor(self):
        if DIRECTO:
            return DIRECTO.replace("ws://", "")
        with Jugador.candado:                          # un solo pedido a la vez
            if Jugador.sala["cupo"] == 0:              # sala llena: pide otro servidor
                t0 = time.perf_counter()
                r = requests.post(ALLOCATOR, json=PEDIDO, timeout=10, **CERTS)
                r.raise_for_status()
                gs = r.json()
                medir("asignacion", t0)
                Jugador.sala = {"addr": f"{gs['address']}:{gs['ports'][0]['port']}", "cupo": JUGADORES_POR_SALA}
            Jugador.sala["cupo"] -= 1
            return Jugador.sala["addr"]

    def on_start(self):
        self.id, self.n = uuid.uuid4().hex[:8], 0      # el servidor acepta ids alfanuméricos de hasta 16 caracteres
        self.x, self.y, self.z, self.a = random.uniform(0, 600), random.uniform(40, 120), random.uniform(-500, 0), 0.0
        self.ws = create_connection(f"ws://{self.pedir_servidor()}", timeout=5)

    @task
    def jugar(self):
        self.a += random.uniform(-0.05, 0.05)
        self.x += math.cos(self.a) * 4; self.z += math.sin(self.a) * 4
        self.ws.send(json.dumps({"id": self.id, "name": "Bot", "x": self.x, "y": self.y, "z": self.z, "a": self.a,
                                 "cp": 0, "score": 0, "crash": 0, "up": [0, 0, 0, 0, 0, 0], "sk": 0, "hp": 100}))
        self.n += 1
        if self.n % 20 == 0:                           # un ping por segundo (mide la red, no el tick)
            t0 = time.perf_counter()
            try:
                self.ws.send(json.dumps({"ping": t0}))
                while json.loads(self.ws.recv()).get("pong") != t0:
                    pass                               # descarta los snapshots acumulados
                medir("rtt", t0)
            except Exception as e:
                medir("rtt", t0, e)

    def on_stop(self):
        try:
            self.ws.close()
        except Exception:
            pass


class Espectador(HttpUser):                            # un segmento cada 2 s, como un reproductor
    wait_time = constant_pacing(2)

    def on_start(self):
        self.i = random.randint(0, 100)

    @task
    def ver_stream(self):
        m = self.client.get("/live/condor/360p.m3u8", name="manifiesto")
        segmentos = [l for l in m.text.splitlines() if l.endswith(".ts")]
        if not segmentos:
            return
        seg = segmentos[self.i % len(segmentos)]; self.i += 1
        with self.client.get(f"/live/condor/{seg}", name="segmento", catch_response=True) as r:
            if r.elapsed.total_seconds() > 2:
                r.failure("rebuffering: el segmento tardó más de lo que dura")
