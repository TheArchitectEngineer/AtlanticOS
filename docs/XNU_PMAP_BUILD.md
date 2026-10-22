# pmap ARM genuino en el perfil de laboratorio — 2026-10-21

El build experimental compila dieciocho objetos con exit 0, incluido
osfmk/arm/pmap/pmap.c. Exige las definiciones reales de pmap_bootstrap,
pmap_enter_options, pmap_page_protect, pmap_ro_zone_memcpy y cpu_ttep. El mapa
de memoria no se ha creado ni ejecutado; estos son objetos sin enlace.

## Patch 0009

El perfil de laboratorio no selecciona el monitor Apple ni su proveedor de
code signing. El patch limita sus imports y APIs a esa selección. Las consultas
Apple de trust caches se omiten del firmware y sus declaraciones quedan
`unavailable`: un consumidor recibe error, sin un verificador que devuelva éxito
o una respuesta falsa de ausencia. Los targets upstream conservan su ruta.

Las dependencias SART/UAT y la llamada sart_bootstrap se excluyen solamente
bajo ATLANTIC_ARM64_LAB. Eso no implementa esos backends ni una IOMMU alternativa.
El laboratorio debe operar sin DMA activo; el BSP G20 aún debe demostrar la
contención de dispositivos y reservas antes de utilizar esta integración.

Se agrega una declaración adelantada del pmap_phys_write_disable ya existente.
Su ruta no PPL llama al pmap_page_protect genuino para quitar escritura de las
asignaciones RO; no se sustituye su cuerpo. Los helpers de lockdown exclusivos
del code signing no seleccionado quedan fuera del firmware. El resto de las
operaciones RO, validación de zonas, modificación de campos y tablas se conserva.

En el panic existente por compresión de una página IOMMU, el laboratorio muestra
el PTE codificado en lugar de invocar el decodificador del backend ausente.
La condición y el panic permanecen; no se trata la página como memoria CPU libre.

## Comprobaciones

Después del build experimental descrito en [XNU_VM_ALLOCATOR_BUILD](XNU_VM_ALLOCATOR_BUILD.md):

```sh
python3 tools/test_pmap_firmware.py --build work/xnu-lab-builds/<id>/report.json
python3 tools/test_pmap_cs_scope.py --build work/xnu-lab-builds/<id>/report.json
```

El primer script aprobó declaraciones y los dos rechazos de APIs no soportadas.
Comprueba el hash del objeto real, sus funciones de texto y la ausencia de
proveedores o referencias a trust caches/AMFI/SART y al decodificador IOMMU.
El segundo repite los tres checks del include real. Ambos registran hashes de
fuentes, fixture, herramienta, build y diagnósticos. En un build estándar el
primer script solo comprueba headers y lo indica: no hay objeto pmap que probar.

Los 18 objetos y checks están en
[xnu-pmap-20261021](../evidence/xnu-pmap-20261021/manifest.json). El inventario
contiene 1.419 nombres externos definidos y 857 sin proveedor, sin nombres
externos repetidos. Cpu_ttep tiene ahora su definición real upstream; eso no
prueba que contenga un TTBR válido en runtime. No se han validado relocaciones,
enlace, TLB, caché, permisos de páginas o uso de DRAM.

## Siguiente cierre

Task.c continúa pendiente por el acoplamiento entre tarea y proceso, no solo por
declaraciones BSD ausentes. El [análisis de vida útil](XNU_TASK_LIFETIME.md)
detalla asignación, referencias y metadata RO que debe conservar la adaptación.
El kernel enlazado, el BSP físico, la recuperación independiente y el handoff
EDK2 siguen sin demostrar. No hay imagen arrancable ni acceso al teléfono en
esta entrega.
