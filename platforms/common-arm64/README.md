# ARM64 común — contrato, no hardware genérico

include/atlantic/platform.h define ABI v1. Cada BSP publica ID, capacidades y
evidencia propia. Direcciones, IRQ, PMIC, GPIO y modos USB no son universales.
El shell G20 compila sin MMIO y devuelve UNSUPPORTED. Entry y vectores propios
tienen pruebas de laboratorio; pmap y reloj nativos siguen sin ejecutarse.
El bring-up físico no debe asumir EL2 ni una CPU Apple.

El [núcleo PE original](../../docs/XNU_PLATFORM_EXPERT.md) comparte los tipos
nativos de XNU entre perfiles ARM64. Su contrato temprano
`xnu-port/platform/atlantic.h` es distinto del HAL portátil anterior: exige un
proveedor BSP fuerte para validar el boot record, la memoria del árbol y la
inicialización real de interrupciones. Todavía no existe ese proveedor para
QEMU ni para el G20. Compilar el núcleo PE no acredita esas capacidades ni
convierte el shell G20 en un controlador funcional.
