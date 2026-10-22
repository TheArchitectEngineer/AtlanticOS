# Meta activa — 2026-10-20

Lograr arranque físico de AtlanticOS con **XNU auténtico reducido**, entry y BSP
originales, y desde ese contexto transferir control a UEFI EDK2 real. La meta no
se considera lograda con una pantalla, un stub propio, una cadena impresa XNU o
el arranque del port UEFI ajeno. Preservar Android; la autorización actual no
incluye flash ni modificación de particiones reales. Publicar evidencia y límites.

Orden acordado con el usuario:

1. Entry ARM64 común y capacidades BSP, formatos y memoria comprobables.
2. Bootstrap sustantivo de XNU: VM/allocators, scheduler, contexto de hilo y timer
   o transición Mach válidos, con upstream/patchset y símbolos identificables.
3. Port G20, instrumentación física y recuperación Android independiente.
4. Preparar/quiesce/commit a EDK2 desde AtlanticOS; comprobar DMA, memoria y entrada.
5. AtlanticBIOS completo, dispositivos de arranque y funciones adicionales.
6. VNC y Wi-Fi al final, tras drivers/red, autenticación y cierre de sesión probados.

Durante bring-up se mantienen únicamente consola, diagnósticos y controles de
recuperación necesarios. El simulador de menú existente conserva su suite; no
absorbe trabajo prioritario antes de que el núcleo y el handoff sean reales.

AtlanticOS está pensado para varios dispositivos. G20 es primera referencia,
no núcleo de la arquitectura. Entry y parsers comunes no contienen MMIO G20.
QEMU virt tiene BSP de laboratorio separado; no cuenta como segundo teléfono.
Cada nueva placa requiere identidad, rangos, empaquetado, capacidades y evidencia
independientes. Añadir carpetas no concede compatibilidad.

El usuario indica que este G20 no dispone de fastbootd. Se registra como
USER_REPORTED_UNAVAILABLE y no se intentará entrar. La evidencia USB obtenida
hasta ahora confirma is-userspace=no del bootloader; no es un test de fastbootd.

Avance comprobado el 2026-10-21: cinco unidades genuinas XNU compiladas con
perfil/ABI propios, aún sin enlace; entry QEMU original EL1/EL2→EL1h y excepción
síncrona comprobada en cuatro recorridos. [CI host](https://github.com/h0nda1337/AtlanticOS/actions/runs/39606710568)
y [CI XNU](https://github.com/h0nda1337/AtlanticOS/actions/runs/39606710790)
aprobaron el commit 75b3f17. No hay ejecución XNU, resultado físico AtlanticOS,
handoff EDK2 ni RAM firmware medida. Los siguientes límites de build están en
[XNU_COMPILER_REQUIREMENTS](XNU_COMPILER_REQUIREMENTS.md); las pruebas físicas
pendientes se detallan en [DEVICE_TEST_PLAN](DEVICE_TEST_PLAN.md).

Ampliación posterior: once unidades reales compiladas, incluyendo start,
cswitch, locore, rutinas de máquina, arm_init y arm_vm_init. [CI host](https://github.com/h0nda1337/AtlanticOS/actions/runs/39611682565)
y [CI XNU](https://github.com/h0nda1337/AtlanticOS/actions/runs/39611682795)
aprobaron 6a2bb69; las 137 constantes de layout coinciden entre Clang 19.1.1 y
19.1.7. Hay 74 pruebas host aprobadas. Siguen pendientes el cierre de símbolos,
hilos/VM completos, enlace, ejecución XNU y evidencia física. Compilar más
unidades no cambia el criterio de aceptación del objetivo.

La ampliación de [dependencias core](XNU_CORE_CLOSURE.md) llega a 39 objetos
experimentales con el compilador original explícito. Pageout, parte de IPC,
enlazador estático, Platform Expert y BSP siguen pendientes. La evidencia
compilada conserva ese alcance; el objetivo físico y el handoff no cambian.

La [integración de IPC](XNU_IPC_BUILD.md) amplía el build experimental a 47
unidades y conserva los accessors RO de hilo y la herencia de importancia
nativos. Los 50 headers MIG se generan con sus roles reales. Esto tampoco
acredita entrega de mensajes, ejecución XNU, arranque físico o handoff EDK2.
