# Puertas de entrega — actualizado 2026-10-24

| Fase / requisito | Estado exacto | Evidencia / siguiente puerta |
|---|---|---|
| 0: lectura completa del handoff | DONE | SHA-256 en evidence/host/provenance.json |
| 0: auditoría G20, código activo, XNU, arquitectura | HOST_TESTED (herramientas) / revisión documental | sources.lock.json y FACT_MATRIX.md |
| 0: identidad Android y bloqueo de este G20 | CONFIRMED por ADB de solo lectura | DEVICE_INTAKE_20261020.md; variante XT2128-1, fingerprint, slot _a y desbloqueo observados |
| 0: recorrido OEM Android → bootloader → Android | CONFIRMED por observación USB/ADB | adb reboot bootloader, is-userspace=no, fastboot reboot y mismo fingerprint/slot; no prueba payload fallback |
| 0: acceso manual a Recovery y bootloader | OBSERVED parcialmente | Recovery confirmado por ADB/ro.bootmode y menú descrito por usuario; posterior is-userspace=no tras selección manual |
| 0: salida física independiente, metadata A/B y vía temporal | PENDING / UNKNOWN | Retorno realizado por fastboot reboot a petición del usuario; Power no probado; 26 variables fastboot vacías; equivalencia OEM y método temporal pendientes |
| 0: firmware descargado y formato offline | HOST_TESTED / PARTIAL_MATCH | STOCK_FIRMWARE_ANALYSIS.md: fingerprint coincide, cabecera v2, DTB + cinco overlays; mirror RETBR frente a amxmx, firmas y equivalencia exacta pendientes |
| 1: política, menú, temporizador, teclas, errores | HOST_TESTED | tests, escenarios y captura en evidence/host |
| Herramientas de inventario de dispositivo | HOST_TESTED | 8 tests nuevos; suite total 54; evidencia de consultas y límites en evidence/device-intake-20261020 |
| Inspector offline de firmware | HOST_TESTED | 12 tests adicionales (suite 66), PAC 64 bits, boot v0-v2, DT tables y gzip/newc acotados; sin IO de teléfono |
| 1: configuración | HOST_TESTED parcial | validación versionada y logs en sesión; prioridad/destino/timeout/red bloqueados en defaults seguros |
| 1: RAM | HOST_TESTED solo proceso host | informe RSS/tracemalloc; objetivo firmware sin medir |
| 2: entry ARM64 de laboratorio | EMULATED / BUILT_ARM64 | preflight original, EL1/EL2→EL1h, stack, FDT, contador y BRK; XNU_NOT_LINKED |
| 2: datos originales FDT → árbol de bootstrap XNU | HOST_TESTED / EMULATED / ABI target | BOOT_DATA_BRIDGE.md: inventario con exclusiones, árbol de 504 bytes, ASan/UBSan, ABI con headers XNU y cuatro recorridos QEMU. Sin boot_args completo ni ejecución de SecureDT/XNU |
| 2: entry G20 y ejecución bootstrap XNU real | UNIMPLEMENTED | objetos compilados no acreditan arranque; enlace, MMU/BSP y PE físico pendientes |
| Herramienta oficial MIG | HOST_TESTED | Binario host genuino y ABI de metadata en MIG_HOST_BUILD.md; las pruebas posteriores de C generados se detallan en las filas RPC |
| Port XNU incremental de laboratorio | BUILT_ARM64 | Trece objetos estándar; 148 experimentales, incluidos timers y políticas nativos. Pasan 129/98 checks. Enlace de 174 objetos falla con 502 diagnósticos indefinidos y cero duplicados; sin imagen ni ejecución. XNU_SCHEDULER_TIMER_PROVIDERS.md |
| 2: núcleo original PE y contrato BSP | BUILT_ARM64 / ABI target | Dos fases nativas, SecureDT real como dependencia y lecturas de timebase emitidas; BSP permanece como import fuerte no resuelto. No hay ejecución de PE ni IRQ comprobada |
| 2: memoria física, caché y atómicos nativos | BUILT_ARM64 / ABI y objetos | Seis fuentes intactas, una guarda del fallback vacío y un adaptador original. DC/IC, barreras, CAS y despacho de pager inspeccionados; no ejecutados. Los wrappers de IO coherente no prueban DMA |
| 2: bootstrap sin BSD/IOKit | BUILT_ARM64 / alcance y objetos | Ocho checks por carril; cuatro llamadas no seleccionadas excluidas. VM, scheduler, tareas, hilos y carga de contexto conservados, sin ejecución Mach |
| 2: cadenas originales y lectores de imagen XNU | HOST_TESTED / BUILT_ARM64 / ABI target | 79 344 contratos portables con ASan/UBSan; cuatro entradas ABI fuertes comprobadas. Dos fuentes nativas intactas seleccionadas; requieren header real validado y mapeado. Sin ejecución del lector Mach-O, strsep o XNU |
| 2: política IPC y registro de kobjects | BUILT_ARM64 / alcance, ABI y objetos | 17 cuerpos core y tabla nativos intactos; sin eventos CoreAnalytics identificados por proceso ni excepción de SDK sin BSD. Dos unidades seleccionadas; terminación completa de guards pendiente. No hay IPC ejecutado |
| 2: timers, políticas y contadores nativos | BUILT_ARM64 / ABI y objetos | Diez unidades añadidas, ocho intactas; doce cuerpos core conservados. SFI devuelve el error upstream de función no soportada; tokens requieren contexto de proceso real. Sin timer, política o IRQ ejecutados |
| Reproducción remota de API v2 y 100 unidades | CI success / BUILT_ARM64 | Run 39891229141 de 49bbae4: 26 checks, fuentes/defines y 137 constantes coincidentes. evidencia/clang-layout-ci100-20261023; no prueba la ampliación posterior o hardware |
| Código RPC MIG de XNU | BUILT_ARM64 | 42 probes compilados por carril; CFILES selecciona 26 para enlace. ABI de 21 descriptores; 14 tablas kobject del perfil sin BSD/IOKit. Sin RPC ejecutado; XNU_RPC_PROVIDERS.md |
| Enlazador ARM64 estático experimental | HOST_TESTED / fixtures enlazados | LLD_STATIC_ARM64.md: v2, 54 checks y 15 imágenes, incluida selección weak/strong; XNU mantiene referencias indefinidas, sin imagen kernel |
| 2: ABI C BSP | BUILT_ARM64 si build_abi termina | objeto sin drivers y sin kernel, hash propio |
| 3: energía y fallback Android | UNIMPLEMENTED | método de reset/PMIC y vía OEM por demostrar |
| 4: handoff EDK2 y almacenamiento | UNIMPLEMENTED | contrato propuesto; sin driver AtlanticOS |
| 5: Ethernet y VNC | UNIMPLEMENTED | política negativa host; no servidor RFB |
| 6: segunda placa / Wi-Fi | UNIMPLEMENTED | ABI versionada preparada, sin segundo port |

La entrega documental de Fase 0 está preparada. Su comprobación experimental
en teléfono permanece abierta; no se declara cerrada toda la Fase 0. La Fase 1
permite verificar lógica y UI. La captura es del framebuffer lógico del host,
no una foto del dispositivo ni emulación de XNU. QEMU sí ejecutó el preflight
ARM64 original después de la primera entrega; los registros están separados.

Prioridad actual: ACTIVE_GOAL.md. AtlanticBIOS completo, VNC y Wi-Fi se posponen
hasta núcleo y handoff. Este G20 se trata como sin fastbootd por indicación del
usuario; no se intentará entrar para investigar o instalar.
