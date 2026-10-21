# Factibilidad del port auténtico de XNU

Conclusión de Fase 0: existe fuente ARM64 real para comenzar investigación,
pero **no hay build ni port AtlanticOS funcional**. No se puede prometer aún
que XNU reducido entre en 100 MiB ni que el conjunto público cierre dependencias
sin SDK/herramientas adicionales. Riesgo técnico alto; siguientes pruebas acotadas.

Se selecciona el tag oficial `xnu-12377.1.9`, commit
`f6217f891ac0bb64f3d375211650a4c1ff8ca1ea`, como base auditada, no como afirmación
de ser la última versión disponible. Está intacto en xnu-upstream, excluido del
Git principal y fijado por dependencies.lock.json. No se importa un port ajeno.
Todos los archivos examinados tienen enlaces y hashes [X01-X12](SOURCE_INDEX.md#x01).

## Dependencias observadas

| Componente upstream | Utilidad real / adaptación necesaria |
|---|---|
| osfmk/arm64/start.s, X04 | entry Apple, assym.s generado, sintaxis Mach-O @page/@pageoff, VBAR/TTBR/SCTLR EL1; adaptador original y configuración de CPU |
| osfmk/arm/arm_init.c, X05 | PE_init_platform, cpu_data_init, configuración de registros Apple, VM y machine_startup; auditar cada camino condicional |
| osfmk/kern/startup.c, X06 | bootstrap VM/zonas, threads, IPC, scheduler, clock_service_create y PE_init_iokit; preservar secuencia real con trazas |
| pexpert/arm/pe_init.c, X07 | callbacks PE, arranque consola y device tree; Platform Expert G20 original |
| pexpert/pexpert/arm64/boot.h, X08 | boot_args no es ABI Linux ni FDT binario compatible |
| pexpert/arm/pe_identify_machine.c, X12 | SecureDT y descubrimiento de MMIO según representación Apple; adaptar sin inventar nodos o casts |
| pmap / VM / ARM page tables | mapa virtual, tamaño de página, coherencia y TLB; medir capacidades CPU antes de elegir flags |
| libkern / libsa / IOKit | inicialización C++, allocators y dependencias cruzadas; no suponer que basta borrar directorios |
| BSD | configuración ARM64 estándar incluye mach_bsd y políticas; generar grafo de símbolos antes de recortar |
| config/MASTER.arm64, X03 | RELEASE/DEVELOPMENT incorporan redes, FS, seguridad, IOKit, VM; no existe perfil AtlanticOS ya listo |
| makedefs/MakeInc.cmd, X02 | xcrun, SDKROOT/HOST_SDKROOT, clang, mig/migcom, iig, linker y herramientas de símbolos; CTF tiene condiciones opcionales |
| makedefs/MakeInc.def:1095 | LD_KERNEL_LIBS incluye -lcc_kext: proveedor no resuelto en este entorno |

VMAPPLE define HAS_GIC_V3 y hay código en pe_fiq.c. Es relevante: XNU público
no carece por completo de GICv3. **No es una configuración UMS512 reutilizable**:
VMAPPLE declara PAC, SME/SME2, PAN3 y otras capacidades que no deben asumirse en
T700. La ruta GIC observada configura Group0/PPI27 y espera un árbol específico;
verificar seguridad/grupos y permisos del firmware OEM antes de adaptarla.

## Herramientas y obstáculos

Host observado: Windows, Python 3.11.9, Git 2.54.0.windows.1, Clang 22.1.4,
LLD/llvm-readobj disponibles. El objeto BSP puede compilarse para aarch64-none-elf;
eso solo demuestra toolchain de C freestanding, no build Mach-O XNU.

Actualización 2026-10-21: [XNU_LAB_BUILD](XNU_LAB_BUILD.md) ya compila once
unidades XNU reales como objetos Mach-O ARM64, con Clang 19, config y MIG
oficiales y cuatro parches originales. La generación de offsets usa el target.
No hay kernel enlazado ni ejecución; thread.c y vm_map.c siguen fallando.

xcrun y SDK Apple no están configurados en esta sesión. MIG oficial ya se construyó
como herramienta host aislada ([receta](MIG_HOST_BUILD.md)) y conectado al build
incremental de laboratorio; falta completar el kernel y sus herramientas. El Makefile público
resuelve herramientas mediante xcrun. El README usa SDKROOT y ejemplos internal;
no afirmar que todos sus caminos requieran necesariamente un SDK privado.
Separar tres investigaciones: headers/generados públicos, herramientas abiertas
reproducibles y dependencias realmente no disponibles. `-lcc_kext`, Img4 y
subsistemas de seguridad requieren inventario de símbolos/licencias antes de
decidir reemplazo auditado, recorte o BLOCKED. No añadir stubs que retornen éxito
en funciones de seguridad/VM/IPC para conseguir un enlace aparente.

Ruta propuesta: primer perfil uniprocesador, sin userland, carga dinámica de
kexts, GPU, sockets ni FS; conservar Mach VM, allocator, scheduler, timer y un
hilo de kernel real. Medir tamaño de símbolos y memoria después de cada recorte.
Un shim con printf y while(1) no cumple el objetivo. QEMU virt con BSP propio
puede probar entry/GIC/Mach en otra plataforma, pero nunca sustituir evidencia G20.
El modelo Python actual no recibe etiqueta EMULATED: no ejecuta instrucciones ARM.

## Experimentos de salida de factibilidad

1. Generar headers/assym/config del perfil mínimo y registrar versiones, comandos
   y hashes. Clasificar cada símbolo no resuelto por upstream público, generado,
   librería externa o privado. No buscar un port ajeno como solución terminada.
2. Ensamblar y enlazar rutas upstream instrumentadas con Platform Expert original
   primero en BSP de laboratorio, con mapa/stack/panic/log verificables.
3. En teléfono, capturar entrada/EL y contador con entry propio y recuperación
   independiente. Después validar IRQ y VM antes de bootstrap Mach.
4. Registrar upstream start/arm_init/kernel_bootstrap y transición de un hilo
   o servicio Mach/timer válido. Verificar PC/símbolos contra imagen hasheada.
5. Medir RAM incluyendo heap, stacks, tablas, framebuffer, DMA y reservas; reportar
   excedente si existe. La meta 99 MiB provisional no es una medición.

La denominación **XNU portado en G20** requiere el paso 4 en dispositivo con
evidencia física. Build, boot de un stub o log con el texto XNU no son suficientes.

APSL 2.0 se conserva íntegra en LICENSES-and-NOTICES/XNU-APPLE_LICENSE; cada
archivo conserva también sus avisos CMU/BSD/etc. Revisar obligaciones por archivo
antes de distribuir binarios y publicar los parches correspondientes. El código
original MIT no cambia la licencia de XNU ni de referencias externas.
