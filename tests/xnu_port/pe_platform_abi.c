/* SPDX-License-Identifier: MIT - Native PE and original BSP ABI checks only. */
#include <stddef.h>
#include <stdint.h>
#include <pexpert/atlantic.h>
/* XNU's arm_vm_init.c declares this locally, rather than in pexpert.h.
 * The verifier checks this declaration against the actual native caller. */
extern void PE_slide_devicetree(vm_offset_t);
_Static_assert(sizeof(boot_args)==1152 && BOOT_LINE_LENGTH==1024,"native boot_args contract");
_Static_assert(offsetof(boot_args,CommandLine)==108,"native command line offset");
_Static_assert(sizeof(struct atlantic_pe_platform_ops)==32,"original BSP descriptor bytes");
_Static_assert(offsetof(struct atlantic_pe_platform_ops,validate_boot_record)==8,"boot callback offset");
_Static_assert(offsetof(struct atlantic_pe_platform_ops,validate_tree_mapping)==16,"mapping callback offset");
_Static_assert(offsetof(struct atlantic_pe_platform_ops,initialize_interrupts)==24,"interrupt callback offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(&PE_init_platform),void (*)(boolean_t,void *)),"native two-phase PE ABI");
_Static_assert(__builtin_types_compatible_p(__typeof__(&PE_slide_devicetree),void (*)(vm_offset_t)),"native tree slide ABI");
_Static_assert(__builtin_types_compatible_p(__typeof__(&PE_register_timebase_callback),void (*)(timebase_callback_func)),"native callback registration ABI");
extern kern_return_t test_boot_record(const boot_args *);
#if ATL_TEST_WRONG_MAPPING_ABI
extern kern_return_t test_tree_mapping(const void *,uint32_t);
#else
extern kern_return_t test_tree_mapping(const void *,vm_size_t);
#endif
#if ATL_TEST_WRONG_IRQ_ABI
extern void test_interrupt_init(void *);
#else
extern kern_return_t test_interrupt_init(void *);
#endif
/* This declaration fixture defines no callback bodies and is never linked into
 * a kernel or hardware test. It only checks the descriptor's native C types. */
const struct atlantic_pe_platform_ops atlantic_pe_platform = {
    ATLANTIC_PE_ABI,sizeof(struct atlantic_pe_platform_ops),
    test_boot_record,test_tree_mapping,test_interrupt_init
};
