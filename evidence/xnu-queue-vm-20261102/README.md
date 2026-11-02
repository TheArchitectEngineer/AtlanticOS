# Colas nativas y VM wait — 2026-11-02

159 unidades experimentales / 13 estándar, 202/176 checks. Se incorporan counter.c
ARM y priority_queue.cpp íntegros. El patch 0031 separa alcance VM/IOSCHED sin
cambiar cuerpos. 156 fuentes anteriores conservadas, 137 constantes y 70 headers
MIG iguales; 42 probes RPC, 26 seleccionados. Enlace estático de 185 objetos:
436 nombres indefinidos, cero duplicados, exit 1 y ninguna imagen. Resuelve 27,
sin nombres pendientes nuevos. La lane estándar usa LLD upstream y registra
sus errores de opciones estáticas; no es el modo estático experimental local.

Se conservan informes completos, objetos nuevos, fixtures C/C++, rechazos ABI,
disassembly, fuentes ligadas por SHA-256 y logs reales del enlace. Las expansiones
completas de los bloques condicionales y otros archivos locales están inventariados
en local-inventory.json; no se presentan como archivos publicados. Las fuentes
nativas/objetos conservan su procedencia XNU y sus licencias, no MIT AtlanticOS.

Los casos de preprocessing son del bloque condicional aislado, no builds de todas
las configuraciones completas. Los bytes de child/key/deadline son sintéticos.
Las instrucciones atómicas de 64 bits se inspeccionan sin ejecutarse. No hay
ejecución de queues, contadores, VM o XNU, ni acceso al G20 o RAM física medida.

El primer ensayo falló al abrir un objeto de caché puesto en cuarentena por
Defender y se descartó: discarded-first-link.log no se usa para contar símbolos.
El enlace auditado usa una reconstrucción nueva con todas las entradas verificadas.
La cuarentena no se restauró y no se cambiaron protecciones/exclusiones.

La CI limpia success conservada corresponde a 157 unidades / 5ce46c8. No se
atribuye a esta ampliación de 159. publish_audit.py conserva las verificaciones
y rutas locales usadas al empaquetar. El contexto físico y handoff siguen pendientes.
