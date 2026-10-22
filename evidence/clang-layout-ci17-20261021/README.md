# Reproducción limpia CI de 17 unidades — 2026-10-21

La ejecución 39700921227 aprobó el commit 2b13d0d en Ubuntu, reconstruyendo LLVM
19.1.7 con la API original AtlanticOS, sus 18 checks y MIG oficial. Compiló las
17 unidades genuinas de aquella revisión, sin enlace o ejecución XNU. Se
verificaron 11.996 archivos de fuentes del toolchain.

El port_id, hashes de los 17 archivos XNU y las 137 constantes target coinciden
con el build local histórico. No se afirma identidad byte a byte de objetos.
Esto reproduce el estado de 17 unidades, no el conjunto actual de 39 ni un BSP.
El reporte local histórico también conservó dos probes fallidos fuera de ese
conjunto; la CI normal de 17 no los contaba ni los compiló.

Los cuatro reportes se conservan tal como se descargaron del artefacto
experimental-layout-and-xnu-metadata, id 12394962622. La fuente y comandos están
fijados por commit y hashes; no se publica un binario de compilador o kernel.
La aprobación de GitHub no acredita arranque, RAM física o hardware G20.
