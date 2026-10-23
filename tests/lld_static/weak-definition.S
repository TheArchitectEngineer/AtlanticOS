// SPDX-License-Identifier: MIT
// Build distinct bodies/data so selection can be checked from linked bytes.
#if !defined(SELECTED_RETURN) || !defined(SELECTED_DATA)
#error Both fixture values must be explicit
#endif
.text
.p2align 2
.globl _selected
#ifdef PRIVATE_DEFINITION
.private_extern _selected
#endif
#ifndef STRONG_DEFINITION
.weak_definition _selected
#endif
_selected:
    mov x0, #SELECTED_RETURN
    ret

.section __DATA,__data
.p2align 3
.globl _selected_value
#ifdef PRIVATE_DEFINITION
.private_extern _selected_value
#endif
#ifndef STRONG_DEFINITION
.weak_definition _selected_value
#endif
_selected_value:
    .quad SELECTED_DATA
.subsections_via_symbols
