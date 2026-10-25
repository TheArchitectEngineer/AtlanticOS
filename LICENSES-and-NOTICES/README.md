# Licencias y procedencia

La licencia raíz MIT cubre el código y documentación originales AtlanticOS,
salvo avisos específicos por archivo. La extensión original de Clang bajo
compiler-port/ usa Apache-2.0 WITH LLVM-exception. No es una relicencia de XNU,
LLVM, EDK2, Linux/Motorola o el port UEFI G20.

El patch original en linker-port/ también usa Apache-2.0 WITH LLVM-exception
y modifica seis archivos oficiales LLD 19.1.7. Conserva su licencia upstream;
LLVM-LICENSE.txt cubre sus avisos. El modo de enlace no procede de un port de
kernel o firmware ajeno. Las bibliotecas LLVM host se registran como dependencias
externas y no se incluyen como binarios en el repositorio.

XNU oficial fijado en dependencies.lock.json: fuente externa intacta, checkout
ignorado, no incorporado en el paquete fuente AtlanticOS. Se conserva su
APPLE_LICENSE íntegra junto a este archivo; los avisos por archivo siguen en
upstream. Los parches originales están en xnu-port/ y conservan la licencia de
los archivos modificados. Antes de distribuir componentes derivados,
mantener procedencia y avisos, revisar cada licencia y adjuntar fuentes aplicables.

El patch 0010 incorpora helpers derivados de kern_proc.c y bsd_kern.c en dos
unidades de metadata. Conserva los avisos Apple/APSL y los demás avisos de sus
archivos de origen, incluidos NeXT, Berkeley y SPARTA. Sus cuerpos se fijan por
líneas y SHA-256 en xnu-port/task-metadata-native.lock.json y se cotejan contra
el commit XNU antes de compilar. Esas funciones son código XNU conservado y
adaptado, no código original MIT AtlanticOS.

El patch 0014 conserva otros siete helpers de metadata RO del hilo procedentes
de bsd_kern.c, con su aviso Apple/APSL. El mismo lock fija ahora 18 cuerpos
nativos en total. Thread.c sigue siendo el propietario de la zona THREAD_RO;
los helpers conservados no sustituyen su allocator o validación de propietario.

Los C RPC se generan con MIG oficial a partir de las definiciones XNU fijadas.
No son implementaciones originales de los servicios. Los C/headers completos y
objetos permanecen privados en work/; se publica receta, hashes y diagnósticos.
Patch 0015 conserva los avisos APSL/Carnegie Mellon de vm_map.defs y los avisos
Apple/APSL de las dos interfaces Arcade. No se relicencian bajo MIT.
Patch 0016 conserva los avisos Apple/APSL y Carnegie Mellon de vm_user.c;
solo corrige los nombres de parámetros en sus ramas de función desactivada.
Patch 0017 conserva los avisos Apple/APSL de ipc_kobject.c. Solo condiciona tres
entradas de dispatch a los proveedores BSD/IOKit seleccionados en firmware.

Patch 0018 conserva cuatro fragmentos de bsd/kern/subr_prf.c para snprintf y
vsnprintf, con sus avisos Apple/APSL, NeXT, Berkeley y USL íntegros. El lock
xnu-port/printf-native.lock.json fija sus líneas y hashes. Los cuerpos llaman
al formateador __doprnt de XNU; no son código MIT AtlanticOS. La declaración
aislada del header sí es original AtlanticOS. Se conserva el reconocimiento:
This product includes software developed by the University of California,
Berkeley and its contributors.

Patch 0019 conserva los avisos de bsd/sys/cdefs.h y kern/kalloc.h. El puente de
declaraciones es una adaptación de XNU; la interpretación original de sus tags
está en SemaAtlanticLayout.cpp bajo Apache-2.0 WITH LLVM-exception. No incorpora
la implementación privada Apple de xnu_usage_semantics o sus builtins.
Patch 0020 conserva los avisos upstream de zalloc.c y cambia dos declaraciones
de almacenamiento para que coincidan con el tipo de allocation ya existente.
Patch 0021 conserva los avisos Apple/APSL de sleh.c. Los seis proveedores de
reloj, timer, contabilidad, commpage y datos ARM se compilan desde upstream sin
modificar sus cuerpos. El código XNU no pasa a estar bajo la licencia MIT de
las herramientas de auditoría y fixtures originales.

La ampliación de proveedores de arranque y planificación selecciona otros 16
archivos nativos sin modificar. Conservan sus avisos Apple/APSL, CMU, NeXT y
Berkeley según cada archivo. bsd/kern/qsort.c incluye el aviso Berkeley de
cuatro cláusulas; el reconocimiento a Berkeley anterior también corresponde
a este componente. No se atribuyen esos cuerpos a la licencia MIT del proyecto.

Los archivos de xnu-port/platform/ son código original AtlanticOS bajo MIT. El
patchset 0022/0023/0026 añade sus copias exactas al árbol XNU; el builder verifica esa igualdad
y las preimágenes nulas de archivos nuevos. Los tipos y proveedores XNU que
incluyen o llaman conservan sus licencias upstream. No se incorpora pe_init.c
de Apple ni un BSP de un port UEFI como implementación de la plataforma.

El adaptador cache_asm.s es original MIT y transfiere la llamada a la rutina de
caché genérica genuina. Seis fuentes nativas de la ampliación de memoria permanecen
intactas; en loose_ends.c el patch 0024 solo acota la guarda del fallback vacío.
Todas conservan sus avisos/licencias upstream; sus
cuerpos, funciones vacías e instrucciones no se atribuyen a AtlanticOS.

El patch 0025 conserva los avisos de startup.c y solo condiciona cuatro llamadas
a componentes BSD/IOKit no seleccionados por el perfil de firmware. No incorpora
implementaciones de esos servicios. La herramienta original que audita alcance,
orden Mach y objetos es MIT; los cuerpos nativos conservan sus licencias.

El patch 0026 también incorpora copias exactas de atlantic-core/string.c e
include/atlantic/string.h, originales MIT, junto al proveedor ABI original de
xnu-port/platform/string.c. Las fuentes kernel_mach_header.c y strsep.c se
seleccionan directamente del snapshot XNU intacto y mantienen sus avisos
Apple/APSL y, en strsep.c, Berkeley. No son implementaciones MIT AtlanticOS.

El patch 0027 adapta cinco archivos IPC nativos para seleccionar componentes
en firmware. Conserva sus avisos Apple/APSL y los avisos CMU de ipc_object.c,
ipc_kmsg.c y mach_debug.c. La tabla de políticas, sus 17 cuerpos core auditados,
el registro de kobjects y las operaciones de derechos siguen siendo XNU.
Las herramientas y fixtures de auditoría originales son MIT; no relicencian
los cuerpos nativos ni implementan CoreAnalytics o IOKit.

La ampliación de scheduler/timers selecciona diez unidades osfmk genuinas. Ocho
permanecen intactas. El patch 0028 conserva los avisos de thread_policy.c y
task_policy.c al acotar dos callbacks BSD y corregir una rama de error ya
prevista. mk_timer, syscall_subr, timeout, affinity, vm_map_store_ll,
counter_common, task_ident y sfi conservan sus avisos Apple/APSL y los demás
avisos por archivo, incluidos CMU/OSF cuando corresponden. Los algoritmos,
retornos no soportados y funciones vacías upstream no son código MIT AtlanticOS.
Las herramientas y fixtures originales de comprobación sí son MIT.

La ampliación de coaliciones/bank selecciona cuatro unidades osfmk intactas y
bank.c con el patch 0029, que alinea dos guardas con el campo nativo existente.
Conserva los avisos Apple/APSL y CMU/OSF por archivo. Los headers adicionales
se generan con MIG oficial desde la lista MIG_USHDRS y sus .defs; no son SDK
ni declaraciones originales MIT. Los retornos de debug VM desactivado siguen
siendo la implementación upstream y no acreditan ese servicio en AtlanticOS.

EDK2 es un destino futuro, no una dependencia enlazada en esta entrega. El commit
registrado corresponde a la referencia UEFI auditada y conserva sus licencias
BSD-2-Clause-Patent y por componente. No se distribuyen sus binarios o wrappers.

El port G20 incluye adaptaciones con GPL-2.0-only y BSD-2-Clause-Patent. Solo fue
estudiado en work/references, no se copió a drivers AtlanticOS ni se ejecutaron
sus empaquetadores. Las referencias Motorola son para entender hardware;
proveniencia e inventario quedan enlazados, no se presentan como código original.

Atlas 5x7: original AtlanticOS, MIT; no fuentes, iconos o imágenes de terceros
empaquetados. La foto pública se inspeccionó localmente pero no se redistribuye.
SHA-256 y URL permiten auditar la fuente sin atribuirnos su prueba.

Python/Tk y Clang/Git son herramientas host externas; sus versiones verificadas
están registradas. El runtime no se incluye. No hay biblioteca criptográfica de
firmware integrada ni claves privadas de prueba/publicación.

El experimento de compilador fija llvmorg-19.1.7 / cd708029e0b2869e80abe31ddb175f7c35361f90.
La fuente upstream y el build permanecen bajo work/; se publica el patchset y
la implementación original, no el tarball ni un SDK. LLVM-LICENSE.txt conserva
el texto de licencia upstream. Este experimento no sustituye código kernel XNU
ni drivers y no constituye compatibilidad completa con builtins privados Apple.
