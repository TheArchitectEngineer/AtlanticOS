# Semántica nativa de tipos y allocator — 2026-10-22

El proveedor de layout v1 conservaba la representación C de punteros, escalares,
records y arrays, pero perdía las anotaciones de uso de XNU. Es una limitación
de aquella implementación experimental: ppnum_t es uint32_t en C y lleva
__kernel_ptr_semantics. Al omitir esa declaración, upl_page_info se clasificaba
como datos puros y el allocator rechazaba su cola junto al header upl.
Los objetos históricos compilados con v1 no acreditan una segregación correcta
de todos los tipos nativos ni un allocator en ejecución.

La fuente oficial explica por qué una dirección almacenada en un entero debe
mantener semántica de puntero, y por qué un campo puede anularla cuando contiene
una dirección de usuario considerada datos por el kernel:
[Apple Security Research](https://security.apple.com/blog/towards-the-next-generation-of-xnu-memory-safety/).
El snapshot fijado define los tres macros en
[bsd/sys/cdefs.h](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/bsd/sys/cdefs.h)
y anota ppnum_t en
[mach/vm_types.h](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/osfmk/mach/vm_types.h).

## Puente original y contrato v2

Patch 0019 conserva las declaraciones nativas mediante el atributo estándar
Clang annotate, solo cuando KERNEL y CONFIG_ATLANTIC_C_LAYOUT seleccionan
explícitamente el proveedor AtlanticOS:

| Declaración nativa | Anotación consumida por la API original | Encoding |
|---|---|---|
| __kernel_ptr_semantics | atlantic.layout.pointer | 1 |
| __kernel_data_semantics | atlantic.layout.data | 2 |
| __kernel_dual_semantics | atlantic.layout.dual | 3, OR de puntero y datos |

No se anuncia soporte de xnu_usage_semantics ni de los builtins privados Apple.
El atributo annotate existe en el Clang upstream fijado; la interpretación de
estos tres nombres dentro de la API de layout es código original AtlanticOS.
Véase [Attr.td de LLVM 19.1.7](https://github.com/llvm/llvm-project/blob/cd708029e0b2869e80abe31ddb175f7c35361f90/clang/include/clang/Basic/Attr.td).
Fuera de la selección explícita, cdefs conserva la rama Apple y el fallback
originales. Un compilador sin API v2 debe ser rechazado.

El walker inspecciona las declaraciones typedef antes de canonicalizar el tipo
para que los aliases conserven su uso. Una anotación de campo prevalece sobre
la de su typedef; un typedef exterior puede anular la de su alias subyacente.
Se validan también las anotaciones interiores. Arrays de escalares conservan
su stride, atomic conserva el tipo de valor y los bitfields su rango real.
La anotación no cambia tamaño, alineación ni offsets.

Las anotaciones reconocidas solo se admiten sobre escalares o arrays de
escalares de tamaño fijo. Etiquetas desconocidas, argumentos adicionales,
anotaciones contradictorias y anotaciones de aggregates producen error al
consultar el layout. Las anotaciones ajenas a este namespace no participan.
Siguen vigentes los límites C/AArch64 LP64 little endian, tamaño y profundidad;
PAC/arm64e y las representaciones no soportadas se rechazan.

La identidad C de dos aliases puede ser la misma aunque sus layouts de uso
sean distintos. __atlantic_layout_compatible compara sus layouts calculados y
no acepta identidad C como atajo. Conserva el caso especial de identidad void
que usa el macro nativo de punteros; void no es un wildcard de layout por sí solo.

La primera reconstrucción con v2 detectó una discrepancia en zone_leaks:
allocation y free usan vm_offset_t, pero array/next estaban declarados como
uintptr_t *. Conservar el uso permite detectar esta diferencia que la identidad
C sola ocultaba. Patch 0020 declara esos dos punteros como vm_offset_t *;
mantiene las llamadas nativas, helper, algoritmo de diagnóstico y tipo de los
elementos temporales. El fixture exige la identidad C de los aliases y rechaza
que su metadata de uso se trate como intercambiable. La comprobación del
allocator sigue activa; el intento fallido original se conserva.

## Verificación exigida

El contrato del compilador incorpora ocho rechazos nuevos y aserciones positivas
de typedefs, overrides de campos, arrays, atomic, bitfields y compatibilidad.
Son 26 comandos: fixture ARM64, IR plegado y 24 rechazos por diagnóstico previsto.
La prueba incremental aprobó esos 26 y compiló vm_pageout.c nativo completo.
Después se reconstruyó el compilador desde cero: 11.996 archivos fuente
verificados, los 26 casos aprobados y hash de binario registrado. La integración
completa con ese binario compila 100 unidades reales; el resultado incremental
permanece separado. El estándar conserva 13 unidades con Clang estándar.

El fixture kalloc_layout.c usa los tipos reales y exige que ppnum_t tenga
summary 2 y upl_page_info summary 8: su granulo combina número de página con
semántica de puntero y flags de datos. Se emite el view variable nativo de
struct upl con struct upl_page_info. El negativo exige que un header de punteros
seguido por una cola verdaderamente data-only siga siendo rechazado.

tools/test_xnu_usage_semantics.py compara los mismos tipos con el puente activo
y con la selección desactivada. Deben cambiar los summaries de ppnum_t,
vm_offset_t, upl_page_info y hw_lck_ptr_t; los campos explícitos de datos de
shared_file_mapping_slide_np deben seguir siendo datos. Trece constantes del
ABI target deben coincidir entre ambos contextos. Otros tres casos comparan
los macros con upstream fuera del proveedor. Todo se obtiene mediante IR o
preprocesamiento, sin ejecutar allocator o kernel.

vm_pageout.c, vm_pageout_xnu.h y memory_object_types.h conservan sus bytes
upstream. No se cambia la representación UPL, no se divide su allocation, no
se rebaja KALLOC_TYPE_TRAILING_DATA_CHECK y no se altera su llamada a
kalloc_type/kfree_type. Compilar pageout tampoco demuestra presión de memoria,
reclaim o I/O funcionando en el teléfono.

## Resultado y siguiente puerta

Con el compilador limpio pasan 36 checks de alcance/ABI experimentales y 30
estándar, además de las 78 pruebas host. Se generan 57 headers MIG y compilan
42 probes RPC por carril; CFILES mantiene 26 para el enlace y 14 subsistemas
requeridos por kobject experimental. Las 137 constantes genassym coinciden.
Las nuevas pruebas del allocator incluyen el positivo nativo y tres rechazos:
puntero incompatible, cola data-only y alias de dirección con uso incorrecto.

El intento estricto con el mismo LLD v2 probado y 126 objetos termina en exit 1:
778 diagnósticos de símbolos indefinidos, cero duplicados y ninguna imagen.
Los fixtures 54/15 del linker se reutilizan por hash del binario e inputs.
El estándar conserva sus opciones estáticas rechazadas y 829 diagnósticos.

La [evidencia de esta revisión](../evidence/xnu-usage-semantics-20261022/manifest.json)
contiene 192 artefactos, incluidos el build limpio, contrato, IR, enlace y el
intento anterior que detectó el tipo de zone_leaks. Los hashes de aquel intento
intermedio pertenecen a su revisión previa al fix. No se presenta como build
actual aprobado.

Los probes de ipc_policy, mach_debug y sleh sin modificar siguen fallando;
vm_pageout ya compila. En sleh, las constantes y descriptores BRK sí están en
la fuente pública kern/trap_telemetry.h: el include depende de CONFIG_TELEMETRY,
aunque se usa también para rutas fatales. DEVELOPMENT activa además recuperación
de traps sin exigir ese proveedor. Una copia con tres guards corregidos compila
con el binario limpio; se publica su diff y reporte como preview no integrado.
El enlace actual no contiene ese objeto. Faltan su integración, checks del
alcance fatal/recuperable, codificación BRK y pruebas de excepciones reales.

Todavía faltan muchos proveedores, Platform Expert, BSP físico y arranque.
Estos resultados no ejecutan pageout, excepciones, un allocator o XNU.

## Reproducir

```sh
python3 tools/build_atlantic_clang.py --cache work/clang-layout-usage-v2 --jobs 4
python3 tools/build_xnu_lab.py --layout-compiler work/clang-layout-usage-v2/build/bin/clang --layout-proof work/clang-layout-usage-v2/tests/report.json
python3 tools/test_xnu_usage_semantics.py --build <reporte-base-experimental> --output work/usage-semantics-tests
python3 tools/probe_xnu_core.py --build <reporte-base-experimental> --output work/core-probes
```

El build registra el hash del compilador y del contrato probado. Los objetos,
el enlace estricto y sus dependencias se vuelven a comprobar con ese proveedor;
las pruebas históricas de v1 permanecen identificadas por su revisión.
Arranque físico G20, recuperación independiente, RAM real y handoff EDK2
continúan pendientes.
