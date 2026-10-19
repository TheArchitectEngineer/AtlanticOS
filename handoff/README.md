# Handoff — adaptadores reales UNIMPLEMENTED

Android: mecanismo OEM probado, recuperación independiente; nunca jump ciego a
boot_a/boot_b o cambio automático de metadata. EDK2: contrato destino explícito,
quiesce, transferencia de RAM/CPU y fin de ejecución XNU en V1. LoadImage y
StartImage existen solo después de inicializar EDK2 real. Los mocks de policy.py
prueban estados/errores, no transferencias de control ARM64.
