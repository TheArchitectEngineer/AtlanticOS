# SLEH nativo, reloj y encodings ARM64

107 unidades base experimentales y 13 estándar; 42 probes RPC por carril, 26
seleccionados para enlace. Se agrega SLEH y seis unidades upstream sin modificar
de reloj, timer, contabilidad, datos ARM y commpage. 51 checks de alcance/ABI
experimentales, 45 estándar y 78 tests host aprobados. Ninguno ejecuta XNU.

Los 15 checks BRK por carril inspeccionan instrucciones reales, registros,
selección de features y rechazo de un ID incorrecto. El objeto SLEH tiene tres
descriptores fatales; una relocation UNSIGNED liga el callback hard al handler
local nativo. Sin proveedor de telemetría no se registra recuperación o su test.
El carril estándar no compila ese objeto, y lo registra explícitamente.

Enlace experimental de 133 objetos: exit 1, 765 diagnósticos indefinidos, cero
duplicados, sin imagen. Compilador v2 (26 checks) y linker v2 (54/15) se reutilizan
por hash, sin declarar nuevos builds de herramientas. Los probes de ipc_policy
y mach_debug siguen fallando; SLEH/pageout compilan y están seleccionados.

Reportes, Makefiles, IR y logs seleccionados; sin objetos o imágenes del teléfono.
La CI de 100 unidades del commit 49bbae4 se conserva en otro bundle: no prueba
la revisión de 107 unidades. Arranque físico G20, recuperación independiente,
RAM real y handoff EDK2 siguen pendientes. Véase docs/XNU_ARM64_EXCEPTIONS.md.
