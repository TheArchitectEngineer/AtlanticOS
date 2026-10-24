# Proveedores de arranque y planificación — 2026-10-23

La ampliación selecciona 16 archivos adicionales del snapshot XNU fijado, sin
cambiar su contenido. También refuerza las comprobaciones de tres unidades ya
seleccionadas: cpu.c, cpu_common.c y lock_mtx.c. Son dependencias reales del
núcleo; su compilación no demuestra arranque, Platform Expert operativo ni un
BSP G20 funcional.

Upstream: xnu-12377.1.9, commit
f6217f891ac0bb64f3d375211650a4c1ff8ca1ea. Los hashes de los archivos y de los
objetos quedan en el reporte base; no se distribuye una copia de estos fuentes
bajo la licencia del proyecto.

| Fuentes nativas añadidas o comprobaciones ampliadas | Definiciones comprobadas en objetos ARM64 |
|---|---|
| pexpert/gen/bootargs.c, pexpert/arm/pe_bootargs.c | PE_parse_boot_argn, PE_parse_boot_arg_str, PE_boot_args, PE_get_default |
| pexpert/gen/device_tree.c | SecureDTInit, SecureDTLookupEntry, SecureDTGetProperty e iteradores |
| kern/sched_rt.c, arm/preemption_disable.c | colas RT, selección de hilo, timebase y control nativo de preempción |
| kern/compact_id.c, kern/mpsc_queue.c | IDs compactos, colas daemon y deallocation diferida de hilos |
| kern/thread_group.c, kern/restartable.c | grupos de hilo y registro/sincronización de rangos restartable |
| kern/machine.c, arm/cpu_common.c, arm64/cpu.c | machine_info, processor_up, CpuDataEntries, cpu_data_init y soporte CPU |
| arm64/status.c, arm64/lowmem_vectors.c, arm/machine_cpuid.c | estado de hilo, low globals y lecturas MIDR/CLIDR/CCSIDR |
| kern/backtrace.c, kern/btlog.c, kern/lock_mtx.c, bsd/kern/qsort.c | backtraces, diagnóstico de allocations, mutexes y ordenación nativos |

Los prefijos kern/, arm/ y arm64/ de la tabla corresponden a osfmk/. Los
símbolos exigidos por el builder incluyen funciones sustantivas. En particular,
cpu_bootstrap tiene un cuerpo vacío en upstream: encontrar ese símbolo no
acredita inicialización de CPU. También se exigen cpu_data_init, cpu_stack_alloc
y cpu_timebase_init del mismo objeto, sin sustituirlos por implementaciones.

## Contextos de headers por componente

La receta anterior reutilizaba MACH_KERNEL_PRIVATE para todos los archivos.
Eso mezcla clock_t de Mach y tipos libsa con sys/types.h al compilar device_tree.c.
El intento fallido se conserva en work/ como diagnóstico de desarrollo.

La receta de Platform Expert ahora elimina MACH_KERNEL_PRIVATE y selecciona
PEXPERT_KERNEL_PRIVATE, según pexpert/conf/Makefile.template. El helper qsort
usa el contexto BSD_KERNEL_PRIVATE. Esto no habilita MACH_BSD ni IOKIT: sigue
vigente el perfil de firmware que rechaza BSD userland e IOKit.
No se alteran typedefs nativos ni se suprimen los errores de tipos.

## Contrato pendiente con Platform Expert original

Los parsers nuevos dejan estas obligaciones abiertas:

1. **Argumentos.** PE_boot_args obtiene CommandLine mediante PE_state.bootArgs.
   El Platform Expert original de AtlanticOS debe construir y conservar el
   boot_args compatible, validar el límite y terminador de la línea, y mantener
   su memoria válida durante el uso. El parser no crea ese estado por sí mismo.
2. **Árbol.** SecureDT consume la representación nativa de XNU: cabecera de nodo
   con dos uint32_t, nombres de propiedad de 32 bytes, longitud de 32 bits y
   valor alineado a cuatro bytes. Los enteros de esa estructura son nativos
   del target; no se interpreta un DTB Linux con un cast. Los valores de las
   propiedades tienen además esquemas específicos de cada consumidor.
3. **Conversión.** El [puente original posterior](BOOT_DATA_BRIDGE.md) valida e
   inventaría el FDT y produce un árbol separado para DRAM y CPU primaria. Las
   exclusiones permanecen aparte y todavía deben integrarse con el allocator/MMU.
   Faltan bindings de periféricos y ejecución del consumidor real; copiar valores
   reg/clocks sin interpretar sus celdas y esquema no establece compatibilidad.
4. **Defaults.** PE_get_default conserva primero la búsqueda nativa de /defaults
   y solo cae a IODTGetDefault cuando no encuentra ese nodo. El enlace aún exige
   ese proveedor. Hay que acotar el fallback al IOKit seleccionado y documentar
   la ausencia de defaults en firmware, sin inventar un servicio IOKit.
5. **CPU e interrupciones.** Los datos nativos de CPU necesitan stacks, puntero
   de hilo/CPU, MMU y topología válidos. Las rutinas cpu_signal y de idle siguen
   dependiendo del BSP y de métodos de alimentación/IRQ por verificar. No se
   ejecutan durante estas comprobaciones de compilación.

No se selecciona pe_init.c de Apple como implementación de la plataforma G20.
El parser de árboles reutiliza XNU auténtico; el adaptador, Platform Expert y
los drivers de cada dispositivo siguen siendo responsabilidad de AtlanticOS.

## Verificación

Compilan 123 unidades experimentales y 13 estándar, sin fallos. Se generan los
57 headers MIG y compilan 42 probes RPC por carril; CFILES selecciona 26 para
el enlace. Pasan los 51 checks de alcance/ABI experimentales y los 45 estándar,
con 21 descriptores RPC y los 14 subsistemas requeridos por kobject experimental.
Los defines y las 137 constantes genassym coinciden con la revisión de 107 unidades.

El enlace estricto experimental de **149 objetos** con LLD v2 falla con exit 1:
**672 diagnósticos indefinidos, cero duplicados y ningún archivo de salida**.
Frente al enlace anterior de 765 nombres, se resuelven 109 e ingresan 16
dependencias nuevas. La [comparación de nombres](../evidence/xnu-boot-providers-20261023/link-dependency-delta.json)
permite revisar ambas listas; ese cambio no equivale a 109 servicios ejecutados.
El carril estándar de 39 objetos conserva 829 diagnósticos y el rechazo de
las opciones estáticas upstream, también sin imagen.

La [evidencia nueva](../evidence/xnu-boot-providers-20261023/manifest.json) contiene
88 artefactos con hashes. Las pruebas previas del compilador v2 (26 checks) y de
LLD v2 (54 checks, 15 imágenes) se reutilizan tras cotejar sus inputs y binarios;
esta revisión no reconstruye esas herramientas. Los probes de ipc_policy y
mach_debug siguen fallando; SLEH y pageout compilan y están seleccionados.

La CI host y la estándar del commit 4e573de terminaron con success:
[host](https://github.com/h0nda1337/AtlanticOS/actions/runs/40049556590),
[XNU estándar](https://github.com/h0nda1337/AtlanticOS/actions/runs/40049556545).
La reconstrucción experimental de aquel commit seguía en curso al cerrar esta
evidencia. Esos runs corresponden a la revisión anterior de 107 unidades y no
acreditan las 123 de esta ampliación.

Las pruebas de alcance/ABI siguen siendo pruebas de objetos y preprocesado.
El protocolo físico de [DEVICE_TEST_PLAN](DEVICE_TEST_PLAN.md) conserva las
puertas de carga temporal y recuperación independiente de Android. Todavía no
hay imagen XNU para ejecutarlo, handoff a EDK2 o consumo RAM firmware medido.

## Reproducir

Con las fuentes fijadas, MIG y el proveedor explícito ya comprobados:

```sh
python3 tools/build_xnu_lab.py --layout-compiler <clang-v2> --layout-proof <prueba-api-v2>
python3 tools/build_xnu_rpc.py --build <reporte-base>
python3 tools/test_xnu_rpc.py --build <reporte-base> --rpc <reporte-rpc> --output work/provider-rpc-check
python3 tools/diagnose_xnu_link.py --build <reporte-base> --rpc <reporte-rpc> --linker <lld-v2> --atlantic-static-proof <prueba-lld-v2> --output work/provider-link-check
```

En WSL/NTFS, añadir --windows-git a los dos builders. El [modo LLD estático](LLD_STATIC_ARM64.md)
requiere su prueba vigente y una carpeta nueva por intento. Las recetas exactas
de compilación, defines, archivos y hashes se conservan en la evidencia.
