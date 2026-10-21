# Plan exacto de pruebas del Moto G20

Se necesita el teléfono **para cerrar la parte experimental de Fase 0 y después
iniciar bring-up**, no para seguir compilando el simulador. El 2026-10-20 se recibió
acceso a un G20 que el usuario entregó ya desbloqueado. Por instrucción del usuario,
la batería no es umbral de aceptación ni se consulta en el inventario. Usar cable
de datos estable. No desbloquear, flashear ni instalar imágenes
para las observaciones T00-T02. Todo resultado se liga a variante/build exactos.

| ID / orden | Observación requerida y procedimiento | Interpretación / gate |
|---|---|---|
| T00 stock | Con teléfono encendido, registrar modelo/variante, build fingerprint, versión bootloader, bloqueo/AVB y arranque Android normal. Si ADB ya está autorizado, consultar getprop ro.product.model, ro.build.fingerprint, ro.boot.verifiedbootstate, ro.boot.flash.locked, ro.boot.slot_suffix. No ejecutar getprop global al publicar, puede contener datos personales. | Falta un dato → UNKNOWN, no inferir por modelo. ADB denegado → registrar, no rootear. |
| T01 recuperación independiente | Con usuario presente, comprobar por botones OEM documentados acceso a bootloader/recovery y retorno Android stock. Registrar vídeo/foto de cada transición y si conserva datos. No elegir wipe/factory reset. | PASS solo si Android vuelve sin AtlanticOS/PC/red. Menú recovery visible no demuestra que arranque stock. |
| T02 variables solo consulta | En bootloader ya alcanzado, consultar product, version-bootloader, current-slot, slot-count, has-slot:boot y successful/unbootable/retry de cada slot si el OEM los soporta. Registrar errores literales; no set_active. | A/B solo confirmado por datos. UNRECOGNIZED no significa slot ausente. Guardar metadata antes de futuros experimentos. |
| T03 stock offline | Conseguir firmware oficial del build correcto por vía permitida, guardar URL/hash/fechas y analizar boot header, tamaños, compresión, DTB/DTBO/vendor_boot y reservas sin conectarlo a un dispositivo de bloques. | Header válido solo establece estructura; no demuestra que el OEM acepte nuestra imagen. Nunca usar offsets de otra variante. |
| T04 vía temporal | Investigar documentación/código bootloader y consulta OEM para determinar si acepta payload temporal en RAM con bloqueo actual. Un ensayo de carga propia exige imagen/contrato revisado, recuperación T01 y autorización específica posterior. No se ejecuta ahora. | Si no existe vía temporal documentada → BLOCKED; no proponer reemplazar slot para sortearlo. |
| T05 entry/CPU, etapa posterior | Entry original sin shim captura x0-x3, CurrentEL/MPIDR, SCTLR/TTBR/TCR/VBAR permitidos, CNTFRQ/contador, hash DTB y reservas antes de modificar estado; salida por canal ya verificado. Binario/ELF/map/hash exactos. | Log solo prueba entry, no XNU. No leer EL2 desde EL1. Si no hay salida fiable, parar y diseñarla. |
| T06 botones/timer/IRQ | Identificar nodos GPIO/PMIC del stock y fuentes nativas; driver original de lectura. Muestrear Up/Down/Power, held inicial, rebotes, corto/largo y contador contra referencia externa; después IRQ timer con GIC/grupos documentados. | Prueba de polling no valida interrupciones; botón USB no valida botones físicos. Registrar eventos y ticks reales. |
| T07 reset/off/fallback | Con mecanismo identificado y autorización de prueba, confirmar físicamente reset y off por separado; observar pantalla/USB y consumo si hay medidor. Después power físico y Android stock. Registrar watchdog antes/después. | Reset solicitado no equivale a reset completado. USB ausente no prueba apagado total. Sin retorno stock no habilitar autoboot. |
| T08 XNU real | Imagen upstream fijada + patchset original + entry/BSP. Registrar PCs/símbolos de start_first_cpu, arm_init, kernel_bootstrap y un hilo/timer/servicio Mach operativo con contexto válido. | Solo aquí se evalúa DEVICE_VERIFIED de port XNU. Un stub o nombre en log falla. |
| T09 RAM | Capturar intervalos/reservas/high-water de todas las categorías al menú, red opcional y precommit; comprobar guardas y ausencia de solapamientos. | PASS <104857600 bytes solo con contabilidad completa. Medir pico de precarga también. |
| T10 SD read-only | En tarjeta de laboratorio con identidad y referencias independientes de esa tarjeta, comparar exactamente sectores 0/2048/99072 cuando esos LBAs sean válidos y correspondan al plan preparado; revisar límites antes. Después FAT32/archivo/hash/EOF. | Identificación no es lectura. Otra tarjeta requiere sus LBAs/contenido; no reutilizar referencias ajenas. No tocar medio durante esta entrega. |
| T11 USB/NIC | Validar rol Type-C, VBUS/PHY, enumerate, transferencias control y Bulk; luego MSC con lectura o NIC de modelo/chip concreto con paquetes verificables. | Hub/LED/HID no prueba Bulk, MSC ni Ethernet. VNC espera a NIC y canal autenticado. |
| T12 EDK2 | Contrato del destino acordado, PREPARE/QUIESCE/COMMIT instrumentados, DMA detenido, canarios y mapa final; probar entrada EDK2 sin XNU residente. Después LoadImage/StartImage y ResetSystem propios EDK2. | Shell de otro firmware no valida este handoff. Boot Manager no equivale a Windows PE. |

Cada prueba física guarda: ID, timestamp y zona, variante seudonimizada, build
stock, estado de bloqueo, imagen/hash, source commit/patchset, comandos exactos,
log bruto, foto/vídeo hasheado, resultado, fallos y retorno a Android. Publicar
seriales, IMEI, cuentas o claves nunca es necesario. Conservar originales privados.

No hay instrucciones ejecutables de flash en este plan. Cualquier desbloqueo o
escritura sería trabajo separado con consentimiento y recuperación concreta.
T00 ya tiene observaciones ADB propias en DEVICE_INTAKE_20261020.md. T01 y T02
requieren la transición física/observación del usuario y consultas fastboot, sin
escrituras. Las etapas posteriores deben esperar a sus puertas previas y código
revisable. La identidad Android observada no prueba integridad de cada imagen.

## Subpruebas pendientes de T05: CPU del G20

Las cuatro ejecuciones QEMU de [ENTRY_LAB](ENTRY_LAB.md) solo cierran el
laboratorio. Para el G20 se necesitan estos resultados independientes, después
de disponer de carga temporal y recuperación verificadas; no se ejecutan aquí:

1. Captura inicial sin transición: hash de imagen/ELF, x0-x3, CurrentEL, MPIDR,
   SCTLR del EL actual y CNTFRQ; canal de salida propio ya identificado y
   timestamp de una grabación física. M/C/I activos no autorizan a borrarlos:
   exigen estudiar coherencia y traducción. Sin salida, el resultado es
   INDETERMINATE, no asumir que se alcanzó entry o una causa concreta.
2. Imagen específica del BSP G20 que continúe en EL1h: registrar CurrentEL=1,
   DAIF, stack alineado dentro de RAM propia y VBAR apuntando a vectores de esa
   imagen. Desde EL1 no consultar HCR/CNTHCTL/otros registros EL2. Si el OEM ya
   entra en EL1, debe seguir funcionando esa ruta sin una transición ficticia.
3. Contador accesible que progrese y comparación de CNTFRQ contra tiempo
   externo; después IRQ por separado con PPI/grupo/GIC identificados. Un delta
   positivo por polling no acredita una interrupción ni valida la frecuencia.
4. Excepción síncrona deliberada en una imagen de ensayo revisada: BRK con
   inmediato conocido, ESR/ELR y PC simbolizado coincidentes, captura física y
   retorno Android por la ruta independiente. No reutilizar la imagen QEMU ni
   asumir que su semihosting existe en el teléfono. Si no hay recuperación
   independiente probada, esta subprueba sigue pendiente.

Ninguna de estas subpruebas, aun pasando, satisface T08: todavía haría falta
ejecutar Mach/XNU real, ligado al upstream, patchset y binario exactos.
