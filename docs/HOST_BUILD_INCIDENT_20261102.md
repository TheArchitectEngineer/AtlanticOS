# Objeto de caché puesto en cuarentena — 2026-11-02

Windows Defender informó de la cuarentena de
work/xnu-lab-builds/71c767f7ac383d0d/sched_prim.o: detecciones a las
11:11:14 y 11:12:47, hora de México (UTC−06:00), acción completada a las 11:12:52.
Clasificación registrada: Trojan:Script/Wacatac.C!ml, ThreatID 2147749377.

El objeto era un Mach-O ARM64 compilado de osfmk/kern/sched_prim.c. Su hash
registrado durante la auditoría anterior era
9dbcb171edae85957f6a21830433fc38979982e409dd823eb49e71cb379f7b8b.
Primero falló su lectura con Invalid argument; después el archivo dejó de estar
presente. Los informes anteriores permanecen como evidencia histórica; ese
archivo ya no puede utilizarse como entrada verificable de un enlace nuevo.
La clasificación por sí sola no establece si se trata de un falso positivo.

El primer ensayo de enlace de VM/colas/contadores se detuvo en esa lectura.
Su conteo de undefined no era válido y se descartó. La comparación publicada
usa una reconstrucción completa de la nueva revisión, con port_id distinto
por el patch 0031 y los flags C++ nativos. Cada entrada del enlace se verificó
contra los hashes del informe nuevo. No se recuperó ni reutilizó el objeto
en cuarentena, ni se cambiaron ajustes de Defender, exclusiones o protecciones.
Una lectura o hash fallido debe seguir invalidando cualquier enlace posterior.

Se verificó además el compilador montado contra su hash fijado:
ba90e68369b433c1192809ceacff55904b0a5d1ab6a2bfa4a27e4930e98a1572.
La CI Linux proporciona reproducción independiente del código, con su alcance
de build declarado; no constituye un diagnóstico antimalware. No se ejecutaron
objetos ARM64 en Windows ni se accedió al teléfono durante esta investigación.

Metadata y error original se conservan en
[la evidencia de esta revisión](../evidence/xnu-queue-vm-20261102/manifest.json).
