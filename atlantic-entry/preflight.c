/* SPDX-License-Identifier: MIT - diagnostics, not XNU bootstrap. */
#include <atlantic/entry.h>
#include <atlantic/fdt.h>
#include <atlantic/boot_tree.h>
#ifndef ATL_BUILD_ID
#define ATL_BUILD_ID "UNIDENTIFIED"
#endif
struct AtlanticEntryCapture atlantic_entry_capture;
static struct AtlanticBootInventory boot_inventory;
static _Alignas(8) uint8_t xnu_boot_tree[ATL_XNU_TREE_MAX_BYTES];
#if ATL_TEST_BOOT_ARGS
#include <atlantic/boot_prepare.h>
static struct AtlanticBootPreparation boot_candidate;
#endif
extern uint8_t __image_start[], __image_memory_end[];
extern uint8_t __stack_bottom[], __stack_top[], atl_entry_vectors[];

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
    int data_status=atl_boot_inventory(&dt,&boot_inventory);
    if (!data_status) data_status=atl_boot_exclude(&boot_inventory,dtb,dt.total_bytes);
    if (!data_status) data_status=atl_boot_exclude(&boot_inventory,
        (uint64_t)(uintptr_t)__image_start,
        (uint64_t)(uintptr_t)__image_memory_end-(uint64_t)(uintptr_t)__image_start);
    size_t tree_bytes=0;
    if (!data_status) data_status=atl_xnu_boot_tree(&boot_inventory,c->mpidr,c->cntfrq,
        xnu_boot_tree,sizeof(xnu_boot_tree),&tree_bytes);
    if (data_status) { hex("BOOT_DATA_ERROR=",(uint64_t)(int64_t)data_status);line("FAIL:BOOT_DATA\n");finish(1); }
    hex("BOOT_RAM_BANKS=",boot_inventory.ram_count);
    hex("BOOT_RESERVED_RANGES=",boot_inventory.reserved_count);
    hex("BOOT_DECLARED_CPUS=",boot_inventory.cpu_count);
    hex("XNU_TREE_BYTES=",tree_bytes);
    line("PASS:BOOT_DATA_DECLARATIONS_XNU_TREE_ONLY\n");
#if ATL_TEST_BOOT_ARGS
    int prepare_status=atl_laboratory_boot_candidate(&boot_inventory,(uint32_t)tree_bytes,&boot_candidate);
    if (prepare_status) {
        hex("BOOT_PREPARE_ERROR=",(uint64_t)(int64_t)prepare_status);
        line("FAIL:BOOT_PREPARE_CANDIDATE\n"); finish(1);
    }
    hex("CANDIDATE_IMAGE_PA=",boot_candidate.image_pa);
    hex("CANDIDATE_BOOTSTRAP_BYTES=",boot_candidate.bootstrap_bytes);
    hex("CANDIDATE_TOP_OF_DATA=",boot_candidate.top_of_data);
    line("CANDIDATE_BOOT_ARGS_HEX=");
    for (unsigned offset=0;offset<sizeof(boot_candidate.boot_args);offset+=64) {
        static const char digits[]="0123456789abcdef";
        char chunk[129];
        for (unsigned j=0;j<64;++j) {
            uint8_t b=boot_candidate.boot_args[offset+j];
            chunk[2*j]=digits[b>>4]; chunk[2*j+1]=digits[b&15];
        }
        chunk[128]=0; line(chunk);
    }
    line("\nPASS:BOOT_ARGS_CANDIDATE_ONLY\nCANDIDATE_NOT_PLACED_OR_MAPPED\n");
#endif
    if (atl_entry_prepare_el1()!=1) { line("FAIL:EL1_TRANSITION\n"); finish(1); }
    uint64_t el, sctlr, daif, stack, vectors, freq, first, last;
    __asm__ volatile("mrs %0, CurrentEL" : "=r"(el));
    __asm__ volatile("mrs %0, SCTLR_EL1" : "=r"(sctlr));
    __asm__ volatile("mrs %0, DAIF" : "=r"(daif));
    __asm__ volatile("mov %0, sp" : "=r"(stack));
    __asm__ volatile("mrs %0, VBAR_EL1" : "=r"(vectors));
    __asm__ volatile("mrs %0, CNTFRQ_EL0" : "=r"(freq));
    __asm__ volatile("isb; mrs %0, CNTVCT_EL0" : "=r"(first));
    for (unsigned i=0;i<10000;++i) __asm__ volatile("nop");
    __asm__ volatile("isb; mrs %0, CNTVCT_EL0" : "=r"(last));
    hex("EXECUTION_EL=",el>>2); hex("EL1_SCTLR=",sctlr);
    hex("EL1_DAIF=",daif); hex("EL1_SP=",stack); hex("EL1_VBAR=",vectors);
    hex("EL1_COUNTER_DELTA=",last-first);
    if (el!=4 || (sctlr&0x1005) || (daif&0x3c0)!=0x3c0 || (stack&15) ||
        stack<(uint64_t)(uintptr_t)__stack_bottom || stack>(uint64_t)(uintptr_t)__stack_top ||
        vectors!=(uint64_t)(uintptr_t)atl_entry_vectors || freq!=c->cntfrq || last<=first) {
        line("FAIL:EL1_STATE\n"); finish(1);
    }
    line("PASS:EL1_STACK_VECTORS_COUNTER\n");
#if ATL_TEST_EL1_TRAP
    line("TEST:EL1_BRK_EXPECTED\nNO_XNU_BOOT_CLAIM\n");
    __asm__ volatile("brk #0xa71");
    line("FAIL:BRK_RETURNED\n"); finish(1);
#endif
    line("PASS:ENTRY_CAPTURE_DTB_TIMER\nNO_XNU_BOOT_CLAIM\n");
    finish(0);
}
