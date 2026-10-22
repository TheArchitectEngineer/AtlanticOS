# Código RPC nativo generado por MIG — 2026-10-22

BUILT_ARM64: el carril experimental conserva 47 objetos base y el estándar 13.
Cada uno compila además los 42 C RPC de las recetas nativas. Los headers pasan
a 57 por los efectos de MIG_KUSRC. No se crea un servidor host_security C que
no está en su lista upstream.

Tres interfaces no tienen métodos: device y las dos Arcade desactivadas. Sus
salidas reales no acreditan servicios. Se comprueban símbolos de código, datos,
hashes y transporte kernel de emisores no vacíos. No se declara mach_msg ni
un conversor ficticio para ocultar errores de generación.

Dos casos de configuración exigen las comprobaciones nativas de tipos MIG;
cinco comparaciones conservan headers/C byte a byte fuera de firmware o con
Arcade activado. Dos casos target verifican el ABI de los 21 descriptores y
rechazan un prefijo alterado. Las 17 tablas requeridas por ipc_kobject tienen
proveedores generados en experimental; estándar declara que no comprueba ese
objeto. Los 14 checks base también aprueban por carril.

El enlace estricto de 89/55 objetos termina con 1 y no produce imagen. En
experimental informa 1245 símbolos indefinidos, sin errores de duplicados;
el inventario por nombres cuenta 2985 definiciones y 1259 sin proveedor.
Siguen pendientes handlers/dependencias nativos y un linker estático correcto.
Pageout no forma parte del conjunto aceptado y mantiene su bloqueo documentado.

Los reportes/logs preservan comandos y hashes. Solo se publican líneas de error
de los guards PMU/BSD/IOKit/API, con hash del log completo. CPP completo, fuentes
RPC generadas, headers completos y objetos quedan privados. La fixture de ABI
de descriptores es código de prueba original. No se publican imágenes OEM.

No se ejecutó un kernel, tabla MIG, handler o mensaje RPC. No hubo acceso al
teléfono, cambios Android o flash. RAM física, arranque G20 y handoff EDK2 no
están comprobados; estos artefactos no cumplen esa aceptación.
