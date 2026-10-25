/* SPDX-License-Identifier: MIT - Native XNU data ABI fixture, never kernel code. */
#include <stddef.h>
#include <stdint.h>
#include <pexpert/boot.h>
#include <arm64/proc_reg.h>
#include <arm/pmap.h>
_Static_assert(sizeof(boot_args)==1152 && BOOT_LINE_LENGTH==1024,"native record");
_Static_assert(offsetof(boot_args,Revision)==0 && offsetof(boot_args,Version)==2,"version fields");
_Static_assert(offsetof(boot_args,virtBase)==8 && offsetof(boot_args,physBase)==16,"memory bases");
_Static_assert(offsetof(boot_args,memSize)==24 && offsetof(boot_args,topOfKernelData)==32,"managed memory");
_Static_assert(offsetof(boot_args,Video)==40 && sizeof(Boot_Video)==48,"headless video");
_Static_assert(offsetof(boot_args,machineType)==88 && offsetof(boot_args,deviceTreeP)==96,"tree pointer");
_Static_assert(offsetof(boot_args,deviceTreeLength)==104 && offsetof(boot_args,CommandLine)==108,"tree length and command");
_Static_assert(offsetof(boot_args,bootFlags)==1136 && offsetof(boot_args,memSizeActual)==1144,"tail fields");
_Static_assert(ARM_PGBYTES==4096 && ARM_TT_L2_SIZE==2097152 && BOOTSTRAP_TABLE_SIZE==32768,"native geometry");
_Static_assert(VM_KERNEL_LINK_ADDRESS==UINT64_C(0xfffffff007004000),"native fixed link base");
_Static_assert(TCR_EL1_BOOT==UINT64_C(0x22a5192519),"native bootstrap TCR");
const uint64_t atl_native_boot_geometry[]={ARM_PGSHIFT,ARM_PGBYTES,ARM_TT_L2_SHIFT,
    ARM_TT_L2_SIZE,BOOTSTRAP_TABLE_SIZE,VM_KERNEL_LINK_ADDRESS,TCR_EL1_BOOT};
/* Values independently derived from the public LLD high fixture and the
 * documented 32 MiB candidate window, not generated from the portable record. */
const boot_args atl_native_boot_reference={
    .Revision=kBootArgsRevision2,.Version=kBootArgsVersion2,
    .virtBase=UINT64_C(0xfffffff007000000),.physBase=0x42000000,.memSize=0x2000000,
    .topOfKernelData=0x42024000,.machineType=0x41544c31,
    .deviceTreeP=(void *)UINT64_C(0xfffffff00701c000),.deviceTreeLength=504,
    .CommandLine="-v",.memSizeActual=0x8000000,
};
