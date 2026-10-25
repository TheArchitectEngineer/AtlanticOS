/* SPDX-License-Identifier: MIT - Original FDT inventory and native XNU serializer. */
#include <atlantic/boot_tree.h>

#define AFFINITY_MASK UINT64_C(0x000000ff00ffffff)
static void clear(void *p, size_t n) { uint8_t *b = p; while (n--) *b++ = 0; }
static int eq(const char *a, const char *b) {
    while (*a && *a == *b) { ++a; ++b; }
    return *a == *b;
}
static int string_is(const uint8_t *p, uint32_t n, const char *s) {
    uint32_t i = 0;
    while (s[i]) { if (i >= n || p[i] != (uint8_t)s[i]) return 0; ++i; }
    return i + 1 == n && p[i] == 0;
}
static uint32_t be32(const uint8_t *p) {
    return (uint32_t)p[0]<<24 | (uint32_t)p[1]<<16 | (uint32_t)p[2]<<8 | p[3];
}
static uint64_t cells(const uint8_t *p, uint32_t n) {
    return n == 2 ? (uint64_t)be32(p)<<32 | be32(p+4) : be32(p);
}
static int cell_width(uint32_t n) { return n == 1 || n == 2; }
static int valid_range(uint64_t start, uint64_t bytes) {
    return bytes && bytes <= UINT64_MAX - start;
}
static int aliases(const void *a, size_t an, const void *b, size_t bn) {
    uintptr_t ap = (uintptr_t)a, bp = (uintptr_t)b;
    if (an > UINTPTR_MAX-ap || bn > UINTPTR_MAX-bp) return 1;
    return an && bn && ap < bp+bn && bp < ap+an;
}
static int add_range(struct AtlanticPhysicalRange *p, uint32_t *count, uint32_t max,
                      uint64_t start, uint64_t bytes) {
    if (!valid_range(start, bytes)) return ATL_FDT_OVERFLOW;
    if (*count == max) return ATL_BOOT_LIMIT;
    p[*count].start = start; p[*count].bytes = bytes; ++*count;
    return 0;
}
/* RAM overlaps are ambiguous. Reservations may overlap or be adjacent, and
 * remain excluded as a union, including reusable and no-map declarations. */
static int normalize(struct AtlanticPhysicalRange *p, uint32_t *count, int reserved) {
    for (uint32_t i = 0; i < *count; ++i) {
        if (!valid_range(p[i].start, p[i].bytes)) return ATL_FDT_OVERFLOW;
        for (uint32_t j = i; j && p[j].start < p[j-1].start; --j) {
            struct AtlanticPhysicalRange t = p[j]; p[j] = p[j-1]; p[j-1] = t;
        }
    }
    uint32_t n = 0;
    for (uint32_t i = 0; i < *count; ++i) {
        if (n && p[i].start <= p[n-1].start+p[n-1].bytes) {
            uint64_t end = p[n-1].start+p[n-1].bytes, next = p[i].start+p[i].bytes;
            if (!reserved && p[i].start < end) return ATL_BOOT_AMBIGUOUS;
            if (next > end) p[n-1].bytes = next-p[n-1].start;
        } else p[n++] = p[i];
    }
    *count = n;
    return 0;
}

enum Role { OTHER, ROOT, RAM, RESERVED, RES_RANGE, CPUS, CPU };
enum Seen { AC = 1, SC = 2, REG = 4, TYPE = 8, RANGES = 16, STATUS = 32, SIZE = 64 };
struct Frame {
    enum Role role;
    uint32_t seen, ac, sc, reg_bytes;
    const uint8_t *reg;
    unsigned memory_type, cpu_type, unavailable;
};
struct InventoryContext {
    struct AtlanticBootInventory map;
    struct Frame stack[ATL_FDT_MAX_DEPTH];
    unsigned seen_reserved, seen_cpus;
};
static int parent_widths(const struct InventoryContext *c, enum Role role,
                          uint32_t *ac, uint32_t *sc) {
    const struct Frame *f = role == RES_RANGE || role == CPU ? &c->stack[1] : &c->stack[0];
    if ((f->seen & (AC|SC)) != (AC|SC) || !cell_width(f->ac)) return ATL_BOOT_SCHEMA;
    if (role == CPU ? f->sc != 0 : !cell_width(f->sc)) return ATL_BOOT_SCHEMA;
    if (role == RES_RANGE && (f->ac != c->stack[0].ac || f->sc != c->stack[0].sc ||
                              !(f->seen & RANGES))) return ATL_BOOT_SCHEMA;
    *ac = f->ac; *sc = f->sc;
    return 0;
}
static int collect(void *context, const struct AtlanticFdtEvent *e) {
    struct InventoryContext *c = context;
    struct Frame *f = &c->stack[e->depth];
    if (e->kind == ATL_FDT_NODE_BEGIN) {
        clear(f, sizeof(*f));
        if (!e->depth) f->role = ROOT;
        else if (e->depth == 1) {
            if (eq(e->name, "reserved-memory")) {
                if (c->seen_reserved++) return ATL_BOOT_AMBIGUOUS;
                f->role = RESERVED;
            } else if (eq(e->name, "cpus")) {
                if (c->seen_cpus++) return ATL_BOOT_AMBIGUOUS;
                f->role = CPUS;
            } else if (eq(e->name, "memory") ||
                       (e->name[0]=='m' && e->name[1]=='e' && e->name[2]=='m' &&
                        e->name[3]=='o' && e->name[4]=='r' && e->name[5]=='y' && e->name[6]=='@')) {
                f->role = RAM;
            }
        } else if (e->depth == 2) {
            if (c->stack[1].role == RESERVED) f->role = RES_RANGE;
            else if (c->stack[1].role == CPUS &&
                     (eq(e->name,"cpu") || (e->name[0]=='c' && e->name[1]=='p' &&
                      e->name[2]=='u' && e->name[3]=='@'))) f->role = CPU;
        }
        return 0;
    }
    if (e->kind == ATL_FDT_PROPERTY) {
        if (f->role == OTHER && e->depth != 1) return 0;
        unsigned flag = 0;
        if (eq(e->name,"#address-cells")) flag = AC;
        else if (eq(e->name,"#size-cells")) flag = SC;
        else if (eq(e->name,"reg")) flag = REG;
        else if (eq(e->name,"device_type")) flag = TYPE;
        else if (eq(e->name,"ranges")) flag = RANGES;
        else if (eq(e->name,"status")) flag = STATUS;
        else if (eq(e->name,"size")) flag = SIZE;
        if (flag && (f->seen & flag)) return ATL_BOOT_AMBIGUOUS;
        f->seen |= flag;
        if (flag == AC || flag == SC) {
            if (e->bytes != 4) return ATL_BOOT_SCHEMA;
            if (flag == AC) f->ac = be32(e->value); else f->sc = be32(e->value);
        } else if (flag == REG) { f->reg = e->value; f->reg_bytes = e->bytes; }
        else if (flag == TYPE) {
            f->memory_type = string_is(e->value,e->bytes,"memory");
            f->cpu_type = string_is(e->value,e->bytes,"cpu");
        } else if (flag == RANGES && f->role == RESERVED && e->bytes) return ATL_BOOT_SCHEMA;
        else if (flag == STATUS) {
            f->unavailable = !string_is(e->value,e->bytes,"okay") && !string_is(e->value,e->bytes,"ok");
        }
        return 0;
    }
    uint32_t ac, sc;
    if (f->role == ROOT || f->role == CPUS || f->role == RESERVED) {
        enum Role child = f->role == CPUS ? CPU : f->role == RESERVED ? RES_RANGE : RAM;
        return parent_widths(c, child, &ac, &sc);
    }
    if (e->depth == 1 && f->memory_type) f->role = RAM;
    if (f->role != RAM && f->role != RES_RANGE && f->role != CPU) return 0;
    if (f->role != RES_RANGE && f->unavailable) return 0;
    if (f->role == RAM && !f->memory_type) return ATL_BOOT_SCHEMA;
    if (f->role == CPU && !f->cpu_type) return ATL_BOOT_SCHEMA;
    if (!(f->seen & REG)) return f->role == RES_RANGE && (f->seen & SIZE) ?
        ATL_BOOT_DYNAMIC_RESERVATION : ATL_BOOT_SCHEMA;
    int status = parent_widths(c, f->role, &ac, &sc);
    if (status) return status;
    if (f->role == CPU) {
        if (f->reg_bytes != ac*4) return ATL_BOOT_SCHEMA;
        uint64_t affinity = cells(f->reg,ac);
        if (affinity & ~AFFINITY_MASK) return ATL_BOOT_CPU;
        if (c->map.cpu_count == ATL_BOOT_MAX_CPUS) return ATL_BOOT_LIMIT;
        for (uint32_t i=0;i<c->map.cpu_count;++i)
            if (c->map.cpu_affinity[i] == affinity) return ATL_BOOT_AMBIGUOUS;
        c->map.cpu_affinity[c->map.cpu_count++] = affinity;
        return 0;
    }
    uint32_t stride = (ac+sc)*4;
    if (!f->reg_bytes || f->reg_bytes % stride) return ATL_BOOT_SCHEMA;
    for (uint32_t at=0;at<f->reg_bytes;at+=stride) {
        uint64_t start = cells(f->reg+at,ac), bytes = cells(f->reg+at+ac*4,sc);
        status = f->role == RAM ? add_range(c->map.ram,&c->map.ram_count,ATL_BOOT_MAX_RAM,start,bytes) :
            add_range(c->map.reserved,&c->map.reserved_count,ATL_BOOT_MAX_RESERVED,start,bytes);
        if (status) return status;
    }
    return 0;
}
int atl_boot_inventory(const struct AtlanticFdtView *v, struct AtlanticBootInventory *out) {
    struct InventoryContext c;
    if (!out || !v || !v->blob) return ATL_FDT_BOUNDS;
    if (aliases(out,sizeof(*out),v,sizeof(*v)) || aliases(out,sizeof(*out),v->blob,v->total_bytes))
        return ATL_BOOT_BUFFER;
    clear(out,sizeof(*out)); clear(&c,sizeof(c));
    int status = atl_fdt_validate_structure(v);
    if (status) return status;
    for (uint32_t i=0;i<v->reservation_count;++i) {
        uint64_t start,bytes;
        status = atl_fdt_reservation(v,i,&start,&bytes);
        if (!status) status = add_range(c.map.reserved,&c.map.reserved_count,ATL_BOOT_MAX_RESERVED,start,bytes);
        if (status) return status;
    }
    status = atl_fdt_walk(v,collect,&c);
    if (!status) status = normalize(c.map.ram,&c.map.ram_count,0);
    if (!status) status = normalize(c.map.reserved,&c.map.reserved_count,1);
    if (!status && !c.map.ram_count) status = ATL_BOOT_NO_RAM;
    if (status) return status;
    uint8_t *dst = (uint8_t *)out;
    const uint8_t *src = (const uint8_t *)&c.map;
    for (size_t i=0;i<sizeof(*out);++i) dst[i] = src[i];
    return 0;
}
int atl_boot_exclude(struct AtlanticBootInventory *m, uint64_t start, uint64_t bytes) {
    if (!m || m->ram_count > ATL_BOOT_MAX_RAM || m->reserved_count > ATL_BOOT_MAX_RESERVED ||
        !valid_range(start,bytes)) return ATL_BOOT_SCHEMA;
    unsigned contained = 0;
    for (uint32_t i=0;i<m->ram_count;++i) {
        if (!valid_range(m->ram[i].start,m->ram[i].bytes)) return ATL_BOOT_SCHEMA;
        if (start >= m->ram[i].start && bytes <= m->ram[i].bytes &&
            start-m->ram[i].start <= m->ram[i].bytes-bytes) contained = 1;
    }
    if (!contained) return ATL_BOOT_SCHEMA;
    for (uint32_t i=0;i<m->reserved_count;++i)
        if (!valid_range(m->reserved[i].start,m->reserved[i].bytes)) return ATL_BOOT_SCHEMA;
    int status = add_range(m->reserved,&m->reserved_count,ATL_BOOT_MAX_RESERVED,start,bytes);
    if (!status) status = normalize(m->reserved,&m->reserved_count,1);
    return status;
}

/* Native wire structure is audited separately against pinned XNU headers.
 * Explicit little endian stores avoid host struct layout, padding and aliases. */
struct Writer { uint8_t *p; size_t at; };
static void le32(struct Writer *w, uint32_t v) {
    for (unsigned i=0;i<4;++i) { if (w->p) w->p[w->at] = (uint8_t)(v>>(i*8)); ++w->at; }
}
static void property(struct Writer *w, const char *name, const uint8_t *data, uint32_t bytes) {
    unsigned end = 0;
    for (unsigned i=0;i<32;++i) {
        uint8_t c = end ? 0 : (uint8_t)name[i];
        if (!c) end = 1;
        if (w->p) w->p[w->at] = c;
        ++w->at;
    }
    le32(w,bytes);
    for (uint32_t i=0;i<((bytes+3)&~3u);++i) {
        if (w->p) w->p[w->at] = i < bytes ? data[i] : 0;
        ++w->at;
    }
}
static void number(struct Writer *w, const char *name, uint64_t v, uint32_t bytes) {
    uint8_t data[8];
    for (unsigned i=0;i<8;++i) data[i]=(uint8_t)(v>>(8*i));
    property(w,name,data,bytes);
}
static void node(struct Writer *w, uint32_t props, uint32_t children, const char *name, uint32_t len) {
    le32(w,props); le32(w,children); property(w,"name",(const uint8_t *)name,len);
}
static void emit(struct Writer *w, uint64_t base, uint64_t size, uint32_t cpu, uint32_t freq) {
    node(w,1,3,"/",2);
    node(w,4,0,"chosen",7);
    number(w,"dram-base",base,8);
    /* A zero-length unknown property aligns the following uint64_t payload to
     * 8 bytes while preserving the native 4-byte property stride. */
    property(w,"atlantic,padding",0,0);
    number(w,"dram-size",size,8);
    node(w,1,0,"defaults",9);
    node(w,1,1,"cpus",5);
    node(w,4,0,"cpu",4);
    number(w,"reg",cpu,4);
    property(w,"state",(const uint8_t *)"running",8);
    number(w,"timebase-frequency",freq,4);
}
int atl_xnu_boot_tree(const struct AtlanticBootInventory *m, uint64_t mpidr, uint64_t freq,
                      void *output, size_t capacity, size_t *used) {
    if (!used || (m && aliases(used,sizeof(*used),m,sizeof(*m))) ||
        (output && aliases(used,sizeof(*used),output,capacity))) return ATL_BOOT_BUFFER;
    *used = 0;
    if (!m || !output || ((uintptr_t)output&7) ||
        aliases(output,capacity,m,sizeof(*m))) return ATL_BOOT_BUFFER;
    if (!m->ram_count || m->ram_count > ATL_BOOT_MAX_RAM ||
        m->reserved_count > ATL_BOOT_MAX_RESERVED || m->cpu_count > ATL_BOOT_MAX_CPUS) return ATL_BOOT_SCHEMA;
    uint64_t base = m->ram[0].start, end = base;
    for (uint32_t i=0;i<m->ram_count;++i) {
        if (!valid_range(m->ram[i].start,m->ram[i].bytes)) return ATL_BOOT_SCHEMA;
        if (m->ram[i].start != end) return ATL_BOOT_NOT_CONTIGUOUS;
        end = m->ram[i].start+m->ram[i].bytes;
    }
    for (uint32_t i=0;i<m->reserved_count;++i)
        if (!valid_range(m->reserved[i].start,m->reserved[i].bytes)) return ATL_BOOT_SCHEMA;
    uint64_t affinity = mpidr & AFFINITY_MASK;
    if (affinity > UINT32_MAX || !freq || freq > UINT32_MAX) return ATL_BOOT_CPU;
    unsigned found = 0;
    for (uint32_t i=0;i<m->cpu_count;++i) {
        if (m->cpu_affinity[i] & ~AFFINITY_MASK) return ATL_BOOT_CPU;
        if (m->cpu_affinity[i] == affinity) ++found;
    }
    if (found != 1) return ATL_BOOT_CPU;
    struct Writer dry = {0,0};
    emit(&dry,base,end-base,(uint32_t)affinity,(uint32_t)freq);
    if (dry.at > capacity || dry.at > ATL_XNU_TREE_MAX_BYTES) return ATL_BOOT_BUFFER;
    struct Writer w = {output,0};
    emit(&w,base,end-base,(uint32_t)affinity,(uint32_t)freq);
    *used = w.at;
    return 0;
}
