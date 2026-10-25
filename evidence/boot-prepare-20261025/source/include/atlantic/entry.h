/* SPDX-License-Identifier: MIT - shared ARM64 preflight and BSP laboratory ABI. */
#ifndef ATLANTIC_ENTRY_H
#define ATLANTIC_ENTRY_H
#include <stddef.h>
#include <stdint.h>
#define ATL_ENTRY_ABI 1u
struct AtlanticEntryCapture {
    uint64_t x[4], current_el, sctlr, cntfrq, counter, mpidr, initial_daif;
    uint64_t initial_sp, initial_vbar, tcr, ttbr0;
};
struct AtlanticEarlyPlatform {
    uint32_t abi_version, struct_bytes;
    const char *board_id;
    uint64_t readable_ram_start, readable_ram_bytes;
    int (*write)(const char *text);
    void (*finish)(unsigned status);
};
extern const struct AtlanticEarlyPlatform atlantic_early_platform;
extern struct AtlanticEntryCapture atlantic_entry_capture;
void atl_entry_main(const struct AtlanticEntryCapture *capture);
void atl_entry_exception(uint64_t esr, uint64_t elr, uint64_t far);
/* Laboratory BSP provider only; hardware BSPs must establish their own contract. */
unsigned atl_entry_prepare_el1(void);
#if ATL_TEST_BOOT_ARGS
struct AtlanticBootInventory;
struct AtlanticBootPreparation;
/* Test-only BSP probe. Produces a candidate, never places or runs a payload. */
int atl_laboratory_boot_candidate(const struct AtlanticBootInventory *, uint32_t tree_bytes,
                                  struct AtlanticBootPreparation *);
#endif
_Static_assert(sizeof(struct AtlanticEntryCapture) == 112, "assembly capture ABI");
#endif
