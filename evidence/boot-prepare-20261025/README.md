# Candidato boot_args: host y QEMU originales

10 038 casos ASan/UBSan por lane; los 1 152 bytes coinciden con ambos
inicializadores de tipos nativos XNU y con la emisión real ARM64 en QEMU.
Seis runs correctos: normal, BRK y boot-args en EL1 y EL2→EL1h.

El probe rechaza una ventana que cruza el DTB observado de QEMU. Se conserva
una observación fallida anterior a -mstrict-align con ELF, log y PC simbolizado.
No se cuenta como run correcto. No se ejecutan XNU ni el fixture Mach-O.

[Contrato, límites y reproducción](../../docs/BOOT_PREPARATION.md).
source/ fija las entradas originales; los headers nativos se referencian por
hash/lock, sin fingir que todos están intactos. Los objetos de ABI son fixtures
de datos y no proveedores del kernel. No hay payload colocado, contexto BSP
retenido construido, MMU configurada para XNU, ownership, firma comprobada,
teléfono accedido o RAM física medida. XNU_NOT_LINKED permanece en todos los runs.
