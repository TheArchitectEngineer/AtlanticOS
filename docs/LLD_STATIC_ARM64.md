# Enlace fijo ARM64 de laboratorio — 2026-10-22

El patch original de [linker-port](../linker-port/README.md) añade un modo
explícito a LLD oficial 19.1.7. Produce imágenes Mach-O MH_EXECUTE pequeñas con
reubicaciones estáticas comprobadas. **Todavía no enlaza XNU ni acredita una
imagen AtlanticOS arrancable.**

La opción upstream `-static` continúa sin implementarse. Este experimento usa
`--atlantic-static-arm64=<base hexadecimal>` y conserva ese rechazo upstream;
no elimina advertencias para hacer pasar el comando anterior.

## Contrato del modo v2

- Solo ARM64 sin PAC, objetos Mach-O nativos y archivos de objetos estáticos.
  Base virtual fija de 64 bits, distinta de cero y alineada a 16 KiB. Se aceptan
  las regiones de direcciones de 48 bits bajas y altas; el span virtual de la
  imagen queda acotado a 256 MiB. Ese límite no es una medición de RAM firmware.
- Reubicaciones aplicadas por el backend ARM64 real de LLD. No se modifican las
  cabeceras después del enlace. El símbolo __mh_execute_header pertenece al
  segmento que contiene la cabecera y referencia su dirección real.
- MH_NOUNDEFS, sin MH_DYLDLINK ni MH_PIE. Un LC_UNIXTHREAD ARM_THREAD_STATE64
  contiene el PC de entrada; SP y el resto del estado valen cero. El futuro
  bootstrap debe establecer stack, MMU, nivel de excepción y argumentos por su
  propio contrato. LC_UNIXTHREAD no establece EL1 ni ejecuta instrucciones.
- Sin LC_LOAD_DYLINKER, LC_MAIN, comandos de bibliotecas, información dyld,
  exports trie, imports, rebases o stubs dinámicos. Se conserva una tabla de
  símbolos para auditar el resultado.
- Entrada explícita en una sección de instrucciones, con alineación de cuatro
  bytes. No se admiten segmentos ilegibles ni escribibles y ejecutables a la vez;
  una sección de instrucciones debe tener permiso de ejecución.
- Allowlist positiva de opciones; undefined error y warnings fatales. Se rechazan
  dylibs, bitcode/LTO, TLS/TLV, imports weak sin proveedor, Objective-C/Swift y constructores o
  destructores automáticos. No hay KASLR, rebase en el cargador ni soporte general
  de todos los perfiles Mach-O/XNU.

Los metadatos platform_version macos 11 del laboratorio describen el target
Mach-O del compilador; no implican servicios Darwin o macOS presentes en firmware.

## Pruebas

tools/test_atlantic_lld.py ejecuta 54 comandos comprobados y audita 15 imágenes:
una a 0x40000000, otra a 0xfffffff007004000 y otra con un objeto extraído de un
archivo estático, más 12 variantes de selección de símbolos weak/strong.
Inspecciona directamente los bytes del Mach-O, sin depender
del texto de llvm-objdump para aceptar el resultado.

Las comprobaciones cubren PC, símbolo/puntero de cabecera, ausencia de dyld,
permisos RX/R/RW, BSS con más tamaño virtual que bytes de archivo, tabla sin
undefineds y ocho tipos de reubicación: BRANCH26, PAGE21, PAGEOFF12,
GOT_LOAD_PAGE21, GOT_LOAD_PAGEOFF12, POINTER_TO_GOT, UNSIGNED64 y SUBTRACTOR64.
El destino se calcula desde las instrucciones y los datos enlazados. Una carga
GOT resuelta puede ser relajada legalmente por LLD a ADRP + ADD; se verifica su
dirección efectiva y también una entrada GOT real mediante POINTER_TO_GOT.

Los casos negativos rechazan bases inválidas/overflow, arquitectura incorrecta,
PIE/opción static anterior, dynamic lookup, W+X, texto no ejecutable, entrada en
datos, undefined referenciado o sin referencias, import weak sin proveedor,
dos definiciones fuertes, TLS, constructor y LTO.
Ninguno debe producir archivo. Un enlace dinámico normal conserva LC_MAIN,
LC_LOAD_DYLINKER y MH_DYLDLINK; esa prueba limita el alcance del patch.

Un intento inicial detectó el símbolo de cabecera con valor cero bajo no-PIE.
El test de puntero fijado a la base comprueba la corrección. Otro rechazo detectó
que el helper getHex de LLD usa int64_t y no admite el valor alto completo de
XNU. El modo ahora parsea uint64_t y mantiene tests para overflow y valores altos.

## Selección estática weak/strong

La revisión v1 rechazó los helpers legítimos ___copy_helper_block_8_32r y
___destroy_helper_block_8_32r antes del recorrido completo de reubicaciones.
Se conserva esa evidencia en lld-static-arm64-20261022. La revisión v2 usa la
selección original de SymbolTable::addDefined, sin modificarla: la primera
definición débil prevalece entre débiles y una fuerte prevalece entre las
definiciones cargadas. No se extrae un miembro de archivo únicamente para
sustituir un símbolo débil que ya tiene proveedor; se conserva la extracción
lazy nativa de LLD.

Después de esa selección, needsBinding no solicita dyld para una definición
resuelta en modo estático y addNonLazyBindingEntries no añade operaciones de
coalescing/rebase runtime para ella. Las reubicaciones siguen usando getVA y
los backends originales. Los casos globales y private external se prueban con
cuerpos y datos distintos, dos órdenes de weak, tres posiciones de strong,
dirección alta y archivos estáticos. Cada referencia BL, absoluta, PAGE y GOT
debe alcanzar el cuerpo/dato seleccionado. La tabla conserva la metadata weak
que emite LLD para su visibilidad; no se editan atributos en el código XNU.

Un import weak que no se resuelve falla; no se transforma en cero. Dos
definiciones fuertes también fallan. No se generan stubs o bindings dinámicos.

Con los 89 objetos anteriores (47 XNU + 42 probes MIG), v2 ya supera los helpers y
registra las 1.245 referencias indefinidas nativas pendientes. El linker sale
con código 1 y no produce imagen. Esto conserva el límite del
[intento upstream anterior](XNU_RPC_BUILD.md); el cierre de proveedores,
el layout de segmentos y el BSP todavía requieren trabajo.
Ese intento aún contenía toda la lista de generación RPC; la
[integración de proveedores](XNU_RPC_PROVIDERS.md) corrige la selección mediante
CFILES y documenta el enlace actual con 62 unidades base y 26 RPC seleccionadas.

## Reproducir en Linux / WSL x86_64

Requiere Python, Git, CMake, Ninja, Clang/llvm-ar/LLD 19 y la instalación de
desarrollo LLVM 19.1.7. Se registra el hash del libLLVM compartido realmente
enlazado, sus dependencias runtime, herramientas host y configuración CMake.
El código LLD y sus ocho headers libunwind salen del archivo oficial fijado;
las bibliotecas LLVM de desarrollo proceden de la distribución y se identifican
por versión y hashes. Esto no declara una toolchain completa hermética.

El archivo oficial es el mismo que usa build_atlantic_clang.py: commit
cd708029e0b2869e80abe31ddb175f7c35361f90, SHA-256
05e6d7fe6d188dd4d33b812ab5cce7654b886b7c9ce405aa1d942c866bbe959f.

```sh
python3 tools/build_atlantic_lld.py --cache work/lld-clean --archive work/llvm-source.tar.gz
python3 tools/test_atlantic_lld.py --linker work/lld-clean/build/bin/ld64.lld --output work/lld-clean-tests
python3 tools/diagnose_xnu_link.py --build work/xnu-lab-builds/<base-id>/report.json --rpc work/xnu-rpc-builds/<rpc-id>/report.json --linker work/lld-clean/build/bin/ld64.lld --atlantic-static-proof work/lld-clean-tests/report.json --output work/xnu-static-new-attempt
```

Cada intento de tests o enlace exige una carpeta de salida nueva. La receta de
build comprueba 3.901 fuentes preparadas contra sus hashes, incluidos los seis
archivos modificados, y rechaza archivos imprevistos. No monta ni formatea discos.
Un cache en almacenamiento Linux nativo acelera la compilación, sin ser requisito
del formato. El Clang experimental anterior permanece sin cambios.

La evidencia v1 se conserva en evidence/lld-static-arm64-20261022 y la v2 en
evidence/xnu-static-providers-20261022. Su alcance
es host y fixtures compilados, sin emulación de estos programas, arranque XNU,
acceso al teléfono o medición de RAM residente.

Los dos workflows ordinarios del commit anterior 5906836 pasaron en GitHub:
[host](https://github.com/h0nda1337/AtlanticOS/actions/runs/39735865704) y
[XNU estándar + RPC](https://github.com/h0nda1337/AtlanticOS/actions/runs/39735865699).
La [construcción limpia experimental de 47 unidades](https://github.com/h0nda1337/AtlanticOS/actions/runs/39730078469)
también pasó en 79b9e79. Son revisiones anteriores al patch LLD; no acreditan
que GitHub Actions haya recompilado este nuevo linker. Su build limpio y las
54 comprobaciones actuales se ejecutaron localmente en Linux/WSL.
