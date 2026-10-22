// SPDX-License-Identifier: MIT
// Relocation fixture only. This is not the AtlanticOS or XNU entry point.
.section __TEXT,__text,regular,pure_instructions
.p2align 2
.globl __start
__start:
    bl _helper
    adrp x0, _value@PAGE
    add x0, x0, _value@PAGEOFF
    adrp x1, _zero@PAGE
    add x1, x1, _zero@PAGEOFF
    ldr x2, [x0]
    str x2, [x1]
    adrp x4, _value@GOTPAGE
    ldr x4, [x4, _value@GOTPAGEOFF]
    ret
