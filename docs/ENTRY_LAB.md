# Preflight ARM64 original — etapa de laboratorio

El código en atlantic-entry/ se ensambla desde fuente propia. Tiene header Image
AArch64, stack propio, captura de x0-x3/EL/SCTLR/DAIF/MPIDR/contador/VBAR/TCR/TTBR0,
vectores de excepción y validación FDT acotada. No enlaza ni ejecuta XNU.

Las direcciones UART/RAM y la salida semihosting viven exclusivamente en
platforms/qemu-virt/early.c. La entrada común acepta EL1/EL2 con MMU OFF; no
desactiva mapas desconocidos y no accede a registros EL2 desde EL1. No se ha
implementado aún una transición EL2→EL1 para XNU. Capturar estado y construir
vectores no equivale a inicializar Mach, GIC o VM.

Reproducir en Linux/WSL, con Clang, LLD, llvm-objcopy y QEMU AArch64:

```sh
python3 tools/test_freestanding.py --sanitize
python3 tools/build_entry.py
python3 tools/emulate_entry.py
```

build_entry solo permite el BSP qemu-virt. No genera boot.img para teléfono ni
incluye comandos de dispositivos. El ELF y binario Image derivan del mismo
enlace, con hashes y mapa. El tamaño retenido incluye BSS/stack, no solo archivo;
la cifra no representa memoria residente XNU ni prueba la meta de 100 MiB.

emulate_entry crea una máquina sin red o discos y comprueba desde las trazas que
el EL observado coincide con cada ejecución esperada. Semihosting se usa solo
para finalizar el test, nunca para acceder a archivos del host desde el payload.
Los logs incluyen literalmente XNU_NOT_LINKED y NO_XNU_BOOT_CLAIM.

FDT: implementación original, sin código libfdt importado. Verifica header v17,
bounds/alineación/solapamientos, tabla memreserve con terminador y overflow,
nombres/propiedades acotados, raíz única, balance de nodos, profundidad máxima,
orden propiedades/hijos y END. El BSP debe probar primero que el buffer entero
es RAM legible; validar un header no hace segura una dirección física arbitraria.
Todavía no se extrae un mapa allocator ni se convierte a SecureDT/boot_args XNU.

Pruebas host C incluyen truncamientos, offsets inválidos, tamaño desbordado,
reservas y overflow, profundidad excesiva y 10 000 mutaciones con ASan/UBSan.
Las ejecuciones ARM64 con DTB QEMU son EMULATED de este componente únicamente.

Referencia del contenedor: [protocolo Image AArch64](https://www.kernel.org/doc/html/latest/arch/arm64/booting.html).
No es una implementación Linux ni reutiliza su kernel, entry o drivers.
