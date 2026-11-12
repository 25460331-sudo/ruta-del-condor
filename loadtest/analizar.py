"""Genera las gráficas del reporte a partir de los CSV de Locust.

Uso:  python analizar.py rampa            (lee rampa_stats_history.csv y crea ccu_vs_p95.png)
      python analizar.py pico stream
Requiere: pip install pandas matplotlib
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

META_MS = 80
for nombre in sys.argv[1:] or ["rampa"]:
    h = pd.read_csv(f"{nombre}_stats_history.csv")
    h = h[h["Name"] == "Aggregated"].copy()
    h["p95"] = pd.to_numeric(h["95%"], errors="coerce")
    h["fallas"] = pd.to_numeric(h["Failures/s"], errors="coerce")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(h["User Count"], h["p95"])
    ax[0].axhline(META_MS, linestyle="--", color="r", label=f"meta p95 = {META_MS} ms")
    ax[0].set(xlabel="Jugadores simulados", ylabel="Latencia p95 (ms)", title=f"CCU vs latencia ({nombre})")
    ax[0].legend()
    ax[1].plot(h["Timestamp"] - h["Timestamp"].iloc[0], h["User Count"], label="usuarios")
    ax[1].plot(h["Timestamp"] - h["Timestamp"].iloc[0], h["fallas"] * 10, label="fallas/s ×10")
    ax[1].set(xlabel="Segundos", title="Usuarios y errores en el tiempo")
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(f"{nombre}.png", dpi=150)

    sobre = h[h["p95"] > META_MS]
    print(f"[{nombre}] capacidad aprox. (primer cruce de {META_MS} ms): "
          f"{int(sobre['User Count'].iloc[0]) if len(sobre) else 'no se cruzó'} jugadores")
