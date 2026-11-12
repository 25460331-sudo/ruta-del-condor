# Apagar y volver a levantar AWS

Usar siempre un **CMD nuevo** (cierra el viejo): las credenciales viejas dan error.

## 🔴 APAGAR (para de cobrar)
```
aws login
cd "C:\Users\diego\Desktop\Apps - Nube\Juego\infra"
for /f "delims=" %i in ('aws configure export-credentials --format windows-cmd') do %i
terraform destroy
```
Escribir `yes`. Tarda 10–15 min. Al final debe decir `Destroy complete!`.
**Sacar captura de esa pantalla** (entregable de la práctica 3.6).
Si da `ExpiredToken`, repetir los pasos desde `aws login` (retoma donde quedó).
Si falla borrando la VPC, esperar 2 min y volver a correr `terraform destroy`.

## 🟢 LEVANTAR (de nuevo)
Mismos 3 primeros pasos que arriba, y después:
```
terraform apply
```
Escribir `yes` (15–20 min). Luego, en el mismo CMD:
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 130841269953.dkr.ecr.us-east-1.amazonaws.com
docker push 130841269953.dkr.ecr.us-east-1.amazonaws.com/condor-server:1.0
aws eks update-kubeconfig --name condor-default --region us-east-1
kubectl apply -f ..\k8s\fleet.yaml -f ..\k8s\autoscaler.yaml
kubectl get gameservers
```
Si `docker push` dice que no existe la imagen, primero (desde la carpeta `server`):
```
docker build -t condor-server:1.0 .
docker tag condor-server:1.0 130841269953.dkr.ecr.us-east-1.amazonaws.com/condor-server:1.0
```
Nota: la URL de la tabla de líderes cambia al recrear; sale en los `Outputs` del `apply`.
