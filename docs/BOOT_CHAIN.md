# Cadena de arranque y puntos de inserción

Modo A prioritario: bootloader OEM muestra su Orange State, si corresponde,
y después carga una imagen aceptada con entry ARM64 propio AtlanticOS.
AtlanticOS dibuja su pantalla. Esa invitación solo existe después de recibir
control, nunca durante la pantalla OEM.

Modo B: integración bajo el aviso OEM, `BLOCKED_BY_BOOTLOADER`. Haría falta un
contrato OEM documentado o modificación separada, autorizada y recuperable del
bootloader. Un boot.img no añade texto a una pantalla ejecutada antes de él.

El port G20 de referencia declara una entrada U-Boot con Image en `0x80080000`,
x0/DTB `0x82000000`, EL2 y MMU/cachés apagados ([S05/S07/S17](SOURCE_INDEX.md)).
Son observaciones de ese port: todavía no se han repetido con entry AtlanticOS.
No debe tratarse toda la DRAM declarada como memoria libre.

Su build portable recompila seis módulos y los inserta en una base previa,
conservando wrapper y otros módulos ([S04/S15](SOURCE_INDEX.md)). Eso prueba un
proceso de aquel proyecto, no una cadena autónoma para AtlanticOS. No se han
descargado ni utilizado sus imágenes de arranque en este trabajo.

El contenedor de referencia comprueba magic ANDROID!, tamaño 64 MiB y transporte
en `0x1224000`; no basta para establecer el header Android real del teléfono
nuevo. **Versión de boot header, page size, DTB/DTBO/vendor_boot, firma OEM y
descompresión: UNKNOWN hasta analizar copia stock del firmware exacto.**
No se deduce `header_version` por la edad del modelo ni por un solo offset.

El protocolo Image AArch64 es una referencia para interpretar carga, x0 y
estado inicial; XNU usa su propio boot_args y formato de árbol. Se necesita un
adaptador propio, no renombrar un Image Linux ni castear un FDT a boot_args.

La vía preferida a investigar es carga temporal en RAM sin reemplazar stock.
Soporte de `fastboot boot` en esta variante: UNKNOWN; no se ha probado y no
es seguro inferirlo de que fastboot exista. Si el bootloader bloqueado no admite
payload propio, registrar BLOCKED y conservar el teléfono stock. Desbloquear
puede borrar datos y requiere un plan/permiso separado, fuera de esta fase.

Fuentes: [Android boot header](https://source.android.com/docs/core/architecture/bootloader/boot-image-header),
[protocolo AArch64](https://www.kernel.org/doc/html/latest/arch/arm64/booting.html).
