# ARM64 común — contrato, no hardware genérico

include/atlantic/platform.h define ABI v1. Cada BSP publica ID, capacidades y
evidencia propia. Direcciones, IRQ, PMIC, GPIO y modos USB no son universales.
El shell G20 compila sin MMIO y devuelve UNSUPPORTED. Entry, vectores, pmap y
reloj físico comunes se investigarán en Fase 2, sin asumir EL2 o CPU Apple.
