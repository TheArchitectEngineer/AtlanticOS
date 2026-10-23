// SPDX-License-Identifier: MIT
// Exercises references to the linker-selected definition; not a boot program.
.text
.p2align 2
.globl __start
__start:
    bl _selected
    adrp x4, _selected@GOTPAGE
    ldr x4, [x4, _selected@GOTPAGEOFF]
    blr x4
    adrp x1, _selected_value@PAGE
    add x1, x1, _selected_value@PAGEOFF
    ret

.section __DATA,__data
.p2align 3
.globl _selected_pointer, _selected_value_pointer, _selected_got, _selected_value_got
_selected_pointer:
    .quad _selected
_selected_value_pointer:
    .quad _selected_value
_selected_got:
    .long _selected@GOT - .
_selected_value_got:
    .long _selected_value@GOT - .
.subsections_via_symbols
