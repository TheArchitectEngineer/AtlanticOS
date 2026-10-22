# Tarea Mach y metadata nativa conjunta — 2026-10-21

Estado: 22 objetos XNU ARM64 compilados con el proveedor experimental explícito,
incluidos task.c, task_ref.c y dos unidades que conservan helpers originales.
Cuatro comprobaciones de ABI aprueban: dos contextos ARM64 y dos rechazos de
offset incorrecto. No hay kernel enlazado ni operaciones de tarea ejecutadas.

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
fuente ya adaptada. Compilar los objetos no acredita ejecución de estos caminos.
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

## Integración conservada y reproducible

Patch 0010 conserva bsd_info_ro en el perfil firmware y las zonas PROC_TASK y
PROC_RO nativas. Once cuerpos de funciones de kern_proc.c y bsd_kern.c se
cotejan por líneas y hash contra el commit upstream antes de compilar:
[procedencia](../xnu-port/task-metadata-native.lock.json). Se mantienen sus
avisos de licencia y las llamadas reales a kauth_cred_set, zalloc_ro,
zalloc_ro_update_elem, zfree_ro y zone_id_require. No hay allocator alternativo.

El helper de metadata usa los headers BSD privados originales mediante
-UMACH_KERNEL_PRIVATE -DBSD_KERNEL_PRIVATE=1; el acceso get_bsdtask_info se
compila con headers Mach privados. No se mezclan typedefs incompatibles ni se
inventan tipos BSD. MACH_BSD permanece ausente, sin inicialización de procesos
o userland. get_bsdtask_info valida la zona y respeta el flag task_has_proc.

Patch 0011 conserva el ciclo de tarea Mach, ledgers, referencias y datos VM,
condicionando los callbacks opcionales a sus features. Sin MACF no se concede
la excepción AMFI de puertos movibles; sin proceso init, task_is_initproc es
falso. Si IMPORTANCE_INHERITANCE está desactivado, se exige que watchports sea
NULL. No se agregan proveedores ficticios para resolver el enlace. El build
retiene tres warnings de task.c: dos declaraciones ucred y un cast de callback
IO upstream; no se silencian ni se presentan como validados en runtime.

La prueba usa el mismo comando target y headers generados del build:

```sh
python3 tools/test_task_metadata.py --build work/xnu-lab-builds/<build-id>/report.json
```

El fixture se compila a LLVM IR ARM64 en ambos contextos; un parser estricto
extrae las constantes de los tipos reales. El test compara nueve valores
compartidos y exige errores estáticos al alterar el offset del propietario en
un byte. Además comprueba hashes y símbolos T genuinos de los cuatro objetos
cuando existen. El carril estándar de 13 objetos comprueba solo el ABI y deja
objects vacío; no acredita que task.c compile con Clang estándar.

| Campo compartido | Bytes, ambos contextos |
|---|---:|
| sizeof / alineamiento proc_ro | 120 / 8 |
| pr_proc / pr_task | 0 / 8 |
| task_tokens / task_data | 72 / 72 |
| t_flags_ro / task_control_port_options | 112 / 116 |
| sizeof task_ro_data | 48 |

El contexto BSD obtiene sizeof(proc)=1728 y p_refcount=1100; Mach obtiene
sizeof(task)=1616 y bsd_info_ro=976. Ambos alineamientos son 8. Estos valores
pertenecen únicamente al perfil seleccionado; no son offsets OEM ni mediciones
de RAM residente.

El inventario del conjunto registra 1.677 nombres externos definidos y 987 sin
proveedor. Sigue pendiente kauth_cred_set, junto a servicios de IPC/VM/IOKit y
plataforma. Contar nombres no verifica relocations ni viabilidad del enlace.
La evidencia y los logs están en
[xnu-task-metadata-20261021](../evidence/xnu-task-metadata-20261021/manifest.json).

## Trabajo pendiente

La comprobación inicial regenera offsets ARM64 y coteja tipos/tamaños, pero
aún debe ejecutar alloc/free/rollback, tokens y rechazo de backrefs inválidos.
La aceptación runtime
requiere ejecutar las operaciones reales de zona/pmap con permisos RO y trazas
de símbolos. Un test host de un allocator inventado no valida esta integración.

Para aceptarla, el kernel deberá crear una tarea sin proceso, comprobar tokens
y propietario RO, fallar ante un backref incorrecto, revertir asignaciones ante
un fallo de ledger y liberar exactamente una vez al caer la última referencia.
La protección deberá impedir escritura directa a RO y permitir las operaciones
nativas autorizadas. Registrar imagen, símbolos y trazas para cada caso; un
panic esperado cuenta como rechazo solo si identifica la verificación ensayada.
Primero se exige en QEMU y después en G20, con salida independiente a Android
comprobada antes de cualquier payload. Nada de esto se ha ejecutado todavía.
