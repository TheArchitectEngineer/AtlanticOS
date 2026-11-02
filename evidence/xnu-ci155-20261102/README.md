# Reconstrucción limpia de 155 unidades — 2026-11-02

Run 41374630610, commit 1f2fa529cb1c567f3f405f532017d77ad24f8bfa, success.
Se conserva el metadata remoto, los 27 informes originales, Makefile, link.log,
boot_args candidato y un inventario SHA-256 de toda la descarga. La descarga
completa permanece en work/ci155-41374630610; no se vuelven a publicar todos sus logs.
audit_ci155.py registra las verificaciones realizadas y sus rutas locales.

Coinciden las fuentes de las 155 unidades, los 42 RPC generados y sus headers,
70 headers MIG instalados/roles, 50 headers config, defines y 137 constantes.
Pasan 26 checks de API del compilador y 164 de alcance/ABI/objetos.
Solo 77/155 hashes de objeto son iguales: no se afirma reproducción binaria.
Los binarios de compilador y rutas de trabajo difieren entre WSL y GitHub.

La CI usa LLD upstream, que también rechaza tres opciones estáticas. No reproduce
el LLD estático original local. Sí reproduce los mismos 465 nombres indefinidos,
cero duplicados y ausencia de imagen. El parser Mach-O tiene 45 084 casos en esta
CI; los otros 15 fixtures LLD de la prueba local no se ejecutan en este run.
boot_args conserva 10 038 casos y los 1 152 bytes coincidentes con el ABI nativo.

BUILT_ARM64 aquí solo prueba compilación. No hay ejecución XNU, acceso al G20,
handoff EDK2 ni medición de RAM física. El estado success acredita el alcance
del workflow; no un kernel enlazado ni un arranque.
