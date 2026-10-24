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
enum AtlanticFdtEventKind { ATL_FDT_NODE_BEGIN, ATL_FDT_PROPERTY, ATL_FDT_NODE_END };
struct AtlanticFdtEvent {
    enum AtlanticFdtEventKind kind;
    uint32_t depth; /* root is zero, including NODE_END */
    const char *name; /* borrowed, validated NUL-terminated name; NULL at END */
    const uint8_t *value; /* only PROPERTY */
    uint32_t bytes; /* value bytes, excluding structural padding */
};
typedef int (*AtlanticFdtVisitor)(void *context, const struct AtlanticFdtEvent *event);
/* Validate the entire immutable blob before delivering any event. Callback zero
 * continues; any other result stops traversal and is returned verbatim. The
 * caller owns the blob throughout traversal; callbacks must not modify it. */
int atl_fdt_walk(const struct AtlanticFdtView *view, AtlanticFdtVisitor visit, void *context);
#endif
