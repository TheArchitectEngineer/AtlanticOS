# AtlanticBIOS en host

Python 3.11+, biblioteca estándar; Tk 8.6 opcional para ventana. Desde la raíz:

```powershell
python tools/host-simulator/simulate.py --gui
python tools/host-simulator/simulate.py --gui --mock-android
python tools/host-simulator/simulate.py --console --no-framebuffer
python tools/host-simulator/simulate.py --scenario tests/fixtures/countdown.json --report work/countdown.json
python tools/host-simulator/simulate.py --scenario tests/fixtures/menu.json --capture work/menu.png
```

La primera ejecución es mantenimiento sin fallback. `--mock-android` habilita un
fixture exclusivamente host: cuenta 5/4/3/2/1 y registra una transferencia simulada.
Nunca ejecuta Android, XNU, apagado del PC, comandos de dispositivos o sockets.
El menú sin teléfono ofrece los destinos sin soporte como `UNAVAILABLE`.

Flechas arriba/abajo representan Volumen. Enter representa Power: selección al
soltar; 1.5 s abre confirmación de apagado si el BSP mock tiene esa capacidad.
Los botones gráficos permiten mantener una tecla. En consola u/d/p son pulsos
de 80 ms, l representa Power largo, q cierra. La consola no prueba botones físicos.

La UI y las capturas usan exactamente el mismo renderizador RGB y atlas original
5x7 (81 glifos; mínimo 355 bytes empaquetados a un bit por píxel, sin metadata;
el diccionario Python actual es una representación host, no ese tamaño binario).
No se empaquetan fuentes de terceros. `--no-framebuffer` selecciona consola.

La política se muestrea cada 10 ms. El reloj es `time.monotonic_ns()`. Los escenarios
inyectan tiempo virtual para probar límites exactos sin esperar cinco segundos.
La reproducción en tiempo real y la memoria del proceso se miden por separado.
