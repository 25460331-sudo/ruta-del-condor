# Lista de entrega (vence el 16/11) — contra la rúbrica del manual

Reglas del manual: cada práctica pide un entregable; el proyecto final pide repositorio, pipeline en verde, tablero de Grafana, pruebas de carga, reporte (máx. 6 págs.) y presentación de 10 min.

| Rúbrica (peso) | Qué pide | Estado | Falta |
|---|---|---|---|
| Infraestructura como código (20 %) | Todo se crea y se destruye con Terraform; estado remoto; variables por entorno | ✅ Terraform creado y aplicado | Captura de `terraform plan` revisado en un PR; **captura de `destroy` completo**; (opcional) estado remoto en S3 |
| Contenedores y orquestación (20 %) | Flota de Agones sana, recursos definidos, SDK integrado | ✅ 3 servidores `Ready` y 1 `Allocated` (capturas en `evidencias/`) | Reconstruir la imagen con el servidor nuevo (lo hace el pipeline 3.2) |
| Autoescalado (20 %) | Flota, pods y nodos escalan; tiempo de reacción medido | 🟡 FleetAutoscaler y Cluster Autoscaler escritos | Aplicar y **medir** el tiempo de reacción (práctica 3.4) |
| Métricas y pruebas de carga (20 %) | Jugadores y espectadores simulados; curva CCU vs latencia | 🟡 `loadtest/` listo | Prometheus/Grafana + correr rampa, pico y espectadores + gráficas |
| CI/CD y serverless (10 %) | Pipeline automático y tabla de líderes probada bajo carga | 🟡 Lambda ✅; `deploy.yml` listo | Subir a GitHub, secretos, **pipeline en verde**; prueba de carga a la tabla de líderes |
| Comunicación (10 %) | Reporte claro, costo por jugador, demo fluida | 🟡 Borrador en `REPORTE_TECNICO.md` | Completar con resultados, costo, pasar a PDF; presentación de 10 min |

## Entregables de cada práctica
- **3.1** Tabla CPU vs GPU, latencia, decisiones/s por núcleo, vCPU para 2 000 bots a 10 Hz y costo/hora → `python ia/entrenar_bot.py` (Colab con GPU T4 y sin GPU).
- **3.2** Captura del pipeline en verde, imagen con etiqueta del commit y un párrafo de rollback → `.github/workflows/deploy.yml`.
- **3.3** ✅ Capturas de `docker run`, `/metrics`, `get gameservers` antes y después, y qué pasa si se borra un pod `Allocated` (está en el borrador).
- **3.4** Reporte de 2–3 págs. con 3 gráficas, capacidad máxima, tiempo de reacción y recomendación (`loadtest/README.md`).
- **3.5** ✅ URL funcionando + captura de concurrencia durante la prueba + comparación de costo serverless vs VM.
- **3.6** Repo con `infra/`, `plan` revisado en PR, captura del clúster y evidencia de `destroy`.

## Orden recomendado (4 días)
1. **Hoy:** crear el repo en GitHub, subir todo, cargar los secretos y dejar el pipeline en verde (así queda la imagen nueva en ECR). Correr 3.1 en Colab (30 min).
2. **Mañana:** Prometheus + Grafana, escenarios de carga (3.4), capturas. Pedir el aumento de cuota de vCPU **hoy** (tarda).
3. **15/11:** completar el reporte con los números, `terraform destroy` con captura, ensayar la demo.
4. **16/11:** entrega.

## Qué hago yo y qué hacés vos
- **Yo:** el código, los scripts, el borrador del reporte y el análisis de los resultados que me pases (CSV/capturas).
- **Vos:** todo lo que necesita tu cuenta o tus datos (GitHub, `aws login`, Colab, correr las pruebas, sacar capturas, aumento de cuota).
