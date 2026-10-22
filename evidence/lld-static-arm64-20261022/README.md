# Evidencia de herramientas: enlace ARM64 estático

HOST_TESTED, 2026-10-22. LLD oficial 19.1.7 con patch original AtlanticOS.
Construcción desde cache nuevo, 3.901 fuentes verificadas, 32 comandos de
prueba aprobados y tres imágenes fixture auditadas por bytes. Ninguna se ejecutó.

La toolchain LLVM de desarrollo host procede de Debian: versión y hashes del
libLLVM compartido y dependencias en build-report.json. No se declara build
hermético completo de LLVM. No se incluyen los binarios del linker o fixtures.

El intento con 89 objetos XNU/MIG se rechaza por los dos helpers weak legítimos
de Blocks antes del recorrido completo de reubicaciones. No desaparecen por
ello las referencias nativas sin proveedor documentadas anteriormente.

No hay imagen kernel enlazada, ejecución XNU, prueba física, handoff EDK2 ni
RAM residente medida. Android y el teléfono no se tocaron en estas pruebas.

Los hashes y comandos permiten auditar/repetir esta observación host; no
constituyen prueba de arranque. Véase docs/LLD_STATIC_ARM64.md.
