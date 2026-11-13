"""Une los CSV de varios pods de Locust y genera las gráficas del reporte.

Uso:  python analizar_multi.py corrida2 rampa     (carpeta con una subcarpeta por pod)
      python analizar_multi.py corrida2 pico
"""
import glob, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

carpeta, etapa = sys.argv[1], sys.argv[2]
META = 80
partes = []
for f in glob.glob(f"{carpeta}/*/{etapa}_stats_history.csv"):
    h = pd.read_csv(f)
    h = h[h["Name"] == "Aggregated"].copy()
    h["t"] = (h["Timestamp"] // 5) * 5                       # alinea los pods en ventanas de 5 s
    for c in ("95%", "99%"):
        h[c] = pd.to_numeric(h[c], errors="coerce")
    partes.append(h.groupby("t").agg({"User Count": "last", "Requests/s": "sum", "Failures/s": "sum",
                                      "95%": "max", "99%": "max"}))
T = pd.concat(partes).groupby(level=0).agg({"User Count": "sum", "Requests/s": "sum", "Failures/s": "sum",
                                             "95%": "max", "99%": "max"})
T.index = T.index - T.index[0]
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
ax[0].plot(T.index, T["User Count"]); ax[0].set(title="Jugadores simulados", xlabel="s")
ax[1].plot(T["User Count"], T["95%"]); ax[1].axhline(META, ls="--", color="r", label=f"meta {META} ms")
ax[1].set(title="Latencia p95 vs jugadores", xlabel="jugadores", ylabel="ms"); ax[1].legend()
ax[2].plot(T.index, T["Failures/s"], color="C3"); ax[2].set(title="Errores por segundo", xlabel="s")
fig.tight_layout(); fig.savefig(f"{etapa}_{carpeta}.png", dpi=150)
est = T[T["User Count"] >= 0.9 * T["User Count"].max()]
print(f"[{etapa}] jugadores máx: {int(T['User Count'].max())} | p95 estable (mediana): {est['95%'].median():.0f} ms | "
      f"p95 máx: {T['95%'].max():.0f} ms | errores totales: {T['Failures/s'].sum()*5:.0f}")
