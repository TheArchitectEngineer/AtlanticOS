# IO — UNIMPLEMENTED en firmware

Capas previstas: block read-only, GPT/FAT32, USB y network. Solo existe
MemoryBlock/GPT primaria en atlantic_core/validation.py para fixtures host.
No hay acceso a discos reales, Linux drivers importados, FAT32, USB Mass Storage,
NIC o Wi-Fi. La ABI no ofrece escrituras de bloques. Implementaciones futuras
serán originales y específicas de BSP, basadas en investigación documentada.
