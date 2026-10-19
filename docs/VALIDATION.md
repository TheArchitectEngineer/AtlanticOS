# Evidencia y puertas de aceptación

| Etiqueta | Significado preciso |
|---|---|
| HOST_TESTED | código/herramienta ejecutado en PC; mocks y fixtures explícitos |
| EMULATED | instrucciones de imagen real ejecutadas en emulador identificado |
| BUILT_ARM64 | artefacto concreto compilado para ARM64, sin afirmar ejecución |
| DEVICE_VERIFIED | binario exacto ejecutado en teléfono identificado, con prueba física |

La entrega contiene HOST_TESTED y, cuando build_abi pasa, BUILT_ARM64 de un
objeto BSP que devuelve UNSUPPORTED. No hay EMULATED ni DEVICE_VERIFIED propios.
Los tests Python no simulan CPU ni temporización eléctrica. La foto pública
V1 se auditó como evidencia externa, nunca se incorpora como logro AtlanticOS.

## Reproducción y registros

```powershell
python tools/validate.py
python tools/build_abi.py
python tools/evidence-validator/validate_evidence.py evidence/host/manifest.json
```

La primera herramienta ejecuta unittest, escenarios con reloj virtual, un replay
con monotonic real de cinco segundos, renders del mismo framebuffer mostrado
por Tk y mediciones reales del proceso host. Mantiene stdout/stderr, versiones,
hashes de fuentes y resultados en work/validation. Un fallo produce exit !=0.
El renderer rechaza desbordamiento de líneas en vez de recortarlo silenciosamente.

build_abi conserva comando, versión, hash y cabecera ELF e_machine=183. El objeto
contiene únicamente interfaz y callbacks no funcionales, no entry/kernel XNU.
La suite host no necesita Clang, teléfono, SDK Apple, red o permisos de admin.

Cobertura: 5/4/3/2/1 y frontera exacta 5 s; botón mantenido y contacto ruidoso;
doble pulsación; power corto/largo/atascado; selección no disponible; ausencia de
framebuffer/USB/SD; VNC sin consentimiento/auth/canal; configuración truncada,
duplicada o insegura; bloques fuera de rango/IO; GPT primaria con CRC/bounds
corruptos; firma ausente/inválida mediante gate mock; fallos prepare/quiesce/commit;
watchdog/reloj; RAM y límite estricto. Validación GPT no equivale a montar FS.

evidence-validator verifica rutas contenidas, SHA-256, etiqueta y campos
requeridos; no puede demostrar autenticidad de una foto ni sustituye revisión.
Un registro DEVICE_VERIFIED requiere además board, firmware, binario, fecha,
captura física y resultado de recuperación. Evitar seriales o claves al publicar.

## Puertas pendientes

F0 experimental: inventario y retorno stock en el teléfono nuevo; marcar BLOCKED
mientras falte. F1: tests/replay/captura en host; listo para revisión con límites
de configuración y VNC explícitos. F2: ejecutar rutas XNU upstream reales con
símbolos y transición operativa Mach. F3: reset/off y Android independiente.
F4: quiesce/DMA y entrada EDK2; medios solo después de sectores verificados.
F5: NIC identificado, tráfico/auth/cierre de sesión. F6: nuevo BSP con evidencias.

Cada cambio de firmware/imagen invalida pruebas físicas anteriores salvo alcance
demostrado. Cada PR debe indicar alcance, RAM, pruebas y recuperación. Una
captura de menú o cadena impresa XNU nunca satisface bring-up de kernel.
