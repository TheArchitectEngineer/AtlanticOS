# Memoria física, caché y atómicos nativos — 2026-10-24

Esta ampliación incorpora siete fuentes genuinas de XNU: seis intactas y una
con el fallback vacío acotado al perfil que lo necesita. Sus cuerpos de memoria
se conservan. Añade un adaptador original para dos entradas de caché que faltan en
el camino ARM64 genérico del snapshot fijado. No ejecuta pmap, un pager, una
operación de caché ni una instrucción atómica. No hay acceso al teléfono.

## Proveedores seleccionados

| Fuente upstream | Comportamiento conservado |
|---|---|
| osfmk/arm64/loose_ends.c | Copia/zero físicos, traducción por phystokv y ventanas pmap, preflight de escritura y bit operations nativas |
| osfmk/arm/caches.c | Wrappers de caché del perfil seleccionado; su camino de IO coherente conserva funciones vacías/barriers upstream |
| osfmk/arm64/caches_asm.s | Mantenimiento arquitectónico ARM64 mediante DC/IC, DSB/ISB y operaciones por set/way |
| osfmk/arm/pmap/pmap_ppl_interface.c | Con NO_MONITOR llama a proveedores pmap internos reales; mapping_free_prime conserva el fallo fatal si no obtiene memoria |
| libkern/gen/OSAtomicOperations.c | CAS acquire/release y operaciones atómicas con la semántica nativa de retorno |
| osfmk/arm64/machine_task.c | Get/set del estado de depuración e herencia de estado de hilos; machine_task_init sigue vacío como upstream |
| osfmk/vm/memory_object.c | Gestión de objetos/control y despacho real por mo_pager_ops; no sustituye los backends de pager |

El build verifica símbolos sustantivos además de los nombres de inicialización.
Las seis fuentes intactas se comparan por hash con el upstream fijado y prístino.
En loose_ends.c solo cambia la guarda del fallback de registro KDP. Las
operaciones de acceso físico siguen dependiendo de gPhysBase/gPhysSize,
traducción, permisos, exclusiones y estructuras pmap válidas; compilar sus cuerpos
no establece esos invariantes. El proveedor original BSP sigue pendiente.

## Adaptador de limpieza forzada

xnu-port/platform/cache_asm.s, incorporado mediante la serie 0023 como
osfmk/arm64/atlantic_cache_asm.s, es código MIT original. Define las entradas
CleanPoC_DcacheRegion_Force_nopreempt y su variante _nohid en la misma dirección.
Ambas hacen un tail branch a CleanPoC_DcacheRegion_Force real. Esa implementación
nativa, en el perfil no Apple, salta al bucle DC CVAC con DSB SY antes/después.
El adaptador no toca el stack, preemption ni registros HID y no contiene un RET
que finja completar la operación. Su dependencia del proveedor real es fuerte.

La compilación exige ARM64 y CONFIG_ATLANTIC_FIRMWARE y rechaza familias Apple y
VMAPPLE. El perfil de laboratorio conserva líneas de 64 bytes y NO_MONITOR.
No se extiende esto a PPL/SPTM, otra placa, DMA o coherencia del G20. El llamador
debe aportar un rango propio, mapeado, aritméticamente válido y de longitud no
nula conforme al proveedor nativo; pmap usa PAGE_SIZE en el sitio actual.

El flag __ARM_COHERENT_IO__ del laboratorio hace que ciertos wrappers C nativos
solo emitan DSB o sean vacíos. Se documentan como tales: no equivalen a un backend
DMA ni a una medición de coherencia. La ruta forzada aquí auditada sí conserva
instrucciones DC CVAC; el BSP físico necesita su propio perfil y pruebas.

## Comprobación reproducible

tools/test_xnu_memory_providers.py exige un build experimental actual y audita:

- Las seis fuentes intactas, el cambio exclusivo de guarda en loose_ends.c,
  objetos seleccionados y mirror del adaptador contra su patch y lock.
- El ABI nativo de rangos y CAS; un callback con direcciones/tamaños truncados
  a 32 bits debe fallar la compilación.
- Una reubicación ARM64_RELOC_BRANCH26 hacia el proveedor fuerte real, con
  ambas entradas en la misma dirección y exactamente un tail branch.
- Los bytes ARM64 reales de DC CVAC/CVAU, IC IVAU y DSB/ISB del proveedor;
  una mutación a RET en el adaptador o que quite el primer DSB debe rechazarse.
- El bucle LDAXR/STLXR con CLREX de CAS y el salto indirecto del pager nativo,
  conservando las dependencias reales y los desensamblados.
- La selección del fallback KDP en cuatro contextos de preprocesado y la
  conservación del cuerpo y objeto del registro real de debug.c.

El primer enlace detectó dos definiciones de kdp_register_callout: un fallback
vacío de loose_ends.c cuando MACH_KDP=0 y el registro real de debug.c. El patch
0024 excluye solo ese fallback en firmware. No se debilita ningún símbolo ni se
habilita el backend KDP para ocultar la colisión. Fuera de firmware, y con KDP
seleccionado, el preprocesado de ese bloque coincide con upstream.

```sh
python3 tools/build_xnu_lab.py --layout-compiler <clang-v2> --layout-proof <prueba-api-v2>
python3 tools/test_xnu_memory_providers.py --build <reporte-base> --output work/memoria-audit-nuevo
python3 tools/build_xnu_rpc.py --build <reporte-base>
python3 tools/diagnose_xnu_link.py --build <reporte-base> --rpc <reporte-rpc> --linker <lld-v2> --atlantic-static-proof <prueba-lld-v2> --output work/memoria-enlace-nuevo
```

En WSL/NTFS añadir --windows-git a ambos builders y usar outputs nuevos. El
carril estándar conserva sus 13 unidades seleccionadas; esta ampliación no
convierte los probes de headers o PE aislado en proveedores base estándar.

## Estado de esta revisión

Compilan 132 unidades experimentales y 13 estándar sin fallos. Pasan 89/57
comprobaciones de alcance, ABI y objetos: 27 nuevas auditan estos proveedores.
El puente de datos pasa ASan/UBSan y el ABI contra headers XNU en ambos carriles;
las 78 pruebas Python también pasan. Las 137 constantes genassym y los defines
coinciden con la entrega PE anterior.

Se generan 57 headers MIG y compilan 42 probes RPC por carril. CFILES selecciona
26 para el enlace; pasan los 21 descriptores y los 14 subsistemas requeridos por
kobject experimental. El enlace estricto de **158 objetos** con LLD v2 termina
con exit 1: **609 diagnósticos indefinidos, cero duplicados y ninguna imagen**.
Frente a 669 se resuelven 60 nombres y no aparecen nuevos indefinidos. La
[comparación de nombres](../evidence/xnu-memory-providers-20261024/link-dependency-delta.json)
no equivale a 60 servicios ejecutados. El estándar de 39 objetos conserva 829
diagnósticos y el rechazo de las opciones estáticas upstream, sin imagen.

La [evidencia](../evidence/xnu-memory-providers-20261024/manifest.json) contiene
118 artefactos con hashes, incluido el primer enlace con la colisión KDP y el
resultado corregido. Las pruebas vigentes del compilador v2 (26 checks) y del
linker v2 (54 checks, 15 imágenes) se reutilizan tras cotejar sus inputs/binarios;
no se reconstruyen esas herramientas aquí. Los probes de ipc_policy y mach_debug
conservan sus fallos y no describen por sí solos todas las dependencias restantes.

Los nuevos checks son de fuente, ABI y objetos. No ejecutan copia física, caché,
atómicos, pmap, pager, PE, SecureDT, IRQ, Mach o XNU. Los recorridos QEMU anteriores
solo corresponden al preflight original y no se reasignan a estos proveedores.
Siguen pendientes la imagen XNU, productor boot_args, BSP/MMU y vía temporal,
el arranque físico, el handoff EDK2 y la medición de RAM firmware.
