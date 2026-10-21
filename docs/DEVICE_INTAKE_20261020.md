# Inventario propio del Moto G20 — 2026-10-20

T00: 40 consultas ADB de solo lectura a un dispositivo físico autorizado. Las
33 respuestas no vacías están registradas; 4 propiedades vacías y 3 denegaciones
se conservan sin convertirlas en valores supuestos. No se consultó batería.
El usuario entregó el teléfono ya desbloqueado; AtlanticOS no lo desbloqueó.

Informe: [adb-intake.json](../evidence/device-intake-20261020/adb/adb-intake.json).
HOST_TESTED identifica la herramienta host y su alcance explícito de observación
ADB/USB. **No es DEVICE_VERIFIED de firmware AtlanticOS ni una prueba de XNU.**
Los originales permanecen privados en work/; el informe público redacta seriales.

| Dato consultado | Observación directa |
|---|---|
| Modelo / SKU | moto g(20), XT2128-1 |
| Dispositivo / placa | java / p352 |
| Hardware | ums512_1h10 |
| Fingerprint | motorola/java_retail/java:11/RTAS31.68-66-3/66-3:user/release-keys |
| Android / API | 11 / 30 |
| Parche de seguridad declarado | 2023-03-01 |
| Bootloader declarado | U-Boot 2015.07 (Feb 21 2023 - 13:36:54 +0800)SHARKL5PRO |
| ro.boot.flash.locked | 0 |
| ro.boot.vbmeta.device_state | unlocked |
| ro.boot.verifiedbootstate / veritymode | orange / enforcing |
| Slot Android / A/B declarado | _a / ro.build.ab_update=true |
| Arranque Android completado | sys.boot_completed=1 |
| Kernel ejecutado | Linux 4.14.193-ab66-3; no kernel AtlanticOS |
| Sesión ADB | uid=2000(shell), contexto SELinux shell; no root solicitado |
| MemTotal Android | 3 570 364 kB; no mide RAM XNU ni tamaño total de DRAM libre |

Se pudieron listar enlaces de particiones: boot_a/b, vendor_boot_a/b, dtb_a/b,
dtbo_a/b, vbmeta y super, entre otras. Solo nombres/symlinks: **ningún sector o
contenido de esas particiones fue leído**. La presencia de vendor_boot no basta
para establecer boot header v3/v4; el header exacto permanece UNKNOWN hasta T03.

El directorio de device tree es enumerable y contiene nodos como memory,
reserved-memory, psci, gpio-keys y interrupt-controller@12000000. Leer los valores
model/compatible devuelve Permission denied; también /proc/sys/kernel/osrelease.
Se conserva el error. No se llamó su/adb root ni se alteraron permisos/SELinux.
Los nodos no demuestran direcciones/timers/drivers funcionando en AtlanticOS.

El fingerprint y las propiedades de AVB son declaraciones del Android actual.
No prueban por sí solos integridad stock, firma de cada partición ni que el otro
slot sea arrancable. No se afirma AVB deshabilitado porque veritymode sigue
declarando enforcing. El Orange State observado como propiedad no es una foto
del aviso dibujado por el bootloader.

## Fastboot y regreso Android observados en la misma sesión

La secuencia de botones propuesta no dio entrada verificable; el usuario indicó
que no lograba entrar. No se concluye que los botones estén averiados. Se envió
una única solicitud explícita `adb -s <dispositivo> reboot bootloader` fuera del
colector y se detectó el mismo transporte fastboot a los 11.141 s de muestreo.
No se usó `adb reboot fastboot` ni se solicitó fastbootd.

[Transición registrada](../evidence/device-intake-20261020/transition/transition.json).
El colector fastboot consultó 28 variables permitidas, sin getvar all, OEM o
comandos de escritura. Solo dos devolvieron valores no vacíos:

| Variable | Respuesta / interpretación |
|---|---|
| version | 1.0; protocolo declarado, no versión de firmware |
| is-userspace | no; el dispositivo declara bootloader, no fastbootd |
| product, version-bootloader, secure, unlocked | Vacíos con exit 0: VALUE_NOT_CONFIRMED |
| current-slot, slot-count, has-slot y slot-successful/unbootable/retry | Vacíos con exit 0; no contradicen lo observado en Android ni prueban slots inválidos |
| partition-size, partition-type, max-download-size | Vacíos con exit 0; tamaños y capacidad de carga siguen UNKNOWN |

[Informe de fastboot](../evidence/device-intake-20261020/fastboot/fastboot-intake.json).
No se deriva soporte de boot temporal de la presencia de fastboot o del
desbloqueo. No se probaron comandos OEM desconocidos para suplir esas respuestas.

Se envió una única solicitud normal `fastboot -s <dispositivo> reboot` y Android
regresó: ADB reapareció en el muestreo de 16.469 s y boot_completed=1 se observó
en la iteración de aproximadamente 36 s, con el mismo fingerprint, slot `_a` y
flash.locked=0. [Registro de retorno](../evidence/device-intake-20261020/transition/return-android.json).
No se cambió slot, cargó imagen, leyó contenido de partición ni flasheó.

Esto comprueba Android → bootloader fastboot → Android mediante comandos OEM
normales. **No comprueba recuperación mediante botones ni retorno tras payload
AtlanticOS**. La capacidad android_fallback_verified de la BSP permanece false.
T01 sigue abierta; T02 tiene observaciones parciales con metadata A/B y tamaños
no disponibles; T03 firmware exacto/header/DTB y T04 boot temporal siguen UNKNOWN.
El teléfono se dejó en Android, no detenido en fastboot.

Referencia de la secuencia física: [soporte Motorola, pasos de entrada 2-3](https://en-us.support.motorola.com/app/answers/detail/a_id/150983/~/reset-phone).
Se usa únicamente entrada al menú, **no** el procedimiento de borrado del artículo.
Semántica A/B: [documentación oficial AOSP](https://source.android.com/docs/core/ota/ab/ab_implement).
La diferencia bootloader/fastbootd y `is-userspace` está definida por
[AOSP fastbootd](https://source.android.com/docs/core/architecture/bootloader/fastbootd).
