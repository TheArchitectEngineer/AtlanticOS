# Plan original Mach-O estático — evidencia host

45 099 casos por lane nativa, ASan/UBSan, 33 024 truncamientos exactos,
12 000 mutaciones, 53 rechazos dirigidos y 15 imágenes genuinas Atlantic LLD v2.
La lane host sin fixtures/headers nativos ejecuta 45 084 casos.

API, límites, asignación/carga pendiente y reproducción:
[STATIC_IMAGE_PLAN](../../docs/STATIC_IMAGE_PLAN.md).

Los reportes y logs son las salidas reales; source/ fija el código probado.
lld-fixtures/ contiene programas assembler originales MIT, no un kernel XNU.
El objeto portable ARM64 no tiene imports; los objetos ABI solo comprueban
headers oficiales. No se ejecuta código ARM64, XNU o BSP en esta evidencia.

prior-native153-ci.json registra la CI limpia previa de c8fc3cd: no prueba el
parser añadido después. No hay carga, firma comprobada, acceso al teléfono,
flasheo, handoff EDK2 o medición de RAM física.

Los fallos exploratorios quedan privados en work/macho-plan-*; revelaron el
flag SG_READ_ONLY y el BSS dentro del padding de archivo, ambos comprobados
en las pruebas finales. Los reportes finales corresponden al código de source/.
