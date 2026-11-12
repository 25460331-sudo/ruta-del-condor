# Cómo publicar el juego

El juego es una carpeta estática: **`cliente/`** (un `index.html` y `lib/three.min.js`). No necesita internet ni compilar nada.
Sin servidor entra solo al **modo práctica** (con bots). También se puede abrir directo con `index.html?solo`.

## Opción A — La más rápida (sin AWS)
Subir la carpeta `cliente/` completa a cualquiera de estos servicios (arrastrar y soltar):
- **Netlify Drop** (app.netlify.com/drop) o **GitHub Pages** o **itch.io** (subir como "HTML5").
- Resultado: un link público. Funciona en modo práctica (las páginas `https` no pueden usar el servidor `ws://`).

## Opción B — En AWS (S3 sitio web)
Con sesión iniciada (`aws login`) y en la carpeta del proyecto. Cambiar `TU-ID` por algo único:
```
aws s3 mb s3://ruta-condor-TU-ID --region us-east-1
aws s3api put-public-access-block --bucket ruta-condor-TU-ID --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
aws s3 sync cliente s3://ruta-condor-TU-ID --exclude "*.bak"
aws s3 website s3://ruta-condor-TU-ID --index-document index.html
```
Crear `politica.json` con esto (cambiando `TU-ID`) y aplicarlo:
```
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::ruta-condor-TU-ID/*"}]}
```
```
aws s3api put-bucket-policy --bucket ruta-condor-TU-ID --policy file://politica.json
```
Dirección: `http://ruta-condor-TU-ID.s3-website-us-east-1.amazonaws.com`
Para borrarlo después: `aws s3 rb s3://ruta-condor-TU-ID --force`.
Nota: las cuentas de laboratorio pueden bloquear buckets públicos; si da error, usar la Opción A.

## Multijugador público (opcional)
1. Reconstruir y subir la imagen del servidor (carpeta `server/`) a ECR y aplicar la flota (ver `APAGAR_Y_LEVANTAR_AWS.md`).
2. Tomar la dirección y puerto del servidor de partida: `kubectl get gameservers`.
3. En el juego, abrir **Ajustes** y poner `ws://DIRECCION:PUERTO`. Si la página es `http` funciona; si es `https`, el servidor necesita `wss://` (balanceador con certificado).

## Lista de comprobación antes de publicar
- [ ] Abrir `index.html?solo` y jugar una carrera completa.
- [ ] Probar en el celular (controles táctiles) y con calidad Baja.
- [ ] Revisar `AUDITORIA.md` (riesgos abiertos).
- [ ] Si hay servidor público: reconstruir la imagen con el `server.py` nuevo.
