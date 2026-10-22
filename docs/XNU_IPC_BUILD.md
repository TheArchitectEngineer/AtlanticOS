# IPC, MIG y metadata RO nativos — 2026-10-21

Este documento conserva el estado inicial de 47 objetos y 50 headers. La
[integración RPC posterior](XNU_RPC_BUILD.md) añade los C generados y amplía
los headers coherentes a 57, con una selección IDL corregida para firmware.

El build experimental termina con 47 objetos XNU ARM64; el estándar mantiene
13. Se incorporan ipc_importance, ipc_object, ipc_port, ipc_kmsg, ipc_mqueue,
ipc_right, ipc_kobject y una unidad de accessors RO originales del hilo.
Todos conservan cuerpos reales de XNU. No hay kernel enlazado o ejecutado.

## Selección e interfaces originales

IMPORTANCE_INHERITANCE=1 forma parte del perfil, como en MACH_BASE upstream.
Se conserva su implementación y las rutas de special reply/watchports; no se
quitan llamadas para hacer compilar IPC. Los inicializadores originales
ipc_init, ipc_importance_init y mig_init conservan sus registros STARTUP(MACH_IPC).

Las recetas de osfmk/mach/Makefile distinguen headers públicos y emisores del
kernel. Cuando coinciden, la variante kernel-user tiene precedencia. Ahora se
genera la lista completa MIG_KUHDRS con KERNEL_USER=1 y maxonstack=1024, además
de los kernel-server con KERNEL_SERVER=1 y mach_msg2. El reporte conserva roles,
comandos y hashes de cada salida; no se reutiliza un header con un rol distinto.

| Rol seleccionado | Headers únicos |
|---|---:|
| Sender público que no tiene variante kernel-user | 15 |
| Kernel sender | 13 |
| Kernel server Mach | 21 |
| Kernel server device | 1 |
| Total | 50 |

Device se genera con la receta oficial y IOKIT ausente. El resultado genuino
tiene iokit_MSG_COUNT=0 y cero descriptores de rutina. Sus declaraciones no
implementan servicios IOKit ni un driver AtlanticOS. Todavía falta generar,
compilar e integrar el código C RPC requerido y sus proveedores; los headers
por sí solos no suministran mach_vm_subsystem o las demás tablas de servidor.

## Cambios de fuente

Patch 0013 limita tro_proc al bloque MACF que lo consume, manteniendo el acceso
RO del hilo fuera de ese guard. El índice de política de la tabla MIG permanece
disponible para trazado con MACF desactivado. El dispatch, filtro MACF y checks
de replies originales se conservan; no se agrega un proceso ficticio.

Patch 0014 conserva siete funciones de bsd_kern.c en una unidad Mach privada:
get_thread_ro, sus variantes unchecked/current, el panic de propietario y los
get_threadtask normal/early. Thread.c mantiene su zona THREAD_RO y la creación
del objeto. Los helpers conservan zone_require_ro, comparación tro_owner y el
TASK_NULL temprano cuando aún no existe metadata. El lock de procedencia fija
18 cuerpos nativos en total, con avisos APSL, y los coteja antes de compilar.

## Comprobaciones realizadas

Cada carril pasa cinco casos de metadata, tres de ABI MIG y seis de
API/dependencia pmap. El estándar comprueba headers/layouts; no contiene los
objetos experimentales. El carril experimental verifica también cinco objetos
de metadata y sus símbolos de código genuinos.

La fixture MIG usa tipos y structs generados reales. Comprueba que un puerto
de kernel es un ipc_port_t de 64 bits, mientras su nombre permanece en 32 bits;
verifica el offset del campo de notificación y la firma kernel-server de cinco
argumentos. Se rechazan un nombre pasado como objeto de puerto y un callback
server con la firma antigua de dos argumentos. No se entregó ningún mensaje.

La fixture de metadata compara nueve valores proc_ro entre contextos privados
Mach y BSD. Agrega el layout real de thread_ro y rechaza un offset de propietario
alterado en un byte. Ambos compiladores obtienen los mismos valores:

| Valor ARM64 del perfil | Bytes |
|---|---:|
| proc_ro / alineamiento | 120 / 8 |
| proc / task / alineamientos | 1728 / 1624 / 8 |
| task.bsd_info_ro | 976 |
| thread_ro / alineamiento | 48 / 8 |
| thread_ro.tro_owner / tro_task | 0 / 8 |
| thread.t_tro | 1016 |

El task anterior medía 1616 bytes sin importancia. Las 137 constantes genassym
coinciden con esa revisión, pero eso no implica identidad de todos los tipos.
El nuevo perfil regenera y comprueba sus offsets; no mezcla objetos de perfiles.
Estos tamaños no son RAM residente.

## Enlace y trabajo pendiente

El inventario registra 2.837 nombres definidos y 1.035 sin proveedor. Los
getters RO de hilo ya tienen sus definiciones nativas. El intento real de enlace
informa 1.021 símbolos indefinidos y termina con exit 1, sin archivo de salida.
LLD 19.1.7 sigue rechazando static/image_base y señalando no_pie como ignorado
para arm64. El inventario por nombres y la auditoría del linker tienen alcances
distintos; ninguna de esas cifras acredita un kernel enlazable.

Pageout sigue fallando dos checks del allocator para upl con trailer de datos.
El probe conserva el código upstream sin modificar y no produce objeto. No se
desactiva el check ni se clasifica el trailer de datos como punteros. Sigue
pendiente resolver ese contrato de asignación/liberación y el resto de VM.

Para repetir los checks tras el build de XNU:

```sh
python3 tools/test_task_metadata.py --build work/xnu-lab-builds/<build-id>/report.json
python3 tools/test_ipc_mig_abi.py --build work/xnu-lab-builds/<build-id>/report.json
python3 tools/diagnose_xnu_link.py --build work/xnu-lab-builds/<build-id>/report.json --output work/link-new-attempt
```

El diagnóstico de enlace registra un rechazo esperado y nunca acepta una
imagen como kernel. El comando build_xnu_lab.py --probe-remaining intenta
además pageout y devuelve no cero si falla. La evidencia está en
[xnu-ipc-20261021](../evidence/xnu-ipc-20261021/manifest.json).

## Aceptación runtime pendiente

Primero en QEMU y después en G20, con imagen/hash, símbolos y trazas reales:

- Crear tarea/hilo con zonas nativas y comprobar identidad del propietario RO.
  Un propietario incorrecto debe fallar en el panic de circularidad; un puntero
  de otra zona debe fallar en zone_require_ro. Son pruebas separadas y aún no
  se han ejecutado.
- Enviar y recibir un mensaje entre dos hilos Mach mediante puertos/colas reales;
  comprobar id, payload, derechos y liberación de referencias. Una impresión
  en consola o una llamada a una función host no satisface la prueba.
- Registrar donación y retirada de prioridad a través de importancia/turnstiles,
  con espera y despertar efectivos. No debe quedar una referencia o boost al
  destruir el puerto y los hilos.
- Comprobar un mensaje sin handler mediante el error MIG original. El descriptor
  device vacío no debe convertirse en una respuesta de servicio IOKit exitoso.

En G20 deben estar verificadas previamente una vía temporal de ejecución y la
salida física independiente a Android. Las pruebas que provocan un panic no
deben ejecutarse allí sin esa recuperación. El plan de dispositivo mantiene
ese requisito y la prohibición actual de flash/particiones. RAM física, BSP,
IRQ/timer, arranque XNU y handoff EDK2 siguen sin comprobarse.
