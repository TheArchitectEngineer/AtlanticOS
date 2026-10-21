/* SPDX-License-Identifier: MIT - Original bounded FDT validation. */
#ifndef ATLANTIC_FDT_H
#define ATLANTIC_FDT_H
#include <stddef.h>
#include <stdint.h>
#define ATL_FDT_MAX_BYTES (2u * 1024u * 1024u)
#define ATL_FDT_MAX_DEPTH 32u
enum AtlanticFdtError {
    ATL_FDT_OK = 0, ATL_FDT_BOUNDS = -1, ATL_FDT_FORMAT = -2,
    ATL_FDT_VERSION = -3, ATL_FDT_DEPTH = -4, ATL_FDT_OVERFLOW = -5
};
struct AtlanticFdtView {
    const uint8_t *blob;
    uint32_t total_bytes, struct_offset, struct_bytes, strings_offset, strings_bytes;
    uint32_t reservation_offset, reservation_count;
};
/* Caller must establish that the whole supplied capacity is readable RAM.
 * Validation does not make a physical address safe to dereference. */
int atl_fdt_open(const void *blob, size_t capacity, struct AtlanticFdtView *out);
int atl_fdt_validate_structure(const struct AtlanticFdtView *view);
int atl_fdt_reservation(const struct AtlanticFdtView *view, uint32_t index,
                        uint64_t *start, uint64_t *bytes);
#endif
