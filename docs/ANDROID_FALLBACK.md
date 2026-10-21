# Android independiente y recuperación

Estado actualizado 2026-10-20: teléfono conectado con desbloqueo previo del
usuario; identidad y Android actual observados por ADB. Se comprobó entrada
solicitada con adb reboot bootloader y regreso con fastboot reboot al mismo
fingerprint/slot. Después se observó Recovery tras acciones manuales y bootloader
tras selección del menú reportada por el usuario. El retorno se hizo con fastboot
reboot a petición del usuario; salida autónoma por Power y retorno tras payload
propio no probados. Ver DEVICE_INTAKE_20261020.md. No se habilita fallback AtlanticOS.
No hay scripts de flasheo, escritura de particiones, selección de slot, AVB o
desbloqueo. No se alteró el contenido de imágenes Android.

No saltar a boot_a/boot_b desde XNU. Son contenedores que requieren bootloader,
DT, ramdisk, autenticación y estado de CPU correctos. A/B no garantiza que ambos
slots sean arrancables: retries, successful y unbootable importan. No asumir
que la variante nueva usa la misma disposición o build del laboratorio anterior.

La evidencia externa V1 [S11/S19](SOURCE_INDEX.md#s11) muestra texto de reinicio
forzado y respuesta posterior ADB; eso apoya una vuelta a Android en aquella
prueba. V4 registra expresamente que no se revalidó [S10](SOURCE_INDEX.md#s10).
No demuestra la ruta AtlanticOS ni un Android bootable tras cualquier cambio.

Orden para demostrar independencia:

1. Registrar modelo exacto, build stock, estado de bloqueo/AVB, mapa de particiones
   permitido y variables A/B de solo consulta. No cambiar metadata.
2. Identificar combinaciones de botones OEM y verificar que arrancan stock y
   alcanzan bootloader/recovery desde apagado, sin depender de AtlanticOS o red.
3. Conseguir firmware stock correspondiente y verificar hashes/procedencia offline.
   Distinguir copia de firmware distribuible de respaldo único del dispositivo;
   no rootear ni leer particiones protegidas para obtenerlo en esta fase.
4. Documentar si el OEM admite boot temporal en RAM. Si no hay método aceptado
   y recuperable para payload propio, parar en BLOCKED sin sustituir un slot.
5. En una etapa autorizada posterior, cargar entry propio temporal y probar un
   retorno usando mecanismo OEM documentado. Repetir con hashes y power cycle.
   No activar persistencia/autoboot hasta tener esta prueba independiente.

La cuenta atrás real exige un registro ligado a placa, firmware y método de
retorno, target presente y verificado, además de autodiagnóstico. Nunca basta
un booleano guardado en settings. Un cambio de firmware invalida la evidencia.
El fixture host Android solo sirve a tests y nunca se exportará como evidencia
de plataforma ni autorización para una futura imagen real.

Si el retorno falla: permanecer en diagnóstico cuando sea viable y usar la ruta
OEM física independiente; no alternar slots, reintentar sin límite, modificar
GPT o desactivar verificación. El futuro procedimiento de instalación será
documento separado revisable con recuperación y autorización explícitas.

Referencia: [AOSP boot_control y variables A/B](https://source.android.com/docs/core/ota/ab/ab_implement).
