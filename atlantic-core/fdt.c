/* SPDX-License-Identifier: MIT - Original implementation, no libfdt source copied. */
#include <atlantic/fdt.h>

static uint32_t be32(const uint8_t *p) {
    return (uint32_t)p[0]<<24 | (uint32_t)p[1]<<16 | (uint32_t)p[2]<<8 | p[3];
}
static uint64_t be64(const uint8_t *p) { return (uint64_t)be32(p)<<32 | be32(p+4); }
static int range(uint32_t at, uint32_t bytes, uint32_t total) {
    return at <= total && bytes <= total-at;
}
static int overlap(uint32_t a, uint32_t an, uint32_t b, uint32_t bn) {
    return an && bn && a < b+bn && b < a+an;
}
int atl_fdt_open(const void *blob, size_t capacity, struct AtlanticFdtView *out) {
    struct AtlanticFdtView v = {0};
    const uint8_t *p = blob;
    uint32_t cursor;
    if (!p || !out || capacity < 40) return ATL_FDT_BOUNDS;
    *out = v;
    if (be32(p) != 0xd00dfeedu) return ATL_FDT_FORMAT;
    v.blob = p; v.total_bytes = be32(p+4);
    if (v.total_bytes < 40 || v.total_bytes > capacity || v.total_bytes > ATL_FDT_MAX_BYTES)
        return ATL_FDT_BOUNDS;
    if (be32(p+20) != 17 || be32(p+24) > 17) return ATL_FDT_VERSION;
    v.struct_offset = be32(p+8); v.strings_offset = be32(p+12);
    v.reservation_offset = be32(p+16);
    v.strings_bytes = be32(p+32); v.struct_bytes = be32(p+36);
    if (v.struct_offset < 40 || (v.struct_offset & 3) || !v.struct_bytes || (v.struct_bytes & 3) ||
        v.strings_offset < 40 || v.reservation_offset < 40 || (v.reservation_offset & 7) ||
        !range(v.struct_offset,v.struct_bytes,v.total_bytes) ||
        !range(v.strings_offset,v.strings_bytes,v.total_bytes) ||
        overlap(v.struct_offset,v.struct_bytes,v.strings_offset,v.strings_bytes))
        return ATL_FDT_BOUNDS;
    cursor = v.reservation_offset;
    for (;;) {
        uint64_t start, size;
        if (!range(cursor,16,v.total_bytes) || overlap(cursor,16,v.struct_offset,v.struct_bytes) ||
            overlap(cursor,16,v.strings_offset,v.strings_bytes)) return ATL_FDT_BOUNDS;
        start = be64(p+cursor); size = be64(p+cursor+8);
        if (start == 0 && size == 0) break;
        if (!size || size > UINT64_MAX-start) return ATL_FDT_OVERFLOW;
        ++v.reservation_count;
        cursor += 16;
    }
    *out = v;
    return ATL_FDT_OK;
}

int atl_fdt_reservation(const struct AtlanticFdtView *v, uint32_t index,
                        uint64_t *start, uint64_t *bytes) {
    const uint8_t *p;
    uint64_t offset;
    if (!v || !v->blob || !start || !bytes || index >= v->reservation_count)
        return ATL_FDT_BOUNDS;
    offset = (uint64_t)v->reservation_offset+(uint64_t)index*16;
    if (offset > UINT32_MAX || !range((uint32_t)offset,16,v->total_bytes)) return ATL_FDT_BOUNDS;
    p = v->blob+(uint32_t)offset;
    *start = be64(p); *bytes = be64(p+8);
    return ATL_FDT_OK;
}

int atl_fdt_validate_structure(const struct AtlanticFdtView *v) {
    uint32_t at = 0, depth = 0, root_seen = 0, root_closed = 0;
    uint8_t child_seen[ATL_FDT_MAX_DEPTH] = {0};
    const uint8_t *p;
    if (!v || !v->blob || !range(v->struct_offset,v->struct_bytes,v->total_bytes) ||
        !range(v->strings_offset,v->strings_bytes,v->total_bytes)) return ATL_FDT_BOUNDS;
    p = v->blob+v->struct_offset;
    while (range(at,4,v->struct_bytes)) {
        uint32_t token = be32(p+at);
        at += 4;
        if (token == 1) { /* BEGIN_NODE */
            uint32_t name_start = at;
            if (root_closed) return ATL_FDT_FORMAT;
            if (depth == ATL_FDT_MAX_DEPTH) return ATL_FDT_DEPTH;
            while (at < v->struct_bytes && p[at]) {
                if (p[at] == '/' || at-name_start >= 255) return ATL_FDT_FORMAT;
                ++at;
            }
            if (at == v->struct_bytes) return ATL_FDT_BOUNDS;
            if (!depth) {
                if (root_seen || at != name_start) return ATL_FDT_FORMAT;
                root_seen = 1;
            } else child_seen[depth-1] = 1;
            ++at;
            if (at > UINT32_MAX-3) return ATL_FDT_OVERFLOW;
            at = (at+3)&~3u;
            if (at > v->struct_bytes) return ATL_FDT_BOUNDS;
            child_seen[depth++] = 0;
        } else if (token == 2) { /* END_NODE */
            if (!depth) return ATL_FDT_FORMAT;
            if (--depth == 0) root_closed = 1;
        } else if (token == 3) { /* PROP */
            uint32_t bytes, name, end;
            if (!depth || child_seen[depth-1] || !range(at,8,v->struct_bytes)) return ATL_FDT_FORMAT;
            bytes = be32(p+at); name = be32(p+at+4); at += 8;
            if (name >= v->strings_bytes || !range(at,bytes,v->struct_bytes)) return ATL_FDT_BOUNDS;
            end = name;
            while (end < v->strings_bytes && v->blob[v->strings_offset+end]) ++end;
            if (end == v->strings_bytes || end == name) return ATL_FDT_FORMAT;
            at += bytes;
            if (at > UINT32_MAX-3) return ATL_FDT_OVERFLOW;
            at = (at+3)&~3u;
            if (at > v->struct_bytes) return ATL_FDT_BOUNDS;
        } else if (token == 4) { /* NOP */
            continue;
        } else if (token == 9) { /* END */
            if (depth || !root_seen || !root_closed) return ATL_FDT_FORMAT;
            while (at < v->struct_bytes) if (p[at++]) return ATL_FDT_FORMAT;
            return ATL_FDT_OK;
        } else return ATL_FDT_FORMAT;
    }
    return ATL_FDT_FORMAT;
}

int atl_fdt_walk(const struct AtlanticFdtView *v, AtlanticFdtVisitor visit, void *context) {
    uint32_t at = 0, depth = 0;
    int status;
    if (!visit) return ATL_FDT_BOUNDS;
    status = atl_fdt_validate_structure(v);
    if (status) return status;
    const uint8_t *p = v->blob + v->struct_offset;
    while (at < v->struct_bytes) {
        struct AtlanticFdtEvent e = {0};
        uint32_t token = be32(p + at);
        at += 4;
        if (token == 1) {
            e.kind = ATL_FDT_NODE_BEGIN; e.depth = depth++;
            e.name = (const char *)(p + at);
            while (p[at]) ++at;
            at = (at + 4) & ~3u;
        } else if (token == 2) {
            e.kind = ATL_FDT_NODE_END; e.depth = --depth;
        } else if (token == 3) {
            e.kind = ATL_FDT_PROPERTY; e.depth = depth - 1;
            e.bytes = be32(p + at);
            e.name = (const char *)(v->blob + v->strings_offset + be32(p + at + 4));
            e.value = p + at + 8;
            at = (at + 8 + e.bytes + 3) & ~3u;
        } else if (token == 9) {
            return ATL_FDT_OK;
        } else { /* validated NOP */
            continue;
        }
        status = visit(context, &e);
        if (status) return status;
    }
    return ATL_FDT_FORMAT; /* unreachable for an immutable validated blob */
}
