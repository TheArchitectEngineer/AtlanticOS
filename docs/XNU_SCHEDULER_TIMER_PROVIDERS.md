# Timers, políticas de planificación y proveedores nativos — 2026-10-24

La ampliación selecciona diez unidades XNU para completar dependencias reales
de Mach IPC, scheduler y VM. Ocho fuentes permanecen intactas; la serie 0028
adapta dos límites de política. No incorpora un scheduler, timer, allocator o
identidad de proceso que imite XNU.

| Fuente nativa | Papel y límite |
|---|---|
| kern/mk_timer.c | Creación, armado, leeway, cancelación, expiración y liberación de puertos timer; depende de thread_call, IPC y zonas genuinos |
| kern/syscall_subr.c | Handoff, yield y depresión de prioridad con callbacks de timer reales |
| kern/timeout.c | Diagnóstico de timeouts con timebase y contabilidad de interrupciones; no demuestra IRQ ni PMU |
| kern/thread_policy.c | Políticas QoS, prioridad y turnstiles; se acotan dos callbacks de I/O BSD |
| kern/task_policy.c | Estado, herencia y actualización de políticas de tarea; se corrige una rama de error sin BSD |
| kern/affinity.c | Objetos y referencias de afinidad nativos; no demuestra multicore G20 |
| vm/vm_map_store_ll.c | Enlaces y coherencia de la lista de entradas VM, junto al backend RB ya seleccionado |
| kern/counter_common.c | Inicialización, allocation y operaciones de contadores nativos, incluidos per-CPU |
| kern/task_ident.c | Tokens nativos con validación de contexto y referencias; todavía depende de proveedores de proceso reales |
| kern/sfi.c | Rama upstream de SFI desactivado: controles devuelven KERN_NOT_SUPPORTED; no hay servicio SFI activo |

Las rutas son relativas a osfmk/ del snapshot fijado. Estos cuerpos son XNU y
conservan sus licencias; AtlanticOS aporta la selección, los ajustes y las
herramientas de integración.

## Ajustes de política

thread_policy.c declaraba rethrottle_thread solo con MACH_BSD, pero mantenía
dos llamadas fuera de esa selección. En firmware sin BSD se excluyen esas dos
llamadas. Se conserva el cambio efectivo de política, el bucle CAS del override
de I/O, las actualizaciones de prioridad y la propagación de turnstiles. Fuera
de firmware o con BSD, las llamadas originales permanecen seleccionadas.

send_resource_violation_with_fatal_port tenía una rama sin BSD que asignaba a
kr, declarado únicamente en el bloque BSD. La corrección devuelve directamente
el KERN_NOT_SUPPORTED previsto y mantiene finish/return dentro del alcance BSD.
La rama BSD conserva su salida preprocesada. No se fabrica un proc, PID,
notificación entregada ni resultado de éxito. Las notificaciones de recursos
sin BSD siguen sin estar soportadas.

## Qué no acreditan los objetos

mk_timer.c usa mach_absolute_time y thread_call de XNU. Compilarlo no demuestra
programación del timer físico, llegada de IRQ, latencia, cancelación concurrente
o entrega de mensajes. El backend BSP y su interrupción siguen pendientes.

task_ident.c conserva las llamadas a proc_find_ident/proc_ident_with_policy,
proc_task y proc_rele. No aporta esos proveedores ni inventa identidad BSD.
El constructor nativo rechaza kernel_task y contextos sin información válida;
no se declara un servicio de tokens operativo en firmware.

SFI conserva su rama desactivada original, incluida sfi_reevaluate vacía. Los
controles devuelven el error nativo de función no soportada. En timeout.c, las
consultas de ciclos/instrucciones con CONFIG_CPU_COUNTERS desactivado conservan
los ceros upstream; no son mediciones del PMU. Tamaños de objetos y contadores
no representan RAM residente de AtlanticOS.

## Comprobaciones reproducibles

tools/test_xnu_scheduler_providers.py coteja ocho fuentes intactas y dos
preimágenes/postimágenes. Comprueba cuatro combinaciones de selección, doce
cuerpos core conservados y el ABI de headers reales: slots de argumentos de
timers ARM64, deadline y dirección de salida de 64 bits, callback de labels,
creación de políticas y contadores per-CPU. Las variantes de deadline de 32
bits y de callback incorrecto deben ser rechazadas.

En experimental se inspeccionan los diez objetos, sus exports/imports fuertes,
la dependencia real del timer desde ipc_policy, el ciclo de callbacks, la
allocation per-CPU y las dependencias de identidad aún pendientes. Los retornos
de SFI desactivado y de notificación de recursos se comparan con una referencia
compilada desde KERN_NOT_SUPPORTED del header nativo. Esa referencia es una
fixture aislada; no se selecciona ni enlaza como proveedor del kernel.
El carril estándar conserva sus 13 unidades y solo comprueba fuentes/ABI.

```sh
python3 tools/build_xnu_lab.py --layout-compiler <clang-v2> --layout-proof <prueba-api-v2>
python3 tools/test_xnu_scheduler_providers.py --build <reporte-base> --output work/scheduler-audit-nuevo
python3 tools/build_xnu_rpc.py --build <reporte-base>
python3 tools/diagnose_xnu_link.py --build <reporte-base> --rpc <reporte-rpc> --linker <lld-v2> --atlantic-static-proof <prueba-lld-v2> --output work/scheduler-link-nuevo
```

En WSL/NTFS añadir --windows-git a ambos builders y usar outputs nuevos.

## Estado de esta revisión

Compilan 148 unidades experimentales y 13 estándar sin fallos. Las 138 fuentes
previamente seleccionadas conservan sus hashes; se añaden las diez unidades de
esta revisión. Defines y las 137 constantes genassym no cambian. Pasan 129/98
comprobaciones de alcance, ABI y objetos, los 78 tests Python, los 79 344
contratos host de cadenas y el puente de datos con sanitizadores/ABI nativo.
Se generan 57 headers MIG, compilan 42 probes RPC por carril y CFILES selecciona
26 para enlace; tres interfaces sin métodos no acreditan servicios.

El enlace estricto de **174 objetos** falla con **502 diagnósticos indefinidos,
cero duplicados y ninguna imagen**. Frente a 561, 76 nombres tienen
proveedor nativo y aparecen 17 dependencias nuevas; no se eliminan referencias
sin proveedor por selección. El conjunto de nombres coincide con el ensayo
previo independiente de estos candidatos. El estándar conserva 39 objetos,
825 diagnósticos y el rechazo upstream de opciones estáticas, sin imagen.

La [evidencia](../evidence/xnu-scheduler-timers-20261024/manifest.json) contiene
282 artefactos con hashes. Conserva los fallos iniciales de thread_policy,
task_policy y coalition como diagnósticos anteriores. En esa revisión faltaba
coalition_notification_server.h de MIG oficial; no se creó un header vacío ni
se declaró integrada esa unidad. Las pruebas vigentes de Clang API v2 y LLD v2 se reutilizan por hashes
comprobados. Los recorridos QEMU anteriores solo ejecutan el preflight original.

No hay timer, scheduler, política, IRQ, IPC o XNU ejecutado en el teléfono.
No hay acceso al dispositivo, handoff EDK2 o medición de RAM firmware.

La ampliación posterior de [coaliciones/bank](XNU_COALITION_BANK_PROVIDERS.md)
genera el header faltante mediante MIG_USHDRS y selecciona coalition.c intacto.
El manifiesto de timers conserva el alcance de sus 148 unidades y 502
diagnósticos; no se le atribuye la ampliación posterior ni ejecución física.
