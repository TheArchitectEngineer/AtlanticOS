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
