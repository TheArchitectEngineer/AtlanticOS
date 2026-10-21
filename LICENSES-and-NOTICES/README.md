# Licencias y procedencia

La licencia raíz MIT cubre el código y documentación originales AtlanticOS,
salvo avisos específicos por archivo. La extensión original de Clang bajo
compiler-port/ usa Apache-2.0 WITH LLVM-exception. No es una relicencia de XNU,
LLVM, EDK2, Linux/Motorola o el port UEFI G20.

XNU oficial fijado en dependencies.lock.json: fuente externa intacta, checkout
ignorado, no incorporado en el paquete fuente AtlanticOS. Se conserva su
APPLE_LICENSE íntegra junto a este archivo; los avisos por archivo siguen en
upstream. Los parches originales están en xnu-port/ y conservan la licencia de
los archivos modificados. Antes de distribuir componentes derivados,
mantener procedencia y avisos, revisar cada licencia y adjuntar fuentes aplicables.

EDK2 es un destino futuro, no una dependencia enlazada en esta entrega. El commit
registrado corresponde a la referencia UEFI auditada y conserva sus licencias
BSD-2-Clause-Patent y por componente. No se distribuyen sus binarios o wrappers.

El port G20 incluye adaptaciones con GPL-2.0-only y BSD-2-Clause-Patent. Solo fue
estudiado en work/references, no se copió a drivers AtlanticOS ni se ejecutaron
sus empaquetadores. Las referencias Motorola son para entender hardware;
proveniencia e inventario quedan enlazados, no se presentan como código original.

Atlas 5x7: original AtlanticOS, MIT; no fuentes, iconos o imágenes de terceros
empaquetados. La foto pública se inspeccionó localmente pero no se redistribuye.
SHA-256 y URL permiten auditar la fuente sin atribuirnos su prueba.

Python/Tk y Clang/Git son herramientas host externas; sus versiones verificadas
están registradas. El runtime no se incluye. No hay biblioteca criptográfica de
firmware integrada ni claves privadas de prueba/publicación.

El experimento de compilador fija llvmorg-19.1.7 / cd708029e0b2869e80abe31ddb175f7c35361f90.
La fuente upstream y el build permanecen bajo work/; se publica el patchset y
la implementación original, no el tarball ni un SDK. LLVM-LICENSE.txt conserva
el texto de licencia upstream. Este experimento no sustituye código kernel XNU
ni drivers y no constituye compatibilidad completa con builtins privados Apple.
