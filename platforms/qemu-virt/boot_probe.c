/* SPDX-License-Identifier: MIT - QEMU-only candidate probe; no XNU execution. */
#include <atlantic/entry.h>
#include <atlantic/boot_prepare.h>
#if !ATL_TEST_BOOT_ARGS
#error Only compile this original BSP probe in its explicit laboratory mode
#endif
extern const uint8_t atl_probe_macho_start[], atl_probe_macho_end[];
int atl_laboratory_boot_candidate(const struct AtlanticBootInventory *inventory,
                                  uint32_t tree_bytes, struct AtlanticBootPreparation *out) {
    struct AtlanticBootRequest request={
        .managed_pa=0x42000000,.managed_bytes=0x4000000,
        .tree_bytes=tree_bytes,.retained_bytes=4096,.command="-v",.command_bytes=2,
    };
    size_t bytes=(size_t)((uintptr_t)atl_probe_macho_end-(uintptr_t)atl_probe_macho_start);
    /* QEMU supplies its real DTB at 0x44000000 in this 128 MiB configuration.
     * The 64 MiB candidate crosses it and must fail from the actual inventory. */
    if (atl_xnu_boot_prepare(inventory,atl_probe_macho_start,bytes,&request,out)!=ATL_PREPARE_RESERVED)
        return ATL_PREPARE_PROFILE;
    (void)atlantic_early_platform.write("PASS:BOOT_ARGS_RESERVED_WINDOW_REJECTED\n");
    request.managed_bytes=0x2000000;
    return atl_xnu_boot_prepare(inventory,atl_probe_macho_start,bytes,&request,out);
}
