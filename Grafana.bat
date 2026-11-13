@echo off
rem Abre Grafana en http://localhost:3000 y reconecta solo si se corta.
rem Antes hay que haber hecho: aws login
echo Grafana en http://localhost:3000/d/condor-carga   (no cierres esta ventana)
:a
kubectl port-forward -n monitoring svc/monitoreo-grafana 3000:80
timeout /t 2 >nul
goto a
