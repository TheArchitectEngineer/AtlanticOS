/* SPDX-License-Identifier: MIT - Original AtlanticOS tests of genuine XNU ABI. */
#include <pexpert/pexpert.h>
#include <kern/misc_protos.h>
#include <pexpert/atlantic_log.h>

_Static_assert(sizeof(struct AtlanticEarlyLog) == 16432, "fixed owned RAM instance");
_Static_assert(sizeof(struct AtlanticEarlyLogSnapshot) == 48, "snapshot ABI v1");
_Static_assert(sizeof(struct AtlanticEarlyLogRecord) == 1040, "bounded formatter capture");
_Static_assert(sizeof(enum AtlanticEarlyLogStatus) == 4, "native status return ABI");
_Static_assert(__builtin_types_compatible_p(__typeof__(PE_kputc), void (*)(char)), "kputc is a variable");
_Static_assert(__builtin_types_compatible_p(__typeof__(PE_putc), void (*)(char)), "putc is a variable");
_Static_assert(__builtin_types_compatible_p(__typeof__(&kprintf), void (*)(const char *, ...)), "native kprintf");
_Static_assert(__builtin_types_compatible_p(__typeof__(&__doprnt),
    int (*)(const char *, va_list, void (*)(int, void *), void *, int, int)), "native formatter ABI");
#if ATL_TEST_WRONG_PUTC_ABI
void (*atl_bad_putc)(int) = PE_kputc;
#endif
#if ATL_TEST_WRONG_LOG_SNAPSHOT_ABI
int (*atl_bad_snapshot)(void *, unsigned int, struct AtlanticEarlyLogSnapshot *) = atlantic_xnu_log_snapshot;
#endif
