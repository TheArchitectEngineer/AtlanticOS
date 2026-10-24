/* SPDX-License-Identifier: MIT
 * Native header/macro encoding fixtures. No instruction is executed.
 */
#include <kern/assert.h>
#include <kern/trap_telemetry.h>

_Static_assert(MACH_ASSERT_TRAP_CODE == XNU_HARD_TRAP_ASSERT_FAILURE,
    "native assertion and descriptor must agree");
_Static_assert(sizeof(struct kernel_brk_descriptor) == 24, "native BRK descriptor target size");
_Static_assert(__builtin_offsetof(struct kernel_brk_descriptor, base) == 4, "native descriptor base field");
_Static_assert(__builtin_offsetof(struct kernel_brk_descriptor, max) == 6, "native descriptor max field");
_Static_assert(__builtin_offsetof(struct kernel_brk_descriptor, options) == 8, "native descriptor options field");
_Static_assert(__builtin_offsetof(struct kernel_brk_descriptor, handle_breakpoint) == 16, "native descriptor callback field");
_Static_assert(__builtin_strcmp(ML_TRAP_REGISTER_1, "x8") == 0, "assert descriptor register");
_Static_assert(__builtin_strcmp(ML_TRAP_REGISTER_2, "x16") == 0, "assert first value register");
_Static_assert(__builtin_strcmp(ML_TRAP_REGISTER_3, "x17") == 0, "assert second value register");
_Static_assert(CLANG_ARM_TRAP_BOUND_CHK == 0x5519, "native reserved bounds comment");

void atl_builtin_trap(void) { __builtin_trap(); }
void atl_debug_trap(void) { __builtin_debugtrap(); }
void atl_native_assert(void) { release_assert(0); }
void atl_native_assert_values(unsigned long a, unsigned long b)
{
    mach_assert_abort3x(3U, "a", "==", "b", a, b);
}
