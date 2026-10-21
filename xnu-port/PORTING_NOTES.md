# Estado del port real

Upstream: apple-oss-distributions/xnu, xnu-12377.1.9,
f6217f891ac0bb64f3d375211650a4c1ff8ca1ea. Patchset vacío.

| Componente | Ejecutado por AtlanticOS | Estado |
|---|---|---|
| Entry ARM64 propio, preflight | Solo QEMU EL1/EL2 | EMULATED sin XNU enlazado; no G20 |
| Transición EL2 a EL1 para XNU | No | UNIMPLEMENTED |
| osfmk/arm64/start.s / osfmk/arm/arm_init.c | No | UNIMPLEMENTED |
| Mach VM, allocators, scheduler, hilos | No | UNIMPLEMENTED |
| Platform Expert UMS512 | No | UNIMPLEMENTED |
| pmap, GIC, timer | No | UNIMPLEMENTED |
| BSD/IOKit/libkern/libsa | No | Dependencias auditadas; recorte pendiente |
| Build completo en Windows sin SDK Apple | No | BLOCKED por adaptación de build/herramientas |
| Objeto C BSP ARM64 sin drivers | Consultar evidence | Solo ABI; no contiene XNU |

No hay componentes XNU deshabilitados mediante parches todavía. El plan propone
uniprocesador, sin userland, kexts dinámicos, red o GPU al principio, conservando
bootstrap Mach, VM y scheduler reales. No se ha demostrado que ese recorte enlace.
No afirmar que BSD/IOKit se pueden quitar cambiando una sola opción.

Para cada futuro parche registrar razón, símbolos afectados, tests, hash de
preimagen/postimagen y diferencias con upstream. Mantener dSYM/map/símbolos.
Ver docs/XNU_PORTING_FEASIBILITY.md y docs/DEVICE_TEST_PLAN.md.
