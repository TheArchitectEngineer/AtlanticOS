# Contrato de entrada y handoff — borrador v1, no ABI ejecutada

Este documento define lo que hay que acordar antes de Fase 2. No promete que el
bootloader OEM o el EDK2 publicado acepten estos campos. Estado: UNIMPLEMENTED.

## Entrada OEM a AtlanticOS

El [candidato OEM analizado offline](STOCK_FIRMWARE_ANALYSIS.md) usa cabecera
Android v2 / página 2048 y lleva una Android DT table dentro de su sección dtb.
Sus campos de carga no son todavía direcciones runtime demostradas de esta
unidad. No empaquetar AtlanticOS suponiendo v3 por la existencia de vendor_boot.

Entry AArch64 little endian, fuente propia. Guardar x0-x3, MPIDR y CurrentEL en
zona propia antes de llamar a C. No usar stack ajeno sin validar. Capturar SCTLR,
VBAR y registros de traducción del EL disponible; nunca leer registros EL2 desde
EL1. Enmascarar interrupciones solo de manera justificada y preservar estado
para diagnóstico. Registrar CNTFRQ y accesibilidad del contador.

La evidencia externa sugiere EL2 con MMU/I/D-cache OFF ([S07/S17](SOURCE_INDEX.md)).
En cada nueva imagen medirlo de nuevo. No suponer que EL2 permanece disponible
si un bootloader diferente entra en EL1. EL2→EL1, HCR, SPSR, timers y GIC deben
tener transiciones explícitas, barreras y vectores válidos; no existe código
AtlanticOS que las implemente todavía. Secure world y EL3 quedan bajo OEM.

Validar FDT por magic, totalsize acotado, offsets/alineación y terminadores.
Copiarlo a RAM propia antes de liberar memoria del loader. Extraer memory,
memreserve, reserved-memory, chosen/initrd/framebuffer y psci; comparar con
firmware y rangos de la imagen. DTB es entrada no confiable. No explorar MMIO
arbitrario para descubrir periféricos. Todo el bootstrap se limita a rangos
documentados hasta tener pruebas de memoria en el dispositivo.

## Contexto interno AtlanticBootContext v1 propuesto

Registro serializable little endian independiente de punteros C, alineado a 8.
No reinterpretar bytes como struct nativa. Campos con tamaño y versión:

| Campo | Forma / regla |
|---|---|
| magic, major/minor, total_bytes | `ATLC` + v1; rechazar major desconocido y límites inválidos |
| image_sha256, upstream_commit, patchset_sha256 | vincular todo log al binario y fuentes exactos |
| board_id + firmware_id | cadenas UTF-8 acotadas, identificador normalizado |
| initial_el, cpu_count, primary_mpidr | observados, no constantes genéricas |
| memory_map_pa/count/entry_bytes | rangos 64 bits con overflow/solapamientos prohibidos |
| region {start, bytes, attributes, owner} | owner OEM_SECURE, RESERVED, ATLANTIC, PAYLOAD o TRANSFER; mapa RAM y MMIO separados |
| dtb_pa/bytes | copia propia validada; conservar original hasheado |
| framebuffer | PA, bytes de reserva, width/height/stride/formato; `height*stride <= reserva` |
| clock_frequency + sample_ticks | calibración y reloj de cuenta atrás monotónico |
| log_pa/bytes + final_memory_report | ring buffer limitado con checksums y high-water marks |
| trust + fallback record ID | OEM/AVB y firma propia separados; no claves privadas |

Mapa de intervalos sin doble conteo: tablas, stacks, heap, DMA y framebuffer se
asignan a propietarios. Un alias virtual referencia el mismo intervalo físico.
No tocar carveouts modem/TEE, ramoops, RPMB, buffers bootloader ni initrd. No
solapar carga, stack, DTB, destino EDK2 o buffers heredados. Regiones liberadas se
marcan únicamente después de que su propietario deje de usarlas.

## AtlanticOS a XNU

El boot_args de [X08](SOURCE_INDEX.md) exige virtBase/physBase/memSize,
topOfKernelData, vídeo, árbol y otros campos. XNU consulta SecureDT ([X12](SOURCE_INDEX.md));
el FDT de Linux no es automáticamente su representación compatible. Diseñar
adaptador o acceso original a FDT desde Platform Expert; nunca un cast.

El adaptador fijará PAGE_SIZE/pmap según CPU, reservas y configuración XNU.
No heredar PAC, Apple CPU, KTRR/SPTM o páginas 16 KiB de VMAPPLE sin soporte
comprobado. Las llamadas al Platform Expert y al scheduler siguen siendo rutas
reales de upstream, instrumentadas y enlazadas. El Python host no participa.

## ABI BSP en ejecución

`include/atlantic/platform.h`: ABI v1 con struct_bytes, ID y lista de capacidades.
Cada callback devuelve ATL_UNSUPPORTED si falta; se validan buffers y rangos.
No se interpreta un cero inicial como capacidad verificada. Los punteros solo
son válidos dentro de la instancia XNU/BSP; no sobreviven al handoff.
`list_boot_sources`: count es in/out capacidad/cantidad, sin escrituras parciales
en buffer pequeño; error ATL_INVALID hasta definir código de buffer insuficiente.
`block_read` solo acepta sectores completos y exige `sectors <= count-lba`.

## AtlanticOS a EDK2

Un adaptador debe acordar con la entrada **exacta** del destino: PA de carga y
entry, EL, stack, estado de MMU/cachés, DTB/HOBs, memoria transferida y reservas.
No confundir cargar un firmware EDK2 con llamar a una aplicación EFI.
No existe aún esa ABI implementada ni imagen destino integrada.

1. PREPARE: validar manifiesto/firma/board, destino, rangos y capacidad; mantener
   recuperación independiente. Nada irreversible ni cambio de slots.
2. QUIESCE: cerrar VNC/sockets, limpiar secretos, detener IRQ/timer/DMA de cada
   periférico, verificar finalización, resolver watchdog y flush de cachés según
   atributos. Si un dispositivo no se detiene, abortar antes de commit.
3. COMMIT: congelar asignaciones; emitir mapa final/hashes, invalidar callbacks
   XNU y transferir control una vez. No retornar a un contexto XNU destruido.
4. Si falla antes de commit, mantener diagnóstico sin retry automático. Si falla
   después, depender de recuperación OEM física: ningún mock demuestra que el
   código real pueda regresar. La ausencia de DMA residual requiere prueba real.

EDK2 inicializa sus Boot Services, protocolos y Runtime Services. Solo entonces
se usa LoadImage/StartImage para EFI ARM64. No se llama ExitBootServices desde
XNU suponiendo que ya existe una sesión UEFI. ResetSystem futuro debe resolverse
en EDK2; no salta a funciones de XNU que ya no está residente.

Referencias oficiales: [Boot Services](https://uefi.org/specs/UEFI/2.10/07_Services_Boot_Services.html),
[System Table y Runtime](https://uefi.org/specs/UEFI/2.10/04_EFI_System_Table.html),
[Runtime Services](https://uefi.org/specs/UEFI/2.10/08_Services_Runtime_Services.html).
