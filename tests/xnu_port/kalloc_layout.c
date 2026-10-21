/* SPDX-License-Identifier: MIT
 * Compile-time checks of the genuine kalloc macros with our opt-in provider.
 * No allocator is run by this translation unit.
 */
#include <kern/kalloc.h>

struct atl_data { unsigned long count; };
struct atl_ptr { void *pointer; };
struct atl_pair { void *pointer; unsigned long count; };
union atl_overlap { void *pointer; unsigned long count; };

_Static_assert(KALLOC_TYPE_IS_DATA_ONLY(struct atl_data), "data classification");
_Static_assert(!KALLOC_TYPE_IS_DATA_ONLY(struct atl_ptr), "pointer classification");
_Static_assert(!KALLOC_TYPE_HAS_OVERLAPS(struct atl_pair), "separate granules");
_Static_assert(KALLOC_TYPE_HAS_OVERLAPS(union atl_overlap), "overlapping granules");
_Static_assert(KT_SUMMARY_GRANULES(struct atl_pair) == 6, "pointer and data summary");
_Static_assert(__builtin_strcmp(KALLOC_LAYOUT_SIGNATURE(struct atl_pair), "12") == 0,
    "target signature");
KALLOC_TYPE_ASSERT_COMPATIBLE_POINTER((struct atl_pair *)0, struct atl_pair);
KALLOC_TYPE_ASSERT_COMPATIBLE_POINTER((void *)0, struct atl_pair);
_Static_assert(!KALLOC_TYPE_IS_COMPATIBLE_PTR((struct atl_ptr *)0, struct atl_data),
    "incompatible layouts must remain incompatible");

#ifdef ATL_TEST_BAD_POINTER
KALLOC_TYPE_ASSERT_COMPATIBLE_POINTER((struct atl_ptr *)0, struct atl_data);
#endif

KALLOC_TYPE_DEFINE(atlantic_layout_view, struct atl_pair, KT_SHARED_ACCT);
