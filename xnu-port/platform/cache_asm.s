/* SPDX-License-Identifier: MIT - Original AtlanticOS generic ARM64 adapter.
 * XNU's pmap requires these no-preemption/no-Apple-HID entry points, but this
 * snapshot does not supply their bodies for the generic ARM64 cache path.
 * On a non-Apple profile the native Force routine already performs the real
 * DC CVAC loop and DSB barriers without changing preemption or HID registers.
 * Tail-branch to that actual implementation; never replace it with a return.
 * Callers retain the native owned/mapped range and nonzero-length obligations.
 */
#include <machine/asm.h>
#include <pexpert/arm64/board_config.h>

#if !CONFIG_ATLANTIC_FIRMWARE || !defined(__arm64__)
#error AtlanticOS cache adapter requires the explicit ARM64 firmware profile
#endif
#if defined(APPLE_ARM64_ARCH_FAMILY) || defined(VMAPPLE)
#error AtlanticOS cache adapter requires the generic non-Apple cache provider
#endif

    .text
    .align 2
    .globl EXT(CleanPoC_DcacheRegion_Force_nopreempt)
    .globl EXT(CleanPoC_DcacheRegion_Force_nopreempt_nohid)
LEXT(CleanPoC_DcacheRegion_Force_nopreempt)
LEXT(CleanPoC_DcacheRegion_Force_nopreempt_nohid)
    ARM64_PROLOG
    b EXT(CleanPoC_DcacheRegion_Force)
