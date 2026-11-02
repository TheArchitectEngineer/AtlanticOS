# Revisión de estimación — 2026-11-02

Base: commit `1073f78e9fa3b9ca1f36177eb51050e44c10483d`. El
[informe de avance](../../docs/PROGRESS_ESTIMATE.md) separa estimación de esfuerzo
de puertas de aceptación. Los porcentajes y sus intervalos son juicios de
ingeniería, sin significado estadístico. No miden porcentaje de código terminado
ni probabilidad de arranque. Esta revisión no añade ejecución XNU.

`review.json` liga por SHA-256 los informes publicados de 159 unidades base,
42 probes RPC y enlace de 185 objetos: exit 1, 436 nombres indefinidos, cero
duplicados y ninguna imagen. Incluye las consultas GitHub de tres runs del
commit exacto. Host y carril estándar: success; reconstrucción experimental:
in_progress en la consulta. Son snapshots, no seguimiento de un resultado futuro.

`blocks-runtime-probe.json` conserva el comando, hash de fuente y fallo real
del runtime nativo Blocks; `blocks-runtime-exp.log` contiene su diagnóstico.
Solo se normaliza el prefijo local del workspace a `<ROOT>`. El hash de fuente
corresponde al archivo preparado con finales LF, cotejado con el upstream
mediante lectura de texto que normaliza CRLF. No se produjo objeto del runtime,
no se vació metadata y no se integró el probe. No es una prueba del allocator
ejecutado ni de todos los tipos C++.

`manifest.json` permite verificar los archivos de esta revisión. Los informes
de build previos permanecen en `../xnu-queue-vm-20261102`; no se reescriben.
No se accedió al G20, no se modificaron particiones y no se midió RAM firmware.
