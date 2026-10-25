/* SPDX-License-Identifier: MIT - original laboratory BSP, NOT Moto G20 MMIO. */
#include <atlantic/entry.h>
static int write_text(const char *text) {
    volatile uint32_t *dr=(volatile uint32_t *)(uintptr_t)0x09000000;
    volatile uint32_t *fr=(volatile uint32_t *)(uintptr_t)0x09000018;
    if (!text) return -1;
    while (*text) {
        unsigned polls=1000000;
        while ((*fr&(1u<<5)) && --polls) { }
        if (!polls) return -1;
        *dr=(uint8_t)*text++;
    }
    return 0;
}
static void finish(unsigned status) {
    uint64_t args[2]={0x20026,status};
    register uint64_t op __asm__("x0")=0x20; /* SYS_EXIT_EXTENDED, no host files. */
    register uint64_t param __asm__("x1")=(uint64_t)(uintptr_t)args;
    __asm__ volatile("hlt #0xf000" : "+r"(op), "+r"(param) : : "memory");
    for (;;) __asm__ volatile("wfe");
}
const struct AtlanticEarlyPlatform atlantic_early_platform={
    .abi_version=ATL_ENTRY_ABI,.struct_bytes=sizeof(struct AtlanticEarlyPlatform),
    .board_id="qemu,virt-laboratory",.readable_ram_start=0x40000000,
    .readable_ram_bytes=128u*1024u*1024u,.write=write_text,.finish=finish
};
