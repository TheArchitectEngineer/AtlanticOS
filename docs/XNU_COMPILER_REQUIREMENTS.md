# Requisitos abiertos del compilador XNU — 2026-10-21

La compilación incremental aprobada no acredita que Clang genérico pueda
construir todas las unidades. El probe real de thread.c llega a tres builtins
Apple que no están disponibles en los dos toolchains examinados. Sus usos están
en osfmk/kern/kalloc.h del commit f6217f891ac0bb64f3d375211650a4c1ff8ca1ea.

| Operación | Semántica observada en la fuente primaria | Estado |
|---|---|---|
| __builtin_clzg / __builtin_ctzg | Operaciones genéricas de bits usadas en kern/bits.h | Clang 19 compila trece unidades estándar; Clang 18.1.3 falla. El driver exige capacidades del target, sin fallback |
| __builtin_xnu_types_compatible | Tipos iguales o compatibles por firma XNU; kalloc trata void como wildcard | API Apple sin proveedor probado; alternativa explícita C experimental |
| __builtin_xnu_type_summary | Resumen del layout: presencia de encodings de granulos, incluidos solapamientos | API Apple sin proveedor probado; alternativa explícita C experimental |
| __builtin_xnu_type_signature | Firma por granulos de ocho bytes; distingue padding, punteros, datos y PAC | API Apple sin proveedor probado; alternativa explícita C sin PAC |

Los comentarios upstream describen los bits bajos del resumen y reservan el
resto para otras semánticas. KALLOC_TYPE_ADJUST_FLAGS y KALLOC_TYPE_EMIT_SIG
consumen esos datos para clasificar allocations y producir descriptores de
tipos. No son metadata decorativa que pueda sustituirse por cero o cadena vacía.
Definir todos los tipos como compatibles eliminaría una comprobación real.

Clang documenta [__builtin_types_compatible_p y __has_builtin](https://clang.llvm.org/docs/LanguageExtensions.html).
La compatibilidad de tipos C no demuestra igualdad con la firma de layout XNU:
dos records distintos pueden compartir firma. Un reemplazo directo no está
justificado. Una política más estricta basada en identidad sería un cambio
explícito de API con sus propios límites, nunca una emulación silenciosa del
builtin Apple.

No se ha identificado todavía un proveedor abierto y probado para estas tres
operaciones. Los resultados de búsqueda no demuestran que no exista. Los
siguientes pasos son inspeccionar un toolchain/fuente primario concreto, fijar
su versión/licencia y probar la semántica para el target antes de integrarlo;
o desarrollar generación original de metadata fiel al layout del compilador,
rechazando casos que todavía no pueda representar. No importar un port ajeno.

Se inspeccionaron seis archivos concretos del fork público swiftlang/llvm-project,
commit 725c8c73c8413d3075a6a100676e8d4b80036947: Builtins.def/td, TokenKinds.def,
AST/Type.h, ParseExpr.cpp y SemaExpr.cpp. No contienen los tres nombres literales.
Las URLs y hashes de esos archivos están en el [registro de inspección](research/swift-clang-source-audit-20261021.json).
Esto es una búsqueda textual limitada, no una compilación de ese fork ni prueba
de ausencia en todo el repositorio, otras ramas o compiladores. No se integró
ese fork como dependencia ni se importó código de su implementación al port.

La batería de aceptación debe cubrir aliases y calificadores, records de igual
firma pero distinta identidad, datos y punteros mezclados, arrays, padding,
unions/bitfields y tipos incompletos/no soportados. Debe comprobar tamaños y
offsets reales del target, firmas/resúmenes exactos y rechazo de usos inválidos.
No bastaría compilar thread.c con errores silenciados o chequear solo sizeof.

Actualización experimental: [compiler-port](../compiler-port/README.md) contiene
una API original de layouts C sobre LLVM 19.1.7, con source/patch fijados.
El compilador completo se construyó y pasó 18 comprobaciones preparadas. No
declara implementar los builtins privados Apple. El selector explícito de kalloc
y los guards BSD permiten compilar thread.c como duodécimo objeto real. Los
checks de macros kalloc y rechazo de punteros incompatibles pasaron. El build
normal no lo activa; el enlace y runtime siguen pendientes. La ampliación
posterior compila dieciocho objetos con VM/allocators/pmap. Véanse
[XNU_THREAD_BUILD](XNU_THREAD_BUILD.md) y [XNU_PMAP_BUILD](XNU_PMAP_BUILD.md).

El include de TrustCache se condicionó al monitor que utiliza sus tipos en el
perfil de firmware; los targets upstream conservan el include. Vm_map.c compila
sin modificar sus verificadores o protecciones, cuyas dependencias siguen sin
cerrar. Las pruebas de selección exigen la API real para PPL y ruta upstream.
Pmap compila tras separar los servicios Apple no seleccionados; sus APIs de
trust caches se diagnostican como unavailable, sin un proveedor alternativo.
Task.c requiere separar BSD/MAC y resolver la vida útil conjunta con proc/RO.
La carga dinámica/payloads sigue denegada mientras su verificación propia no esté
implementada. No añadir headers vacíos ni funciones de seguridad que retornen éxito.

Los diagnósticos conservados están en [XNU_LAB_BUILD](XNU_LAB_BUILD.md). El
próximo éxito requerido sigue siendo código genuino compilable y enlazable,
seguido de ejecución sustantiva instrumentada de Mach/VM/hilos/timer; este
inventario no reemplaza ninguna de esas pruebas.
