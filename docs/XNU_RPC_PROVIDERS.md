# Proveedores nativos y selección de enlace — 2026-10-22

El carril experimental compila **62 unidades reales de XNU**; el estándar
conserva 13. Cada carril genera y compila además los 42 C de las recetas MIG
como probes. De ellos, **26 están seleccionados por el configurador nativo
para el enlace** de este perfil. No hay kernel enlazado o ejecutado.

## Quince unidades añadidas

| Fuentes XNU conservadas | Cuerpos nativos comprobados por símbolos de código |
|---|---|
| ipc/mach_msg.c | Trap Mach de mensajes y su procesamiento |
| ipc/ipc_notify.c, ipc/ipc_pset.c | Notificaciones y conjuntos de puertos |
| ipc/ipc_eventlink.c, ipc/ipc_voucher.c | Eventlinks, vouchers y registro STARTUP de vouchers |
| kern/ipc_mig.c | Transporte kernel_mach_msg_rpc y kernel_mach_msg_send |
| kern/ipc_tt.c | Puertos de tareas/hilos y conversores de mapas |
| kern/ipc_host.c, kern/ipc_clock.c | Conversores de host/procesador/reloj |
| kern/host.c, kern/host_notify.c | Consultas y notificaciones del host |
| kern/sync_sema.c | Creación, espera y señal de semáforos |
| vm/vm_memory_entry.c | Creación y operaciones de memory entries |
| vm/vm_upl.c | Commit/abort de rangos UPL existentes |
| vm/vm_user.c | Operaciones VM exportadas, con sanitización nativa |

La receta conserva las funciones locales y sus registros STARTUP. En particular,
ipc_voucher_init es una función local t y su registro MACH_IPC tiene el prefijo
nativo. No se vuelve externa para satisfacer un check inventado. Los proveedores
compilados aún tienen llamadas sin resolver y no acreditan mensajes entregados,
semáforos operativos o mapeos de memoria ejecutados.

Patch 0016 corrige dos casts a un parámetro size inexistente en las ramas de
reclamación diferida desactivada de vm_user.c. Usa los parámetros actuales y
mantiene KERN_NOT_SUPPORTED, sin escribir outputs ni agregar un proveedor.
Las ramas con reclamación diferida habilitada permanecen intactas. vm_pageout.c
sigue pendiente por su contrato de allocation del header/trailer UPL; compilar
vm_upl.c no resuelve ese allocator.

## Corrección de la receta RPC

La receta anterior confundía COMP_FILES de osfmk/mach/Makefile, que enumera la
generación, con los C seleccionados para el kernel. El intento con 62 + 42
objetos reveló 24 duplicados, entre ellos upl_abort y funciones VM: los emisores
upl_user.c y vm_map_user.c no pertenecen a este enlace nativo.

Ahora se registra el hash de config/Makefile en el build base y se usa su CFILES,
producido por el SETUP/config oficial con el perfil real. No se evalúa texto
Makefile como comandos. El parser acepta rutas literales Mach/device y rechaza
selecciones ambiguas, vacías, duplicadas o rutas generadas que escapen del grupo.
Cuatro pruebas host cubren esa lectura, incluida la distinción de COMP_FILES.

El resultado selecciona 26 C y deja 16 objetos como probes de generación y ABI.
Los 42 se verifican por hash y símbolos; el diagnóstico enlaza solo la selección
recalculada desde el Makefile comprobado. No se ignoran errores de duplicados ni
se renombran servicios a mano. Los emisores de excepciones Mach exc_user.c y
mach_exc_user.c siguen seleccionados.

Patch 0017 adapta la tabla nativa mig_e del firmware a esa selección: sus dos
receptores de excepciones BSD y el receptor IOKit requieren sus proveedores.
No se registran cuando MACH_BSD/IOKIT están desactivados. Quedan 14 subsistemas
requeridos, todos suministrados por los RPC seleccionados. Cinco casos de
preprocesamiento comprueban las combinaciones: 17 fuera de firmware, 17 con
ambos proveedores, 14 con ambos desactivados, 16 con BSD y 15 con IOKit. Los
dos contextos que deben conservar upstream son byte a byte iguales. Es un
check de selección de tabla; no ejecuta un dispatch ni prueba BSD/IOKit.

Los 21 descriptores generados se siguen comparando con el ABI real
mig_kern_subsystem, incluidos un caso negativo de prefijo y el stride nativo de
rutinas. El carril estándar no compila ipc_kobject.c y registra su cobertura
de tabla como no comprobada. El carril experimental sí comprueba el objeto real
y los proveedores seleccionados de sus 14 referencias de subsistema.

## Enlace y límites actuales

El [modo estático ARM64 v2](LLD_STATIC_ARM64.md) conserva el coalescing nativo
weak/strong. Una construcción limpia de LLD, con los seis archivos modificados
fijados por hash, pasa 54 comandos y audita 15 imágenes fixture. El compilador
experimental de layouts conserva su binario y sus 18 checks anteriores.

El intento real experimental enlaza 88 objetos (62 + 26) con undefined error,
warnings fatales y sin dead strip. Termina con exit 1, **1.094 diagnósticos de
símbolos indefinidos, cero duplicados y ninguna imagen**. El inventario por
nombres contiene 3.322 definiciones y 1.108 nombres sin proveedor; no equivale
al trabajo del linker, que también resuelve símbolos sintéticos de secciones.

El carril estándar intenta 39 objetos (13 + 26), registra 829 diagnósticos de
indefinidos y cero duplicados, y sigue rechazando las opciones estáticas upstream.
Su rechazo no constituye validación del linker experimental, que se prueba con
su propio binario y fixtures.

Todavía faltan proveedores Mach/VM y de máquina, Platform Expert, layout completo
de segmentos, bootstrap real, BSP G20, temporizador/IRQ y una vía temporal de
prueba con recuperación independiente. No hay arranque físico AtlanticOS,
handoff EDK2 o medición de RAM residente. Ninguna prueba de esta ampliación
accede al teléfono o modifica Android.

## Reproducir

Las recetas y toolchains fijadas conservan las instrucciones de los documentos
de compilador, MIG y LLD. Con un build base actual:

```sh
python3 tools/build_xnu_lab.py --layout-compiler <clang> --layout-proof <layout-report.json>
python3 tools/build_xnu_rpc.py --build work/xnu-lab-builds/<base-id>/report.json
python3 tools/test_xnu_kobject_scope.py --build work/xnu-lab-builds/<base-id>/report.json --output work/table-scope-new
python3 tools/test_xnu_rpc.py --build work/xnu-lab-builds/<base-id>/report.json --rpc work/xnu-rpc-builds/<rpc-id>/report.json
python3 tools/diagnose_xnu_link.py --build work/xnu-lab-builds/<base-id>/report.json --rpc work/xnu-rpc-builds/<rpc-id>/report.json --linker <ld64.lld> --atlantic-static-proof <lld-fixture-report.json> --output work/link-new
```

En WSL con Git sobre NTFS se añade --windows-git a los builders. Los directorios
de intentos anteriores se conservan. La evidencia seleccionada está en
[xnu-static-providers-20261022](../evidence/xnu-static-providers-20261022/manifest.json):
reportes, hashes, comandos, diagnósticos y scopes. Los objetos, fuentes generadas
completas y árboles upstream permanecen bajo work/, sin incorporarlos al repo.
