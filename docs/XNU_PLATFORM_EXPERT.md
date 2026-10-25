# Núcleo original de Platform Expert — 2026-10-23

AtlanticOS implementa su núcleo de Platform Expert en
xnu-port/platform/pe_platform.c, con la frontera BSP en platform/atlantic.h.
La serie 0022 incorpora exactamente esos archivos al árbol XNU preparado; el
builder coteja ambos cuerpos y hashes. No se usa pe_init.c de Apple como
implementación del dispositivo. El código común no contiene direcciones MMIO,
GPIO, GIC, PMIC o identificadores particulares del G20.

Compilan 124 unidades experimentales, incluida esta unidad original, y las
13 estándar del conjunto base. No hay ejecución de este PE ni de SecureDT.
La compilación aislada del mismo PE también se comprueba con el compilador
estándar, sin presentarla como unidad seleccionada en ese conjunto base.

## Dos fases nativas diferentes

El consumidor nativo arm/arm_init.c copia primero el boot_args completo a
const_boot_args y después llama a PE_init_platform(FALSE, args). Datos añadidos
informalmente detrás de la estructura no sobrevivirían esa copia. La fase
posterior llama a PE_init_platform(TRUE, &BootCpuData); el camino secundario
puede pasar NULL. No es otro boot_args y el código no lo trata como tal.

La fase FALSE comprueba el contrato y consulta SecureDTInit, SecureDTLookupEntry
y SecureDTGetProperty reales. Los campos DRAM deben concordar con boot_args.
La afinidad primaria y la frecuencia se cotejan con lecturas arquitectónicas
MPIDR_EL1 y CNTFRQ_EL0. No hay frecuencia de 24 MHz asumida ni valores fabricados
para CPU, bus o memoria. PE_state.initialized solo se publica al cerrar esas
comprobaciones. Los registros aquí citados todavía no se han leído en el teléfono.

La fase TRUE exige la fase de datos y llama al backend BSP de interrupciones con
el argumento original de XNU. Un fallo produce panic mediante el proveedor XNU
real; no continúa como si la IRQ estuviera inicializada. Esto no acredita que
panic pueda imprimirse o retornar a Android en hardware: faltan consola y pruebas.

PE_register_timebase_callback y PE_call_timebase_callback entregan la frecuencia
validada como razón Hz/1 a la interfaz nativa de rtclock. Un callback antes de la
fase de datos falla. PE_slide_devicetree conserva el delta modular vm_offset_t
usado por el llamador nativo, comprueba de nuevo propiedad/lectura del span,
reinicializa SecureDT y solo entonces cambia el puntero PE. Un delta no prueba
por sí solo que el destino esté mapeado. El boot_args copiado no se modifica.

## Contrato BSP obligatorio

atlantic_pe_platform es una referencia externa fuerte, de 32 bytes en este ABI
ARM64: versión/tamaño y tres callbacks de tipos nativos. Debe aportarlo un módulo
BSP original seleccionado para la placa. No se define una tabla por defecto,
no se enlaza un mock y no se considera implementado un backend por declarar
sus funciones.

| Callback | Obligación antes de KERN_SUCCESS |
|---|---|
| validate_boot_record | Identidad de placa/build, imagen real, ownership del loader, mapa/traslación y exclusiones de RAM demostrados desde contexto retenido; no basta comparar campos de C |
| validate_tree_mapping | Todo el span pertenece al payload y es memoria normal legible en la traducción activa, incluso tras reubicarlo |
| initialize_interrupts | Inicialización real de controlador/ruta IRQ por CPU; NULL exige obtener el contexto secundario legítimo |

Durante la validación inicial PE_state todavía no está publicado. Los callbacks
de comprobación no deben llamar a PE_boot_args o PE_parse_boot_argn: reciben
el registro directo y deben usar su contexto retenido. El contrato completo
de ese contexto y su productor forma parte del trabajo pendiente del cargador.

**No se suministra aún este proveedor.** Falta implementar sus funciones para
QEMU y para el G20, con evidencia independiente de cada BSP. Su símbolo debe
seguir sin resolver en el enlace del kernel actual; silenciarlo o añadir una
tabla que devuelva éxito no completaría esta tarea.

El PE es común a perfiles ARM64 de firmware. El selector BSP y sus capacidades
siguen siendo independientes por dispositivo; el prototipo actual no acredita
compatibilidad de otra placa ni SMP del G20.

## boot_args que deberá producir el cargador

Se conservan los tipos y campos reales del snapshot XNU fijado: tamaño 1152,
línea de 1024 bytes y versión/revisión 2. machineType usa ATL1 (0x41544c31), un
tag de nuestro contrato de firmware, sin significado OEM. Se exigen RAM/aritmética
válidas y alineación mínima 4 KiB; el BSP debe comprobar la granulación efectiva,
todos los rangos y protecciones. memSize describe memoria administrable y no
se presenta como consumo del kernel. memSizeActual debe concordar con el DRAM
del árbol. topOfKernelData debe quedar dentro del rango acordado.

La línea debe estar terminada dentro de su límite. La primera integración es
headless y requiere vídeo nulo; un framebuffer futuro exige ampliar de forma
explícita el contrato y su prueba de ownership. **El productor completo de estos
boot_args todavía no existe.** El árbol de 504 bytes de BOOT_DATA_BRIDGE.md solo
resuelve parte de los datos y no convierte un ELF de prueba en un kernel XNU.

La [preparación posterior](BOOT_PREPARATION.md) ya serializa el candidato completo
de 1 152 bytes y lo coteja con inicializadores nativos de ambas toolchains.
En nuestro contrato ATL1, deviceTreeP contiene la futura KVA que este PE leerá.
El productor se ejecuta en QEMU sin XNU, sin colocar la imagen/árbol o construir
el contexto retenido; no existe aún un proveedor de callbacks que pruebe
ownership y configure interrupciones. El resultado no habilita PE_init_platform.

## Verificación y estado

Pasan 62 comprobaciones de alcance/ABI/objetos experimentales y 57 estándar:
incluyen 11 nuevas sobre PE integrado y 12 sobre el probe estándar aislado.
También pasan el puente de datos con ASan/UBSan y las 78 pruebas Python.
Los 57 headers MIG, 42 probes RPC, 26 objetos seleccionados y 21 descriptores
conservan sus checks; los 14 subsistemas requeridos de kobject tienen proveedores.
Las 137 constantes genassym y los defines coinciden con la revisión anterior.

El enlace estricto de **150 objetos** con LLD v2 falla con exit 1: **669
diagnósticos indefinidos, cero duplicados y ninguna imagen**. Resuelve cuatro
nombres del enlace anterior de 672 (_PE_init_platform, registro de timebase,
PE_state y gPEClockFrequencyInfo) e introduce el import BSP fuerte
_atlantic_pe_platform. El estándar de 39 objetos conserva 829 diagnósticos y
el rechazo de las opciones estáticas upstream, sin incorporar su probe PE.

La [evidencia de esta revisión](../evidence/xnu-original-pe-20261023/manifest.json)
contiene 77 artefactos. Se reutilizan por hashes las pruebas vigentes del
compilador v2 (26 checks) y del linker v2 (54 checks, 15 imágenes); no se
reconstruyen aquí. Los probes ipc_policy y mach_debug siguen fallando, y no son
la lista completa de proveedores pendientes.

Los checks del nuevo PE son de ABI C, preprocesado y objetos Mach-O ARM64:
comparan prototipos nativos, rechazan callbacks con tipos incompatibles y
composiciones sin firmware/con BSD/IOKit, comprueban el import BSP fuerte y
las instrucciones emitidas para los registros. No ejecutan callbacks, PE,
SecureDT, IRQ, scheduler o Mach. Las cuatro ejecuciones QEMU de la entrega
anterior solo ejercitan el entry y puente originales; no se reasignan a este PE.

Antes del arranque físico faltan cierre de símbolos y segmentos, boot_args real,
BSP/IRQ, MMU/pmap, logging, vía temporal y recuperación independiente. La meta
sigue exigiendo XNU real instrumentado, transición Mach válida, RAM firmware
medida y handoff EDK2. Ninguna de esas puertas se declara cerrada aquí.

## Reproducir

Con las fuentes fijadas y las pruebas vigentes de las herramientas:

```sh
python3 tools/build_xnu_lab.py --layout-compiler <clang-v2> --layout-proof <prueba-api-v2>
python3 tools/test_xnu_platform.py --build <reporte-base> --output work/pe-audit-nuevo
python3 tools/build_xnu_rpc.py --build <reporte-base>
python3 tools/diagnose_xnu_link.py --build <reporte-base> --rpc <reporte-rpc> --linker <lld-v2> --atlantic-static-proof <prueba-lld-v2> --output work/pe-enlace-nuevo
```

En WSL/NTFS añadir --windows-git a ambos builders. Cada output de auditoría
debe ser nuevo; no sobrescribir evidencias previas. Omitir las opciones layout
del primer comando obtiene el conjunto estándar de 13 unidades y permite
comprobar el probe PE aislado. El diagnóstico de enlace conserva el fallo
estricto; no produce una imagen para arrancar.

La [ampliación posterior de memoria](XNU_MEMORY_PROVIDERS.md), con las series
0023/0024, lleva el conjunto actual a 132 unidades. Los números de 124 y 150
objetos anteriores describen esta entrega PE del 2026-10-23 y su evidencia.
