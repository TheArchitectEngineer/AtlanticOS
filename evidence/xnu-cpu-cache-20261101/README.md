# CPU y caché XNU: evidencia de compilación y ABI

Builds locales del 2026-10-25; hashes revalidados para publicación 2026-11-01.
155 unidades experimentales / 13 estándar; 164/134 checks. Se añaden dos
fuentes intactas, sin cambiar las 153 previas, los 70 headers o el patchset.
El enlace de 181 objetos falla: 465 indefinidos, cero duplicados, ninguna imagen.

[Contrato y reproducción](../../docs/XNU_CPU_CACHE_PROVIDERS.md).
La lane estándar usa probes aislados, no aumenta sus 13 unidades seleccionadas.
El patrón de campo MIDR es sintético. Las lecturas de registros son opcodes
inspeccionados, no ejecutados. Los tres hooks Apple vacíos ya son así en XNU;
no implementan temporizador o BSP G20. NEON del perfil no es una medición.

Los reportes enlazan fuentes/objetos/comandos y sus hashes; source/ conserva
la selección y auditor originales. Las fuentes XNU se obtienen del upstream
fijado mediante las recetas y avisos del repositorio. No se atribuyen aquí
los runs QEMU del preflight anterior, ni ejecución XNU, hardware, EDK2 o RAM.

Se publica una selección acotada de reportes, objetos y diagnósticos. El
inventario completo de 2 006 registros locales está en full-local-inventory.json;
logs vacíos y diagnósticos repetidos de componentes anteriores permanecen en
la copia local bajo work/. Los comandos y hashes permiten reproducirlos. El
manifest.json valida exactamente los archivos publicados, no los omitidos.
