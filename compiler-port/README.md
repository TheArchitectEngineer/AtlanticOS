# Extensión experimental del compilador para layouts C

V2: compilador completo reconstruido desde cero y 26 comprobaciones aprobadas,
con anotaciones de uso de typedefs/campos conservadas y ocho rechazos nuevos.
Se verificaron 11.996 archivos fuente del archive fijado y su patch. La v1 histórica aprobó 18 checks
de representación C pero perdía esas anotaciones nativas. Véase
[semántica de tipos XNU](../docs/XNU_USAGE_SEMANTICS.md). El proveedor no está
activado en el build estándar de trece unidades. No prueba un kernel ni
compatibilidad del teléfono.

La [evidencia v2](../evidence/xnu-usage-semantics-20261022/manifest.json) registra
el build limpio y la integración actual de 100 objetos XNU, sin enlace kernel.

La [reproducción limpia de 17 unidades en CI](../evidence/clang-layout-ci17-20261021/manifest.json)
reconstruyó LLVM y MIG desde fuentes fijadas y pasó los 18 checks de la API.
Reproduce aquella revisión histórica; no acredita la v2 o el conjunto actual.

El XNU fijado usa metadata de tipos en su allocator. Su código público describe
encodings por granulos de ocho bytes y el resumen de sus bits bajos, pero los
Clang probados no implementan las operaciones Apple requeridas. Esta extensión
ofrece una API propia y explícita; no declara implementar los builtins privados
Apple ni suplanta __has_builtin o un SDK.

LLVM base: llvmorg-19.1.7, cd708029e0b2869e80abe31ddb175f7c35361f90.
Archivo HTTPS fijado: SHA-256 05e6d7fe6d188dd4d33b812ab5cce7654b886b7c9ce405aa1d942c866bbe959f.
El patch y [sus preimágenes/postimágenes](patches.lock.json) se pueden auditar.
Las fuentes upstream y binarios permanecen en work/. La implementación y el
fragmento del parser se publican también por separado para facilitar revisión;
el builder exige que coincidan con lo aplicado al source.

## Contrato v2

| Operación original | Resultado |
|---|---|
| __atlantic_layout_signature(T) | Literal C: un dígito hexadecimal por granulo de ocho bytes |
| __atlantic_layout_summary(T) | Bits de presencia: 1<<encoding para cada granulo |
| __atlantic_layout_compatible(A,B) | Igual secuencia de encodings de uso; void solo es idéntico a void |

El modelo utiliza el ASTRecordLayout y los tamaños del target, nunca offsets
host: padding=0, puntero=1, escalar no puntero=2. Dentro de un granulo se combina
con OR; una mezcla o union de puntero y datos produce 3. Los arrays recorren su
stride real, los bitfields sus rangos de bits y los records sus offsets reales.
Los miembros flexibles no añaden bytes a sizeof(header); el tipo del payload
variable debe analizarse por separado. Se conservan granulos de padding final.
Atomic recorre la representación de su valor y conserva el padding externo.

V2 consume annotate("atlantic.layout.pointer"), annotate("atlantic.layout.data")
y annotate("atlantic.layout.dual") en typedefs y campos. Sus encodings son 1,
2 y 3; el campo puede anular al typedef, y el alias exterior al interior. No se
elimina la información de typedef antes de analizarla. La identidad C no permite
omitir una comparación de layouts que tengan anotaciones distintas. El macro
__ATLANTIC_XNU_LAYOUT__ vale 2 y la selección XNU exige esa versión.

Los overrides se limitan a escalares o arrays de escalares de tamaño fijo.
Anotaciones desconocidas, contradictorias, con argumentos extra o aplicadas a
aggregates producen error. No se declara compatibilidad con el atributo privado
xnu_usage_semantics; el puente XNU utiliza el atributo estándar annotate.

El resumen solo define los bits bajos del modelo: no inventa significados de
los bits reservados Apple. Estos literals son metadata de memoria, no firmas
criptográficas ni verificación de firmware.

El contrato está limitado a C, AArch64 little endian, punteros de 64 bits y
char de ocho bits. Rechaza arm64e, qualifiers PAC, vectores booleanos compactos,
tipos incompletos/variables/sin tamaño, objetos de tamaño cero o mayores a
1 MiB y anidamiento mayor de 128. La compatibilidad permite identidad C sin
emitir layout; void solo es idéntico a void, no un wildcard universal.
Los casos no soportados producen error, sin constantes de éxito alternativas.

## Reproducción preparada

Desde Linux x86_64, con clang-19, lld-19, cmake, ninja, git y Python:

```sh
python3 tools/build_atlantic_clang.py --cache work/clang-layout-build --jobs 4
```

La receta descarga el archivo fijado, extrae LLVM/Clang/cmake/third-party sin
tests/docs upstream, verifica preimágenes y aplica el patch. Comprueba todas
las fuentes seleccionadas al reutilizar el cache. Construye con assertions
LLVM, backends AArch64/X86 y ejecuta tools/test_atlantic_clang.py; falla si un
caso negativo no se rechaza por el diagnóstico previsto. Conserva comandos,
logs y hashes, con alcance HOST_TESTED cuando esos pasos realmente terminen.

En WSL conviene un filesystem Linux nativo cuyo respaldo esté en F: o G:.
La receta pública no monta ni formatea nada. El experimento local usa un archivo
ext4 de desarrollo bajo G:\AtlanticOS\work; su proceso mantiene WSL activo
durante configure/build/tests para conservar el montaje. Ese archivo no es
una imagen del teléfono y no se publica.

Las pruebas preparadas comparan layouts y constantes contra expectativas
manuales y offsets del target; incluyen alias, padding, packed, arrays, unions,
bitfields, bloques y atomic, y rechazo de tipos/plataformas no soportados.
También exigen literals en LLVM IR sin llamadas runtime a esta API.
La suite se ejecutó con el compilador terminado y produjo literals en IR.
El selector explícito en XNU pasó además los checks de clasificación y punteros
de kalloc. El éxito de estos fixtures y objetos no demuestra que hilos, VM o
allocator XNU funcionan.

Evidencia: [clang-layout-20261021](../evidence/clang-layout-20261021/manifest.json).
La [CI 39626520147](https://github.com/h0nda1337/AtlanticOS/actions/runs/39626520147)
reconstruyó la receta pública completa y aprobó API y doce objetos XNU del
commit 7c9eaf2; [reportes](../evidence/clang-layout-ci-20261021/manifest.json).

Clang conserva su licencia Apache-2.0 WITH LLVM-exception; véase
[LLVM-LICENSE](../LICENSES-and-NOTICES/LLVM-LICENSE.txt).

La [CI limpia de v2 y 100 unidades](../evidence/clang-layout-ci100-20261023/manifest.json)
del commit 49bbae4 aprobó 26 checks y reprodujo fuente/defines/137 constantes
target. No declara igualdad binaria entre hosts, ejecución XNU o la revisión
posterior con SLEH y reloj.
