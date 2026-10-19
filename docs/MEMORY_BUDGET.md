# RAM: objetivo y método

Objetivo estricto: residente antes del handoff **<104 857 600 bytes**, incluyendo
todo lo que AtlanticOS posee o reserva para funcionar. Estado dispositivo:
**UNMEASURED**; no hay XNU enlazado ni ejecutado. La memoria del simulador Python
no demuestra que el firmware quepa.

| Categoría provisional | MiB |
|---|---:|
| XNU reducido, Mach/VM/heap | 42 |
| BSP, drivers, tablas y stacks adicionales | 15 |
| UI/framebuffer | 12 |
| Boot/verificación/config | 7 |
| Red/VNC opcional | 12 |
| Reserva emergencia/fragmentación | 11 |
| Total propuesto, sin medición | 99 |

El mapa DXE de referencia reserva 0x04200000 = 69 206 016 bytes (66 MiB) en
0x83300000..0x87500000 ([S08](SOURCE_INDEX.md#s08)). Es una arena del firmware
existente, no capacidad física total ni consumo residente AtlanticOS. Tampoco
demuestra un presupuesto de XNU: pueden existir otros buffers fuera de ella.

Framebuffer de referencia: 720*1600*4 = 4 608 000 bytes visibles. La reserva
declarada es 0x009E4000 = 10 371 072 bytes ([S06](SOURCE_INDEX.md#s06)). Para la
meta se cuenta la reserva retenida, no solo los píxeles visibles. Doble buffer,
scratch, compresión VNC y buffers NIC se cuentan aparte si se asignan.

## Instrumentación física requerida

Emitir mapa antes y después de MMU, bootstrap VM, menú, red opcional y PREPARE,
además de justo antes de COMMIT. Cada intervalo tiene PA, tamaño, dueño,
categoría, committed/reserved, máximo alcanzado y sitio de asignación.
Las reservas incluyen kernel text/data/BSS, tablas, stacks por CPU y excepciones,
heaps/zonas Mach, DTB, logs, framebuffer y sus reservas, DMA y payload EDK2
precargado. Las reservas OEM excluidas del allocator se registran aparte; si
AtlanticOS las retiene como framebuffer u otro recurso, sí entran en su total.

Contar la unión de intervalos físicos una vez. No sumar committed a reserved
si committed está contenido, ni dos aliases virtuales al mismo framebuffer.
Reportar total retenido y pico de asignaciones por separado. Incluir tamaño de
imagen comprimida/descomprimida y doble residencia temporal durante handoff.
Un firmware de 20 MiB en disco no es una medición de 20 MiB RAM.

`atlantic_core.validation.memory_report` prueba contabilidad de fixtures con
solapamientos/overflow rechazados y el límite estricto. No calcula RAM de un
teléfono. La futura instrumentación XNU necesita hooks originales en su allocator
y page tables, conservando comportamiento real. Cualquier memoria no clasificada
impide declarar PASS de presupuesto.

## Medición host real y separada

`python tools/validate.py` mide tracemalloc y RSS/peak working set del proceso de
validación, además de replay real de cinco segundos. Resultados en
`work/validation/host-memory.json`, copiados a evidence/host tras validación.
Windows: GetProcessMemoryInfo; Linux: /proc/self/status o getrusage. El informe
identifica OS, versión y alcance. Tracemalloc cubre asignaciones Python; RSS
incluye intérprete/librerías/overhead y no se suma a tracemalloc.

No extrapolar ese valor a XNU ni deducir DEVICE_VERIFIED. Si el firmware supera
el límite: publicar el excedente por categoría, reducir buffers/subsistemas
reales y volver a medir. No ocultar memoria reservada ni moverla fuera del contador.
