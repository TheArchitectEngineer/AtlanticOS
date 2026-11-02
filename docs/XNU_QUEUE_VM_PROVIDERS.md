# Colas nativas, contadores ARM y sincronización VM — 2026-11-02

Compilan **159 unidades experimentales / 13 estándar**. Se incorporan completos
e intactos osfmk/arm/counter.c y libkern/c++/priority_queue.cpp. El patch 0031
modifica únicamente límites de configuración de vm_object.c; conserva todos
sus cuerpos. Las otras 156 fuentes anteriores mantienen sus hashes.

El enlace estático estricto procesa **185 objetos** y falla con **436 nombres
indefinidos**, cero duplicados, exit 1 y ninguna imagen. Resuelve 27 nombres de
la revisión anterior, sin dependencias nuevas: seis contadores, nueve entradas
de colas requeridas y doce funciones VM/page-worker. Las otras sobrecargas
compiladas no se cuentan como símbolos previamente pendientes resueltos.

## C++ auténtico de libkern

El builder admite archivos .cpp mediante los flags oficiales de MakeInc.def:
-std=gnu++2b, -fsized-deallocation y -fapple-kext. Para esta unidad también aplica
LIBKERN_KERNEL_PRIVATE y OSALLOCDEBUG del Makefile.template de libkern. La
receta C conserva -std=gnu11. Se usan los headers reales del snapshot fijado y
los includes freestanding; no hay SDK reconstruido mediante prototipos ficticios.
libkern/conf/files declara priority_queue.cpp como fuente standard.

El objeto contiene las 48 entradas de las ocho variantes de heap nativas:
genéricas, de scheduler, deadlines y scheduler estable, min/max. Su único import
es mach_assert_jump_key, que mantiene las assertions reales. No requiere un
runtime C++ adicional para esta unidad. Los heaps genéricos usan comparadores
y callbacks con ABI Blocks del caller; el kernel completo todavía tiene
dependencias de Blocks pendientes. Las colas requieren sincronización y lifetime
correctos del caller. Compilarlas no demuestra scheduling o timers operativos.

Las pruebas C y C++ usan el mismo header nativo, rechazan combinaciones de
cola/nodo incompatibles y comprueban tamaños/alineación. Dos inicializadores
sintéticos comparan los bytes del child firmado de 48 bits junto a una key de
16 bits y un deadline de 64 bits. No son direcciones del G20 ni permisos para
acceder a esos números como punteros.

## Contadores escalables ARM

counter.c aporta las seis sobrecargas genuinas: add/inc/dec y sus variantes
preemption_disabled. Conserva zpercpu_get, el proveedor real cpu_number y
PAGE_SHIFT_CONST. Se comprueban LDXR/STXR de 64 bits y el retry CBNZ en los seis
cuerpos; cambiar el load a 32 bits en una copia de inspección hace fallar el
auditor. El objeto original no se modifica. El contador depende de contexto CPU,
mangle de arranque, memoria per-CPU y startup válidos.

En ARM, las variantes preemption_disabled realizan la misma operación atómica
nativa. No deshabilitan preempción por sí mismas. Son contadores de software;
no miden ciclos, PMU o frecuencia física. recount.c y counter_common.c ya estaban
seleccionados y no se vuelven a contar como unidades nuevas.

## Esperas y despertares reales de VM

El upstream sitúa un bloque amplio bajo CONFIG_IOSCHED, incluidas primitivas
core de espera, wakeup y la tabla page-worker. Nuestro perfil no selecciona ese
componente I/O; por eso faltaban esos proveedores aunque vm_object.c compilaba.

El patch 0031 separa los límites: conserva vm_object_sleep/wakeup, variantes de
paging/mapping wait, vm_page_sleep/wakeup/done y los workers cuando se selecciona
el perfil AtlanticOS. CONFIG_IOSCHED sigue controlando la repriorización de I/O
y su callback vnode. El código nativo mantiene locks, wanted/busy, block hints,
sleep con heredero y balance de priority-floor. Su tabla usa por defecto 256
buckets, con el tunable upstream en DEVELOPMENT; su memoria aún debe medirse.
Otras dependencias vnode/BSD del núcleo permanecen pendientes.

Ocho casos de preprocessing del bloque condicional comparan firmware/no firmware,
I/O scheduler activo/inactivo y PAGE_SLEEP_WITH_INHERITOR activo/inactivo. Son
pruebas aisladas del alcance, sin compilar headers simulados. Las ramas ajenas
al cambio conservan la salida upstream; en firmware sin I/O aparecen las esperas
sin incluir los callbacks de repriorización. Doce cuerpos se cotejan literalmente.
El objeto experimental completo y probes de tipos con headers reales verifican
el perfil seleccionado por separado. No se afirma un build kernel completo para
todas las combinaciones hipotéticas.

## Verificación y límites

Pasan **24/26 comprobaciones nuevas**; la lane estándar compila dos probes
adicionales y conserva sus 13 unidades base. La regresión completa pasa
**202/176 checks**. Se preservan las 137 constantes de genassym, 70 headers MIG,
42 probes RPC compilados y 26 seleccionados. También pasan los contratos host
existentes de cadenas, boot_args y Mach-O con sanitizadores; las 78 pruebas
Python pasan. No se ejecutan las colas, los contadores, las esperas VM o XNU.

```sh
# Linux/WSL, desde la raíz. Usar una carpeta de salida nueva.
python3 tools/test_xnu_queue_vm.py --build work/xnu-lab-builds/<id>/report.json \
  --output work/queue-vm-tests-new
```

Evidencia: [xnu-queue-vm-20261102](../evidence/xnu-queue-vm-20261102/manifest.json).
La [CI limpia anterior](https://github.com/h0nda1337/AtlanticOS/actions/runs/41402958398)
terminó success para **157 unidades en 5ce46c8**; no prueba esta ampliación a 159.

Una caché anterior perdió sched_prim.o por cuarentena de Defender. El primer
ensayo que se detuvo al abrir ese objeto no se utilizó para calcular el delta.
El enlace citado usa una reconstrucción completa de la nueva revisión y hashes
verificados. [Registro del incidente host](HOST_BUILD_INCIDENT_20261102.md).
No se modificaron protecciones ni se restauró la cuarentena.

Faltan cierre del kernel, contexto retenido/MMU, BSP G20, timer/IRQ, carga temporal
y recuperación independientes comprobadas, XNU físico y handoff EDK2. La RAM
residente sigue sin medir. No se han tocado particiones ni Android.
