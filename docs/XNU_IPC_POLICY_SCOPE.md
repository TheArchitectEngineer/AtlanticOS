# Política IPC nativa y límites de componentes — 2026-10-24

La serie 0027 permite compilar ipc_policy.c y mach_debug.c del XNU fijado con
el perfil de firmware. Conserva la política de puertos, validación de mensajes,
inmovilidad, excepciones y registro de kobjects genuinos. No incorpora un SDK,
identidad BSD, proveedor de CoreAnalytics o implementación IOKit ficticios.

## Selección de componentes

La cola de eventos CoreAnalytics de ipc_policy.c requiere proc_ro, plataforma,
SDK e identidad de firma de procesos BSD. En firmware sin MACH_BSD no se
seleccionan esa cola, su declaración pública ni sus cuatro sitios de llamada.
Las rutas de copia de derechos de ipc_object.c e ipc_kmsg.c mantienen su lógica
y limpieza nativas; solo se acota el envío opcional de eventos. Fuera del modo
firmware se conserva la selección upstream. El contador diagnóstico atómico,
los guards y la comprobación de reply ports siguen presentes.

La excepción de compatibilidad que permite llamadas de kobject sin recepción
depende del SDK de un proceso. Firmware sin BSD rechaza esa forma de llamada
con MACH_SEND_INVALID_OPTIONS. Mantiene la validación real de tipo de puerto,
flags y llamadas combinadas de envío/recepción. No concede una identidad de
plataforma ni un SDK antiguo para permitir un mensaje.

mach_debug.c solo excluye los casos que describen objetos IOKit y la etiqueta
de salida usada por esos casos cuando firmware no selecciona IOKIT. Conserva
lookup, locks, validación de derechos, tipo de objeto y descripción de entradas
de memoria Mach. Compilar estas funciones no acredita un servicio de debug
operativo ni creación de puertos en ejecución.

## Límite de EXC_GUARD

El cuerpo nativo de mach_port_guard_ast permanece intacto. Todavía referencia
exit_with_mach_exception, sin proveedor seleccionado, y task_violated_guard,
que ya tiene su cuerpo nativo en task.c. El camino completo de terminación y
diagnóstico sin BSD sigue pendiente antes de considerar operativo ese servicio.
Esas referencias permanecen fuertes. No hay función vacía, retorno de éxito
ni descarte de errores para eliminarlas del enlace. Esta entrega no prueba
que una tarea infractora termine correctamente en un firmware Mach.

## Verificación

tools/test_xnu_ipc_policy_scope.py compara seis contextos de preprocesado de
los fragmentos reales modificados. Los contextos BSD/IOKit habilitados son
comprobaciones de selección; el perfil completo todavía los rechaza.
Comprueba las ramas conservadas fuera de firmware, 17 cuerpos core y la tabla
de políticas intactos, el ABI de los headers reales y rechazos de opciones
truncadas o acceso a la API CoreAnalytics no seleccionada. Inspecciona los
objetos ARM64, sus imports fuertes y registros nativos de startup.

El estándar conserva su selección base y compila un probe aislado de política.
El probe de mach_debug debe fallar por __builtin_xnu_type_summary ausente; no
se sustituye la metadata del allocator. Los probes no se incluyen en su enlace.
Ninguna prueba de este
documento ejecuta Mach IPC, un kobject, EXC_GUARD o XNU en el teléfono.

```sh
python3 tools/build_xnu_lab.py --layout-compiler <clang-v2> --layout-proof <prueba-api-v2>
python3 tools/test_xnu_ipc_policy_scope.py --build <reporte-base> --output work/ipc-policy-audit-nuevo
python3 tools/build_xnu_rpc.py --build <reporte-base>
python3 tools/diagnose_xnu_link.py --build <reporte-base> --rpc <reporte-rpc> --linker <lld-v2> --atlantic-static-proof <prueba-lld-v2> --output work/ipc-policy-link-nuevo
```

En WSL/NTFS añadir --windows-git a ambos builders. Usar outputs nuevos.

## Estado de esta revisión

Compilan 138 unidades experimentales y 13 estándar, con cero fallos. Frente
a la revisión de cadenas se añaden dos unidades nativas y cambian solo dos
unidades anteriores: los sitios opcionales de eventos en ipc_object/ipc_kmsg.
Las 137 constantes genassym y los defines seleccionados se conservan.
Pasan 117/88 comprobaciones de alcance, ABI y objetos, 78 tests Python, los
79 344 contratos originales de cadenas y el puente de datos con ASan/UBSan.
Compilan 42 probes RPC por carril y CFILES conserva 26 seleccionados.

El enlace estricto de **164 objetos** con LLD v2 falla con **561 diagnósticos
indefinidos, cero duplicados y ninguna imagen**. Frente a 594, 33 nombres
tienen proveedor real y uno deja de referenciarse por selección: el envío de
eventos CoreAnalytics. Aparece una dependencia nueva, mk_timer_port_label_dealloc,
cuyo proveedor genuino está en osfmk/kern/mk_timer.c, no seleccionado en esa revisión.
La comparación separa esos efectos; excluir un evento no implementa su servicio.
El estándar conserva 39 objetos, 825
diagnósticos y el rechazo upstream de las opciones estáticas, sin imagen.

La [evidencia](../evidence/xnu-ipc-policy-scope-20261024/manifest.json) registra
194 artefactos con hashes, incluidos errores esperados, imports y comparación
de dependencias. Las pruebas vigentes de Clang API v2 y LLD v2 se reutilizan por
hashes comprobados. No hay kernel enlazado, IPC o XNU ejecutados ni acceso al
teléfono. La recuperación independiente, RAM firmware y handoff EDK2 siguen
sin prueba física.

La ampliación posterior de [timers y políticas](XNU_SCHEDULER_TIMER_PROVIDERS.md)
selecciona el proveedor mk_timer genuino. El manifiesto IPC permanece como
registro de sus 138 unidades y 561 diagnósticos. La terminación de guards sin
BSD y su prueba física siguen pendientes.
