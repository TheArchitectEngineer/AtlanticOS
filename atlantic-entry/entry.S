/* SPDX-License-Identifier: MIT - Original AArch64 entry, no foreign loader. */
.section .entry, "ax"
.global _image_start
_image_start:
    b atl_entry_start
    nop
    .quad 0x80000
    .quad __image_memory_end - _image_start
    .quad 0
    .quad 0, 0, 0
    .word 0x644d5241
    .word 0
.global atl_entry_start
atl_entry_start:
    mov x19, x0
    mov x20, x1
    mov x21, x2
    mov x22, x3
    mrs x23, CurrentEL
    mrs x24, DAIF
    mov x25, sp
    cmp x23, #4
    b.eq 1f
    cmp x23, #8
    b.ne atl_entry_halt
1:  msr DAIFSet, #15
    msr SPSel, #1
    adrp x4, __stack_top
    add x4, x4, :lo12:__stack_top
    mov sp, x4
    adrp x4, __bss_start
    add x4, x4, :lo12:__bss_start
    adrp x5, __bss_end
    add x5, x5, :lo12:__bss_end
2:  cmp x4, x5
    b.hs 3f
    stp xzr, xzr, [x4], #16
    b 2b
3:  adrp x0, atlantic_entry_capture
    add x0, x0, :lo12:atlantic_entry_capture
    stp x19, x20, [x0, #0]
    stp x21, x22, [x0, #16]
    str x23, [x0, #32]
    str x24, [x0, #72]
    str x25, [x0, #80]
    mrs x4, MPIDR_EL1
    str x4, [x0, #64]
    adrp x6, atl_entry_vectors
    add x6, x6, :lo12:atl_entry_vectors
    cmp x23, #8
    b.eq 4f
    mrs x4, SCTLR_EL1
    mrs x5, VBAR_EL1
    msr VBAR_EL1, x6
    mrs x7, TCR_EL1
    mrs x8, TTBR0_EL1
    b 5f
4:  mrs x4, SCTLR_EL2
    mrs x5, VBAR_EL2
    msr VBAR_EL2, x6
    mrs x7, TCR_EL2
    mrs x8, TTBR0_EL2
5:  isb
    str x4, [x0, #40]
    str x5, [x0, #88]
    str x7, [x0, #96]
    str x8, [x0, #104]
    /* This preflight accepts an MMU-off entry only. Do not disable an unknown map. */
    tbnz x4, #0, atl_entry_halt
    mrs x4, CNTFRQ_EL0
    mrs x5, CNTVCT_EL0
    stp x4, x5, [x0, #48]
    bl atl_entry_main
atl_entry_halt:
    wfe
    b atl_entry_halt

.section .vectors, "ax"
.balign 2048
.global atl_entry_vectors
atl_entry_vectors:
.rept 16
    b atl_entry_trap
    .balign 128
.endr
atl_entry_trap:
    msr DAIFSet, #15
    mrs x3, CurrentEL
    cmp x3, #8
    b.eq 6f
    mrs x0, ESR_EL1
    mrs x1, ELR_EL1
    mrs x2, FAR_EL1
    b 7f
6:  mrs x0, ESR_EL2
    mrs x1, ELR_EL2
    mrs x2, FAR_EL2
7:  bl atl_entry_exception
    b atl_entry_halt
