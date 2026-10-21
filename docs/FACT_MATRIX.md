# Matriz de hechos, inferencias y bloqueos

Auditoría: 2026-10-19. Referencia G20 fijada en commit
`321c01f87c78e7e9c5d82f692b71fcdad8ef921a` (publicación 2026-10-09).
Cada ID enlaza archivo/línea y hash en [SOURCE_INDEX](SOURCE_INDEX.md).

CONFIRMED significa que el hecho está respaldado por la fuente indicada.
Cuando es evidencia externa, **no** significa DEVICE_VERIFIED de AtlanticOS.
Las declaraciones del código sin log/foto suficiente se distinguen expresamente.

| Hecho | Estado | Propietario / fuente con líneas | Fecha física / limitación |
|---|---|---|---|
| DXE, framebuffer y Shell arrancan | CONFIRMED, reportado por autor | Port UEFI, [S01](SOURCE_INDEX.md#s01) | Publicado 2026-10-09; no repetido aquí |
| Plataforma SD ready=1 e identificación 60 456 960 sectores | CONFIRMED | Port UEFI [S02/S10](SOURCE_INDEX.md#s02) | 2026-10-08 V4 |
| Block I/O publicado | CONFIRMED | Port UEFI [S10](SOURCE_INDEX.md#s10) | 2026-10-08; no equivale a leer sectores |
| CMD17 113A0011→113A0013 rechazado antes de esperar DMA | CONFIRMED | Port UEFI [S09](SOURCE_INDEX.md#s09), comparación en sdhci_ro.c:183-189; [S10](SOURCE_INDEX.md#s10) | 2026-10-08 |
| DMA funciona / DMA está averiado | UNKNOWN | [S02/S10](SOURCE_INDEX.md#s02) | tries=1, complete=0, guards=1, fault=1 no resuelven hardware |
| IRQ=0x2 V2/V3 es transfer complete | CONFIRMED | [S02](SOURCE_INDEX.md#s02), [S09](SOURCE_INDEX.md#s09) define IRQ_TRANSFER en línea 24 | Sin datos PIO verificados |
| Lectura de sector y FAT probadas | BLOCKED | Port UEFI [S02/S03](SOURCE_INDEX.md#s02) | Deben validarse antes de FS |
| Hub 1A40:0801 alimentado/enumerado, HID=0 | CONFIRMED, reportado | Port UEFI [S01/S02](SOURCE_INDEX.md#s01) | No teclado funcional |
| V5 SET_ADDRESS(1) falla fase SETUP | CONFIRMED, reporte fotográfico | [S14](SOURCE_INDEX.md#s14) | Fecha física no especificada en ese README |
| V6 mide causa específica EP0 | CONFIRMED en fuente; UNTESTED físico | [S13/S14](SOURCE_INDEX.md#s13) | Sin nueva validación física |
| USB Bulk / Mass Storage / Ethernet | UNKNOWN / UNIMPLEMENTED en AtlanticOS | [S13/S14](SOURCE_INDEX.md#s13) no los demuestran | Enumerar hub no satisface esas dependencias |
| Almacenamiento interno | UNKNOWN, no intentado | Handoff principal; S01/S02 no reportan prueba interna | No se registra como fallo |
| Bootstrap DXE 0x83300000..0x87500000 = 66 MiB | CONFIRMED en fuente | [S08](SOURCE_INDEX.md#s08) | No es RSS ni toda la DRAM física |
| RAM adicional / ACPI / CPU para Windows integrados | BLOCKED | [S03/S04](SOURCE_INDEX.md#s03) | Propuestas separadas, no integradas físicamente |
| Windows PE arrancó | CONFIRMED negativo | [S02/S10](SOURCE_INDEX.md#s02) | NO, 2026-10-08 |
| Carga 0x80080000, x0=0x82000000/FDT | CONFIRMED como declaración del código | [S05/S17](SOURCE_INDEX.md#s05) | Requiere nueva captura propia; no todos los logs originales públicos |
| EL2, MMU/cache OFF | CONFIRMED como experimento declarado | [S07/S17](SOURCE_INDEX.md#s07) | AtlanticOS debe remedirlo |
| FB 0x9E000000, 720x1600, stride 2880, BGRX | CONFIRMED en código de referencia | [S06](SOURCE_INDEX.md#s06) | Pruebas white/RGBW descritas; repetir por variante |
| GICv3 D=0x12000000 / R=0x12040000 | INFERRED para nuevo firmware | [S05](SOURCE_INDEX.md#s05) | Falta IRQ/timer propio; acceso y grupos seguros por verificar |
| Timer 26 MHz / PPIs 29/30/27/26 | CONFIRMED como declaración de cabecera | [S05](SOURCE_INDEX.md#s05) | Leer CNTFRQ y medir IRQ; no solo constante |
| PSCI compatible 0.2 vía SMC en DT | CONFIRMED como declaración de cabecera | [S05](SOURCE_INDEX.md#s05) | No demuestra SYSTEM_OFF/RESET seguros |
| Botones Volume/Power GPIO/PMIC y debounce real | UNKNOWN | No BSP físico AtlanticOS | Identificar DT y medir sin adivinar MMIO |
| Reinicio forzado volvió a Android tras V1 | CONFIRMED, evidencia externa acotada | [S11](SOURCE_INDEX.md#s11), [S19](SOURCE_INDEX.md#s19) | 2026-10-04; foto revisada visualmente y hash validado aquí |
| Fallback Android tras V4 / con AtlanticOS | UNKNOWN | [S10](SOURCE_INDEX.md#s10): NOT_CHECKED_DURING_PUBLICATION | No generalizar V1 a nueva imagen |
| Boot header/version/page size | CONFIRMED en candidato descargado, UNKNOWN igualdad con teléfono | [Análisis offline](STOCK_FIRMWARE_ANALYSIS.md): v2 / 2048, fingerprint ramdisk coincide | Canal RETBR frente a amxmx; sin lectura de boot original ni verificación de firma OEM |
| fastboot boot temporal soportado | UNKNOWN | No prueba propia | Requiere teléfono y estudio OEM; no asumir por A/B |
| Insertar menú bajo Orange State sin bootloader | BLOCKED_BY_BOOTLOADER | Diseño BOOT_CHAIN.md | No hay API demostrada |
| Upstream XNU identificado y descargado | CONFIRMED, HOST_TESTED de procedencia | [X01-X12](SOURCE_INDEX.md#x01), dependencies.lock.json | xnu-12377.1.9; sin cambios |
| XNU contiene ruta GICv3 para VMAPPLE | CONFIRMED en fuente | [X09/X10](SOURCE_INDEX.md#x09) | Depende de features Apple/virtualización y Group0; no copiar configuración |
| Clang genérico compila XNU completo sin SDK Apple | BLOCKED en entorno actual | [X02](SOURCE_INDEX.md#x02), falta xcrun/mig/iig/SDK | No se ejecutó un build completo fallido para demostrar imposibilidad universal |
| XNU ejecutado / RAM <100 MiB en G20 | UNKNOWN / UNIMPLEMENTED | Ninguna evidencia propia | No hay DEVICE_VERIFIED AtlanticOS |

No se ejecutaron suites del port UEFI ni se recompilaron sus drivers: esos
resultados publicados siguen siendo de su autor. La inspección local es una
auditoría estática y visual de referencias, no una validación eléctrica.
