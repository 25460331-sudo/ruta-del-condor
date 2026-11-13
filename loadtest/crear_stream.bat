@echo off
rem Practica 3.4 - stream de prueba para espectadores (video de 5 min a 360p, HLS) en un S3 publico.
rem Antes: aws login   (en esta misma ventana)
set BUCKET=condor-stream-nube2026a
set CARPETA=%TEMP%\condorstream
echo [1/4] Generando el video de prueba (1 minuto)...
mkdir "%CARPETA%" 2>nul
cd /d "%CARPETA%"
ffmpeg -y -loglevel error -f lavfi -i testsrc2=size=640x360:rate=30 -t 300 -c:v libx264 -preset veryfast -b:v 800k -maxrate 800k -bufsize 1600k -g 60 -hls_time 2 -hls_playlist_type vod -hls_segment_filename "360p_%%03d.ts" 360p.m3u8
if errorlevel 1 goto error
echo [2/4] Creando el bucket %BUCKET% (publico, solo para esta prueba)...
aws s3 mb s3://%BUCKET% --region us-east-1
aws s3api put-public-access-block --bucket %BUCKET% --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
echo {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::%BUCKET%/*"}]}> politica.json
aws s3api put-bucket-policy --bucket %BUCKET% --policy file://politica.json
echo [3/4] Subiendo el video...
aws s3 cp . s3://%BUCKET%/live/condor/ --recursive --exclude "*" --include "360p*"
aws s3 website s3://%BUCKET% --index-document 360p.m3u8
echo [4/4] Listo. Probar en el navegador:
echo http://%BUCKET%.s3-website-us-east-1.amazonaws.com/live/condor/360p.m3u8
goto fin
:error
echo Fallo ffmpeg. Avisa a Claude con lo que dice arriba.
:fin
pause
