# ✈️ Ruta del Cóndor — Unidad 3 (Infraestructura y despliegue de videojuegos en la nube)

Juego multijugador de carreras aéreas (aviones) desplegado en AWS con contenedores, Kubernetes + Agones, serverless e infraestructura como código.
Autores: Diego Reyes Natilla · José Heriberto Osorio.

## Estructura
| Carpeta | Qué contiene |
|---|---|
| `cliente/` | Juego en el navegador (`index.html` + `lib/three.min.js`, sin internet). Menú con 6 skins, mejoras permanentes visibles en el avión, cajas por rareza con aviso, Núcleo legendario, radar, copiloto, controles táctiles y modo práctica con bots. |
| `server/` | Servidor de partida (Python, WebSocket, 20 ticks/s, métricas Prometheus), `Dockerfile` y tests. |
| `k8s/` | Flota y autoescalado de Agones, monitor de Prometheus, asignación de partida. |
| `infra/` | Terraform: VPC, EKS, ECR, Agones (Helm), Cluster Autoscaler, Lambda + DynamoDB. |
| `serverless/` | Función Lambda de la tabla de líderes. |
| `evidencias/` | Capturas de las prácticas. |

## Cómo jugarlo
Doble clic en `Jugar.bat` (abre el servidor local, la web y el navegador). Sin servidor, la página entra sola en modo práctica.

## Infraestructura en AWS
Ver `APAGAR_Y_LEVANTAR_AWS.md` (crear/destruir con Terraform) y `GUION_DEMO.md`.

## Documentos
- `PARA_EL_PROFE.md` estado y dudas · `GUION_DEMO.md` demo de 5 min · `AUDITORIA.md` auditoría de seguridad · `PUBLICAR.md` cómo publicarlo.

## Entrega
- Lista de entrega y estado por práctica: `ENTREGA_CHECKLIST.md`
- Reporte técnico: `REPORTE_TECNICO.md` · Auditoría: `AUDITORIA.md`
- Prácticas: 3.1 `ia/` · 3.2 `.github/workflows/deploy.yml` · 3.3 `server/` + `k8s/` · 3.4 `loadtest/` · 3.5 `serverless/` · 3.6 `infra/`

## Pruebas
```
cd server && pip install -r requirements.txt pytest && pytest -q
```
