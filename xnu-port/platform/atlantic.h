/* SPDX-License-Identifier: MIT - Original AtlanticOS/XNU BSP boundary. */
#ifndef _PEXPERT_ATLANTIC_H_
#define _PEXPERT_ATLANTIC_H_
#include <pexpert/pexpert.h>
#include <pexpert/boot.h>
#define ATLANTIC_PE_ABI 1u
#define ATLANTIC_PE_MACHINE_TYPE 0x41544c31u /* ATL1; never an OEM machine ID. */
#define ATLANTIC_PE_TREE_MAX 16384u

/* This descriptor must be supplied by an original, board-selected BSP.
 * There is deliberately no default provider or success fallback.
 * validate_boot_record must prove the image/DRAM/loader ownership and exclusion
 * policy from its retained boot context, not merely check these C fields.
 * validate_tree_mapping must prove the entire span is owned, readable normal
 * memory in the active translation regime (including after a VM slide).
 * initialize_interrupts receives the native CPU argument; NULL on secondary
 * initialization is valid and requires the backend's actual per-CPU context.
 * KERN_SUCCESS means the requested operation has really completed. */
struct atlantic_pe_platform_ops {
    uint32_t abi_version, struct_bytes;
    kern_return_t (*validate_boot_record)(const boot_args *);
    kern_return_t (*validate_tree_mapping)(const void *, vm_size_t);
    kern_return_t (*initialize_interrupts)(void *cpu_data);
};
extern const struct atlantic_pe_platform_ops atlantic_pe_platform;
#endif
