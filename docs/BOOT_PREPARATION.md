# Preparación original de boot_args y memoria — 2026-10-25

AtlanticOS produce un **boot_args candidato de 1 152 bytes** a partir de un
Mach-O validado, declaraciones RAM/reservas y una ventana explícita. El módulo
portable es atlantic-core/boot_prepare.c. Se prueba en host y se ejecuta como
código ARM64 original en QEMU; no coloca el payload, habilita MMU, construye
el contexto retenido o llama al kernel.

## Perfil y contrato

Se coteja el registro completo con inicializadores del tipo boot_args real,
compilados con ambas toolchains. Los headers modificados se verifican contra
pre/postimágenes del lock; no se describen como intactos. Los objetos confirman:

| Dato del perfil actual | Valor |
|---|---|
| ARM_PGSHIFT / ARM_PGBYTES | 12 / 4 KiB |
| ARM_TT_L2_SHIFT / ARM_TT_L2_SIZE | 21 / 2 MiB |
| BOOTSTRAP_TABLE_SIZE | 32 KiB / ocho páginas hardware |
| VM_KERNEL_LINK_ADDRESS | 0xfffffff007004000 |
| TCR_EL1_BOOT | 0x22a5192519 |
| T0SZ / T1SZ / IPS | 25 / 25 / 2: VA 39 bits, PA 40 bits |

Son valores compilados, **no capacidades observadas del T700**. El módulo solo
acepta este perfil; otra configuración necesita su propio contrato y prueba ABI.
El tamaño software de página tampoco se deduce solo del tamaño hardware.

Se cotejan siete fragmentos con upstream: tres macros de tablas/bloques, cálculo
del alcance inicial, conversión del argumento a KVA, copia a const_boot_args y
liberación del prefijo anterior al kernel. Se conservan, sin algoritmos sustitutos.
El código nativo resta el desplazamiento hasta el header y redondea el resto a
bloques L2; los descriptores enmascaran direcciones a bloque. La alineación
Mach-O de 16 KiB por sí sola no prueba ese alcance. La ruta nativa también puede
liberar el prefijo anterior al kernel; no debe usarse para contexto retenido.

AtlanticBootRequest declara managed_pa/managed_bytes, tamaño del árbol, capacidad
del futuro contexto y línea ASCII. La ventana debe estar en un único banco RAM
declarado, alineada a 2 MiB, tener entre 4 y 256 MiB y excluir **cada reserva**.
También se comprueban el prefijo mapeado y la cola que inicialmente queda sin
mapping. No se aplanan bancos separados. La identidad TTBR0 limita la PA a
39 bits, aunque IPS permita 40. La colocación conserva el desplazamiento del
header dentro del bloque y se acota el número de tablas antes de emitir salida.
El archivo se vuelve a validar con atl_macho_plan; no se confía en un plan C
arbitrario como si acreditara inspección de sus bytes.

Después del span entero de la imagen se reservan contexto, árbol y boot_args.
Las páginas auxiliares de 16 KiB conservan alineación de ambas páginas software
posibles. topOfKernelData incluye esos espacios y deja al menos otra página
dentro del alcance inicial. Esto **no demuestra un límite del consumo nativo
temprano**: habrá que instrumentarlo hasta que XNU reemplace sus mappings.

El registro usa revisión/versión 2, tag propio ATL1, vídeo/bootFlags/padding cero
y línea terminada dentro de 1 024 bytes. memSize describe la ventana y
memSizeActual el DRAM declarado; **ninguno mide RAM residente**. En el contrato
AtlanticOS, deviceTreeP lleva la futura KVA que nuestro PE deberá consumir con
traducción activa. No se dereferencia ese puntero al preparar el candidato.
Los otros campos de AtlanticBootPreparation son un plan C, no una ABI wire nueva.

No se escribe ninguna PA calculada. Fallos dejan argumentos y salida intactos;
se rechaza solapamiento de sus spans. Alias físicos mediante otras traducciones
y permisos runtime siguen siendo responsabilidad del BSP. No hay heap, libc,
MMIO G20, firma comprobada o proveedor PE de éxito ficticio.

## Evidencia

- 10 038 casos host por lane con ASan/UBSan: 10 000 mutaciones y 30 rechazos
  dirigidos. Incluyen overflow, reservas, límites, línea completa, aliases,
  imagen que no cabe, PA fuera del perfil y dirección de enlace baja.
- Coinciden los 1 152 bytes con ambos inicializadores ARM64 nativos, incluidos
  padding y puntero. Se verifican constantes y siete fragmentos de código.
  Es compilación/inspección de objetos, sin ejecutar XNU.
- Dos runs QEMU del probe boot-args, EL1 y EL2→EL1h: ejecutan nuestro parser y
  productor, emiten todo el registro por UART y Python compara cada byte con
  una construcción independiente. Su SHA-256 coincide con las referencias host.
- Una ventana de 64 MiB desde 0x42000000 cruza el DTB real de QEMU en 0x44000000
  y debe fallar. La de 32 MiB termina antes y permite preparar el candidato.
  El mapping inicial calculado cubre 30 MiB; los 2 MiB finales necesitan las
  tablas posteriores de XNU, todavía no ejecutadas.
- Se repiten normal y BRK en ambos EL: seis runs ARM64 correctos en total.
  Las instrucciones de los fixtures Mach-O no se ejecutan.

El primer intento ARM encontró una excepción de alineación en un STURH generado
desde el serializador byte a byte: PC simbolizado en le64, ESR=0x96000061 y FAR
impar. El prearranque ahora usa -mstrict-align; se conserva el diagnóstico fallido
y se comprueba la corrección con los seis runs. No se desactiva la comprobación
de CPU. Cambian las opciones del preflight original, no las 153 unidades XNU;
su estado y alineación se verificarán durante la integración.

El probe correcto tiene 73 304 bytes de archivo y 158 208 reservados por su
linker para imagen/BSS/stack; normal tiene 15 368 / 98 960. **No miden RAM XNU,
un loader completo o el G20**, ni acreditan el objetivo físico de menos de
100 MiB. Los fixtures son assembler original MIT enlazado anteriormente por
LLD; no son kernel, BootShim, BSP importado o firmware OEM. Los logs conservan
XNU_NOT_LINKED y CANDIDATE_NOT_PLACED_OR_MAPPED donde corresponde.

## Reproducción y pendiente

```sh
python3 tools/test_boot_prepare.py --sanitize --output work/prepare-host-new
python3 tools/test_boot_prepare.py --sanitize --output work/prepare-abi-new \
  --xnu-build work/xnu-lab-builds/<build-id>/report.json
python3 tools/build_entry.py --probe boot-args --output work/prepare-qemu-new
python3 tools/emulate_entry.py --build work/prepare-qemu-new
```

Cada prueba host exige carpeta nueva. Para los otros recorridos construir y
emular normal y el1-trap por separado. CI host ejecuta las seis rutas QEMU y
el contrato portable; las lanes XNU contrastan el inicializador y geometría.

[Evidencia](../evidence/boot-prepare-20261025/manifest.json). Falta colocar,
copiar/zero-fill y autenticar la imagen, construir/anclar el contexto retenido,
probar traducciones y asignaciones tempranas, implementar IRQ/BSP y ejecutar
kernel y handoff EDK2. El enlace sigue en 179 objetos / 476 indefinidos, sin imagen.

Fuentes oficiales:
[boot.h ARM64](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.1.9/pexpert/pexpert/arm64/boot.h),
[start.s](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.1.9/osfmk/arm64/start.s)
y [arm_vm_init.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.1.9/osfmk/arm64/arm_vm_init.c).
