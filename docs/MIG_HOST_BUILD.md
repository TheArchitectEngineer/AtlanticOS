# MIG oficial en Linux — adaptación de herramienta, 2026-10-20

Se compiló `migcom` desde Apple `bootstrap_cmds-138`, commit
`c71d2d72f48995baaea76148f61002e5299841de`, con headers Mach del XNU fijado.
El código de Apple permanece sin parches. El listado de C, parser.y y lexxer.l
se contrasta con el target activo del proyecto Xcode oficial. `handler.c` existe
en el repositorio pero no pertenece a ese target; incluir todos los .c produjo
errores de una interfaz antigua. Se usa la lista oficial, sin reparar ese archivo
inactivo ni sustituir MIG por una implementación ajena.

## Separación host / target

`tools/mig-host/include` es un pequeño puente original para **la herramienta
Linux x86_64 LP64**, no un SDK ni headers del kernel AtlanticOS. Usa la libc real
de Linux e incorpora los headers públicos Mach sin mezclar las definiciones
internas de libc Darwin con glibc. Proporciona únicamente los alias de metadata
necesarios: natural unsigned de 32 bits, nombre de puerto de 32 bits, dirección
de usuario de 64 bits y UUID de 16 bytes. Los tipos de mensajes/descriptores
siguen definidos por XNU. Las anotaciones de compilador que no afectan a esos
datos se adaptan solo en este proceso host.

El guard rechaza su inclusión sin `ATL_MIG_HOST_TOOL`, en otras arquitecturas o
con macros de kernel. Una prueba negativa comprueba ese rechazo. El puente no
ofrece funciones VM, IPC, scheduler, seguridad ni hardware que retornen éxito.
No se añaden stubs para conseguir un enlace del kernel.

`tests/mig/abi.c` comprueba con los headers XNU reales los tamaños y offsets de
metadata usados por el generador: cabecera Mach 24 bytes, ID en offset 20,
puerto descriptor 12, OOL/OOL ports/guarded 16, cuerpo 4, NDR 8, natural/boolean
4 y VM offset/user address 8. Estas aserciones son necesarias para esta receta;
no sustituyen pruebas de IPC o ABI ejecutada por un kernel ARM64.

## Qué se comprobó

1. Build del binario host genuino con Bison, Flex y Clang; prueba de versión.
2. Generación de una interfaz sintética con RPC ID 44000 y nombre esperado.
3. Rechazo de sintaxis inválida con exit 1. El log identifica explícitamente
   las salidas negativas esperadas para no confundirlas con un build fallido.
4. Preprocesamiento de `clock.defs`, `mach_host.defs` y `mach_port.defs` del XNU
   oficial con `--target=arm64-apple-darwin`, `__MIG__`, `KERNEL_SERVER=1` y
   `MACH_KERNEL_PRIVATE=1`. **La ruta include del puente host está ausente**.
5. Generación KernelServer de esos tres módulos con `-novouchers -mach_msg2`,
   como las opciones pertinentes del Makefile upstream. Se producen C de usuario
   y servidor, headers y IDs: 20 archivos entre prueba sintética y módulos reales.

No se compilaron esos archivos generados, no se ejecutó un RPC, no se enlazó
XNU y no se accedió al teléfono. El triple Darwin selecciona las definiciones
ARM64 de upstream para el preprocesamiento; no demuestra un SDK Apple instalado
ni implica que la configuración Apple de CPU pueda usarse en el T700.

El intento inicial usando `aarch64-none-elf` falló en el guard de arquitectura
de `mach/machine/thread_state.h`: ese target define `__aarch64__` y los headers
upstream esperan el entorno ARM64 Apple. Se registra la causa; no se retiró el
guard ni se hicieron pasar los headers x86 por interfaces de un target ARM64.

## Reproducción

En Debian/WSL x86_64 con git, clang, bison y flex disponibles, desde la raíz:

```sh
python3 tools/fetch_xnu.py
python3 tools/fetch_mig.py
python3 tools/build_mig.py
```

Si esas fuentes ya están presentes en un checkout Windows situado en /mnt/g,
omitir los fetch y ejecutar `python3 tools/build_mig.py --windows-git` permite
comprobar ambos commits e integridad con git.exe y convertir solo sus
rutas mediante wslpath. Evita recorrer todo el árbol NTFS con Git Linux; el
compilador, parser y generador siguen siendo los binarios Linux reales.

Fuentes descargadas desde los repositorios oficiales fijados en
`dependencies.lock.json`. Las herramientas fetch preservan checkouts existentes
si no coinciden o tienen cambios. La comprobación de build usa la normalización
CRLF de Git explícitamente para admitir checkouts compartidos con Windows; no
resetea ni reescribe fuentes. Clang 19.1.7, Bison y Flex se registran por versión
en la ejecución local. La CI instala sus herramientas explícitamente y vuelve
a generar todo; el reporte identifica la versión usada en cada ejecución.

Salidas privadas en `work/mig-host`: binario, interfaces generadas, log y
`report.json` con hashes, fuentes originales del puente, comandos y versiones.
Los avisos upstream permanecen en sus archivos y APPLE_LICENSE del checkout;
la licencia MIT de las herramientas AtlanticOS no modifica sus licencias.
No se redistribuyen los binarios ni las interfaces upstream en este hito.

Workflow [Official XNU host tools](../.github/workflows/xnu-tools.yml), activado
por cambios relevantes o manualmente. Una ejecución satisfactoria solo acredita
la construcción de esta herramienta y la generación de interfaces.

La evidencia local está en [evidence/mig-host-20261020](../evidence/mig-host-20261020/manifest.json).

## Próximo trabajo de kernel

Resolver el frontend de Make (consultas de memoria/CPU host, xcrun y herramientas
explícitas), headers/generados, perfil ARMv8 apropiado para Cortex-A75/A55,
Mach-O y dependencias de símbolos. `-lcc_kext` y otros proveedores siguen
pendientes. MIG resuelve una dependencia concreta de generación; no elimina
los demás obstáculos descritos en [XNU_BUILD_LOG](XNU_BUILD_LOG.md).
