# Entry ARM64 propio — preflight de laboratorio

entry.S y preflight.c implementan captura de estado y validación FDT para el BSP
de laboratorio QEMU. Se identifican como XNU_NOT_LINKED: no son bootstrap Mach.
Ver docs/ENTRY_LAB.md para comandos, evidencia y límites. El entry del G20 y su
contenedor propio siguen pendientes de formato/recuperación comprobados.
Sin BootShim, wrappers binarios externos o contenedor del port UEFI previo.
