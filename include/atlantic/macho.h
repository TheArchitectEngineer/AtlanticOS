/* SPDX-License-Identifier: MIT - Original bounded static-image validation. */
#ifndef ATLANTIC_MACHO_H
#define ATLANTIC_MACHO_H
#include <stddef.h>
#include <stdint.h>

/* This is the narrow Atlantic static ARM64 v2 profile, not a general Mach-O
 * loader. These limits are input policies, not measurements of resident RAM. */
#define ATL_MACHO_MAX_BYTES (256u * 1024u * 1024u)
#define ATL_MACHO_PAGE_BYTES 16384u
#define ATL_MACHO_MAX_SEGMENTS 16u
#define ATL_MACHO_MAX_SECTIONS 128u
#define ATL_MACHO_MAX_COMMANDS 64u
#define ATL_MACHO_MAX_SYMBOLS 1048576u

enum AtlanticMachoError {
    ATL_MACHO_OK = 0, ATL_MACHO_BOUNDS = -40, ATL_MACHO_FORMAT = -41,
    ATL_MACHO_UNSUPPORTED = -42, ATL_MACHO_LIMIT = -43,
    ATL_MACHO_LAYOUT = -44, ATL_MACHO_SYMBOL = -45, ATL_MACHO_ENTRY = -46
};
struct AtlanticMachoSegment {
    uint64_t virtual_address, virtual_bytes, mapping_bytes;
    uint64_t file_offset, file_bytes;
    uint32_t protection; /* Mach VM_PROT_READ/WRITE/EXECUTE: 1/2/4. */
    char name[16];      /* Fixed-width bytes, possibly without a terminator. */
};
struct AtlanticMachoPlan {
    uint64_t virtual_base, virtual_span, entry;
    uint32_t segment_count, section_count, symbol_count, command_bytes;
    struct AtlanticMachoSegment segments[ATL_MACHO_MAX_SEGMENTS];
};
/* Caller supplies readable, immutable file bytes and a distinct writable out.
 * All failures leave out and input untouched, including alias rejection.
 * Success describes copy/zero-fill spans and page-rounded mapping extents;
 * it allocates, copies, maps and executes nothing. No heap, MMIO or libc.
 *
 * A plan is NOT a signature, an ownership proof, a physical placement decision,
 * a BSP capability or authorization to execute. The future loader must retain
 * the immutable input, authenticate it, enforce reservations, allocate owned
 * memory, copy/zero it, establish translations/permissions and the XNU ABI.
 * The zero SP in LC_UNIXTHREAD is deliberately not an executable stack. */
int atl_macho_plan(const void *file, size_t bytes, struct AtlanticMachoPlan *out);
#endif
