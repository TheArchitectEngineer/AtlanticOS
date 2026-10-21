# Desconocidos priorizados

| Prioridad | Desconocido | Experimento / criterio de cierre |
|---|---|---|
| P0 | Integridad stock de la variante ya identificada | T00 observa XT2128-1/RTAS31.68-66-3, unlocked/orange; faltan hashes de firmware exacto, sin PII |
| P0 | Recuperación Android realmente independiente | Recorrido OEM por comandos reproducido; T01 por botones y retorno tras payload no probados. T02: metadata de slots vacía |
| P0 | Vía temporal aceptada por OEM, header/compresión | T03/T04; formato y mecanismo demostrados; BLOCKED si no existe |
| P0 | Toolchain XNU y librerías no resueltas | Headers/assym/MIG; grafo de símbolos; clasificar -lcc_kext y seguridad |
| P0 | EL inicial / transición EL2→EL1, DT y carveouts | T05; registros capturados con entry original y rangos validados |
| P1 | Logging temprano y fallback sin framebuffer | Canal real identificado, trazas verificables sin MMIO especulativo |
| P1 | Timer, GIC, grupos seguros y CPU features | T06; CNTFRQ y IRQ real, no flags VMAPPLE heredados |
| P1 | Mach VM/allocator/scheduler mínimos y RAM | T08/T09; upstream ejecutado con transición operativa y mapa completo |
| P1 | Botones PMIC/GPIO y reset/off | T06/T07; driver original, secuencia documentada y retorno stock |
| P2 | Semántica SD CMD17 bit1 readback | Estudiar fuente nativa Motorola y comparar con evidencia; no concluir DMA roto |
| P2 | Read-only SD, FAT32 y rendimiento | T10; bytes exactos, hashes, límites y lectura sostenida |
| P2 | ABI destino EDK2 y recursos supervivientes | T12; DMA parado, ownership, no callbacks XNU residentes |
| P3 | MUSB Bulk, NIC USB-C y pila IP | T11; adaptador identificado y paquetes; después RFB seguro |
| P3 | Persistencia segura de settings / firmas | Formato canónico, biblioteca auditada, vectores y recuperación independiente |
| P4 | Wi-Fi, interno eMMC/UFS, segunda placa | Estudio de buses/firmware/licencias y BSP separados con pruebas |

Riesgos: no hay garantía de boot temporal ni de cierre de build público XNU.
Un teléfono nuevo no elimina restricciones OEM. Mantener UNKNOWN/BLOCKED donde
corresponda en vez de convertir objetivos en capacidades anunciadas.
