# Código RPC generado de XNU — 2026-10-22

Este documento conserva la prueba inicial de 47 + 42 objetos. La
[integración posterior de proveedores](XNU_RPC_PROVIDERS.md) distingue los 42 C
generados/compilados de los 26 seleccionados para el kernel por CFILES. La
receta inicial de diagnóstico había enlazado toda la lista de generación;
ese alcance histórico no describe la selección correcta del kernel actual.

El build conserva 47 unidades nativas con el proveedor experimental y 13 con
Clang estándar. Cada carril genera y compila además los 42 archivos C RPC de las
recetas upstream: 21 emisores kernel-user, 20 servidores Mach y el servidor
device. Son código de serialización/dispatch y descriptores generados por MIG;
no implementan por sí solos los servicios, drivers o handlers que invocan.
Todavía no hay kernel enlazado o ejecutado.

## Recetas y selección

Las listas MIG_KUSRC y MIG_KSSRC determinan los C. MIG_KSHDRS contiene un header
adicional, host_security_server.h, sin C correspondiente en MIG_KSSRC. No se
inventó una unidad para igualar el número de headers y fuentes.

Los emisores generan también headers internos como efecto de MIG_KUSRC. Ese
conjunto tiene precedencia sobre los headers públicos del mismo nombre, incluido
vfs_nspace.h. Ahora se verifican 57 salidas únicas: 14 sender públicos, 21
kernel-sender y 22 kernel-server. Cada C regenerado exige que su header coincida
byte a byte con la variante elegida en el build base.

El primer intento compiló 40 de 42 C y conservó dos fallos. vm_map.defs no
seleccionaba KernelUser y producía una llamada mach_msg de userland. El servidor
Arcade pedía convert_port_to_arcade_register sin su proveedor seleccionado.
No se agregaron declaraciones o implementaciones ficticias para resolverlos.

Patch 0015 selecciona KernelUser en vm_map solo para firmware y emisores del
kernel. MIG genera ahora la llamada nativa mach_msg_rpc_from_kernel; el objeto
no depende de mach_msg de userland. Las dos interfaces Arcade respetan la
selección de su proveedor en firmware. Fuera del perfil AtlanticOS, y con Arcade
activado, cinco comparaciones de headers y C generados son byte a byte iguales
a upstream. Los avisos APSL y Carnegie Mellon de las fuentes se conservan.

## Alcance de las comprobaciones

- Los 42 C generan objetos Mach-O ARM64 en ambos carriles, con hashes de entrada,
  definiciones, salida y objeto. Las fuentes originales XNU siguen intactas;
  los parches se aplican a un checkout separado.
- Dos casos de configuración comprueban las opciones nativas de mach/mig.h y
  rechazan desactivar __MigTypeCheck. Los emisores no vacíos deben referenciar
  transporte kernel real; se prohíben dependencias mach_msg/mach_msg_overwrite.
- Cinco casos comparan generación contra fuentes upstream en los contextos que
  el patch no debe cambiar. No prueban que Arcade esté implementado en firmware.
- Dos casos de ABI compilan los 21 descriptores de servidor con el tipo real
  mig_kern_subsystem: offsets, tipo del demux y stride de kern_routine_descriptor.
  Un offset alterado debe ser rechazado.
- En el carril experimental, los objetos RPC suministran las 17 tablas de
  subsistema referenciadas por el objeto ipc_kobject real. El carril estándar no
  contiene ese objeto y declara kobject_table_checked=false.

Los tres interfaces sin métodos son device, arcade_register y arcade_upcall.
Sus salidas seleccionadas se generan de verdad, pero no acreditan servicios
IOKit/Arcade ni se cuentan como métodos RPC funcionales. No se entregaron mensajes
ni se ejecutó un handler, comprobación de tipo runtime o tabla MIG.

Los 14 checks base por carril siguen pasando: metadata, ABI de declaraciones MIG
y pmap. Las 137 constantes target se regeneran con cada perfil. Todo esto tiene
alcance de compilación, tipos y relaciones de símbolos.

## Enlace real y dependencias

El intento estricto incluye 89 objetos en experimental (47 + 42) y 55 en estándar
(13 + 42), sin dead strip, bibliotecas falsas o símbolos ignorados. Ambos terminan
con exit 1 y no producen imagen. En experimental hay 1.245 diagnósticos de símbolos
indefinidos y ningún error de símbolo duplicado. El inventario por nombres cuenta
2.985 definiciones y 1.259 nombres sin proveedor; tiene alcance distinto del linker.

Incorporar las tablas RPC hace visibles sus handlers y dependencias. Todavía
faltan código Mach/VM/IPC nativo, rutinas de máquina y servicios de plataforma.
LLD 19.1.7 además sigue rechazando static/image_base y no_pie para arm64. Suministrar
las tablas no demuestra que el conjunto pueda arrancar.

Pageout continúa pendiente por el contrato de asignación de upl con trailer de
datos. No se ha eliminado su check de tipos. El siguiente trabajo debe cerrar
proveedores nativos y disponer de un linker estático correcto antes de ejecutar
un kernel y medir memoria real.

## Reproducir

Después del build base correspondiente y con las herramientas oficiales fijadas:

```sh
python3 tools/build_xnu_rpc.py --build work/xnu-lab-builds/<base-id>/report.json
python3 tools/test_xnu_rpc.py --build work/xnu-lab-builds/<base-id>/report.json --rpc work/xnu-rpc-builds/<rpc-id>/report.json
python3 tools/diagnose_xnu_link.py --build work/xnu-lab-builds/<base-id>/report.json --rpc work/xnu-rpc-builds/<rpc-id>/report.json --output work/link-new-attempt
```

En WSL sobre NTFS se añade --windows-git al builder. Se conservan intentos previos
si ya existe su carpeta. Un build o diagnóstico parcial no se acepta como completo.
El diagnóstico solo registra un rechazo; no acepta una imagen como kernel.
Reportes, comandos y límites están en
[xnu-rpc-20261022](../evidence/xnu-rpc-20261022/manifest.json).

Las pruebas runtime siguen siendo las de [IPC](XNU_IPC_BUILD.md): intercambio real
entre hilos Mach, derechos y referencias, prioridad, errores MIG y validación RO.
Deben realizarse primero en QEMU y después en G20 con recuperación independiente
verificada. No hubo acceso al teléfono, cambios Android, arranque temporal o
flasheo. RAM física, BSP G20 y handoff EDK2 continúan sin verificar.
