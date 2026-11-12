# Avance — Ruta del Cóndor (Diego Reyes · José Osorio)

## Listo
**Infraestructura en AWS (Terraform, región us-east-1)**
- Red, clúster EKS, registro ECR e instalación de Agones (prácticas 3.3 y 3.6).
- Servidor de partida en contenedor (WebSocket, 20 ticks/s, métricas Prometheus), probado en local y en AWS.
- Flota de Agones: 3 servidores `Ready`; se pidió una partida y uno pasó a `Allocated`.
- Tabla de líderes serverless (Lambda + DynamoDB) funcionando (práctica 3.5).
- Evidencias (capturas) en `evidencias/`.

**Juego jugable (cliente web 3D)**
- Vuelo con cámara trasera, aros que aparecen y desaparecen (6–20 s, se achican, inclinados, exclusivos), 8 nidos de salida, 3 bots, suministros con armas (misil, mina, escudo), eventos de clima (tormenta, nieve, avión, tornado), zona límite con halcón peregrino, minimapa y sonidos.
- Gana el primero a 100 puntos o el mejor a los 3:00. Funciona sin servidor (modo práctica) y en multijugador contra el servidor del juego.

## Falta
1. Práctica 3.4: Prometheus/Grafana, pruebas de carga con Locust (1 000 jugadores, 500 espectadores) y reporte con gráficas. Autoescalado de nodos ya escrito en Terraform, falta aplicarlo.
2. Práctica 3.2: pipeline CI/CD con GitHub Actions.
3. Práctica 3.1: bot de IA en Colab (CPU vs GPU).
4. Publicar el cliente (S3 sitio web http) y conectarlo a la tabla de líderes.
5. Reporte técnico, presentación y `terraform destroy` final.

## Dudas para el profe
1. ¿Se evalúa el juego o la infraestructura? ¿Basta con el servidor de partida más bots de carga que simulan jugadores?
2. La cuenta AWS tiene USD 140 de crédito: ¿hay límite de vCPU para simular 1 000 jugadores (~30 vCPU)?
3. Streaming: ¿alcanza con espectadores simulados sobre un video HLS de prueba (S3 + CloudFront)?
4. IA: ¿vale entrenar un bot sencillo (CartPole) como pide el material?
5. Somos 2 personas y el material habla de 3–4: ¿se ajusta el alcance?
6. Formato de entrega final (16/11): ¿repo + reporte de 6 páginas + presentación de 10 minutos?

## Limitaciones conocidas
- Los puntos y golpes los decide cada cliente (se podría hacer trampa); en producción los validaría el servidor.
- Los bots corren dentro de cada navegador, no en el servidor.
