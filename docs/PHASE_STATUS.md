# Puertas de entrega — actualizado 2026-10-22

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
| 2: entry G20 y ejecución bootstrap XNU real | UNIMPLEMENTED | objetos compilados no acreditan arranque; enlace/pmap/Platform Expert pendientes |
| Herramienta oficial MIG | HOST_TESTED | MIG_HOST_BUILD.md: binario host genuino, ABI de metadata y 20 archivos de interfaces generados; sin compilar esos C ni enlazar kernel |
| Port XNU incremental de laboratorio | BUILT_ARM64 | Trece objetos estándar; cuarenta y siete con compilador experimental explícito. IPC, importancia y metadata RO nativos; headers ampliados a 57 en XNU_RPC_BUILD.md; sin enlace ni ejecución |
| Código RPC MIG de XNU | BUILT_ARM64 | 42 archivos generados y compilados por carril, 57 headers; ABI de 21 descriptores y proveedores de 17 tablas kobject comprobados en experimental; sin RPC ejecutado |
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
