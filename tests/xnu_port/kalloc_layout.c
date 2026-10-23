/* SPDX-License-Identifier: MIT
 * Compile-time checks of the genuine kalloc macros with our opt-in provider.
 * No allocator is run by this translation unit.
 */
#include <kern/kalloc.h>
#include <vm/vm_pageout_xnu.h>

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

/* Native ppnum_t is an integer with pointer usage, not a data-only value. */
_Static_assert(!KALLOC_TYPE_IS_DATA_ONLY(ppnum_t), "native ppnum_t pointer usage");
_Static_assert(KT_SUMMARY_GRANULES(ppnum_t) == 2, "physical page number granule");
_Static_assert(__builtin_strcmp(KALLOC_LAYOUT_SIGNATURE(struct upl_page_info), "3") == 0,
    "native UPL physical-page and flag granule");
_Static_assert(!KALLOC_TYPE_IS_DATA_ONLY(struct upl_page_info), "native UPL descriptor is not data-only");
KALLOC_TYPE_VAR_DEFINE(atlantic_upl_layout_view, struct upl, struct upl_page_info, KT_SHARED_ACCT);

_Static_assert(__builtin_types_compatible_p(vm_offset_t, uintptr_t), "address aliases keep their C ABI");
_Static_assert(!KALLOC_TYPE_IS_COMPATIBLE_PTR((uintptr_t *)0, vm_offset_t),
    "address usage must survive C alias identity");
KALLOC_TYPE_ASSERT_COMPATIBLE_POINTER((vm_offset_t *)0, vm_offset_t);

#ifdef ATL_TEST_BAD_ADDRESS_USAGE
KALLOC_TYPE_ASSERT_COMPATIBLE_POINTER((uintptr_t *)0, vm_offset_t);
#endif

#ifdef ATL_TEST_BAD_TRAILING_DATA
KALLOC_TYPE_VAR_DEFINE(atlantic_bad_trailer, struct atl_ptr, struct atl_data, KT_SHARED_ACCT);
#endif
