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
partes, finales = [], []
for f in sorted(glob.glob(f"{carpeta}/*/{etapa}_stats_history.csv")):
    h = pd.read_csv(f)
    h = h[h["Name"] == "Aggregated"].copy()
    h["t"] = (h["Timestamp"] // 5) * 5                       # alinea los pods en ventanas de 5 s
    partes.append(h.groupby("t").agg({"User Count": "last", "Requests/s": "sum", "Failures/s": "sum"}))
    finales.append(pd.read_csv(f.replace("_history", "")))
T = pd.concat(partes).groupby(level=0).sum()
T.index = T.index - T.index[0]
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
ax[0].plot(T.index, T["User Count"]); ax[0].set(title="Jugadores simulados", xlabel="segundos")
ax[1].plot(T.index, T["Requests/s"]); ax[1].set(title="Mensajes medidos por segundo", xlabel="segundos")
ax[2].plot(T.index, T["Failures/s"], color="C3"); ax[2].set(title="Errores por segundo", xlabel="segundos")
fig.suptitle(f"Prueba de {etapa}"); fig.tight_layout(); fig.savefig(f"{etapa}_{carpeta}.png", dpi=150)

rtt = [d[d.Name == "rtt"].iloc[0] for d in finales]
agg = [d[d.Name == "Aggregated"].iloc[0] for d in finales]
asi = [d[d.Name == "asignacion"].iloc[0] for d in finales if (d.Name == "asignacion").any()]
print(f"[{etapa}] jugadores máx: {int(T['User Count'].max())}")
print("  RTT por pod  mediana:", [int(x['50%']) for x in rtt], " p95:", [int(x['95%']) for x in rtt], " p99:", [int(x['99%']) for x in rtt])
print(f"  Errores: {int(sum(a['Failure Count'] for a in agg))} de {int(sum(a['Request Count'] for a in agg))} "
      f"({100*sum(a['Failure Count'] for a in agg)/sum(a['Request Count'] for a in agg):.2f} %)")
print("  Asignaciones:", int(sum(a['Request Count'] for a in asi)), "con", int(sum(a['Failure Count'] for a in asi)), "rechazadas (429)")
