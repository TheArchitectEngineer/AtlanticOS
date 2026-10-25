# Bootstrap Mach y componentes seleccionados — 2026-10-24

El patch 0025 corrige cuatro llamadas incondicionales de startup.c para el perfil
de firmware sin BSD ni IOKit. No añade implementaciones de esas APIs ni reemplaza
el bootstrap por un menú o un bucle propio. El código de VM, scheduler, tareas,
hilos, IPC, reloj y carga del contexto sigue siendo el de XNU fijado.

| Llamada | Propietario / selección | Regla de AtlanticOS firmware |
|---|---|---|
| workq_init | bsd/pthread/pthread_workqueue.c, dealloc queue de workqueues BSD | Solo con MACH_BSD |
| bsd_scale_setup | bsd/dev/unix_startup.c, límites BSD | Solo con MACH_BSD; cálculos de task_max/thread_max Mach permanecen |
| device_service_create | osfmk/device/device_init.c, opcional iokit en osfmk/conf/files | Solo con IOKIT; no simular un servicio de dispositivos |
| OSKextRemoveKextBootstrap | libkern/OSKextLib.cpp llama al gestor C++ OSKext | Solo con IOKIT en este perfil estático, sin gestor kext integrado |

Fuera de CONFIG_ATLANTIC_FIRMWARE se preserva la selección original, incluso si
los macros de componente no están definidos. Las guardas mantienen también la
llamada cuando el componente se selecciona dentro de los fragmentos de prueba.
Esto no habilita composiciones firmware con BSD/IOKit: el perfil completo sigue
rechazándolas hasta tener sus proveedores. La frontera del gestor kext es una
decisión del perfil de AtlanticOS; no una afirmación de que todos los builds XNU
configuran C++ e IOKit de la misma manera.

## Lo que debe permanecer

kernel_bootstrap conserva VM, sched_init, activación pmap, mapping_free_prime,
machine_init, clock_init, task_init, thread_init, turnstiles_init y la creación
del hilo bootstrap antes de load_context. El hilo bootstrap conserva idle,
scheduler, thread_daemon_init, inicialización por rangos STARTUP, reloj, habilitar
interrupciones, lockdown, restricciones VM y pageout. load_context conserva
stack_alloc_try, el registro del procesador y machine_load_context reales.

No se elimina console_init ni el logging pendiente. Tampoco se elimina una
operación de memoria por llevar «kext» en su nombre: kext_alloc_init, por ejemplo,
participa en el mapa VM y requiere un análisis distinto. Los símbolos restantes
siguen siendo imports fuertes; no se ignoran los errores del enlace.

## Verificación

tools/test_xnu_startup_scope.py coteja los hashes upstream/patch, preprocesa cuatro
funciones nativas completas en seis contextos y compara bytes de salida fuera
de firmware. Para firmware comprueba la selección de las cuatro llamadas, los
cálculos de límites Mach y el orden sustantivo del bootstrap. Sobre startup.o
real verifica que desaparecen esos cuatro imports y permanecen las dependencias
Mach necesarias. No ejecuta el bootstrap, scheduler, hilo, IRQ o servicio Mach.

```sh
python3 tools/build_xnu_lab.py --layout-compiler <clang-v2> --layout-proof <prueba-api-v2>
python3 tools/test_xnu_startup_scope.py --build <reporte-base> --output work/bootstrap-audit-nuevo
python3 tools/build_xnu_rpc.py --build <reporte-base>
python3 tools/diagnose_xnu_link.py --build <reporte-base> --rpc <reporte-rpc> --linker <lld-v2> --atlantic-static-proof <prueba-lld-v2> --output work/bootstrap-enlace-nuevo
```

En WSL/NTFS añadir --windows-git a ambos builders y usar outputs nuevos. Omitir
las opciones layout obtiene el carril estándar, que también audita startup.o.

## Estado de esta revisión

Compilan las mismas 132 unidades experimentales y 13 estándar, sin añadir ni
retirar unidades. Pasan 97/65 comprobaciones de alcance, ABI y objetos: las ocho
nuevas por carril comprueban estos límites del bootstrap. También pasan las 78
pruebas Python y el puente de datos con ASan/UBSan y ABI nativo en ambos carriles.
Los defines y las 137 constantes genassym coinciden con la revisión anterior.

Se generan 57 headers MIG y compilan 42 probes RPC por carril, con 26 objetos
seleccionados por CFILES. Pasan los 21 descriptores y los 14 subsistemas requeridos
por kobject experimental. El enlace estricto de **158 objetos** con LLD v2 falla
con exit 1: **605 diagnósticos indefinidos, cero duplicados y ninguna imagen**.
Frente a 609 desaparecen exactamente las cuatro referencias excluidas y no
aparecen nuevas. No son cuatro servicios implementados: sus componentes no
están seleccionados. El estándar de 39 objetos conserva 825 diagnósticos y el
rechazo de las opciones estáticas upstream, también sin imagen.

La [evidencia](../evidence/xnu-bootstrap-scope-20261024/manifest.json) contiene
122 artefactos con hashes y la comparación de dependencias. Las pruebas vigentes
del compilador v2 y de LLD v2 se reutilizan tras verificar inputs y binarios;
no se reconstruyen aquí. Los probes de ipc_policy y mach_debug siguen fallando.

No se ejecuta bootstrap, scheduler, hilo, IRQ, Mach, PE o XNU. Los recorridos QEMU
anteriores solo ejercitan el preflight original. Siguen pendientes el cierre de
imagen, boot_args/BSP/MMU, carga temporal y recuperación independiente probada,
el arranque físico, RAM firmware medida y el handoff EDK2.

La ampliación posterior de [cadenas e imagen](XNU_STRING_IMAGE_SUPPORT.md)
registra 136 unidades y 594 diagnósticos indefinidos. La evidencia de esta
revisión permanece como registro de sus 132 unidades y 605 diagnósticos.
