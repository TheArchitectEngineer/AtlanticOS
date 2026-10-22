# Reproducción independiente del compilador y doce objetos — 2026-10-21

Run GitHub Actions 39626520147, commit 7c9eaf2: success. La receta pública descargó
LLVM oficial fijado, verificó/aplicó la extensión original, construyó el compilador,
pasó 18 checks, construyó MIG y compiló doce unidades genuinas XNU sin enlace.

La comparación con el reporte local concuerda en port_id, inputs y 137 constantes
del target. Cada ejecución vincula su propio hash de compilador con su prueba API.
No se exige ni se afirma identidad binaria entre los objetos de ambos entornos.
El reporte adicional local acredita solo preparación pública de 11.996 fuentes.

Se conservan reportes y estado final descargado. Los logs completos del run están
en GitHub sujetos a su retención. No se publican ejecutables LLVM ni objetos XNU.
No se ejecutó XNU, no hubo pruebas físicas ni acceso al teléfono.
