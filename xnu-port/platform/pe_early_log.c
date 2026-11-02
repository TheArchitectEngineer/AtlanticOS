/* SPDX-License-Identifier: MIT - Original AtlanticOS platform diagnostics.
 * XNU's genuine __doprnt remains the formatter, including its log policy.
 * This transport retains bytes in owned kernel BSS. No serial, video, IRQ,
 * input, os_log service or native console initialization is claimed/provided.
 */
#include <pexpert/pexpert.h>
#include <kern/misc_protos.h>
#include <pexpert/atlantic_log.h>
#include <libkern/section_keywords.h>

#if !CONFIG_ATLANTIC_FIRMWARE || !defined(__arm64__)
#error AtlanticOS RAM diagnostics require the explicit ARM64 firmware profile
#endif
#if defined(MACH_BSD) || defined(IOKIT)
#error AtlanticOS RAM diagnostics do not implement the BSD or IOKit log service
#endif
#if CONFIG_NO_KPRINTF_STRINGS
#undef kprintf
#endif

static struct AtlanticEarlyLog boot_log;

static void
memory_putc(char character)
{
    (void)atl_early_log_append(&boot_log, &character, 1, 0);
}

typedef void (*atlantic_putc_t)(char);
SECURITY_READ_ONLY_LATE(atlantic_putc_t) PE_kputc = memory_putc;
SECURITY_READ_ONLY_LATE(atlantic_putc_t) PE_putc = memory_putc;

__attribute__((noinline)) void
kprintf(const char *format, ...)
{
    struct AtlanticEarlyLogRecord record = { 0 };
    va_list arguments;
    va_start(arguments, format);
    /* Formatting occurs outside the gate, so recursive formatting cannot
     * retain the gate. Preserve native kprintf's radix and is_log semantics. */
    __doprnt(format, arguments, atl_early_log_capture, &record, 16, TRUE);
    va_end(arguments);
    (void)atl_early_log_append(&boot_log, record.data, record.bytes, record.truncated_bytes);
}

enum AtlanticEarlyLogStatus
atlantic_xnu_log_snapshot(void *destination, size_t capacity,
    struct AtlanticEarlyLogSnapshot *metadata)
{
    return atl_early_log_snapshot(&boot_log, destination, capacity, metadata);
}
