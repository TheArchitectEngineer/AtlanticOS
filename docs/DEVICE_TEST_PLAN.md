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
| T04 vía temporal | Investigar documentación/código bootloader y consulta OEM para determinar si acepta payload temporal en RAM con bloqueo actual. La meta activa autoriza avanzar hacia ese arranque temporal; un ensayo exige imagen/contrato auditable y recuperación T01 verificada. No se ha ejecutado. | Si no existe vía temporal documentada → BLOCKED; no proponer reemplazar slot para sortearlo. |
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

## Subpruebas pendientes de T08: SLEH y reloj XNU

Estado: PENDING_HARDWARE. Las pruebas de objetos de
[XNU_ARM64_EXCEPTIONS](XNU_ARM64_EXCEPTIONS.md) no cierran estas subpruebas.
Antes de ejecutarlas deben estar aprobadas T01/T04/T05, existir una imagen XNU
enlazada y auditada, un BSP G20 identificado y un canal de salida fiable. Todo
payload debe ser temporal; no modificar slots, particiones ni Android.

1. **Assertion fatal nativa.** Tras registrar entrada a kernel_bootstrap y un
   hilo Mach real con VM/stack válidos, una build de diagnóstico llama al macro
   nativo de assertion de tres operandos con dos valores centinela publicados.
   Guardar hash/mapa del binario y del descriptor, PC del call site, estado
   salvado por XNU y vídeo/log físico. Se espera ESR.EC=0x3C y comentario BRK
   0xBFFC, con ELR dentro del call site identificado. x8 debe señalar el
   descriptor dentro de la imagen y x16/x17 contener los centinelas; el handler
   nativo debe producir el diagnóstico y terminar por panic, sin reanudar el PC.
   El resultado solo pasa si se distinguen estas rutas XNU del preflight entry.
   Pantalla negra, reset sin registro o una cadena impresa no prueban la ruta.
   Después comprobar retorno stock por la recuperación independiente.
2. **Timer y contabilidad nativos.** Con PPI/grupo/GIC y fuente del contador
   ya verificados para este BSP, registrar CNTFRQ/contador y timebase entregada
   a XNU. Desde un hilo Mach real, programar al menos diez deadlines mediante
   las APIs timer_call de XNU; capturar IRQ físico y PCs simbolizados que pasen
   por sleh_irq o sleh_fiq, rtclock_intr y timer_intr hasta el callback. Registrar
   mach_absolute_time antes/después, deadlines, callbacks y cambios de contexto
   entre dos hilos reales. Los tiempos deben progresar y concordar con la
   frecuencia observada y una referencia externa, con tolerancia fijada antes
   del ensayo según el canal. El contador avanzando sin callbacks solo acredita
   polling; callbacks sin traza de la IRQ no prueban GIC/timer. El BSP no hereda
   un PPI o frecuencia de QEMU. La contabilidad de tiempo no acredita PMU.

Estas pruebas tampoco cierran por sí solas T09 o T12. No hay aún una imagen
XNU ejecutable para realizarlas y no se solicita provocar un fallo en el teléfono.

## Subprueba pendiente de T05/T08: datos de arranque

Estado: PENDING_HARDWARE. El puente de BOOT_DATA_BRIDGE.md se probó con el FDT
generado por QEMU y con un candidato stock offline, sin comprobar este G20.
Tras cerrar T01/T04 y disponer de canal de salida y payload temporal auditado:

1. Capturar x0/EL/MPIDR/CNTFRQ y acotar el DTB recibido con el mapa de RAM ya
   establecido para el BSP. Guardar copia privada/hash del árbol efectivo antes
   de liberar recursos del loader. Inventariar bancos y memreserve/reserved-memory;
   comparar con los overlays realmente aplicados y las reservas del payload,
   framebuffer, stack y DMA. El mapa base del PAC no reemplaza esta observación.
2. Verificar que la afinidad primaria observada aparece una vez y que la
   frecuencia usada procede del contador medido. Si faltan celdas, hay overflow,
   ambigüedad, reserva dinámica o huecos no representables, registrar rechazo
   y usar únicamente la ruta de retorno OEM ya validada. No inventar un mapa.
3. Cuando exista XNU enlazado con Platform Expert propio, inicializar SecureDT
   real sobre memoria propia y conservada. Capturar PCs/símbolos de sus llamadas
   para consultar /chosen/DRAM y /cpus/CPU primaria, junto con los bytes/valores
   devueltos y sus hashes. Deben coincidir exactamente con el inventario y los
   registros físicos; comprobar que el árbol y FDT no se alteran inesperadamente.
   Lectura propia, cadenas impresas o un fixture ABI no sustituyen al consumidor.

La asignación y la apertura física deben excluir los carveouts no-map y respetar
la propiedad de cada rango; añadir una exclusión no demuestra que sea seguro
cargar una imagen allí. Esta subprueba tampoco acredita el bootstrap Mach de T08,
handoff EDK2 ni RAM firmware. No hay imagen XNU disponible para ejecutarla ahora.

## Subprueba pendiente de T08: Platform Expert original

Estado: PENDING_HARDWARE. Las comprobaciones de ABI y objetos de
[XNU_PLATFORM_EXPERT](XNU_PLATFORM_EXPERT.md) no ejecutaron este código. Antes
del ensayo hacen falta T01/T04/T05, una imagen XNU enlazada y auditada, el
productor boot_args y un BSP original con validaciones e IRQ reales.

1. Registrar hash de imagen, mapa de símbolos, boot_args nativo de versión y
   revisión 2 y contexto retenido del BSP. Capturar los PCs de la copia nativa
   a const_boot_args y de PE_init_platform(FALSE, args). Comparar los 1152 bytes
   copiados con el productor; ninguna cola informal puede aportar el contexto.
   No publicar datos personales de la línea de arranque.
2. Registrar los rangos mapeados y su propiedad antes de consultar el árbol.
   Las validaciones BSP deben cerrar todos sus rangos, exclusiones y permisos
   con PE_state todavía sin publicar. Capturar PCs de SecureDT real y los
   valores devueltos para DRAM, afinidad primaria, estado y frecuencia. Comparar
   con el mapa efectivo y MPIDR_EL1/CNTFRQ_EL0 observados en este teléfono.
   Solo entonces debe cambiar PE_state.initialized a TRUE.
3. Registrar PE_init_platform(TRUE, &BootCpuData) y el backend de IRQ del BSP;
   ese puntero es contexto de CPU, nunca boot_args. El backend debe demostrar
   configuración real por CPU y permitir la prueba de IRQ/timer de T06/T08.
   Si se habilitan CPUs secundarias, capturar también su llamada con NULL y el
   contexto real que obtiene el BSP. Un retorno de éxito sin IRQ no pasa.
4. Capturar el delta modular usado por arm_vm_init y los rangos antes/después
   de PE_slide_devicetree. Demostrar que el destino completo sigue siendo
   memoria propia, normal y legible, que SecureDT usa la nueva dirección y que
   el boot_args copiado conserva el comportamiento nativo. Verificar después
   la razón Hz/1 entregada al callback nativo del reloj contra CNTFRQ observado.

Una build temporal separada puede inyectar un registro inválido para confirmar
el rechazo, solo con recuperación independiente y canal panic ya probados.
Un BSP ausente debe fallar en el enlace y nunca reemplazarse con callbacks que
devuelvan éxito. Una parada sin PC/log fiable es INDETERMINATE. Guardar evidencia
física y verificar retorno a Android con T01 al terminar; estas subpruebas no
acreditan por sí solas un hilo Mach operativo, RAM firmware ni handoff EDK2.

## Subpruebas pendientes de T08: memoria física, caché y atómicos

Estado: PENDING_HARDWARE. Los checks de [XNU_MEMORY_PROVIDERS](XNU_MEMORY_PROVIDERS.md)
solo inspeccionan fuentes, ABI y objetos. Exigen primero T01/T04/T05, una imagen
XNU auditada, BSP/MMU reales, canal de salida y dos hilos Mach funcionales.

1. Reservar mediante el allocator real páginas scratch propias, mapeadas y
   fuera de toda exclusión. Registrar VA/PA, permisos, traducción, tamaños,
   canarios y hashes iniciales. Invocar bcopy_phys y bzero_phys nativos sobre
   rangos no solapados, incluidos fragmentos que crucen un límite de página.
   Comprobar bytes esperados y canarios antes/después, con PCs simbolizados de
   la ruta directa o de ventanas pmap realmente tomada. No ensayar direcciones
   arbitrarias, carveouts, MMIO o memoria del loader como si fueran scratch.
2. Registrar CTR/CLIDR/CCSIDR y validar granulación/líneas del perfil del G20.
   Para un rango scratch de longitud no nula, registrar la ruta desde
   CleanPoC_DcacheRegion_Force_nopreempt_nohid hasta el bucle DC CVAC y ambos DSB.
   Confirmar que preemption no cambia y que no se accede a HID Apple. Después,
   con una página de código scratch y transiciones RW/RX hechas por pmap,
   ejecutar un fragmento auditado con resultado conocido, cambiarlo y comprobar
   el resultado nuevo mediante la ruta nativa de sincronización D/I-cache.
   PCs o contadores solos no demuestran coherencia DMA; esta exige un dispositivo
   y buffer propios verificados por separado. QEMU tampoco mide la caché física.
3. Desde dos hilos Mach reales, comprobar CAS exitoso/fallido y los valores
   anteriores devueltos por OSAddAtomic64. Ejecutar incrementos concurrentes con
   un total conocido y verificar el resultado final, capturando PCs del bucle
   exclusivo, IDs de CPU e intercalados. Con una sola CPU solo se acredita esa
   configuración; SMP exige CPUs secundarias y BSP ya verificados.

Conservar capturas físicas, mapa y hashes exactos, resultados y fallos, liberar
solo las páginas propias y comprobar el retorno stock con T01. Estas pruebas no
acreditan un pager backend, acceso a almacenamiento, RAM firmware ni handoff EDK2.

## Subprueba pendiente de T08: bootstrap Mach sin BSD/IOKit

Estado: PENDING_HARDWARE. Los checks de [XNU_BOOTSTRAP_SCOPE](XNU_BOOTSTRAP_SCOPE.md)
son de fuentes y objetos. Requieren primero T01/T04/T05, una imagen XNU enlazada
y auditada, boot_args/contexto BSP válidos y un canal de salida propio fiable.
Usar únicamente la vía temporal acordada, sin slots ni escrituras de particiones.

1. Vincular binario, mapa y configuración exactos a la captura física. Auditar
   la ausencia de imports a workq_init, bsd_scale_setup, device_service_create y
   OSKextRemoveKextBootstrap; no deducir esa ausencia de un log silencioso.
2. Capturar PCs simbolizados de vm_mem_bootstrap, sched_init, task_init,
   thread_init y kernel_thread_create. Registrar la identidad del hilo Mach,
   su stack propio, traducción/permisos y estado runnable. Un retorno KERN_SUCCESS
   o una cadena impresa sin estado nativo válido no pasa la prueba.
3. Capturar la transición load_context → machine_load_context y la llegada real
   a kernel_bootstrap_thread mediante el contexto/continuación de XNU. Registrar
   SP, PC y puntero del hilo/CPU, todos dentro de rangos auditados. Seguir idle,
   scheduler, thread_daemon_init y el reloj nativos; completar después la prueba
   separada de timer/IRQ y servicio Mach de T08.
4. Comprobar que el bootstrap alcanza lockdown y pageout sin intentar crear
   servicios de componentes excluidos. No añadir funciones vacías para conseguir
   ese recorrido. Inventariar stacks, daemons y segmentos retenidos para T09:
   excluir el gestor kext no demuestra liberar memoria o cumplir el límite RAM.

El resultado solo pasa con evidencia física del camino Mach y retorno Android
por T01. Una parada sin registro fiable es INDETERMINATE. Los contextos BSD/IOKit
del test de preprocesado no son configuraciones hardware habilitadas, y este
ensayo tampoco acredita drivers, framebuffer, VNC o transferencia EDK2.

## Subprueba pendiente de T08: soporte de cadenas e imagen

Estado: PENDING_HARDWARE. Los contratos host de
[XNU_STRING_IMAGE_SUPPORT](XNU_STRING_IMAGE_SUPPORT.md) no ejecutan XNU ni su
lector Mach-O. Antes se exigen T01/T04/T05, imagen XNU auditada, contexto BSP,
traducción/ownership y canal de salida fiables; carga únicamente temporal.

1. Capturar el header realmente mapeado y su vínculo con binario/mapa/commit.
   Validar fuera del lector nativo todos los load commands, tamaños, overflow,
   segmentos/secciones, VM y permisos. Registrar la dirección real que resuelve
   _mh_execute_header; un símbolo definido o un struct del mismo tamaño no basta.
   El [plan de imagen original](STATIC_IMAGE_PLAN.md), probado solo en host,
   deberá integrarse antes de esta prueba: conservar bytes autenticados, registrar
   plan y asignaciones físicas excluyendo carveouts, verificar copy/zero-fill por
   readback y capturar traducciones/permisos activos por segmento. PC fuera de
   instrucciones, BSS/padding no cero, páginas W+X o cualquier alias con una
   reserva hacen fallar la prueba antes de entrar a XNU. Un plan aceptado sin
   esos registros no prueba que la imagen haya sido cargada correctamente.
2. Durante arm_vm_init, capturar PCs simbolizados de los lectores genuinos y sus
   resultados para segmentos/secciones/UUID/final de imagen. Comparar con el
   manifiesto auditado y con traducciones activas. Direcciones de cabecera OEM
   o de una imagen diferente no son referencias válidas. No pasar headers
   malformados al parser nativo suponiendo que los rechazará de forma segura.
3. Desde un hilo Mach real y sobre buffers scratch propios, capturar la entrada
   strcmp/memcmp/strlcpy/strlcat, transferencia al helper original y resultados.
   Repetir igualdad/desigualdad, byte alto, capacidad 0/1, truncamiento y append
   sin NUL dentro de su límite, con canarios y tamaños previamente auditados.
   Los 79 344 casos host no prueban por sí solos este ABI/contexto en hardware.

Guardar evidencia física y comprobar retorno stock por T01. La prueba no
acredita lectura de almacenamiento, servicios IPC, EDK2 o RAM firmware completa.

## Subprueba pendiente de T08: política y registro IPC nativos

Estado: PENDING_HARDWARE. [XNU_IPC_POLICY_SCOPE](XNU_IPC_POLICY_SCOPE.md) comprueba
fuentes, ABI y objetos. Antes de la prueba física se requieren T01/T04/T05,
imagen kernel auditada, contexto BSP/MMU y salida fiables; carga solo temporal.

1. Capturar PCs simbolizados de ipc_kobject_register_startup y de los tres
   inicializadores de políticas seleccionados por STARTUP. Inspeccionar la tabla
   real después del registro: tipo, nombre, inmovilidad y callbacks deben
   corresponder a los ops nativos del binario. Un símbolo definido o un listado
   del objeto no prueba que el inicializador se haya ejecutado.
2. Desde contexto Mach propio, verificar creación y copia de derechos sobre
   puertos scratch, con cuentas antes/después y cleanup real. Confirmar que las
   llamadas combinadas válidas mantienen su comportamiento y que la excepción
   de SDK para llamadas de kobject sin recepción no está habilitada.
3. Antes de habilitar mensajes de emisores no confiables, resolver el camino
   Mach de terminación de guards que aún depende de BSD. Después, provocar una
   infracción controlada en una tarea descartable y capturar validación,
   EXC_GUARD, resultado y terminación cuando corresponda. Debe comprobarse que
   la tarea no sigue ejecutando tras una violación fatal. Una excepción sin
   terminación demostrada no satisface esa propiedad.

Registrar los códigos y PCs esperados según el caso exacto de XNU, el hash de
imagen y la captura física. La exclusión de eventos CoreAnalytics no acredita
un servicio de telemetría. Conservar prueba de retorno Android por T01; no hay
resultado aceptado para estos pasos todavía.

## Subprueba pendiente de T08: timers y políticas nativas

Estado: PENDING_HARDWARE. [XNU_SCHEDULER_TIMER_PROVIDERS](XNU_SCHEDULER_TIMER_PROVIDERS.md)
solo comprueba compilación, ABI, selección y objetos. Requiere T01/T04/T05/T06,
kernel auditado, BSP/MMU/IRQ y un canal de captura fiable; carga temporal.

1. Registrar la ejecución de los inicializadores nativos de políticas y
   contadores per-CPU, con PCs, CPU/MPIDR y rangos de allocations. Comprobar que
   las referencias iniciales se conservan al pasar del almacenamiento temprano
   a las zonas per-CPU y que esas páginas pertenecen al mapa validado. Tamaño de
   objetos o contadores no sustituye una medición de RAM residente.
2. Crear un timer Mach scratch en un contexto admitido por su API. Capturar
   port/label, deadline de 64 bits, entrada thread_call, IRQ real, ejecución de
   mk_timer_expire y recepción de su mensaje. Comparar mach_absolute_time con
   el contador/frecuencia capturados por T06. Repetir con leeway, deadline ya
   vencido y cancelación antes de expirar. No inferir entrega por un callback
   programado ni por un retorno KERN_SUCCESS.
3. Destruir el puerto con el callback pendiente y verificar cancelación,
   referencias, keep-alive y liberación de zona cuando active llega a cero.
   Repetir bajo concurrencia controlada para detectar doble liberación, uso
   posterior a free o notificaciones después del punto de cancelación definido
   por XNU. Conservar el caso exacto y el orden de eventos; una traza parcial
   no demuestra ausencia de carreras.
4. Capturar cambios reales de prioridad/QoS y propagación por turnstiles en
   hilos Mach descartables. Comprobar que los callbacks de I/O BSD no se invocan
   sin ese componente. Los controles SFI y notificaciones de recursos no
   soportados deben devolver su error nativo; no interpretar ese resultado como
   servicio activo. No atribuir identidad de proceso a un token sin sus
   proveedores y contexto reales.

El resultado exige PCs, retornos, contabilidad de referencias y evidencia física
vinculados al hash de imagen. Un callback sin IRQ/cancelación/cleanup verificables
es PARTIAL; un bloqueo sin captura fiable es INDETERMINATE. Registrar retorno
Android por T01. No hay aceptación física de esta subprueba todavía.

## Subprueba pendiente de T08: coaliciones, bank y notificación MIG

Estado: PENDING_HARDWARE. [XNU_COALITION_BANK_PROVIDERS](XNU_COALITION_BANK_PROVIDERS.md)
solo comprueba fuentes, headers, ABI y objetos. Requiere T01/T04/T05/T06, imagen
kernel auditada, BSP/MMU/IRQ/IPC y captura fiables; usar carga temporal.

1. Registrar la ejecución real de coalitions_init y bank_init, creación de
   ledgers, referencias y registro del gestor de vouchers. Comprobar que cada
   tarea queda asociada a las coaliciones correctas y que adoption/remove/release
   mantienen los balances y referencias; comparar contra el caso exacto nativo.
2. Antes de crear un contexto bank, demostrar un proveedor y contexto reales de
   proceso/persona o la política explícita que haga esa operación no disponible
   en firmware sin BSD. No usar PID, UID, persona, entitlement o UUID ficticios.
   Un registro de startup sin ese contexto no acredita bank operativo.
3. En un ensayo aislado con un puerto destinatario propio, capturar los PCs de
   coalition_notification y mach_msg_send_from_kernel, ID de mensaje, ID de
   coalición de 64 bits, flags de 32 bits y recepción del mensaje. Verificar la
   liberación del send right y el camino nativo cuando no hay destinatario.
   Generar dos headers o compilar el emisor no demuestra entrega.
4. Con telemetría desactivada, comprobar que el campo bank ausente no se accede
   y que su getter conserva el cero de dato no disponible. No interpretar ese
   cero como la identidad real de una coalición. Verificar iteración UPL solo
   sobre páginas propias, con referencias y cleanup trazados. Los endpoints VM
   debug desactivados deben conservar KERN_FAILURE, sin anunciar inspección VM.

Guardar binario, mapa, PCs, payloads, errores y balances antes/después con sus
hashes y captura física. Falta de contexto de identidad o referencias sin
trazar deja el componente como UNVERIFIED. Un cuelgue sin registro fiable es
INDETERMINATE. Comprobar el retorno Android por T01; no hay resultado físico
aceptado de esta subprueba todavía.
