# Entry ARM64 propio — preflight de laboratorio

entry.S y preflight.c implementan captura de estado y validación FDT para el BSP
de laboratorio QEMU. Se identifican como XNU_NOT_LINKED: no son bootstrap Mach.
Ver docs/ENTRY_LAB.md para comandos, evidencia y límites. El entry del G20 y su
contenedor propio siguen pendientes de formato/recuperación comprobados.
Sin BootShim, wrappers binarios externos o contenedor del port UEFI previo.

El [puente de datos](../docs/BOOT_DATA_BRIDGE.md) inventaría RAM, reservas y CPU
del FDT, añade exclusiones del DTB/imagen y produce el árbol de bootstrap XNU de
504 bytes. Se ejecuta en el preflight QEMU, sin invocar SecureDT ni el kernel.
