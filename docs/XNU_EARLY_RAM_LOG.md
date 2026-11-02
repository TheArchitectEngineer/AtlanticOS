# Diagnóstico temprano original en RAM — 2026-11-02

El patch 0030 añade cuatro archivos nuevos, sin modificar fuentes nativas:
el transporte portable early_log.c/.h, atlantic_log.h y el adaptador original
pe_early_log.c. Este último se integra como osfmk/kern/atlantic_early_log.c.
Se amplía el conjunto experimental a **157 unidades**; el estándar conserva
13 y compila ambos componentes nuevos como probes aislados.

La regresión completa pasa **178/150 checks** de alcance/ABI/objetos. El enlace
estricto de **183 objetos** conserva **463 nombres indefinidos**, cero duplicados,
exit 1 y ninguna imagen. Se resuelven exactamente kprintf y PE_kputc, sin nuevas
dependencias pendientes. PE_putc es una definición adicional que aún no estaba
entre los nombres requeridos; no se cuenta como un tercer símbolo resuelto.
Se conservan los hashes de las 155 fuentes anteriores, 137 constantes de layout
y 70 headers MIG; 42 probes RPC compilados, 26 seleccionados por CFILES.

## Contrato y comportamiento

Un buffer circular propio retiene hasta 16 384 bytes. Su instancia ocupa
16 432 bytes de BSS, incluidos estado y contadores; esto es tamaño de un objeto,
no medición de RAM residente. La captura por llamada kprintf tiene capacidad
de 1 024 bytes y un contexto C de 1 040 bytes, más el frame/va_list/formateador
que determine la compilación. La contabilidad física deberá incluir todo ello.

kprintf llama al **__doprnt auténtico de XNU**, conservando radix 16 e is_log=TRUE.
osfmk/kern/printf.c permanece íntegro y seleccionado. Se almacena el prefijo de
1 024 bytes y se cuenta el resto como truncado. La capacidad acotada no establece
un tiempo máximo de formateo: XNU sigue recorriendo el formato y los argumentos,
que deben ser válidos y pertenecer a llamadas confiables del núcleo. Se conserva
la política nativa de ocultación de punteros, dependiente de la configuración;
el perfil DEVELOPMENT no promete ocultarlos.

El formateo se hace fuera del gate. Append y snapshot intentan un único CAS débil
de 32 bits con acquire; una contención o fallo espurio devuelve BUSY y marca
contention_seen. No hay spin, esperas, cambios de IRQ, asignaciones ni drenado.
La marca usa un store atómico; no se introduce un contador de pérdidas con
un bucle de incremento atómico. Los contadores protegidos registran mensajes
aceptados, bytes aceptados/sobrescritos y truncados; aritmética módulo 2^64.

Un append no se intercala con otro append o snapshot aceptado. El almacenamiento
es de bytes, sin framing ni terminador añadido: el overwrite puede cortar el
principio de un mensaje antiguo. Snapshot copia los bytes retenidos en orden
y metadata ABI v1 bajo el mismo gate. Una capacidad insuficiente o error deja
los outputs intactos. Las funciones rechazan solapamientos, desbordamientos y
alineación inválida; el caller sigue siendo responsable de mapear/probar los
spans legibles/escribibles. Esas comprobaciones no conceden propiedad de RAM.

## Relación con XNU y con el BSP

PE_kputc y PE_putc son **variables de puntero a función**, conforme al header
nativo. Sus relocations apuntan a memory_putc, que realmente guarda un byte.
atlantic_xnu_log_snapshot permite extraer una copia mediante buffers propios.
No existe todavía un mecanismo físico del G20 para exportarla.

Es un transporte de diagnóstico privado del perfil firmware, con captura RAM
activa. No implementa el forwarding os_log del Platform Expert Apple ni sus
controles de salida serie. Tampoco sustituye el ring de consola nativo de
osfmk/console/serial_console.c. PE_init_printf, console_init, entrada, UART,
framebuffer y los servicios de logging que aún carecen de proveedor conservan
sus dependencias pendientes. No se añaden funciones vacías de inicialización.

El adaptador usa el contexto de headers del núcleo para consumir misc_protos.h.
Los prototipos privados de PE declaran printf con retorno void, frente al int
del núcleo; mezclar ambos contextos se rechazó en el preflight. La solución
mantiene los headers auténticos y compila el adaptador en su contexto core.
No se copia pe_kprintf.c como plataforma AtlanticOS.

El buffer exige **RAM normal/shareable, mapeada y con exclusive accesses
operativos**, BSS inicializada y stack válido. No se enlaza al preflight MMU-off
actual. Los dos objetos nuevos usan -mstrict-align y -mno-outline-atomics; no se
desactivan checks de alineación del CPU. Las rutas nativas de start.s preparan
MMU antes de arm_init; falta demostrar que nuestra futura integración satisface
ese contrato. Si un CPU se detiene sosteniendo el gate, snapshot devuelve BUSY:
no se promete recuperar mensajes en cualquier panic ni persistencia tras reset.

## Verificación realizada

Pasan 14 comprobaciones nativas experimentales y 16 estándar; las dos extras
son compilaciones aisladas. Se verifican tipos reales de __doprnt/kprintf y
punteros PE, dos rechazos ABI, los cuatro archivos contra su lock, dependencias
fuertes, relocations del formateador/transporte, punteros inicializados y BSS.
El IR conserva 16/TRUE. Los objetos emiten LDAXR/STXR/STLR y no contienen una
rama que reintente el gate; mutar la rama a un retry hace fallar el auditor.
No se importan helpers atómicos, UART, MMIO o IRQ en los componentes nuevos.
El adaptador conserva la dependencia real bzero, ya provista por XNU nativo.

Las pruebas host contrastan 6 000 registros con un modelo independiente y
16 000 intentos concurrentes de cuatro escritores y un lector. Comprueban
contenido, orden por escritor, coherencia de contadores, wraps, truncaciones,
aliasing, buffers pequeños, errores y contención. Pasan ASan/UBSan en ambas
lanes y un ejecutable separado con ThreadSanitizer en la experimental. El número
de asserts y de BUSY varía con la planificación; no se presenta como una cantidad
fija de contratos independientes.

```sh
# Linux/WSL, desde la raíz; usar una carpeta de salida nueva.
python3 tools/test_early_log.py --sanitize --output work/early-log-host-new
python3 tools/test_early_log.py --sanitize --thread-sanitize \
  --xnu-build work/xnu-lab-builds/<id>/report.json --output work/early-log-native-new
```

El formatter nativo, este adaptador ARM64 y XNU **no se han ejecutado**. Los tests
host solo ejecutan el transporte/capturador original. Las pruebas físicas de
T08 y la exportación requieren imagen XNU enlazada, memoria/BSP/canal verificados
y T01/T04 aprobadas. El handoff EDK2 y la RAM total siguen sin demostrarse.

Evidencia local: [early-ram-log-20261102](../evidence/early-ram-log-20261102/manifest.json).
La CI limpia anterior reproduce 155 unidades; no se atribuye a ese run esta
ampliación de dos unidades originales.
