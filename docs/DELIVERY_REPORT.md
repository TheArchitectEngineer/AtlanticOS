# Primera entrega verificada — 2026-10-19

Código inicial publicado en [commit 481abe8](https://github.com/h0nda1337/AtlanticOS/commit/481abe8983f8cb19007eb596ac9175eb696ab894).
Trabajo principal: `G:\AtlanticOS`. Repositorio independiente; ningún cambio en
el port UEFI de referencia ni en el checkout oficial XNU.

| Comprobación realizada | Resultado y alcance |
|---|---|
| Lectura del handoff completo | SHA-256 registrado en evidence/host/provenance.json |
| Auditoría de fuentes | 31 objetos Git con commit, archivo/línea y SHA-256; fuente activa SD V4, evidencia y USB V6 examinados |
| Pruebas locales Windows | 46 tests aprobados; logs en evidence/host/tests.log |
| Replay de temporizador real | Ver evidence/host/realtime-timer.json; 5/4/3/2/1 con monotonic host, Android mock |
| Capturas UI | Menú, mantenimiento, countdown, setup y confirmación de energía; mismo renderer que GUI |
| Tk backend | Construcción offscreen y carga PNG comprobadas; no se declara prueba humana de clics |
| Medición de memoria | RSS/peak working set y tracemalloc reales del proceso host en evidence/host/host-memory.json; RAM firmware null |
| Objeto BSP AArch64 | 2432 bytes, ELF e_machine=183, SHA-256 7d0c5bb9fe60dbf343cf7d2d4ceee80f706961287e6d499f713211a0fab169ea; ningún driver ni XNU |
| Evidencias | 17 artefactos host y 3 del build ABI con hashes verificados |
| Clon limpio desde GitHub | 46 tests, hashes de evidencia y build ABI pasan; objeto idéntico con la misma versión Clang |
| GitHub Actions Ubuntu | [Run 39321937000](https://github.com/h0nda1337/AtlanticOS/actions/runs/39321937000) SUCCESS: tests/replay/capturas/RAM host/build ABI/evidencias |
| Hardware propio AtlanticOS | Ninguno; sin EMULATED ni DEVICE_VERIFIED |

Las reproducciones Linux y Windows prueban lógica/tooling. No se supone igualdad
del objeto con versiones distintas de Clang; el hash idéntico anterior pertenece
a la reproducción Windows con el mismo compilador. El job Linux registra su
propia versión de herramientas y no convierte el BSP shell en firmware.

Queda abierta la parte experimental de Fase 0. Siguiente material requerido:
Moto G20 nuevo stock para T00-T02 de DEVICE_TEST_PLAN.md, con variante/build y
ruta OEM de recuperación observados. No necesita ser desbloqueado ni flasheado
para comenzar ese inventario. T03/T04 definirán si hay ruta temporal viable.

XNU reducido, entry original, drivers físicos, firma real, EDK2 handoff, VNC y
medición <100 MiB en teléfono permanecen UNIMPLEMENTED/UNTESTED según sus docs.
El proyecto no atribuye a AtlanticOS los logros físicos del port UEFI existente.
