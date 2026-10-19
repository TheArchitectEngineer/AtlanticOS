# Entry ARM64 propio — UNIMPLEMENTED

No se incluye entry con bucle y nombre XNU. Fase 2 debe conservar x0-x3 y registrar
CurrentEL, SCTLR y DTB antes de alterar la máquina; construir desde fuente propia
el contenedor que acepte el bootloader. Ver docs/BOOT_CONTRACT.md. No BootShim,
wrappers binarios externos ni reutilización del contenedor del port UEFI.
