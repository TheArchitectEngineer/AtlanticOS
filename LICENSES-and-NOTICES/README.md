# Licencias y procedencia

La licencia raíz MIT cubre exclusivamente el código y documentación originales
AtlanticOS. No es una relicencia de XNU, EDK2, Linux/Motorola o el port UEFI G20.

XNU oficial fijado en dependencies.lock.json: fuente externa intacta, checkout
ignorado, no incorporado en el paquete fuente AtlanticOS. Se conserva su
APPLE_LICENSE íntegra junto a este archivo; los avisos por archivo siguen en
upstream. No hay parches todavía. Antes de distribuir componentes derivados,
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
