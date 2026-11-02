# Proveedores nativos de CPU y caché — 2026-11-01

Verificación para publicación de los builds y pruebas locales del 2026-10-25.

Se incorporan dos fuentes XNU completas e intactas al conjunto experimental:
osfmk/arm/cpuid.c y osfmk/arm/machine_routines_apple.c. El backend arquitectónico
osfmk/arm/machine_cpuid.c ya estaba seleccionado. Los tres archivos se cotejan
con el upstream fijado, sin extraer cuerpos, inventar IDs o añadir funciones
de éxito. Su selección también aparece en el CFILES generado por la herramienta
config oficial; la configuración activa NOS_ARM_ASM incluye la compatibilidad C.

El build alcanza **155 unidades experimentales / 13 estándar**. La lane estándar
conserva su selección y solo compila estos tres archivos como probes aislados.
El enlace estricto pasa de 179 objetos / 476 indefinidos a **181 / 465**, cero
duplicados, exit 1 y ninguna imagen. Once nombres reciben proveedores reales;
no se retiran referencias antiguas ni aparecen dependencias nuevas.

## Funciones conservadas y límites

cpuid.c conserva do_cpuid, clasificación de familia/subfamilia, consultas de
debug/VFP y cálculo/publicación de geometría de caché por tipo de cluster.
Se verifica el encadenamiento real hacia machine_read_midr, CLIDR/CCSIDR y
machine_write_csselr. En los objetos seleccionados siguen los MRS de esos
registros, MSR CSSELR_EL1 seguido de ISB y las llamadas de espera a Mach.

do_cacheid necesita topología y CPU local válidos. cache_info devuelve metadata
del CPU de arranque una vez inicializada; cache_info_type espera la publicación
de otra clase de cluster usando acquire, assert_wait, clear_wait y thread_block.
Compilar estos cuerpos no demuestra que esos prerequisitos estén satisfechos.

El valor de cpuid_info no es una copia cruda de MIDR: XNU reemplaza el campo
arm_arch por su clasificación ARMv8. El perfil no define HAS_APPLE_PAC y se
verifica su diferencia con ARMv8E. Las familias ARM no incluidas en la tabla
conservan CPUFAMILY_UNKNOWN; no se asigna una familia Apple al T700. El backend
de VFP marca NEON a partir del perfil compilado, sin consultarlo mediante MRS.
Esto es una suposición del target, **no una capacidad medida del teléfono**.

Tres símbolos proceden de los hooks públicos configure_misc_apple_boot_args,
configure_misc_apple_regs y configure_timer_apple_regs. Sus cuerpos upstream ya
están vacíos; se preservan y se comprueba RET más padding NOP. **No implementan
el timer, registros, interrupciones o drivers del G20.** Los controladores BSP
reales siguen siendo trabajo original pendiente. No se añade un backend Apple
o un éxito ficticio para sustituirlo.

Las rutinas de CPU en osfmk/arm64/cpu.c también estaban seleccionadas antes de
este hito y no se cuentan otra vez. Este cambio no inicia CPUs secundarios ni
ejecuta registros de identificación, cachés, Mach, IRQ o kernel.

## Comprobación

tools/test_xnu_cpu_cache.py contrasta tres fuentes intactas y el CFILES real,
compila tipos nativos y rechaza dos ABI incorrectos: MIDR con retorno de 64 bits
y getter de caché que devuelve un entero de 32 bits. Se conserva la anchura real
de boolean_t en c_valid, los offsets de cache_info_t y sus punteros ARM64.

El patrón 0x412cabc3 es un fixture sintético que comprueba el layout de campos;
**no es un ID observado**. Se auditan siete cadenas de llamadas fuertes en los
objetos y los opcodes del backend. Cambiar MRS por RET o suprimir ISB en una
copia de inspección hace fallar la comprobación, sin modificar los objetos
originales. Pasan 21 comprobaciones experimentales y 24 estándar; la diferencia
son tres compilaciones aisladas adicionales en la lane estándar.

Los headers y roles MIG siguen siendo 70; los probes RPC siguen siendo 42,
con 26 archivos seleccionados por CFILES para el enlace. El cierre no usa
dead-strip, imports ignorados, símbolos weak artificiales ni stubs AtlanticOS.
No se modifica el patchset XNU: permanecen las 29 adaptaciones y su port_id.

```sh
python3 tools/build_xnu_lab.py --windows-git \
  --layout-compiler work/llvm-toolchain/native-active/clang-layout-usage-v2/build/bin/clang \
  --layout-proof work/llvm-toolchain/native-active/clang-layout-usage-v2/tests/report.json
python3 tools/test_xnu_cpu_cache.py --build work/xnu-lab-builds/<id>/report.json \
  --output work/cpu-cache-tests-new
```

Omitir --windows-git en Linux nativo. La primera línea supone la toolchain
experimental ya construida y comprobada; sus requisitos se detallan en
XNU_COMPILER_REQUIREMENTS.md. Para la lane estándar se omiten ambos parámetros layout.
Cada ejecución del auditor exige una carpeta nueva. Evidencia:
[xnu-cpu-cache-20261101](../evidence/xnu-cpu-cache-20261101/manifest.json).

Los seis recorridos QEMU del hito anterior ejecutan entry y productor candidato
originales; no ejecutan estos proveedores ni XNU. Antes de hacerlo faltan
cierre del kernel, contexto retenido/ownership, traducciones, BSP real y carga
temporal/recuperación independientes comprobadas. Tampoco hay handoff EDK2 o
RAM firmware medida. Las pruebas físicas están en DEVICE_TEST_PLAN.md.

Fuentes oficiales fijadas:
[cpuid.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.1.9/osfmk/arm/cpuid.c),
[machine_cpuid.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.1.9/osfmk/arm/machine_cpuid.c)
y [machine_routines_apple.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.1.9/osfmk/arm/machine_routines_apple.c).
No proceden del port UEFI G20; los resultados físicos de aquel proyecto conservan
su atribución externa.
