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

Pendiente: T01 entrada física por botones y retorno stock independientes; T02
slot-successful/unbootable/retry y tamaños de partición por consultas fastboot;
T03 firmware exacto/header/DTB; T04 ruta temporal real. El usuario realizará la
transición física y avisará; ninguna herramienta reinicia automáticamente.

Referencia de la secuencia física: [soporte Motorola, pasos de entrada 2-3](https://en-us.support.motorola.com/app/answers/detail/a_id/150983/~/reset-phone).
Se usa únicamente entrada al menú, **no** el procedimiento de borrado del artículo.
Semántica A/B: [documentación oficial AOSP](https://source.android.com/docs/core/ota/ab/ab_implement).
