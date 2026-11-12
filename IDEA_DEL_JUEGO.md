# Ruta del Cóndor — Propuesta de juego

**Equipo:** Diego Reyes Natilla · José Heriberto Osorio
**Unidad 3 · Infraestructura y despliegue de videojuegos en la nube · Nube: AWS**

## 1. Concepto

*Ruta del Cóndor* es un juego multijugador en línea de **carreras aéreas**: hasta **8 jugadores** controlan cóndores que planean por un circuito entre montañas. Gana quien cruce primero los aros de control y llegue a la meta.

No hay motor: el cóndor pierde altura al planear y la recupera aprovechando **corrientes térmicas** (columnas de aire caliente) que aparecen y desaparecen. La estrategia está en elegir la mejor térmica sin desviarse demasiado de la ruta.

## 2. Mecánicas

| Mecánica | Descripción |
| Planeo | Dirección e inclinación; picar da velocidad pero hace perder altura |
| Térmicas | Zonas que dan altura; se reparten al azar en cada partida |
| Aros de control | El circuito obliga a pasar por ellos en orden |
| Ráfagas | Un empujón corto para adelantar o bloquear a un rival (con recarga) |
| Bots con IA | Si faltan jugadores, la sala se completa con cóndores controlados por IA |

- **Partida:** 3–5 minutos, 8 jugadores (humanos + bots).
- **Puntaje:** por posición de llegada y tiempo total; alimenta una **tabla de líderes global**.
- **Espectadores:** las carreras se pueden ver en vivo como un stream de video.

## 3. ¿Por qué este juego para la unidad?

Cada parte del juego usa uno de los temas de la unidad:

| Tema | Uso en Ruta del Cóndor | Servicio AWS |
|---|---|---|
| 3.1 Cómputo para IA | Entrenar los bots de vuelo (aprendizaje por refuerzo) y medir su inferencia | Colab / SageMaker Studio Lab |
| 3.2 CI/CD | Cada cambio en el servidor se prueba y se publica solo | GitHub Actions → Amazon ECR |
| 3.3 Contenedores | Cada carrera corre en un servidor de juego en contenedor (WebSocket, 20 ticks/s) | EKS + Agones |
| 3.4 Autoescalado y métricas | Más carreras → más servidores y nodos; se mide CCU, latencia p95 y tick | Agones FleetAutoscaler, Cluster Autoscaler, Prometheus + Grafana, Locust |
| 3.5 Serverless | Tabla de líderes con los mejores tiempos | Lambda + DynamoDB |
| 3.6 Infraestructura como código | Toda la infraestructura se crea y se destruye con un comando | Terraform |
| Streaming | Retransmisión de carreras a espectadores | S3 + CloudFront (HLS) |

## 4. Arquitectura (resumen)

```
Jugadores ──WebSocket──► Servidores de carrera (EKS + Agones, autoescalado)
                               │ métricas
                               ▼
                       Prometheus + Grafana
Fin de carrera ──HTTP──► Lambda ──► DynamoDB (tabla de líderes)
Espectadores ──HLS────► CloudFront ──► S3 (stream)
Infraestructura: Terraform · Despliegue: GitHub Actions → ECR
```

## 5. Metas medibles

- Latencia **p95 < 80 ms** con **1 000 jugadores simulados** (125 carreras simultáneas).
- Tick del servidor **p99 < 25 ms** (la mitad del periodo de 50 ms).
- El autoescalado debe agregar servidores antes de que se agote el colchón de 20 %.
- **500 espectadores** simulados a 360p, con extrapolación del costo a 20 000.