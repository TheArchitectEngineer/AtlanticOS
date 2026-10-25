# Coaliciones, bank y roles MIG oficiales — 2026-10-24

Esta revisión completa una regla del build nativo y selecciona cinco fuentes
osfmk para dependencias pendientes de Mach. No implementa identidades de proceso
o persona alternativas ni da por operativos los servicios al compilar sus objetos.

## Headers oficiales y ABI

coalition.c incluye coalition_notification_server.h. Ya existían el header
kernel-sender coalition_notification.h y su C generado por MIG, seleccionado
por CFILES, pero faltaba la variante de header de MIG_USHDRS que usa el consumidor.
La receta oficial osfmk/mach/Makefile genera esa variante con -sheader, sin los
flags KERNEL_USER/KERNEL_SERVER. La interfaz .defs fija la notificación en el
subsystem 5300, con ID de 64 bits y flags de 32 bits.

El builder ejecuta ahora toda la lista MIG_USHDRS. Genera trece variantes
adicionales; exc_server.h y mach_exc_server.h conservan sus variantes internas
kernel-server de mayor prioridad. Se mantienen también la prioridad kernel-sender
y las salidas laterales de MIG_KUSRC. El total pasa de 57 a 70 headers únicos:

| Rol | Headers |
|---|---:|
| sender | 14 |
| user-server | 13 |
| kernel-server, incluido device | 22 |
| kernel-sender | 21 |

No se escribe un header manual ni se modifica coalition.c para ocultar el include.
Generar un header de receptor no genera su servicio. Los C RPC siguen procediendo
de las recetas nativas; se comprueba que ambos headers de coaliciones declaran
el ABI de envío kernel con ipc_port_t, ID de 64 bits y flags de 32 bits. Una
variante que pasa un nombre de puerto de 32 bits debe ser rechazada.

## Fuentes seleccionadas y límites

| Fuente relativa a osfmk/ | Alcance |
|---|---|
| kern/coalition.c | Intacta: grupos, referencias, ledgers y envío de notificaciones nativos |
| bank/bank.c | Una corrección de guardas de campo; conserva el gestor de vouchers, ledgers y dependencias reales de proceso/persona |
| kern/mk_sp.c | Intacta: validación de políticas legacy y llamada al proveedor real de modo/prioridad |
| vm/vm_pmap.c | Intacta: iteración UPL y páginas VM nativas |
| vm/vm_debug.c | Intacta: con MACH_VM_DEBUG desactivado, los cuatro endpoints seleccionados devuelven KERN_FAILURE upstream |

bank_internal.h declara bt_rsrc_coal_id solo con CONFIG_COALITIONS &&
CONFIG_TELEMETRY. Dos usos en bank.c solo comprobaban CONFIG_COALITIONS y no
compilaban cuando telemetría estaba desactivada. La serie 0029 alinea esas dos
guardas con el campo existente. No cambia la estructura ni incorpora un ID de
coalición ficticio. El getter conserva su retorno cero cuando no existe ese
dato de telemetría; ese cero no acredita la identidad de una coalición.

Las llamadas a proc_persona_get, proc_pid, proc_uniqueid, persona_get_id y los
demás proveedores siguen siendo reales. Su integración sin BSD permanece
pendiente, incluido el contexto válido que exige el constructor bank. No hay
PID, credencial, persona o entitlement inventados para resolver el enlace.

Los callbacks de debug VM conservan el fallo de la rama desactivada original;
no constituyen inspección VM funcional. Compilar los iteradores UPL tampoco
prueba sus referencias, protecciones o acceso a páginas en hardware.

## Verificación

tools/test_ipc_mig_abi.py valida los 70 headers, sus cuatro roles y el ABI de
ambos headers de coaliciones. tools/test_xnu_coalition_bank.py compara cuatro
fuentes intactas, la preimagen/postimagen de bank.c y el header interno intacto.
Cuatro combinaciones COALITIONS/TELEMETRY deben seleccionar el campo y sus usos
de forma coherente. Cinco cuerpos core de bank conservan su hash nativo.

La fixture de ABI usa headers reales y debe rechazar el acceso al campo ausente
y un callback con parámetro de 32 bits. Experimental comprueba los cinco objetos,
registro STARTUP de bank, imports fuertes de ledger/voucher/notificación y las
dependencias de identidad. Los cuatro retornos de debug VM se comparan con una
referencia compilada desde KERN_FAILURE nativo. Esa referencia es una fixture
aislada y no se selecciona ni enlaza como proveedor del kernel.

El estándar mantiene 13 unidades seleccionadas y comprueba fuentes/ABI sin
seleccionar estos cinco proveedores. No hay entrega de notificación, bank,
coalición, política, UPL, VM o XNU ejecutados por estas pruebas.

```sh
python3 tools/build_xnu_lab.py --layout-compiler <clang-v2> --layout-proof <prueba-api-v2>
python3 tools/test_xnu_coalition_bank.py --build <reporte-base> --output work/coalition-audit-nuevo
python3 tools/test_ipc_mig_abi.py --build <reporte-base> --output work/coalition-mig-abi-nuevo
python3 tools/build_xnu_rpc.py --build <reporte-base>
python3 tools/diagnose_xnu_link.py --build <reporte-base> --rpc <reporte-rpc> --linker <lld-v2> --atlantic-static-proof <prueba-lld-v2> --output work/coalition-link-nuevo
```

En WSL/NTFS añadir --windows-git a ambos builders y usar outputs nuevos.

## Estado de esta revisión

Compilan 153 unidades experimentales y 13 estándar, con cero fallos. Las 148
fuentes previamente seleccionadas, los 57 headers anteriores, los defines y
las 137 constantes genassym se conservan. Se añaden cinco unidades y trece
headers oficiales. Pasan 143/110 comprobaciones de alcance, ABI y objetos,
78 tests Python, los 79 344 contratos de cadenas y el puente de datos con
sanitizadores/ABI nativo. Compilan 42 probes RPC por carril y CFILES conserva 26
para enlace; tres interfaces sin métodos no acreditan servicios.

El enlace estático estricto de **179 objetos** falla con **476 diagnósticos
indefinidos, cero duplicados y ninguna imagen**. Frente a 502, 38 nombres
tienen proveedor nativo y aparecen 12 dependencias nuevas. No desaparecen
referencias sin proveedor por selección. El conjunto coincide con el ensayo
previo independiente de los cinco candidatos. El estándar conserva 39 objetos,
825 diagnósticos y el rechazo upstream de las opciones estáticas, sin imagen.

La [evidencia](../evidence/xnu-coalition-bank-20261024/manifest.json) contiene
332 artefactos con hashes, incluida la generación oficial inicial y el fallo
bank anterior al ajuste. Las pruebas vigentes de Clang API v2 y LLD v2 se
reutilizan por hashes comprobados. No hay notificación, coalición, bank, UPL,
política, IRQ o XNU ejecutado en el teléfono. Los recorridos QEMU anteriores
solo ejecutan el preflight original. Sin acceso al dispositivo, handoff EDK2
o medición de RAM firmware.
