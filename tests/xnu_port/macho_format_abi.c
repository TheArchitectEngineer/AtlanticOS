/* SPDX-License-Identifier: MIT - Official pinned header ABI, no native execution. */
#include <stddef.h>
#include <mach-o/loader.h>
#include <mach-o/nlist.h>
#include <mach/arm/thread_status.h>
_Static_assert(MH_MAGIC_64==0xfeedfacf && CPU_TYPE_ARM64==0x0100000c,"header profile");
_Static_assert(CPU_SUBTYPE_ARM64_ALL==0 && MH_EXECUTE==2 && MH_NOUNDEFS==1,"static profile");
_Static_assert(sizeof(struct mach_header_64)==32 && offsetof(struct mach_header_64,ncmds)==16,"header");
_Static_assert(sizeof(struct segment_command_64)==72 && offsetof(struct segment_command_64,vmaddr)==24,"segment");
_Static_assert(sizeof(struct section_64)==80 && offsetof(struct section_64,addr)==32,"section");
_Static_assert(sizeof(struct nlist_64)==16 && offsetof(struct nlist_64,n_value)==8,"symbol");
_Static_assert(LC_SEGMENT_64==0x19 && LC_SYMTAB==2 && LC_DYSYMTAB==11,"metadata commands");
_Static_assert(LC_UNIXTHREAD==5 && ARM_THREAD_STATE64==6 && ARM_THREAD_STATE64_COUNT==68,"thread state");
_Static_assert(sizeof(arm_thread_state64_t)==272,"thread bytes");
_Static_assert(offsetof(arm_thread_state64_t,sp)==248 && offsetof(arm_thread_state64_t,pc)==256,"entry and stack fields");
_Static_assert(N_STAB==0xe0 && N_TYPE==14 && N_SECT==14 && N_ABS==2 && N_WEAK_REF==0x40,"symbol types");
_Static_assert(S_NON_LAZY_SYMBOL_POINTERS==6 && S_16BYTE_LITERALS==14,"static section types");
_Static_assert(VM_PROT_READ==1 && VM_PROT_WRITE==2 && VM_PROT_EXECUTE==4,"page permissions");
