# Semántica nativa de tipos XNU y allocator

Compilador original v2 reconstruido desde cero: 11.996 fuentes verificadas,
26 checks aprobados. 100 unidades XNU experimentales y 13 estándar compiladas;
42 probes RPC por carril y 26 seleccionados por CFILES. 36 checks de alcance/ABI
experimentales y 30 estándar, con 13 constantes ABI idénticas entre contextos
de anotaciones de uso. 78 pruebas host aprobadas. No se ejecuta XNU.

vm_pageout.c y los tipos UPL conservan sus bytes upstream. El puente mantiene
ppnum_t como uso de puntero y el allocator sigue rechazando una cola data-only
junto a un header con punteros. También se conserva el rechazo de un array
uintptr_t usado donde el view exige vm_offset_t. El intento histórico previo
al fix de declaraciones de zone_leaks se conserva separado: falló zalloc;
sus inputs pertenecen a aquella revisión intermedia, no a la actual.

Enlace experimental: 126 objetos, exit 1, 778 diagnósticos indefinidos, cero
duplicados y ninguna imagen. El LLD v2 y su prueba 54/15 se reutilizan por hash.
La selección actual no contiene sleh: su copia con tres guards corregidos
compila como preview independiente, sin prueba de excepciones o recuperación.
Los probes de las fuentes aún sin modificar siguen fallando para ipc_policy,
mach_debug y sleh. Un probe de vm_pageout ya compila.

Reportes, Makefiles, IR y logs seleccionados; sin objetos, fuentes RPC completas
o imágenes OEM. Arranque físico G20, recuperación independiente, RAM residente
y handoff EDK2 permanecen pendientes. Véase docs/XNU_USAGE_SEMANTICS.md.
