@echo off
rem Abre el servidor del juego, la pagina web y el navegador con un solo clic.
cd /d "%~dp0"
start "Servidor del juego (no cerrar)" cmd /k "cd server && python server.py"
start "Pagina web (no cerrar)" cmd /k "cd cliente && python -m http.server 8080"
timeout /t 2 /nobreak >nul
start "" http://localhost:8080
