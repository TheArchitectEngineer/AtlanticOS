# Tarea Mach y metadata conjunta con BSD — investigación 2026-10-21

En xnu-12377.1.9, task.c no mantiene una ruta completa de asignación sin BSD.
El perfil AtlanticOS sin MACH_BSD descubre ese acoplamiento; no se resuelve
definiendo globals ficticios o quitando referencias a campos que siguen siendo
necesarios para seguridad y vida útil.

La especificación permite conservar las dependencias BSD/IOKit realmente
necesarias. La adaptación debe evaluar ese subconjunto de XNU antes de introducir
una segunda representación de los datos protegidos de Mach. Conservar tipos
o funciones de metadata no equivale a habilitar userland BSD.

## Hechos de la fuente fijada

| Código upstream | Dependencia comprobada |
|---|---|
| osfmk/kern/task.c:1182 | Asigna kernproc en proc_task_zone y obtiene kernel_task mediante proc_get_task_raw |
| task.c:1212 | Calcula alineamientos y tamaños conjuntos antes de crear la zona PROC_TASK |
| task.c:1537 | task_create_internal recibe child_task ya asignado; no crea un objeto standalone |
| task.c:1773 | Inicializa metadata de tarea mediante proc_ro_ref_task o proc_ro_alloc |
| task.c:2308 | Borra el backref RO y libera el bloque conjunto al terminar referencias |
| task.c:10313 | task_get_ro exige pertenencia a la zona RO y verifica el backref hacia la tarea |
| osfmk/kern/task.h:329 | El campo bsd_info_ro está condicionado a MACH_BSD |
| task.h:648 | task_require valida la zona conjunta mediante el puntero de proceso |
| bsd/kern/kern_proc.c:1866 | Los helpers convierten proc/task usando proc_struct_size |
| kern_proc.c:5398 | El allocator RO admite datos de tarea sin proceso; copia tokens/flags mediante zalloc_ro |
| kern_proc.c:1166 | La referencia de tarea mantiene P_REF_TASK_HOLD en el prefijo de proceso |
| osfmk/kern/bsd_kern.c:92 | get_bsdtask_info valida el bloque y solo entrega un proceso si task_has_proc está activo |

Las referencias anteriores son líneas del commit upstream fijado, no de una
fuente ya adaptada. El estado de los 18 objetos no acredita estos caminos.
Fuentes primarias fijadas: [task.c](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/osfmk/kern/task.c),
[kern_proc.c](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/bsd/kern/kern_proc.c)
y [proc_ro.h](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/bsd/sys/proc_ro.h).

## Invariantes que debe conservar el port

- Tamaño, alineamiento y pertenencia a la zona de cada objeto. Una conversión
  entre punteros debe corresponder a una asignación real, no a un offset supuesto.
- Referencias de tarea y propietario: creación, rollback ante fallo de ledger,
  último release y destrucción deben usar la misma representación de memoria.
- Tokens de seguridad/auditoría, flags, control de puertos y backref RO. Las
  actualizaciones deben conservar las verificaciones de zona/rango y operaciones
  atómicas, usando el allocator y pmap RO genuinos.
- Ausencia de proceso: no fabricar initproc/kernproc para satisfacer el parser.
  Un proceso ausente tampoco puede compararse con un initproc NULL y convertirse
  por accidente en el proceso init.
- Separación de callbacks BSD, AMFI/MAC, corpse/exec y workqueues. No conceder
  excepciones de seguridad por falta de proveedor ni reemplazar APIs core con
  retornos de éxito.

## Trabajo pendiente

Auditar y aislar los helpers originales de metadata necesarios, con avisos de
licencia y dependencias explícitas. Comparar esa integración con una separación
Mach de las zonas, contando sus cambios de ABI y referencias; no elegir por el
solo hecho de que una alternativa compile. El perfil mantendrá MACH_BSD ausente
para userland y no declarará eliminado todo soporte BSD si conserva metadata.

La comprobación inicial debe regenerar offsets ARM64 y ejercitar tipos/tamaños,
alloc/free/rollback, tokens y rechazo de backrefs inválidos. La aceptación runtime
requiere ejecutar las operaciones reales de zona/pmap con permisos RO y trazas
de símbolos. Un test host de un allocator inventado no valida esta integración.

No se ha implementado todavía ninguna de esas alternativas ni asignado una
tarea real durante ejecución de AtlanticOS.
