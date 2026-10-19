# Modelo de seguridad y límites

Red, Wi-Fi y VNC permanecen apagados. No existe servidor, socket o criptografía
de producción en Fase 1. La denegación de imagen/firma y consentimiento se prueba
con callbacks de test; eso no verifica una firma criptográfica real.

Activos: Android recuperable, claves privadas del usuario, integridad de imagen,
datos del teléfono, mapa RAM/secure world y control físico de arranque/energía.
Amenazas: medio removible manipulado, configuración truncada, DT/GPT con overflow,
firmware equivocado, DMA activo al handoff, operador remoto sin permiso y falsa
atribución de evidencia. El atacante con control del bootloader o acceso físico
OEM queda fuera de lo que una firma de payload puede resolver por sí sola.

Tres dominios distintos: raíz BootROM/AVB OEM, verificación AtlanticOS y Secure
Boot UEFI del destino. Una clave propia no reemplaza la raíz OEM; una firma
correcta no obliga al bootloader bloqueado a ejecutar el payload. Si la etapa
que verifica AtlanticOS no es confiable, la firma por sí sola no establece trust.

## Manifiesto propuesto v1 — UNIMPLEMENTED

CBOR determinista (RFC 8949, sección 4.2), mapa de claves fijas, sin claves
duplicadas, longitudes acotadas, sin floats o formas indefinidas. Firmar los
bytes canónicos exactos con separación de dominio `AtlanticOS-manifest-v1`.
Campos: schema_version, release_version, board_ids, firmware constraints,
componentes {nombre, tamaño, SHA-256, load bounds, entry}, upstream commit,
patchset hash, payload key ID, policy y rollback_counter opcional.

Propuesta de algoritmo: Ed25519 (RFC 8032), mediante biblioteca auditada de
procedencia y versión fijadas, si se autoriza su integración. Aún no se eligió
ni incorporó una implementación. Antes de habilitar: vectores oficiales
positivos/negativos, validación estricta de codificaciones y revisión del loader.
SHA-256 de componentes con proveedor auditado; nunca implementar primitivas
propias. El uso hashlib host registra hashes de evidencia y fixtures, no prueba
un verificador firmware. Herramientas de generación/firma offline: UNIMPLEMENTED.

Claves privadas fuera del repositorio, fuera de logs y fuera de cualquier imagen.
Distribuir únicamente claves públicas. Rotación/revocación requiere política
explícita. No afirmar anti-rollback salvo contador seguro identificado y probado;
RPMB no se toca. El checksum de settings detecta corrupción, no autentica cambios.

## Superficies de entrada

GPT: validar geometría/CRC/tabla antes de usar particiones; tamaño de asignación
acotado, rangos de lectura sin overflow y sin writes. El helper actual solo
valida GPT primaria en bytes de fixture; no valida backup/MBR ni habilita boot.
FAT32 y ejecución EFI están UNIMPLEMENTED. Las EFI se delegarán a EDK2 real.

Configuración v1 host: esquema estricto, checksum, tamaño máximo 4096 y defaults
seguros ante cualquier truncamiento o campo inválido. Timeout 5 s, Android
condicionado a prueba independiente, red OFF; no persistencia en teléfono.

VNC futuro exige red/NIC probado, consentimiento local, autenticación resistente,
canal cifrado/túnel seguro y rate limits. No exponer VNC clásico ni descubrimiento
público. Eventos remotos no confirman apagado o acciones sensibles. Un único
framebuffer lógico y logs sin secretos. Cerrar sesiones, detener RX/TX/DMA y
limpiar secretos al handoff. Una red caída no debe bloquear el arranque local.

Fuentes de formato/algoritmo: [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949),
[RFC 8032](https://www.rfc-editor.org/rfc/rfc8032). Son diseño; no hay seguridad
criptográfica auditada o certificada en esta entrega.
