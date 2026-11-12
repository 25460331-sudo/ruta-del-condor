# Práctica 3.4 — Guía paso a paso (AWS)

Antes: clúster levantado (`APAGAR_Y_LEVANTAR_AWS.md`), imagen subida y flota aplicada (`kubectl get gameservers` con servidores `Ready`).
Todo en un **CMD nuevo** con `aws login` + `export-credentials` hechos.

## 1. Monitoreo (Prometheus + Grafana)
```
aws eks update-kubeconfig --name condor-default --region us-east-1
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoreo prometheus-community/kube-prometheus-stack -n monitoring --create-namespace --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
helm upgrade agones agones/agones -n agones-system --reuse-values --set agones.metrics.serviceMonitor.enabled=true
kubectl apply -f ..\k8s\podmonitor.yaml
kubectl port-forward -n monitoring svc/monitoreo-grafana 3000:80
```
Contraseña de Grafana (usuario `admin`), en otro CMD:
```
kubectl get secret -n monitoring monitoreo-grafana -o jsonpath="{.data.admin-password}"
```
(el resultado está en base64: decodificarlo en https://www.base64decode.org o con PowerShell `[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String("..."))`).

Paneles de Grafana (http://localhost:3000 → Dashboards → New):
| Panel | Consulta |
|---|---|
| Jugadores conectados (CCU) | `sum(condor_players_connected)` |
| Tick p99 (ms) | `histogram_quantile(0.99, sum by (le) (rate(condor_tick_seconds_bucket[1m]))) * 1000` |
| Servidores por estado | `sum by (type) (agones_gameservers_count{fleet_name="condor-fleet"})` |
| Nodos del clúster | `count(kube_node_info)` |
| Mensajes rechazados | `sum(rate(condor_messages_rejected_total[1m]))` |

## 2. Generador de carga (en AWS, misma región)
Una VM `t3.xlarge` (o mayor) en `us-east-1` con Python: instalar `pip install locust websocket-client requests pandas matplotlib`.
Si tu conexión doméstica es lenta, **no corras Locust desde tu casa**: agregaría su propia latencia.
Certificados del allocator (desde tu PC con kubectl) y copiarlos a la VM junto con `locustfile.py`:
```
kubectl get secret allocator-client.default -n default -o jsonpath="{.data.tls\.crt}"
kubectl get secret allocator-client.default -n default -o jsonpath="{.data.tls\.key}"
kubectl get secret allocator-tls-ca -n agones-system -o jsonpath="{.data.tls-ca\.crt}"
kubectl get svc agones-allocator -n agones-system -o jsonpath="{.status.loadBalancer.ingress[0].hostname}"
```
(los tres primeros salen en base64: guardarlos decodificados como `client.crt`, `client.key`, `ca.crt`). Si el certificado no incluye el nombre del balanceador: `set VERIFY_TLS=0` (solo laboratorio).

## 3. Escenarios (dimensionar antes: la cuota de vCPU de la cuenta limita)
1 000 jugadores ≈ 125 servidores × 0,25 vCPU ≈ 31 vCPU + sistema. Una cuenta nueva suele permitir ~32 vCPU de instancias estándar: **pedir aumento de cuota** (Service Quotas → EC2 → "Running On-Demand Standard instances") o usar la versión reducida del material (**300 jugadores y 200 espectadores**).
```
export ALLOCATOR_URL=https://<host-allocator>/gameserverallocation
locust -f locustfile.py Jugador -u 300 -r 2 -t 20m --headless --processes -1 --csv rampa
locust -f locustfile.py Jugador -u 300 -r 50 -t 10m --headless --processes -1 --csv pico
python analizar.py rampa pico
```
Anotar para el reporte: capacidad (jugadores por nodo donde el p95 cruza 80 ms), **segundos que tardó en reaccionar** el autoescalado (línea de tiempo de servidores y nodos en Grafana), errores durante el pico.

## 4. Espectadores (muestra pequeña + extrapolación)
Stream de prueba de 5 min a 360p (necesita ffmpeg) y publicado en S3 como sitio web:
```
ffmpeg -f lavfi -i testsrc2=size=640x360:rate=30 -t 300 -c:v libx264 -preset veryfast -b:v 800k -maxrate 800k -bufsize 1600k -g 60 -hls_time 2 -hls_playlist_type vod -hls_segment_filename "360p_%03d.ts" 360p.m3u8
aws s3 mb s3://condor-stream-TU-ID
aws s3 cp . s3://condor-stream-TU-ID/live/condor/ --recursive --exclude "*" --include "360p*"
```
(hacerlo público como en `PUBLICAR.md`). Luego: `locust -f locustfile.py Espectador --host http://condor-stream-TU-ID.s3-website-us-east-1.amazonaws.com -u 200 -r 50 -t 5m --headless --csv stream`.
Fórmula de egress: `GB/hora = espectadores × bitrate(kbps) × 3600 / (8 × 10^6)`. Extrapolar a 20 000 espectadores a 6 000 kbps (≈ 54 TB/h).

## 5. Al terminar
`terraform destroy` (ver `APAGAR_Y_LEVANTAR_AWS.md`) y capturar el final.
