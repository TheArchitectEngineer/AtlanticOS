/* SPDX-License-Identifier: MIT - Original typed boot-data bridge. */
#ifndef ATLANTIC_BOOT_TREE_H
#define ATLANTIC_BOOT_TREE_H
#include <atlantic/fdt.h>
#define ATL_BOOT_MAX_RAM 16u
#define ATL_BOOT_MAX_RESERVED 64u
#define ATL_BOOT_MAX_CPUS 32u
#define ATL_XNU_TREE_MAX_BYTES 16384u
enum AtlanticBootTreeError {
    ATL_BOOT_SCHEMA = -20, ATL_BOOT_LIMIT = -21, ATL_BOOT_DYNAMIC_RESERVATION = -22,
    ATL_BOOT_NO_RAM = -23, ATL_BOOT_AMBIGUOUS = -24, ATL_BOOT_NOT_CONTIGUOUS = -25,
    ATL_BOOT_CPU = -26, ATL_BOOT_BUFFER = -27
};
struct AtlanticPhysicalRange { uint64_t start, bytes; };
struct AtlanticBootInventory {
    struct AtlanticPhysicalRange ram[ATL_BOOT_MAX_RAM], reserved[ATL_BOOT_MAX_RESERVED];
    uint64_t cpu_affinity[ATL_BOOT_MAX_CPUS];
    uint32_t ram_count, reserved_count, cpu_count;
};
/* Declarations only: this does not validate physical RAM or allocate it. Failure
 * clears a valid output; overlapping input/output arguments are rejected and
 * left untouched. Dynamic reserved-memory must be resolved by the loader. */
int atl_boot_inventory(const struct AtlanticFdtView *view, struct AtlanticBootInventory *out);
/* Add loader/image/DTB/framebuffer ownership without dropping FDT reservations.
 * The supplied range must be wholly contained in declared RAM. */
int atl_boot_exclude(struct AtlanticBootInventory *inventory, uint64_t start, uint64_t bytes);
/* Produce only the native XNU bootstrap tree for the observed primary CPU.
 * It contains /chosen DRAM metadata, /defaults, and /cpus/cpu. It does not
 * construct boot_args, peripheral bindings, page tables, or an allocator map.
 * All original FDT declarations/reservations remain in the separate inventory.
 * Output must be 8-byte aligned and distinct from inputs and used. On failure
 * *used=0 unless used aliases an argument (all arguments then stay untouched).
 * No output bytes are written until all checks pass. No heap or MMIO. */
int atl_xnu_boot_tree(const struct AtlanticBootInventory *inventory,
                      uint64_t observed_mpidr, uint64_t observed_cntfrq,
                      void *output, size_t capacity, size_t *used);
#endif
