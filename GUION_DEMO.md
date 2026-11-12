# Guion de demo (5 minutos)

## 0. Antes de entrar (2 min, una sola vez)
- Abrir **CMD nuevo** → `aws login` (ver `APAGAR_Y_LEVANTAR_AWS.md` si algo falla).
- Doble clic en **`Jugar.bat`** (abre el servidor, la web y el navegador).
- Tener abierta la carpeta `evidencias/` y el archivo `PARA_EL_PROFE.md`.

## 1. El juego (1,5 min)
- Mostrar *Ruta del Cóndor*: salida desde los nidos, aros que se achican, bots, suministros, eventos (tormenta/tornado/avión/nieve), zona límite con halcón.
- Decir: "el servidor de partida es el mismo que corre en AWS dentro de un contenedor".

## 2. La infraestructura en AWS (2 min)
En un CMD (con `aws login` hecho y `cd` a `infra`):
```
kubectl get nodes
kubectl get gameservers
terraform output
```
- Explicar: Terraform creó red + EKS + ECR + Agones + Lambda/DynamoDB; Agones mantiene servidores listos (`Ready`) y asigna partidas (`Allocated`).
- Mostrar la tabla de líderes serverless:
```
curl <url_tabla_de_lideres>
```
- Mostrar las capturas de `evidencias/` (antes/después de la asignación).

## 3. Lo que falta y el plan (1 min)
- 3.4 pruebas de carga + Prometheus/Grafana, 3.2 CI/CD, 3.1 bot de IA, reporte.
- Hacer las 6 preguntas de `PARA_EL_PROFE.md`.

## Si algo falla en vivo
- Sin internet / sin AWS: usar el juego en modo práctica y las capturas de `evidencias/`.
- `ExpiredToken`: CMD nuevo y repetir `aws login` + `export-credentials`.
