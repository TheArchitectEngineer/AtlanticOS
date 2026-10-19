# Contribuir

Ejecutar `python tools/validate.py` antes de publicar cambios de política/UI.
Para cambios de ABI/BSP ejecutar también `python tools/build_abi.py`. Adjuntar
comandos/logs/hashes, alcance de RAM y etiquetas de evidencia. No añadir drivers
de un port previo como sustituto de trabajo propio. Citar fuentes al investigar
registros, preservar licencias y mantener xnu-port/series revisable.

No imágenes stock, particiones, secretos, claves privadas, seriales o IMEI en
Git. El simulador no debe ganar acceso a dispositivos ni funciones de flash.
Pruebas físicas requieren código revisable y recuperación independiente;
instalación/desbloqueo/escritura son procedimientos separados autorizados.

Los cambios de XNU deben conservar origen, símbolos y logs que demuestren rutas
reales. HOST_TESTED o BUILT_ARM64 nunca significan DEVICE_VERIFIED.
