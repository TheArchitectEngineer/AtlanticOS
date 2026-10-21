/* SPDX-License-Identifier: MIT - diagnostics, not XNU bootstrap. */
#include <atlantic/entry.h>
#include <atlantic/fdt.h>
#ifndef ATL_BUILD_ID
#define ATL_BUILD_ID "UNIDENTIFIED"
#endif
struct AtlanticEntryCapture atlantic_entry_capture;
extern uint8_t __image_start[], __image_memory_end[];

static void line(const char *text) { (void)atlantic_early_platform.write(text); }
static void hex(const char *key, uint64_t value) {
    char buf[19];
    static const char digits[] = "0123456789ABCDEF";
    buf[0]='0'; buf[1]='x';
    for (unsigned i=0;i<16;++i) buf[2+i]=digits[(value>>((15-i)*4))&15];
    buf[18]=0;
    line(key); line(buf); line("\n");
}
static void finish(unsigned status) {
    atlantic_early_platform.finish(status);
    for (;;) __asm__ volatile("wfe");
}
void atl_entry_exception(uint64_t esr, uint64_t elr, uint64_t far) {
    line("ATLANTIC_ENTRY_EXCEPTION\n");
    hex("ESR=",esr); hex("ELR=",elr); hex("FAR=",far);
    finish(1);
}
void atl_entry_main(const struct AtlanticEntryCapture *c) {
    const struct AtlanticEarlyPlatform *p = &atlantic_early_platform;
    struct AtlanticFdtView dt;
    uint64_t dtb = c->x[0], end;
    if (p->abi_version!=ATL_ENTRY_ABI || p->struct_bytes!=sizeof(*p) || !p->write || !p->finish)
        for (;;) __asm__ volatile("wfe");
    line("ATLANTIC_ENTRY_PREFLIGHT_ONLY\nXNU_NOT_LINKED\n");
    line("BOARD="); line(p->board_id); line("\nBUILD="); line(ATL_BUILD_ID); line("\n");
    hex("INITIAL_EL=",c->current_el>>2); hex("SCTLR=",c->sctlr);
    hex("DTB_PA=",dtb); hex("CNTFRQ=",c->cntfrq); hex("COUNTER=",c->counter);
    hex("ENTRY_OWNED_BYTES=",(uint64_t)(uintptr_t)__image_memory_end-(uint64_t)(uintptr_t)__image_start);
    if (!p->readable_ram_bytes || p->readable_ram_bytes>UINT64_MAX-p->readable_ram_start) {
        line("FAIL:PLATFORM_RAM_BOUNDS\n"); finish(1);
    }
    end=p->readable_ram_start+p->readable_ram_bytes;
    if ((dtb&7) || dtb<p->readable_ram_start || dtb>=end || end-dtb<40) {
        line("FAIL:DTB_ADDRESS\n"); finish(1);
    }
    size_t capacity=(size_t)(end-dtb);
    if (capacity>ATL_FDT_MAX_BYTES) capacity=ATL_FDT_MAX_BYTES;
    if (atl_fdt_open((const void *)(uintptr_t)dtb,capacity,&dt) || atl_fdt_validate_structure(&dt)) {
        line("FAIL:DTB_FORMAT\n"); finish(1);
    }
    hex("DTB_BYTES=",dt.total_bytes);
    hex("DTB_RESERVATIONS=",dt.reservation_count);
    if (!c->cntfrq) { line("FAIL:TIMER_FREQUENCY\n"); finish(1); }
    line("PASS:ENTRY_CAPTURE_DTB_TIMER\nNO_XNU_BOOT_CLAIM\n");
    finish(0);
}
