# VM, allocators e inicialización IPC — 2026-10-21

Compilan trece unidades estándar y diecisiete con el proveedor experimental de
layouts C. La ampliación incorpora machine_routines.c, ipc_init.c, kalloc.c,
zalloc.c y vm_map.c. Sus objetos no están enlazados ni ejecutados. Task.c y pmap
siguen fallando; el probe ampliado devuelve exit 1 y conserva ambos diagnósticos.

## Cambios y comprobaciones

Patch 0007 condiciona el include real de TrustCache/API.h para firmware que no
selecciona PMAP_CS_PPL_MONITOR. Todos los usos de sus tipos en pmap_cs.h están
dentro del bloque de ese monitor. Los demás targets conservan el include
original. No se cambian verificadores, llamadas de protección o políticas de
vm_map.c, ni se crea un header alternativo. Las tres pruebas de dependencia
compilan sin monitor y exigen la API real al seleccionar PPL o la ruta upstream.
Estas pruebas no verifican firmas ni ejecutan un monitor.

Patch 0008 unifica dos guards y un comentario que usaban ZONE_ENABLE_LOGGING
con la definición existente ZALLOC_ENABLE_LOGGING. La búsqueda del snapshot
no encontró una definición del primer nombre. El perfil DEVELOPMENT selecciona
logging: la corrección conserva tanto los campos z_btlog como sus consumidores.
No desactiva logging para evitar los errores de miembros ausentes.

IPC mantiene su función ipc_init estática y su registro STARTUP(MACH_IPC).
El driver exige el símbolo de texto local `t` y la entrada de registro. Las
otras funciones principales se comprueban como texto externo `T`. El linker
todavía deberá retener y recorrer las secciones startup reales.

MIG genera también mach_test_upcall.h desde su .defs oficial, con el rol kernel
sender de MIG_KUHDRS. Ahora se generan 42 headers. No se fabrica el header que
necesita task.c ni se compila aún ese kernel sender C.

## Reproducción

La [receta estándar](XNU_LAB_BUILD.md) construye trece unidades. Con el
[compilador experimental probado](../compiler-port/README.md):

```sh
python3 tools/build_xnu_lab.py \
  --layout-compiler work/clang-layout-build/build/bin/clang \
  --layout-proof work/clang-layout-build/tests/report.json
```

Para conservar también los fallos restantes añadir --probe-remaining. Con ese
flag se comprobaron diecisiete objetos y fallaron task.c y pmap; el exit global
fue 1. No se cuenta el probe completo como un build aprobado.

```sh
python3 tools/test_pmap_cs_scope.py --build work/xnu-lab-builds/<id>/report.json
```

El test usa los flags del build, comprueba la postimagen real del header y
registra los tres resultados. El workflow estándar lo repite en entorno limpio.

## Límites

El inventario de los diecisiete objetos tiene 1.175 nombres externos definidos,
855 sin proveedor y ninguna definición externa repetida por nombre. Esto no
valida relocaciones, tipos de símbolos, selección de secciones o un enlace.
Los 137 offsets/aserciones target y la metadata del compilador siguen pasando.
Ni los tamaños de objetos ni los guards de logging miden RAM residente.

Task.c alcanza APIs BSD/MAC, campos bsd_info_ro ausentes y rutas de watchports,
memorystatus y reclamación diferida sin separar. Pmap alcanza
CoreEntitlements/V2/API.h vía AMFI. No se han agregado procesos ficticios,
campos sin semántica, headers vacíos o respuestas de seguridad de éxito.

La [CI de doce unidades del commit 7c9eaf2](https://github.com/h0nda1337/AtlanticOS/actions/runs/39626520147)
reconstruyó LLVM, pasó 18 checks y reprodujo inputs/137 constantes locales.
Su [evidencia](../evidence/clang-layout-ci-20261021/manifest.json) conserva ese
alcance histórico. La ampliación actual se registra por separado en
[xnu-vm-allocator-20261021](../evidence/xnu-vm-allocator-20261021/manifest.json).

Faltan el cierre de dependencias, pmap/BSP y enlace; después se necesita ejecutar
Mach/VM/hilos/timer reales de forma instrumentada. El objetivo físico G20 y el
handoff EDK2 continúan abiertos y Android no ha sido modificado.
