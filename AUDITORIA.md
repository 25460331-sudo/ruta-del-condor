# Auditoría del juego (cliente + servidor)

Revisión de seguridad, robustez y rendimiento antes de publicar. Cada hallazgo indica si quedó corregido.

## Hallazgos corregidos
| # | Problema | Riesgo | Corrección |
|---|---|---|---|
| 1 | Los nombres de otros jugadores se insertaban con `innerHTML` (ranking y pantalla de resultados) | **XSS**: un jugador podía ejecutar código en los demás | Nombres limpiados al recibirlos (`NOM`) y escapados al mostrarlos (`esc`). Probado con `<img onerror=…>` |
| 2 | Los datos de la red se usaban sin validar (NaN, números enormes, listas gigantes) | Congelar o romper el juego de los demás | `limpiarOtros`: números acotados, listas con tamaño máximo, tipos forzados |
| 3 | `JSON.parse` sin `try/catch` | Un mensaje corrupto detenía el cliente | Se ignora el mensaje inválido |
| 4 | El servidor aceptaba cualquier JSON, de cualquier tamaño y a cualquier ritmo, y lo retransmitía tal cual | Abuso, denegación de servicio, datos falsos hacia otros clientes | Tamaño máx. 4 KB, máx. 60 mensajes/s, lista blanca de campos, validación de tipos y rangos, una conexión = una identidad, métrica `condor_messages_rejected_total`, keepalive. Probado con un cliente hostil |
| 5 | El juego cargaba three.js desde internet (CDN) | No arranca sin internet o con internet lento | three.js incluido en `cliente/lib/` (el juego funciona 100 % sin conexión) |
| 6 | Sin manejo de errores ni de equipos sin WebGL | Pantalla en blanco sin explicación | Pantalla de error amigable con botón *Recargar* |
| 7 | Al escribir el nombre se activaban los controles (M, R, F, espacio) | Mala experiencia | Los campos de texto ignoran los atajos |
| 8 | El conjunto `golpeados` crecía sin límite | Fuga de memoria en sesiones largas | Se limpia en cada partida |
| 9 | Rendimiento fijo | Equipos lentos con tirones | Calidad Alta/Media/Baja y bajada automática si los FPS caen |
| 10 | El audio seguía sonando con la pestaña oculta | Molesto | Se silencia al ocultar la pestaña; volumen y silencio se recuerdan |
| 11 | Ajustes en `localStorage` sin protección | Error si el navegador lo bloquea | Acceso envuelto en `try/catch` |

## Riesgos que siguen abiertos (honestidad)
1. **El cliente decide puntos, golpes y aros** (modelo "confiar en el cliente"): un tramposo puede falsearlos. Una versión comercial validaría las reglas en el servidor.
2. **Los bots corren en cada navegador**, no en el servidor: dos jugadores ven bots distintos.
3. **Sin cuentas ni autenticación**; cualquiera con la dirección del servidor puede entrar.
4. **Sin TLS en el servidor**: una página `https` no puede conectarse a `ws://` (el navegador lo bloquea). Para multijugador público hace falta `wss://` (balanceador con certificado). Mientras tanto el juego cae solo al modo práctica.
5. **La imagen de Docker en AWS es la anterior**: el servidor endurecido (`server/server.py`) está listo, pero hay que reconstruir y subir la imagen para que AWS lo use.
6. **No hay pruebas automáticas del navegador** y no se probó con varias personas reales a la vez ni se escucharon los sonidos.
7. three.js r128 es una versión antigua (estable, sin fallos conocidos para este uso).

## Ronda 2 (mejoras, armas y copiloto)
- El servidor valida también los campos nuevos (`up`, `sk`, `hp`, `mg`, `cd`, `gc`, `ov`, `tb`) con rangos y tamaños máximos; hay 8 tests.
- Daño por ametralladora y misiles lo decide la **víctima** (cada cliente es dueño de su avión), igual que antes: sigue siendo posible hacer trampa desde un cliente modificado.
- El copiloto y el tutorial se pueden apagar en Ajustes.
