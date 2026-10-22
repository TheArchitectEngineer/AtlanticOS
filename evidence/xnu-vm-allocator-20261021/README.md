# Diecisiete objetos XNU de VM/allocators/hilos/IPC — 2026-10-21

BUILT_ARM64: diecisiete unidades genuinas compiladas, sin enlace ni ejecución.
El modo estándar terminó con exit 0 y trece objetos. El modo experimental con
--probe-remaining terminó con exit 1: diecisiete objetos y dos unidades fallidas,
task.c y pmap. No se presenta el probe completo como un build aprobado.

Parches originales 0007/0008: selección del include TrustCache para monitor PPL
y nombre consistente de ZALLOC_ENABLE_LOGGING. Vm_map.c conserva sus protecciones;
zalloc conserva el logging del perfil. Tres pruebas del header real aprobaron
las rutas positiva y negativas. No son pruebas de firma o ejecución PPL.

El texto local ipc_init y su registro STARTUP son exigidos. Otros símbolos
principales son texto externo. Se registran 137 constantes target, aserciones y
42 headers MIG. 1.175 nombres externos definidos y 855 sin proveedor, sin nombres
externos repetidos, no acreditan un enlace ni RAM residente.

Comandos y logs normalizan la raíz local a <ROOT>. Los logs de guards
PMU/BSD/IOKit/proveedor retienen solo los diagnósticos de error; su preprocesado
completo queda en work/. Los otros logs están completos, incluidos los fallos.
No se publican objetos/fuentes completas XNU ni el compilador. No hubo acceso al
teléfono ni ejecución XNU en QEMU o hardware. Android no se modificó.
