# Compatibilidad granular

Estado actualizado 2026-10-20. La columna de referencia es del proyecto UEFI ajeno.
AtlanticOS no tiene ninguna capacidad DEVICE_VERIFIED en teléfono.
El inventario Android/AVB propio está en DEVICE_INTAKE_20261020.md; no habilita
capacidad BSP, fallback o XNU. La recuperación independiente sigue pendiente.

| Capacidad | Moto G20 en port UEFI de referencia | Moto G20 en AtlanticOS | Host simulator |
|---|---|---|---|
| Entry propio + XNU real | No es el objeto de ese proyecto | UNIMPLEMENTED | No ejecuta XNU |
| Plan de imagen estática ARM64 | Cargador ajeno no reutilizado | HOST_TESTED portable; integración BSP pendiente | 45 099 casos / 15 fixtures LLD, sin carga ni ejecución |
| Framebuffer | Físico reportado; BGRX 720x1600 | UNIMPLEMENTED | HOST_TESTED RGB lógico |
| Consola textual | Shell observada; teclado USB no funcional | UNIMPLEMENTED | HOST_TESTED vista textual |
| Volume Up/Down / Power | Sin driver físico demostrado en auditoría | UNKNOWN | HOST_TESTED eventos mock |
| Timer | Cabecera declara CNTFRQ 26 MHz | UNTESTED | HOST_TESTED monotonic_ns |
| GICv3 / IRQ | Direcciones en cabecera, no prueba AtlanticOS | UNTESTED | No emulado |
| Reset / Power Off | PSCI SMC declarado, método específico no demostrado aquí | UNSUPPORTED | HOST_TESTED solicitudes y confirmación |
| Android fallback independiente | V1 retorno reportado; V4 no revalidado | BLOCKED por prueba nueva | MOCK solo con flag explícito |
| microSD identify | ready=1, capacidad, Block I/O | UNIMPLEMENTED | fixture sin medios |
| microSD sector / FAT32 | Sin sector demostrado, FAT omitido | UNIMPLEMENTED | solo bloque/GPT fixture; no FAT32 |
| eMMC/UFS interno | No intentado; no fallo demostrado | UNIMPLEMENTED | Sin acceso físico |
| USB host | Hub enumerado; EP0 V5 fallido; V6 sin prueba | UNIMPLEMENTED | Ausencia de medios comprobada |
| USB HID / Mass Storage / Bulk | Teclado sin funcionar; MSC no demostrado | UNIMPLEMENTED | No emulado |
| USB-C Ethernet | Sin evidencia | UNIMPLEMENTED | No sockets |
| Wi-Fi | Chip/firmware/bus por investigar | UNIMPLEMENTED | OFF |
| RTC / batería / cargador | Por investigar | UNKNOWN | No telemetría fabricada |
| ACPI / SMBIOS / EDK2 handoff | Propuestas separadas; no Windows | UNIMPLEMENTED | Fallos de transacción mock |
| EFI / Windows PE | Windows PE no arrancado | UNIMPLEMENTED | No se ejecutan EFI |
| Firmas propias | Sin integración AtlanticOS | UNIMPLEMENTED | rechazo por defecto probado |
| Red / VNC | Hub no prueba red | UNIMPLEMENTED / OFF | gate negativo; no servidor |
| RAM <100 MiB | 66 MiB de bootstrap, no métrica AtlanticOS | UNMEASURED | RSS real host separado |

Otros teléfonos Qualcomm/MediaTek/Unisoc: UNIMPLEMENTED, sin reclamar soporte.
Cada BSP declara ABI, board IDs, rangos investigados y registros de evidencia
propios. El fixture de host no es una segunda placa compatible.

Fuentes físicas y límites: [matriz de hechos](FACT_MATRIX.md).
