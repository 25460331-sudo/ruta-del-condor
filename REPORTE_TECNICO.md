# Ruta del Cóndor — Reporte técnico (Unidad 3)
**Autores:** Diego Reyes Natilla · José Heriberto Osorio · **Nube:** AWS (us-east-1) · **Fecha:** 16/11/2026

> **BORRADOR.** Los textos marcados **[COMPLETAR]** dependen de mediciones que todavía no se hicieron. Máximo 6 páginas: recortar al final.

## 1. Resumen
*Ruta del Cóndor* es una carrera aérea multijugador en 3D (hasta 8 aviones por partida) con bots, mejoras que duran toda la partida, clima dinámico y tabla de líderes global. Se desplegó en AWS con contenedores, Kubernetes + Agones, serverless e infraestructura como código, y se validó con pruebas de carga que simulan jugadores y espectadores.

## 2. Arquitectura
```
Jugadores ──WebSocket──► Servidores de partida (EKS + Agones, FleetAutoscaler)
                                │ métricas            ▲ Cluster Autoscaler (nodos)
                                ▼
                        Prometheus + Grafana
Fin de partida ──HTTP──► Lambda ──► DynamoDB (tabla de líderes)
Espectadores ──HLS────► S3 / CDN (stream de prueba)
Infraestructura: Terraform · Despliegue: GitHub Actions → Amazon ECR
```
| Componente | Servicio AWS |
|---|---|
| Servidor de partida | EKS 1.31 + Agones (nodos `t3.large`, 2–20) |
| Imágenes | Amazon ECR (`condor-server`) |
| Tabla de líderes | Lambda (Python 3.12) + DynamoDB |
| Streaming (prueba) | S3 + CloudFront **[COMPLETAR]** |
| Observabilidad | Prometheus + Grafana (kube-prometheus-stack) |
| IaC | Terraform (VPC, EKS, ECR, Agones, Lambda, DynamoDB, Cluster Autoscaler) |

## 3. Cómputo para IA (práctica 3.1)
Entrenamiento: bot PPO en CartPole (sustituto didáctico). **[COMPLETAR con `ia/entrenar_bot.py`]**
| | CPU | GPU (T4) |
|---|---|---|
| Entrenamiento 100 000 pasos | **[ ]** s | **[ ]** s |
| Latencia de inferencia | **[ ]** ms | — |
| Decisiones/s por núcleo | **[ ]** | — |
2 000 bots a 10 Hz = 20 000 inferencias/s → **[ ]** vCPU (con 30 % de margen), costo ≈ USD **[ ]**/h.
*Conclusión:* con una red tan pequeña la GPU no gana por el costo de copiar datos; la inferencia va en CPU y la GPU se reserva para entrenar con Spot y checkpoints.

## 4. Contenedores y orquestación (práctica 3.3)
El servidor (Python, WebSocket, 20 ticks/s) se empaqueta en una imagen y corre como `GameServer` de Agones (estados `Ready → Allocated → Shutdown`). La flota mantiene servidores libres y el SDK de Agones recibe `/ready`, `/health` cada 2 s y `/shutdown` al terminar. Evidencia: `evidencias/3.3_*.png` (3 servidores `Ready`, uno pasa a `Allocated` al pedir partida).
*¿Qué pasa si se borra un pod `Allocated`?* La partida en curso se pierde (los jugadores se desconectan) y la flota crea un servidor nuevo `Ready` para reponerlo; por eso Agones marca los pods asignados como no desalojables ante el autoescalado de nodos.

## 5. CI/CD (práctica 3.2)
`push` a `main` → pruebas (`pytest`) → construcción de la imagen → publicación en ECR con la etiqueta del commit. Evidencia: captura del pipeline en verde **[COMPLETAR]**.
*Rollback:* cada versión es una imagen inmutable con la etiqueta del commit; volver atrás es apuntar `k8s/fleet.yaml` a la etiqueta anterior y aplicar; Agones reemplaza solo los servidores libres y deja terminar las partidas en curso (drenado).

## 6. Autoescalado, métricas y pruebas de carga (práctica 3.4)
Tres capas: **partidas** (FleetAutoscaler, buffer 20 %), **servicios** (HPA) y **nodos** (Cluster Autoscaler).
Métricas: CCU, latencia p95 (meta < 80 ms), duración del tick p99 (< 25 ms), servidores por estado, nodos.
Escenarios Locust: rampa (**[ ]** jugadores, 2/s), pico (**[ ]** en 20 s) y **[ ]** espectadores a 360p.
| Resultado | Valor |
|---|---|
| Capacidad máxima medida (p95 cruza 80 ms) | **[ ]** jugadores |
| Jugadores por nodo | **[ ]** |
| Tiempo de reacción del escalado (servidores / nodos) | **[ ]** s / **[ ]** s |
| Errores durante el pico | **[ ]** % |
Gráficas: `rampa.png` (CCU vs p95), línea de tiempo de servidores y nodos, errores/rebuffering **[COMPLETAR]**.
*Extrapolación de espectadores:* 20 000 × 6 000 kbps × 3 600 / (8 × 10⁶) = **54 000 GB ≈ 54 TB por hora**; por eso se sirve desde CDN con varias calidades (ABR).

## 7. Serverless (práctica 3.5)
Tabla de líderes con Lambda + DynamoDB (URL de la función pública): guarda puntajes y devuelve el top 10. Probada con `curl` (ver `evidencias/3.5_*.png`). Prueba de carga a 500 usuarios (80 % lecturas / 20 % escrituras) y efecto del arranque en frío en el p99: **[COMPLETAR]**.
*Costo:* 5 M consultas/mes de 50 ms y 256 MB ≈ 62 500 GB-s, dentro de la capa gratuita de Lambda, frente a una VM encendida todo el mes (≈ USD **[ ]**).

## 8. Infraestructura como código (práctica 3.6)
Todo vive en `infra/` y se crea con `terraform apply` en ~20 min y se borra con `terraform destroy`. Evidencia: `plan` revisado en un pull request **[COMPLETAR]** y `destroy` completo sin recursos huérfanos **[COMPLETAR]**. Lección aprendida: las credenciales temporales de AWS vencen durante el `apply`; Terraform retoma donde quedó.

## 9. Costos
| Concepto | USD/h |
|---|---|
| Plano de control EKS | 0,10 |
| Nodos (**[ ]** × `t3.large`) | **[ ]** |
| Balanceadores y otros | **[ ]** |
| **Total** | **[ ]** |
Costo por jugador/hora = total ÷ jugadores sostenidos = **[COMPLETAR]**. (Precios: confirmar en la calculadora de AWS; varían por región y con el tiempo.)

## 10. Recomendaciones **[COMPLETAR con los datos]**
`bufferSize` de Agones, tipo de máquina, mínimo de nodos y número de regiones, justificados con la capacidad y el tiempo de reacción medidos.

## 11. Seguridad y limitaciones
Auditoría completa en `AUDITORIA.md`: se corrigieron XSS por nombres, datos de red sin validar y un servidor sin límites (tamaño, ritmo, campos permitidos). Riesgos abiertos: el cliente decide puntos y daños (posible trampa), bots locales por navegador y sin TLS (`wss`) en el servidor.
