/* SPDX-License-Identifier: MIT - Real XNU string and Mach-O header ABI only. */
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <libkern/kernel_mach_header.h>
_Static_assert(sizeof(size_t)==8 && sizeof(unsigned long)==8,"native ARM64 sizes");
_Static_assert(sizeof(kernel_mach_header_t)==32,"native Mach-O header");
_Static_assert(sizeof(kernel_segment_command_t)==72,"native segment command");
_Static_assert(sizeof(kernel_section_t)==80,"native section record");
_Static_assert(offsetof(kernel_mach_header_t,ncmds)==16,"native load-command count");
_Static_assert(offsetof(kernel_segment_command_t,vmaddr)==24,"native segment VA");
_Static_assert(offsetof(kernel_section_t,addr)==32,"native section VA");
_Static_assert(__builtin_types_compatible_p(__typeof__(&getsegdatafromheader),
    void *(*)(kernel_mach_header_t *,const char *,unsigned long *)),"native Mach-O output width");
#if ATL_TEST_WRONG_COPY_ABI
size_t (*bad_copy)(char *,const char *,uint32_t) = strlcpy;
#endif
#if ATL_TEST_WRONG_MACHO_ABI
void *(*bad_segment)(kernel_mach_header_t *,const char *,uint32_t *) = getsegdatafromheader;
#endif
