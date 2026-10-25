# Cadenas originales y soporte de imagen nativo — 2026-10-24

Esta integración completa cuatro primitivas de biblioteca necesarias para los
consumidores XNU y selecciona los lectores Mach-O y strsep genuinos del snapshot.
No reemplaza funciones de VM, scheduler, IPC o el kernel por un simulador.

## Implementación original y ABI

atlantic-core/string.c e include/atlantic/string.h son código MIT original:

| Primitiva portable | Entrada externa XNU | Contrato |
|---|---|---|
| atl_string_compare | strcmp | Comparación lexicográfica por bytes unsigned; resultado negativo/cero/positivo |
| atl_memory_compare | memcmp | Compara exactamente n bytes; sin acceso al resto del objeto |
| atl_string_copy | strlcpy | Capacidad incluye NUL; devuelve longitud de origen aunque haya truncamiento |
| atl_string_append | strlcat | Búsqueda de destino acotada a capacidad; devuelve longitud intentada; no escribe si falta NUL en ese límite |

El llamador aporta memoria válida y origen terminado en NUL para operaciones de
cadena; origen/destino de copia y append no se solapan. Capacidad cero no accede
al destino. Los helpers no asignan memoria, no usan libc host ni acceden a MMIO.
Son comunes a BSP, sin direcciones o supuestos del G20.

xnu-port/platform/string.c define proveedores de ABI nativo con nombres C propios
y nombres de ensamblador _strcmp/_memcmp/_strlcpy/_strlcat. Esto evita colisiones
con los overloads inline de los headers XNU, incluidos sus wrappers de tamaño.
Las cuatro firmas se comparan mediante static_assert con las declaraciones
reales de string.h. Los cuerpos transfieren los argumentos a los helpers reales;
no devuelven valores constantes ni enlazan libc host. La serie 0026 incorpora
copias exactas del código y header al árbol preparado; el builder coteja hashes.

## Proveedores XNU intactos

libkern/kernel_mach_header.c conserva sus lectores reales de segmentos, secciones,
UUID y final de imagen. bsd/libkern/strsep.c conserva el tokenizador y sus avisos
Apple/Berkeley. Compilar un helper BSD no habilita MACH_BSD ni procesos BSD.
Sus fuentes se comparan contra el upstream fijado; no se atribuyen a AtlanticOS.

Los lectores Mach-O **suponen un header ya validado, propio y mapeado**. No son
un validador de imágenes hostiles: recorren ncmds/cmdsize y devuelven direcciones
virtuales declaradas. El cargador todavía debe demostrar límites, overflow,
rangos y permisos antes de permitir esas llamadas. El símbolo _mh_execute_header
de C debe describir el header real de la imagen; no se inventa un objeto vacío
para resolverlo. No hay aquí una imagen kernel validada ni un cargador operativo.

## Comprobaciones

tools/test_string_support.py ejecuta 79 344 casos sobre el mismo cuerpo original
portable con ASan/UBSan: límites de capacidad, truncamiento, destinos sin NUL,
canarios, extents malloc exactos, bytes altos y comparaciones contra libc host.
Los nombres propios evitan interponer las funciones de libc o interceptores ASan.
Estas son pruebas funcionales de los helpers; no ejecutan XNU.

El contrato target compara los tipos reales de funciones y los layouts ARM64
Mach-O de 32/72/80 bytes. Capacidades y outputs truncados a 32 bits deben ser
rechazados. Se auditan las cuatro reubicaciones BRANCH26 fuertes a implementaciones
originales reales y la ausencia de imports en su objeto portable. Los dos
proveedores nativos se verifican por fuente/objeto en el carril experimental.
El estándar mantiene sus 13 unidades seleccionadas y compila dos probes aislados
de soporte; esos probes no se añaden a su enlace.

```sh
python3 tools/build_xnu_lab.py --layout-compiler <clang-v2> --layout-proof <prueba-api-v2>
python3 tools/test_string_support.py --sanitize --xnu-build <reporte-base> --output work/string-image-audit-nuevo
python3 tools/build_xnu_rpc.py --build <reporte-base>
python3 tools/diagnose_xnu_link.py --build <reporte-base> --rpc <reporte-rpc> --linker <lld-v2> --atlantic-static-proof <prueba-lld-v2> --output work/string-image-enlace-nuevo
```

En WSL/NTFS añadir --windows-git a ambos builders. Usar outputs nuevos; omitir
--xnu-build permite ejecutar solo los contratos portables y compilar su ELF ARM64.

## Estado de esta revisión

Compilan 136 unidades base experimentales y 13 estándar. Se añaden dos unidades
originales y dos fuentes nativas intactas; las 132 unidades anteriores conservan
sus hashes de fuente. Pasan 105/74 comprobaciones de alcance, ABI y objetos, los
79 344 casos host con sanitizadores, el puente de datos y los 78 tests Python.
Los 42 probes RPC por carril compilan; CFILES sigue seleccionando 26 para enlace.

El enlace estático estricto de 162 objetos falla con **594 diagnósticos
indefinidos, cero duplicados y ninguna imagen**. Once nombres antes sin resolver
tienen proveedores reales y no aparecen dependencias indefinidas nuevas. El
carril estándar mantiene 39 objetos de enlace y 825 diagnósticos indefinidos;
su LLD upstream sigue rechazando las opciones estáticas del perfil.

La [evidencia fechada](../evidence/xnu-string-image-support-20261024/manifest.json)
fija 155 artefactos con hashes, incluidos ambos builds, contratos, diagnósticos
y comparación de símbolos. Las pruebas de Clang API v2 y LLD v2 se reutilizan
por sus hashes comprobados; no se declara una reconstrucción de esas herramientas.
La [CI limpia anterior](https://github.com/h0nda1337/AtlanticOS/actions/runs/40140355927)
aprobó d984bc1 y sus 132 unidades; no prueba esta ampliación de 136.

No hay ejecución del parser nativo, strsep, bootstrap Mach, XNU o código en el teléfono.
Los fallos de ipc_policy siguen requiriendo separar política Mach de SDK/identidad
BSD; no se fabrica un proc_ro para superar esos errores.
