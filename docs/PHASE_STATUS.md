# Puertas de entrega — actualizado 2026-10-20

| Fase / requisito | Estado exacto | Evidencia / siguiente puerta |
|---|---|---|
| 0: lectura completa del handoff | DONE | SHA-256 en evidence/host/provenance.json |
| 0: auditoría G20, código activo, XNU, arquitectura | HOST_TESTED (herramientas) / revisión documental | sources.lock.json y FACT_MATRIX.md |
| 0: identidad Android y bloqueo de este G20 | CONFIRMED por ADB de solo lectura | DEVICE_INTAKE_20261020.md; variante XT2128-1, fingerprint, slot _a y desbloqueo observados |
| 0: recorrido OEM Android → bootloader → Android | CONFIRMED por observación USB/ADB | adb reboot bootloader, is-userspace=no, fastboot reboot y mismo fingerprint/slot; no prueba payload fallback |
| 0: recuperación física independiente, metadata A/B y vía temporal | PENDING / UNKNOWN | Botones sin entrada verificada; 26 variables fastboot vacías; firmware exacto y método temporal pendientes |
| 1: política, menú, temporizador, teclas, errores | HOST_TESTED | tests, escenarios y captura en evidence/host |
| Herramientas de inventario de dispositivo | HOST_TESTED | 8 tests nuevos; suite total 54; evidencia de consultas y límites en evidence/device-intake-20261020 |
| 1: configuración | HOST_TESTED parcial | validación versionada y logs en sesión; prioridad/destino/timeout/red bloqueados en defaults seguros |
| 1: RAM | HOST_TESTED solo proceso host | informe RSS/tracemalloc; objetivo firmware sin medir |
| 2: entry y bootstrap XNU real | UNIMPLEMENTED | herramientas Apple/adaptación y contratos de CPU pendientes |
| 2: ABI C BSP | BUILT_ARM64 si build_abi termina | objeto sin drivers y sin kernel, hash propio |
| 3: energía y fallback Android | UNIMPLEMENTED | método de reset/PMIC y vía OEM por demostrar |
| 4: handoff EDK2 y almacenamiento | UNIMPLEMENTED | contrato propuesto; sin driver AtlanticOS |
| 5: Ethernet y VNC | UNIMPLEMENTED | política negativa host; no servidor RFB |
| 6: segunda placa / Wi-Fi | UNIMPLEMENTED | ABI versionada preparada, sin segundo port |

La entrega documental de Fase 0 está preparada. Su comprobación experimental
en teléfono permanece abierta; no se declara cerrada toda la Fase 0. La Fase 1
permite verificar lógica y UI. La captura es del framebuffer lógico del host,
no una foto del dispositivo ni emulación de XNU. No se ha ejecutado QEMU.
