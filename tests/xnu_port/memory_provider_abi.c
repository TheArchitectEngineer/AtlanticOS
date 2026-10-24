/* SPDX-License-Identifier: MIT - Actual native physical-memory call ABI. */
#include <stdint.h>
#include <arm/pmap.h>
#include <arm/caches_internal.h>
#include <libkern/OSAtomic.h>
_Static_assert(sizeof(vm_offset_t)==8 && sizeof(size_t)==8,"native ARM64 range width");
_Static_assert(__builtin_types_compatible_p(__typeof__(&CleanPoC_DcacheRegion_Force_nopreempt_nohid),
               void (*)(vm_offset_t,size_t)),"native pmap force-cache ABI");
_Static_assert(__builtin_types_compatible_p(__typeof__(&OSCompareAndSwap64),
               Boolean (*)(UInt64,UInt64,volatile UInt64 *)),"native atomic compare/swap ABI");
#if ATL_TEST_TRUNCATED_RANGE
void (*atlantic_bad_range)(uint32_t,uint32_t) = CleanPoC_DcacheRegion_Force_nopreempt_nohid;
#endif
