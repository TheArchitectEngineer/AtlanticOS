/* SPDX-License-Identifier: MIT - Embed our own linked assembler fixture only. */
.section .rodata.boot_probe,"a",%progbits
.balign 8
.global atl_probe_macho_start
.global atl_probe_macho_end
atl_probe_macho_start:
.incbin "evidence/static-image-plan-20261025/lld-fixtures/high.macho"
atl_probe_macho_end:
.section .note.GNU-stack,"",%progbits
