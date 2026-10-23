# Experimento de enlace estático ARM64

SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

Patch original AtlanticOS sobre LLD oficial llvmorg-19.1.7, commit
cd708029e0b2869e80abe31ddb175f7c35361f90. Los archivos modificados conservan
Apache-2.0 WITH LLVM-exception; el texto completo está en
[LLVM-LICENSE.txt](../LICENSES-and-NOTICES/LLVM-LICENSE.txt).

El lock fija archive, patch y los seis pre/postimages. El modo explícito
`--atlantic-static-arm64=<base hexadecimal>` tiene alcance acotado de laboratorio.
No implementa toda la opción ld64 `-static`. La revisión v2 conserva la selección
nativa de definiciones weak/strong durante el enlace y aplica sus referencias
sin dyld. No altera las fuentes XNU, el
compilador experimental ya comprobado ni el comportamiento dinámico por defecto
de LLD.

Receta, pruebas y límites: [LLD_STATIC_ARM64](../docs/LLD_STATIC_ARM64.md).
