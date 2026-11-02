# Estimación de avance — 2026-11-02

Estimación de ingeniería: **aproximadamente 30 % hacia el primer arranque físico
instrumentado de XNU en el G20**, intervalo orientativo **20–40 %**. Para la meta
completa **XNU físico → EDK2**, aproximadamente **25 %**, intervalo **15–35 %**.
Son juicios sobre trabajo y riesgo; no porcentajes medidos, probabilidades de
éxito ni una predicción de fecha. La incertidumbre del BSP es considerable.

El 20 % repetido anteriormente no tenía un desglose actualizado. Esta revisión
cambia el método de estimación; no representa diez puntos de trabajo terminados
hoy. La ejecución física y el handoff permanecen sin demostrar.

Los pesos y créditos siguientes son provisionales. La última columna contiene
hechos verificables. Un crédito parcial no equivale a una puerta superada.

| Bloque hasta primer XNU físico | Peso | Crédito estimado | Estado comprobado |
|---|---:|---:|---|
| Fuentes, toolchain, MIG y pruebas reproducibles | 10 | 10 | Reconstrucción limpia de Clang y 155 unidades; 70 headers MIG y 42 probes RPC. Comportamiento en un kernel ejecutado todavía sin validar |
| Integración nativa y enlace | 25 | 10 | XNU genuino compilado; 183 objetos dejan 463 nombres sin proveedor y ninguna imagen. Falta cerrar y validar el ejecutable |
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

Base de la revisión: [meta](ACTIVE_GOAL.md), [estado](PHASE_STATUS.md),
[pruebas del G20](DEVICE_TEST_PLAN.md), [entry](ENTRY_LAB.md),
[plan de imagen](STATIC_IMAGE_PLAN.md), [boot_args](BOOT_PREPARATION.md) y
[CPU/caché y enlace actual](XNU_CPU_CACHE_PROVIDERS.md).
La [CI limpia de 155 unidades](https://github.com/h0nda1337/AtlanticOS/actions/runs/41374630610)
terminó success en 1f2fa529cb1c567f3f405f532017d77ad24f8bfa; la
[auditoría conservada](../evidence/xnu-ci155-20261102/README.md) documenta coincidencia
de fuentes/ABI y los límites: LLD upstream sin el modo estático original local,
errores de opciones, sin imagen, sin reproducción binaria completa y sin XNU
ejecutado. No se ha accedido al teléfono para esta revisión.

Actualización posterior del mismo día: [logging RAM original](XNU_EARLY_RAM_LOG.md)
eleva el build local a 157 unidades y resuelve dos nombres. El kernel sigue sin
imagen ni ejecución; este avance mantiene el crédito provisional del bloque.
