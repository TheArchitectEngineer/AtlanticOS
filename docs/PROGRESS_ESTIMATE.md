# Estimación de avance — 2026-11-02

Estimación de ingeniería: **aproximadamente 30 % hacia el primer arranque físico
instrumentado de XNU en el G20**, intervalo orientativo **20–40 %**. Para la meta
completa **XNU físico → EDK2**, aproximadamente **25 %**, intervalo **15–35 %**.
Son juicios sobre trabajo y riesgo; no porcentajes medidos, probabilidades de
éxito ni una predicción de fecha. La incertidumbre del BSP es considerable.

El 20 % repetido anteriormente no tenía un desglose actualizado. Esta revisión
cambia el método de estimación; no representa diez puntos de trabajo terminados
hoy. La ejecución física y el handoff permanecen sin demostrar. La base técnica
de esta revisión es el commit **1073f78e9fa3b9ca1f36177eb51050e44c10483d**;
las observaciones se conservan en el [registro de revisión](../evidence/progress-review-20261102/review.json).

Los pesos y créditos siguientes son provisionales. La última columna contiene
hechos verificables. Un crédito parcial no equivale a una puerta superada.

| Bloque hasta primer XNU físico | Peso | Crédito estimado | Estado comprobado |
|---|---:|---:|---|
| Infraestructura inicial: fuentes, toolchain C, MIG y pruebas | 10 | 10 | Clang reconstruido desde fuentes y CI limpia de 157 unidades; 70 headers MIG y 42 probes RPC. Este crédito cubre la infraestructura inicial, no todos los requisitos futuros del compilador |
| Integración nativa y enlace | 25 | 10 | 159 unidades base experimentales y 26 RPC seleccionados; 185 objetos dejan 436 nombres sin proveedor y ninguna imagen. Falta cerrar y validar el ejecutable; el runtime Blocks requiere ampliar y probar la metadata C++ del compilador |
| Entry, datos, carga y MMU | 20 | 7 | Entry original y productor candidato ejecutados en QEMU; ABI boot_args cotejado. Faltan colocar imagen, contexto retenido, propiedad de RAM y traducciones conectadas a XNU |
| Bootstrap Mach operativo | 15 | 0 | Sin ejecución XNU: VM/allocators, primer hilo, transición de contexto y timer pendientes |
| BSP e instrumentación física G20 | 20 | 0 | Sin payload AtlanticOS ejecutado ni IRQ, timer o logging físico propios comprobados |
| Carga temporal y recuperación independiente | 10 | 3 | Identidad/desbloqueo observados; Recovery y bootloader parcialmente comprobados. Vía temporal y recuperación mediante botones tras fallo de payload pendientes |
| **Total estimado** | **100** | **30** | **Primer XNU físico todavía no logrado** |

Para XNU → EDK2 se asigna provisionalmente el 80 % del esfuerzo al primer
arranque y el 20 % a quiesce/handoff y su verificación posterior. Ese último
bloque sigue en cero: 0,8 × 30 = 24, redondeado a aproximadamente 25 %. Es otra
suposición de planificación, sujeta a revisión cuando conozcamos el hardware.
AtlanticBIOS completo, VNC, Wi-Fi y otras placas conservan su alcance posterior;
no forman parte de estas dos estimaciones.

El próximo hito sustantivo es un **ejecutable estático XNU real enlazado**, con
proveedores explícitos y sin imports ignorados o funciones ficticias. Después:
bootstrap nativo en laboratorio con contexto Mach válido, BSP original G20,
carga temporal/recuperación independientes y evidencia física. El handoff
necesita evidencia propia desde ese XNU operativo.

El número de objetos o símbolos no mide linealmente el esfuerzo: añadir un
proveedor puede descubrir dependencias nuevas. La RAM residente sigue sin medir.

Para evitar que otro porcentaje oculte lo pendiente, cada informe de avance debe
indicar también estas puertas. Actualmente están **0 de 4** superadas hacia el
primer XNU físico; el handoff añade una quinta. Son criterios de aceptación,
no tareas de igual tamaño: 0/4 no significa cero trabajo realizado, y 3/4 no
significaría el 75 % del esfuerzo.

| Puerta | Evidencia necesaria para superarla | Estado en la revisión |
|---|---|---|
| P1: imagen XNU estática | Enlace estricto completo, proveedores reales, cero imports pendientes y validación del Mach-O exacto | PENDIENTE: enlace exit 1, sin imagen |
| P2: XNU operativo en laboratorio | Ejecutar la imagen con VM/allocator y contexto válidos; un hilo Mach y timer o transición de contexto instrumentados | PENDIENTE: QEMU ejecuta únicamente el entry/productor originales, XNU_NOT_LINKED |
| P3: vía física G20 | Recuperación independiente por botones, carga temporal comprobada e instrumentación de entry/BSP propios, sin escritura de particiones | PENDIENTE: se observó Recovery OEM; no se probó el retorno independiente tras un payload ni la vía temporal |
| P4: primer XNU físico | Captura física de la imagen exacta alcanzando bootstrap y servicio Mach sustantivo con BSP original; retorno stock | PENDIENTE: ninguna ejecución AtlanticOS en G20 |
| P5: XNU → EDK2 | Desde ese XNU operativo: PREPARE/QUIESCE/COMMIT, DMA/memoria controlados y entrada EDK2 física identificable | PENDIENTE: sin handoff |

Se actualizará el crédito al completar trabajo sustantivo identificado o al
descubrir un cambio de alcance, explicando la razón. Una puerta solo cambia con
su evidencia de aceptación. Más objetos, más tests o menos símbolos indefinidos
se registran como avances de integración; no convierten automáticamente esas
cifras en puntos porcentuales. Una estimación sin cambio debe ir acompañada del
hito que sigue abierto y del avance concreto desde el informe anterior.

Base de la revisión: [meta](ACTIVE_GOAL.md), [estado](PHASE_STATUS.md),
[pruebas del G20](DEVICE_TEST_PLAN.md), [entry](ENTRY_LAB.md),
[plan de imagen](STATIC_IMAGE_PLAN.md), [boot_args](BOOT_PREPARATION.md) y
[colas, esperas VM y enlace actual](XNU_QUEUE_VM_PROVIDERS.md).
La [CI limpia de 155 unidades](https://github.com/h0nda1337/AtlanticOS/actions/runs/41374630610)
terminó success en 1f2fa529cb1c567f3f405f532017d77ad24f8bfa; la
[auditoría conservada](../evidence/xnu-ci155-20261102/README.md) documenta coincidencia
de fuentes/ABI y los límites: LLD upstream sin el modo estático original local,
errores de opciones, sin imagen, sin reproducción binaria completa y sin XNU
ejecutado. No se ha accedido al teléfono para esta revisión.

Actualización de la revisión: el [logging RAM original](XNU_EARLY_RAM_LOG.md)
llevó el build local a 157 unidades. Las colas C++, contadores y esperas VM lo
llevan a 159; el enlace pasa de 463 a 436 nombres pendientes, sin imports nuevos.
El kernel sigue sin imagen ni ejecución; estos avances mantienen el crédito
provisional del bloque, sin declarar cerrada P1.

CI del commit 1073f78 consultada el 2026-11-02: [host](https://github.com/h0nda1337/AtlanticOS/actions/runs/41495850965)
y [carril XNU estándar](https://github.com/h0nda1337/AtlanticOS/actions/runs/41495851003)
terminaron success. La [reconstrucción experimental limpia de 159 unidades](https://github.com/h0nda1337/AtlanticOS/actions/runs/41496031846)
seguía in_progress al consultar; no se le atribuye un resultado futuro ni la
prueba local del enlazador estático original. El carril estándar compila trece
unidades base y no reproduce el núcleo experimental completo.

Bloqueo de integración identificado en un probe posterior: el runtime nativo
`libkern/libclosure/runtime.cpp` necesita descriptores kalloc de records C++.
Nuestra API de layout v2 es explícitamente C y rechaza ese uso, como exige su
contrato actual. No se han eliminado los descriptores ni añadido proveedores
ficticios; la ampliación del compilador y su validación siguen pendientes.
