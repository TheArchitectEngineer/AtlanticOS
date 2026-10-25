/* SPDX-License-Identifier: MIT - Original native-boot candidate preparation. */
#ifndef ATLANTIC_BOOT_PREPARE_H
#define ATLANTIC_BOOT_PREPARE_H
#include <atlantic/boot_tree.h>
#include <atlantic/macho.h>

/* Current pinned XNU profile: hardware 4 KiB, L2 2 MiB, T0/T1 39 bits.
 * A new kernel profile needs its own ABI proof; none of this detects a CPU. */
#define ATL_XNU_BOOT_RECORD_BYTES 1152u
#define ATL_XNU_BOOT_COMMAND_BYTES 1024u
#define ATL_XNU_BOOT_BLOCK_BYTES 2097152u
#define ATL_XNU_BOOT_AUX_PAGE_BYTES 16384u
#define ATL_XNU_BOOT_LINK_BASE UINT64_C(0xfffffff007004000)
#define ATL_XNU_BOOT_MACHINE_TYPE 0x41544c31u
enum AtlanticBootPrepareError {
    ATL_PREPARE_ARGUMENT = -60, ATL_PREPARE_MEMORY = -61,
    ATL_PREPARE_RESERVED = -62, ATL_PREPARE_PROFILE = -63,
    ATL_PREPARE_SPACE = -64, ATL_PREPARE_COMMAND = -65
};
struct AtlanticBootRequest {
    uint64_t managed_pa, managed_bytes;
    uint32_t tree_bytes, retained_bytes; /* Actual tree size; retained capacity. */
    const char *command; /* Readable span; command_bytes excludes the final NUL. */
    size_t command_bytes;
};
struct AtlanticBootPreparation {
    uint64_t managed_pa, managed_bytes, dram_pa, dram_bytes;
    uint64_t virtual_base, image_pa, image_va, image_bytes, entry_pa, entry_va;
    uint64_t bootstrap_pa, bootstrap_va, bootstrap_bytes;
    uint64_t context_pa, context_bytes, tree_pa, tree_va, boot_args_pa, top_of_data;
    uint32_t tree_bytes, bootstrap_table_pages;
    uint8_t boot_args[ATL_XNU_BOOT_RECORD_BYTES];
};
/* Validate immutable Mach-O bytes again; select no physical memory implicitly.
 * The explicit managed window must be within one declared RAM bank, exclude
 * every reservation, and satisfy this native bootstrap's actual block reach.
 * Context/tree/boot_args are placed after the whole image, before top_of_data.
 *
 * Success emits a CANDIDATE wire boot_args with a future KVA tree pointer.
 * It does not allocate/copy/map memory, construct the retained context, verify
 * the tree contents or signature, grant ownership, or execute any image.
 * BSP proof of the complete runtime map and native early-allocation coverage
 * remains mandatory. These are declarations/plans, not measured physical RAM.
 * No heap, libc or MMIO. Failure leaves all arguments untouched. Out must be a
 * distinct writable object; input spans must remain readable and immutable. */
int atl_xnu_boot_prepare(const struct AtlanticBootInventory *inventory,
                         const void *image, size_t image_bytes,
                         const struct AtlanticBootRequest *request,
                         struct AtlanticBootPreparation *out);
#endif
