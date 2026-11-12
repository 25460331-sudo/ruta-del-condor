"""Práctica 3.1 — Entrenar y servir un bot sencillo (CPU vs GPU).

Uso (en Google Colab con GPU T4, o en tu PC):
    pip install gymnasium stable-baselines3
    python entrenar_bot.py --device cpu
    python entrenar_bot.py --device cuda      # solo si hay GPU

Anota los dos tiempos de entrenamiento y la latencia de inferencia: van en la tabla del reporte.
"""
import argparse
import math
import time

import gymnasium as gym
from stable_baselines3 import PPO

ap = argparse.ArgumentParser()
ap.add_argument("--device", default="cpu", help="cpu o cuda")
ap.add_argument("--pasos", type=int, default=100_000)
ap.add_argument("--bots", type=int, default=2000, help="bots activos para dimensionar")
ap.add_argument("--hz", type=float, default=10, help="decisiones por segundo de cada bot")
ap.add_argument("--precio_vcpu_hora", type=float, default=0.0425, help="USD por vCPU-hora (c7i.large ≈ 0.0425; confirmar en la calculadora)")
a = ap.parse_args()

env = gym.make("CartPole-v1")            # sustituto didáctico de la mecánica de equilibrio de un avión
modelo = PPO("MlpPolicy", env, verbose=0, device=a.device)
t0 = time.time()
modelo.learn(total_timesteps=a.pasos)
entrenamiento = time.time() - t0
modelo.save("bot_condor")

obs, _ = env.reset()
N = 10_000
t0 = time.perf_counter()
for _ in range(N):
    accion, _ = modelo.predict(obs, deterministic=True)
lat_ms = (time.perf_counter() - t0) / N * 1000
por_nucleo = 1000 / lat_ms

demanda = a.bots * a.hz                              # decisiones por segundo
vcpu = math.ceil(demanda / por_nucleo * 1.3)         # + 30 % de margen
print(f"\n=== Resultados ({a.device}) ===")
print(f"Entrenamiento ({a.pasos:,} pasos): {entrenamiento:.1f} s")
print(f"Latencia de inferencia: {lat_ms:.3f} ms  ->  {por_nucleo:,.0f} decisiones/s por núcleo")
print(f"{a.bots} bots a {a.hz:g} Hz = {demanda:,.0f} inferencias/s  ->  {vcpu} vCPU (con 30 % de margen)")
print(f"Costo estimado de la inferencia: USD {vcpu * a.precio_vcpu_hora:.2f} por hora")
print("Recordá explicar en el reporte cuál fue más rápida (CPU o GPU) y por qué.")
