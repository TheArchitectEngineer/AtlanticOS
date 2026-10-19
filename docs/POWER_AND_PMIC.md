# Energía y PMIC

Estado G20 AtlanticOS: UNSUPPORTED. El shell BSP C no realiza SMC, MMIO, GPIO,
reinicio ni apagado. El host registra únicamente mock:power:off/restart.

La cabecera de referencia declara PSCI arm,psci-0.2 mediante SMC
([S05](SOURCE_INDEX.md#s05)); no equivale a validar SYSTEM_RESET o SYSTEM_OFF.
Identificar el nodo exacto del DTB stock, versión de firmware, conduit y
disponibilidad antes de diseñar llamadas. No probar function IDs por fuerza bruta.
El segundo camino posible es PMIC/ADI del fabricante, con fuente nativa y
secuencia documentada; aún no está identificado como método de apagado propio.

El manifiesto Motorola de referencia apunta a SC2730 y fuentes de reguladores
([S12/S18](SOURCE_INDEX.md#s12)). Son pistas de investigación, no prueba de que
un reset de ese PMIC sea correcto ni licencia para copiar su driver al proyecto.

Solicitud v1: RESTART, POWER_OFF, CANCEL. Power corto confirma selección al
soltar tras debounce; largo de 1.5 s abre diálogo separado, Cancel por defecto.
Confirmación física posterior; mantener Power atascado no debe confirmar.
Tiempo/umbral físico requieren prueba con BSP real; el host no mide GPIO.

Antes de ejecutar: cerrar red, parar DMA/IRQ, conservar logs, limpiar secretos,
resolver watchdog según documentación y comprobar que los recursos quedaron
quiescentes. Un fallo parcial aborta sin intentar una secuencia PMIC alternativa
desconocida. No desactivar watchdog a ciegas ni simular que fue alimentado.

DEVICE_TEST_PLAN T06/T07 exige reset y apagado por separado, observación de
pantalla/USB/consumo y retorno stock. Si se apaga completamente, un wake source
PMIC externo debe poder encender; software ya detenido no puede prometerlo.
Batería, cargador, causa de reset y RTC quedan UNKNOWN hasta identificar buses,
registros y escalas; no mostrar un porcentaje inventado.

Tras handoff, ResetSystem es responsabilidad del destino EDK2; no conservar
punteros a power_request de XNU. Fuente: [UEFI Runtime Services](https://uefi.org/specs/UEFI/2.10/08_Services_Runtime_Services.html).
