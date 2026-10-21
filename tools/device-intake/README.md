# Inventario físico de solo lectura

Herramientas separadas del simulador: no se ejecutan durante unittest ni CI.
ADB/fastboot solo se usan al invocar explícitamente el script contra un teléfono
autorizado. Sin root, reboot, cargas, flash, erase, OEM, cambios A/B o umbral de
batería. Las consultas están enumeradas; no aceptan comandos arbitrarios.

```powershell
python tools/device-intake/collect.py --output work/device-intake/session-01
# Solo después de llegar por botones al bootloader y dejar el teléfono allí:
python tools/device-intake/fastboot_readonly.py --output work/device-intake/bootloader-01
```

Cada destino debe ser un directorio nuevo dentro de work/. Se conserva stdout y
stderr privado; los seriales del transporte se redactan en public/. Revisar esos
archivos antes de copiar al repositorio. La enumeración exige un único transporte
autorizado; ADB acepta --serial para selección explícita si existen varios.

Propiedades ausentes, acceso denegado y timeouts se conservan como tales. Un
fingerprint OEM no demuestra integridad stock. Listar /dev/block/by-name no
equivale a leer sectores ni a probar un driver AtlanticOS. MemTotal de Android
no mide XNU. No se consulta getprop/getvar all ni serial/IMEI/batería.

Etiqueta HOST_TESTED: herramienta ejecutada en PC con observaciones ADB/USB de
un dispositivo físico. No se marca DEVICE_VERIFIED de AtlanticOS porque no se
ha ejecutado su firmware. El método de entrada física/retorno se documenta por
separado con observación del usuario; la disponibilidad USB sola no lo prueba.
