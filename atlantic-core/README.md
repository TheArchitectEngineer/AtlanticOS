# Núcleo de política firmware — UNIMPLEMENTED

La especificación ejecutable host está en atlantic_core/ (Python). El módulo C
futuro debe implementar boot-policy, eventos, memory, power, config, diagnostics
y security sobre XNU real, conservando escenarios de aceptación. Python no es
dependencia del firmware ni sustituto del kernel. No hay drivers ocultos aquí.
