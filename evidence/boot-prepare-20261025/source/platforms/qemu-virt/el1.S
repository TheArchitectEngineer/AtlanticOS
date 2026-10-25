/* SPDX-License-Identifier: MIT - original Cortex-A57 laboratory CPU setup.
 * Architectural register values, not a loader or code imported from a port.
 * This is linked only by build_entry's qemu-virt target. No G20 acceptance.
 * Caller already owns its stack/vectors and has MMU and both caches disabled.
 * Continue on that same stack at EL1h; preserve the AAPCS64 callee-saved state.
 */
.text
.balign 16
.global atl_entry_prepare_el1
.type atl_entry_prepare_el1, %function
atl_entry_prepare_el1:
    mrs x0, CurrentEL
    cmp x0, #4
    b.eq .Lel1_setup
    cmp x0, #8
    b.ne .Lreturn_el

    /* Own QEMU EL2: AArch64 EL1, stage 2/traps/IRQ routing disabled. */
    mov x1, #(1 << 31)
    msr HCR_EL2, x1
    mov x1, #3
    msr CNTHCTL_EL2, x1
    msr CNTVOFF_EL2, xzr
    mov x1, #0x33ff          /* Armv8.0 CPTR_EL2 RES1; no FP trap at EL2. */
    msr CPTR_EL2, x1
    msr HSTR_EL2, xzr
    msr VTTBR_EL2, xzr
    mov x1, sp
    msr SP_EL1, x1
    adrp x1, atl_entry_vectors
    add x1, x1, :lo12:atl_entry_vectors
    msr VBAR_EL1, x1
    mov x1, #0x0800
    movk x1, #0x30d0, lsl #16  /* SCTLR_EL1 RES1; M/C/I and endian bits zero. */
    msr SCTLR_EL1, x1
    adr x1, .Lel1_setup
    msr ELR_EL2, x1
    mov x1, #0x3c5          /* D/A/I/F masked, EL1h, little-endian AArch64. */
    msr SPSR_EL2, x1
    isb
    eret

.Lel1_setup:
    /* Never accesses EL2 registers on the direct EL1 path. No MMU enablement. */
    msr DAIFSet, #15
    msr CPACR_EL1, xzr      /* General-register-only image; FP remains disabled. */
    msr TCR_EL1, xzr
    msr TTBR0_EL1, xzr
    msr TTBR1_EL1, xzr
    msr MAIR_EL1, xzr
    msr CONTEXTIDR_EL1, xzr
    msr CNTKCTL_EL1, xzr    /* No user counter/timer access. */
    msr CNTP_CTL_EL0, xzr
    msr CNTV_CTL_EL0, xzr   /* Timers remain disabled; no IRQ test is claimed. */
    dsb sy
    isb
    mrs x0, CurrentEL
.Lreturn_el:
    lsr x0, x0, #2
    ret
.size atl_entry_prepare_el1, .-atl_entry_prepare_el1
