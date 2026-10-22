// SPDX-License-Identifier: MIT
.section __TEXT,__text,regular,pure_instructions
.p2align 2
.globl _helper
_helper:
    mov x3, #0x1234
    ret

.section __DATA,__data
.p2align 3
.globl _value, _pointer, _entry_pointer, _delta, _header_pointer, _got_delta
_value:
    .quad 0x1122334455667788
_pointer:
    .quad _value + 8
_entry_pointer:
    .quad __start
_delta:
    .quad _zero - _value
_header_pointer:
    .quad __mh_execute_header
_got_delta:
    .long _value@GOT - .

.section __DATA_CONST,__const
.p2align 3
.globl _readonly
_readonly:
    .quad 0xa1b2c3d4e5f6071

.globl _zero
.zerofill __DATA,__bss,_zero,0x5000,4
