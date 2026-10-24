# Reproducción remota de API v2 y 100 unidades XNU

GitHub Actions run 39891229141 del commit 49bbae4a31bd66e9391bc3dbad851cdb11a9eef9,
conclusion success. Se reconstruyeron LLVM/Clang y MIG desde fuentes fijadas.
11.996 fuentes del compilador verificadas; 26 checks API aprobados; 100 unidades
XNU, 42 probes RPC y 26 seleccionados para el enlace. 36 checks de alcance/ABI.

Las 137 constantes genassym, defines, fuentes de las 100 unidades e inputs de
la API coinciden con la entrega local. Se validaron los hashes de los inputs
contra blobs del commit exacto; no contra la revisión de desarrollo posterior.
Los binarios de compilador pueden diferir por herramientas/dependencias host:
esto es reproducción de fuente, contrato y ABI, sin afirmar identidad binaria.

El enlace diagnóstico termina con exit 1, sin imagen ni duplicados. Sigue sin
haber XNU ejecutado, arranque físico G20, handoff EDK2 o RAM medida. Esta CI es
de 100 unidades; no acredita el conjunto posterior con SLEH y sus proveedores.
Los objetos y las fuentes RPC completas no se publican en este bundle.
