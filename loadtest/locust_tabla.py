"""Práctica 3.5 — carga a la tabla de líderes (Lambda + DynamoDB): 80 % lecturas / 20 % escrituras."""
import random
from locust import HttpUser, between, task


class Cliente(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.nombre = f"carga{random.randint(1, 300)}"        # 300 jugadores de prueba

    @task(8)
    def ver_top10(self):
        self.client.get("/", name="GET top10")

    @task(2)
    def guardar_puntos(self):
        self.client.post("/", json={"jugador": self.nombre, "puntos": random.randint(5, 100)}, name="POST puntaje")
