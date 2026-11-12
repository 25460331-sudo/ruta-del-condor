import asyncio, json, os, re, time, urllib.request
import websockets
from prometheus_client import Counter, Gauge, Histogram, start_http_server

MAX_JUGADORES = 8                      # carrera de 8 aviones
TICK_S = 0.05                          # 20 ticks por segundo
MAX_BYTES = 4096                       # tamaño máximo de un mensaje (evita que un cliente mande basura enorme)
MAX_MSG_S = 60                         # mensajes por segundo permitidos por jugador (el juego manda ~21)
PUERTO = int(os.getenv("PORT", "7654"))
PUERTO_METRICAS = int(os.getenv("METRICS_PORT", "9100"))

JUGADORES = Gauge("condor_players_connected", "Jugadores conectados")
TICK = Histogram("condor_tick_seconds", "Duración del tick",
                 buckets=(.001, .0025, .005, .01, .025, .05, .1))
RECHAZADOS = Counter("condor_messages_rejected_total", "Mensajes rechazados por inválidos o exceso de ritmo")

estado, conexiones = {}, set()
partida = {"iniciada": False}
SDK = f"http://localhost:{os.getenv('AGONES_SDK_HTTP_PORT', '9358')}"

# Solo se retransmiten estos campos, con su tipo (todo lo demás se descarta)
CAMPOS_NUM = ("x", "y", "z", "a", "cp", "fin", "score", "gd", "hn", "ms", "pm", "col", "sk", "hp", "gc")
CAMPOS_BOOL = ("crash", "inv", "sh", "ov", "tb")
CAMPOS_TXT = ("name", "hb", "gn", "gid")
ID_OK = re.compile(r"^[A-Za-z0-9]{1,16}$")


def agones(ruta):
    """Llama al SDK REST de Agones (contenedor auxiliar). Fuera de Agones se ignora."""
    try:
        req = urllib.request.Request(SDK + ruta, data=b"{}", method="POST",
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass


def num(v, lo=-1e11, hi=1e11):
    """Número finito dentro de un rango, o None si no sirve."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    if v != v or v in (float("inf"), float("-inf")):
        return None
    return max(lo, min(hi, float(v)))


def limpiar(d):
    """Valida y recorta un mensaje de jugador. Devuelve un dict seguro o None si es inválido."""
    if not isinstance(d, dict):
        return None
    pid = d.get("id")
    if not isinstance(pid, str) or not ID_OK.match(pid):
        return None
    out = {"id": pid}
    for k in CAMPOS_NUM:
        v = num(d.get(k))
        out[k] = 0 if v is None else v
    for k in CAMPOS_BOOL:
        out[k] = 1 if d.get(k) else 0
    for k in CAMPOS_TXT:
        v = d.get(k)
        out[k] = v[:16 if k != "name" else 14] if isinstance(v, str) else ""
    pr = d.get("pr")                                   # proyectiles: máximo 4, cada uno [id, tipo, x, y, z]
    out["pr"] = []
    if isinstance(pr, list):
        for q in pr[:4]:
            if isinstance(q, list) and len(q) >= 5 and all(num(c) is not None for c in q[:5]):
                out["pr"].append([float(c) for c in q[:5]])
    fal = d.get("fal")
    out["fal"] = [float(c) for c in fal] if isinstance(fal, list) and len(fal) == 3 and all(num(c) is not None for c in fal) else 0
    ac = d.get("ac")                                   # aros ya cobrados: máximo 16 enteros
    out["ac"] = [int(c) for c in ac[:16] if num(c) is not None] if isinstance(ac, list) else []
    cd = d.get("cd")                                   # cajas ya cobradas: máximo 8 enteros
    out["cd"] = [int(c) for c in cd[:8] if num(c) is not None] if isinstance(cd, list) else []
    up = d.get("up")                                   # mejoras del avión: 6 niveles de 0 a 3
    out["up"] = [int(max(0, min(3, num(c) or 0))) for c in up[:6]] + [0] * (6 - len(up[:6])) if isinstance(up, list) else [0] * 6
    mg = d.get("mg")                                   # rayo de la ametralladora: [origen xyz, dirección xyz] o 0
    out["mg"] = [float(c) for c in mg] if isinstance(mg, list) and len(mg) == 6 and all(num(c) is not None for c in mg) else 0
    return out


def snapshot():
    return json.dumps({"t": time.time(), "e": estado})


async def jugador(ws):
    if len(conexiones) >= MAX_JUGADORES:
        await ws.close(code=4000, reason="partida llena")
        return
    conexiones.add(ws)
    JUGADORES.set(len(conexiones))
    partida["iniciada"] = True
    mi_id = None
    ventana, cuenta = time.monotonic(), 0
    try:
        async for msg in ws:
            ahora = time.monotonic()                   # límite de ritmo por conexión
            if ahora - ventana >= 1:
                ventana, cuenta = ahora, 0
            cuenta += 1
            if cuenta > MAX_MSG_S:
                RECHAZADOS.inc()
                await ws.close(code=1008, reason="demasiados mensajes")
                return
            try:
                d = json.loads(msg)
            except (ValueError, TypeError):
                RECHAZADOS.inc()
                continue
            if isinstance(d, dict) and "ping" in d:    # medición de latencia: responde al instante
                v = num(d["ping"])
                if v is not None:
                    await ws.send(json.dumps({"pong": v}))
                continue
            limpio = limpiar(d)
            if limpio is None:
                RECHAZADOS.inc()
                continue
            if mi_id is not None and limpio["id"] != mi_id:   # una conexión = un jugador: no puede cambiar de identidad
                RECHAZADOS.inc()
                continue
            mi_id = limpio["id"]
            estado[mi_id] = limpio
    finally:
        conexiones.discard(ws)
        JUGADORES.set(len(conexiones))
        estado.pop(mi_id, None)                        # el jugador sale del estado


async def bucle():
    n = 0
    while True:
        t = time.perf_counter()
        if conexiones:
            websockets.broadcast(conexiones, snapshot())
        TICK.observe(time.perf_counter() - t)
        n += 1
        if n % 40 == 0:                                # latido a Agones cada 2 s
            await asyncio.to_thread(agones, "/health")
        if partida["iniciada"] and not conexiones:
            await asyncio.to_thread(agones, "/shutdown")   # fin de la carrera
            partida["iniciada"] = False
        await asyncio.sleep(TICK_S)


async def main():
    start_http_server(PUERTO_METRICAS)                 # /metrics para Prometheus
    async with websockets.serve(jugador, "0.0.0.0", PUERTO, max_size=MAX_BYTES,
                                ping_interval=20, ping_timeout=20):
        agones("/ready")                               # listo para recibir una carrera
        await bucle()


if __name__ == "__main__":
    asyncio.run(main())
