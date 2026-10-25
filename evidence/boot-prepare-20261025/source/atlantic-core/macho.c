/* SPDX-License-Identifier: MIT - Original parser; no Apple loader code copied. */
#include <atlantic/macho.h>

static uint32_t le32(const uint8_t *p) {
    return p[0] | (uint32_t)p[1]<<8 | (uint32_t)p[2]<<16 | (uint32_t)p[3]<<24;
}
static uint64_t le64(const uint8_t *p) { return le32(p) | (uint64_t)le32(p+4)<<32; }
static int inside(uint64_t at, uint64_t n, uint64_t base, uint64_t bytes) {
    return at >= base && at-base <= bytes && n <= bytes-(at-base);
}
static int intersects(uint64_t a, uint64_t an, uint64_t b, uint64_t bn) {
    return an && bn && (a <= b ? b-a < an : a-b < bn);
}
static int same16(const uint8_t *a, const uint8_t *b) {
    unsigned i;
    for (i=0; i<16; ++i) if (a[i]!=b[i]) return 0;
    return 1;
}
static int named(const uint8_t *p, const char *name) {
    unsigned i=0;
    while (name[i] && i<16) { if (p[i]!=(uint8_t)name[i]) return 0; ++i; }
    if (i==16) return !name[i];
    for (; i<16; ++i) if (p[i]) return 0;
    return 1;
}
static int valid_name(const uint8_t *p) {
    unsigned i;
    int ended=0;
    if (!p[0]) return 0;
    for (i=0; i<16; ++i) {
        if (!p[i]) ended=1;
        else if (ended || p[i]<33 || p[i]>126) return 0;
    }
    return 1;
}
static int canonical(uint64_t p) {
    return p < UINT64_C(0x0000800000000000) || p >= UINT64_C(0xffff800000000000);
}
struct Section {
    uint64_t address, bytes;
    uint32_t segment;
};

int atl_macho_plan(const void *file, size_t bytes, struct AtlanticMachoPlan *out) {
    const uint8_t *p=file;
    struct AtlanticMachoPlan plan;
    struct Section sections[ATL_MACHO_MAX_SECTIONS];
    uint32_t count, end, at, i, j, sym=0, dysym=0, thread=0, build=0, uuid=0;
    uint32_t symoff, nsyms, stroff, strsize, indirect, nindirect;
    uint64_t entry=0;
    int entry_section=0;
    uintptr_t address=(uintptr_t)file, output=(uintptr_t)out;
    if (!p || !out || bytes<32 || bytes>ATL_MACHO_MAX_BYTES ||
        bytes>UINTPTR_MAX-address || sizeof(*out)>UINTPTR_MAX-output ||
        intersects(address,bytes,output,sizeof(*out))) return ATL_MACHO_BOUNDS;
    if (le32(p)!=0xfeedfacfu || le32(p+4)!=0x0100000cu || le32(p+8)!=0 ||
        le32(p+12)!=2 || le32(p+24)!=1 || le32(p+28)!=0)
        return ATL_MACHO_UNSUPPORTED;
    count=le32(p+16);
    if (!count || count>ATL_MACHO_MAX_COMMANDS || le32(p+20)>32768u)
        return ATL_MACHO_LIMIT;
    if (!inside(32,le32(p+20),0,bytes)) return ATL_MACHO_BOUNDS;
    end=32+le32(p+20);
    /* Byte loops also keep this freestanding object independent of libc. */
    for (i=0; i<sizeof(plan); ++i) ((uint8_t *)&plan)[i]=0;
    plan.command_bytes=end-32;
    at=32;
    for (i=0; i<count; ++i) {
        uint32_t cmd, size;
        if (!inside(at,8,32,end-32)) return ATL_MACHO_BOUNDS;
        cmd=le32(p+at); size=le32(p+at+4);
        if (size<8 || (size&7) || !inside(at,size,32,end-32)) return ATL_MACHO_BOUNDS;
        if (cmd==0x19) { /* LC_SEGMENT_64 */
            struct AtlanticMachoSegment *s;
            uint32_t nsects;
            uint64_t previous_end=0;
            if (size<72) return ATL_MACHO_FORMAT;
            nsects=le32(p+at+64);
            if (plan.segment_count==ATL_MACHO_MAX_SEGMENTS ||
                nsects>ATL_MACHO_MAX_SECTIONS-plan.section_count) return ATL_MACHO_LIMIT;
            if (size!=72+80*nsects || !valid_name(p+at+8) ||
                (le32(p+at+68) && le32(p+at+68)!=0x10))
                return ATL_MACHO_FORMAT;
            s=&plan.segments[plan.segment_count];
            for (j=0; j<16; ++j) s->name[j]=(char)p[at+8+j];
            s->virtual_address=le64(p+at+24); s->virtual_bytes=le64(p+at+32);
            s->file_offset=le64(p+at+40); s->file_bytes=le64(p+at+48);
            s->protection=le32(p+at+60);
            if (!s->virtual_bytes || s->virtual_bytes>ATL_MACHO_MAX_BYTES ||
                s->virtual_bytes>UINT64_MAX-s->virtual_address ||
                !s->virtual_address || (s->virtual_address&16383) || (s->file_offset&16383) ||
                !canonical(s->virtual_address) || s->file_bytes>s->virtual_bytes ||
                !inside(s->file_offset,s->file_bytes,0,bytes) ||
                s->protection!=le32(p+at+56) ||
                (s->protection!=1 && s->protection!=3 && s->protection!=5) ||
                (le32(p+at+68)==0x10 && s->protection!=1))
                return ATL_MACHO_LAYOUT;
            s->mapping_bytes=(s->virtual_bytes+16383)&~UINT64_C(16383);
            if (s->mapping_bytes>UINT64_MAX-s->virtual_address ||
                !canonical(s->virtual_address+s->mapping_bytes-1)) return ATL_MACHO_LAYOUT;
            if (!plan.segment_count) {
                if (!named(p+at+8,"__TEXT") || s->file_offset || s->file_bytes<end || s->protection!=5)
                    return ATL_MACHO_LAYOUT;
                plan.virtual_base=s->virtual_address;
                previous_end=s->virtual_address+end;
            } else {
                const struct AtlanticMachoSegment *last=&plan.segments[plan.segment_count-1];
                if (s->virtual_address<last->virtual_address+last->mapping_bytes ||
                    s->file_offset<last->file_offset+last->file_bytes ||
                    named((const uint8_t *)last->name,"__LINKEDIT")) return ATL_MACHO_LAYOUT;
            }
            if (s->virtual_address-plan.virtual_base>ATL_MACHO_MAX_BYTES ||
                s->mapping_bytes>ATL_MACHO_MAX_BYTES-(s->virtual_address-plan.virtual_base))
                return ATL_MACHO_LIMIT;
            for (j=0; j<plan.segment_count; ++j)
                if (same16(p+at+8,(const uint8_t *)plan.segments[j].name)) return ATL_MACHO_LAYOUT;
            if (named(p+at+8,"__LINKEDIT") && (nsects || s->protection!=1)) return ATL_MACHO_LAYOUT;
            for (j=0; j<nsects; ++j) {
                const uint8_t *q=p+at+72+80*j;
                uint64_t va=le64(q+32), n=le64(q+40);
                uint32_t off=le32(q+48), align=le32(q+52), flags=le32(q+64), kind=flags&255;
                struct Section *section=&sections[plan.section_count];
                if (!valid_name(q) || !same16(q+16,p+at+8) || align>14 ||
                    (va&((UINT64_C(1)<<align)-1)) ||
                    !inside(va,n,s->virtual_address,s->virtual_bytes) || va<previous_end ||
                    le32(q+56) || le32(q+60) || le32(q+72) || le32(q+76) ||
                    (flags&~0x900004ffu)) return ATL_MACHO_LAYOUT;
                if (kind!=0 && kind!=1 && kind!=2 && kind!=3 && kind!=4 && kind!=5 && kind!=6 && kind!=14)
                    return ATL_MACHO_UNSUPPORTED;
                if (kind==1) {
                    uint64_t delta=va-s->virtual_address, backed=0, k;
                    if (off || le32(q+68)) return ATL_MACHO_LAYOUT;
                    /* LLD rounds file segments to pages: the beginning of a
                     * zero-fill section may overlap that zero padding. Prove
                     * it is zero before describing a copy + zero-tail plan. */
                    if (delta<s->file_bytes) backed=s->file_bytes-delta;
                    if (backed>n) backed=n;
                    for (k=0; k<backed; ++k)
                        if (p[s->file_offset+delta+k]) return ATL_MACHO_LAYOUT;
                } else if (!inside(off,n,s->file_offset,s->file_bytes) ||
                           va-s->virtual_address!=off-s->file_offset ||
                           (kind!=6 && le32(q+68))) return ATL_MACHO_LAYOUT;
                if (kind==6 && ((n&7) || align<3)) return ATL_MACHO_LAYOUT;
                if (flags&0x80000400u) {
                    if (s->protection!=5 || kind!=0) return ATL_MACHO_LAYOUT;
                }
                section->address=va; section->bytes=n; section->segment=plan.segment_count;
                ++plan.section_count;
                previous_end=va+n;
            }
            ++plan.segment_count;
        } else if (cmd==2) { /* LC_SYMTAB */
            if (sym || size!=24) return ATL_MACHO_FORMAT;
            sym=at;
        } else if (cmd==11) { /* LC_DYSYMTAB; no runtime relocations or imports. */
            if (dysym || size!=80) return ATL_MACHO_FORMAT;
            dysym=at;
        } else if (cmd==5) { /* LC_UNIXTHREAD, ARM_THREAD_STATE64, count in uint32s. */
            if (thread || size!=288 || le32(p+at+8)!=6 || le32(p+at+12)!=68)
                return ATL_MACHO_ENTRY;
            thread=at; entry=le64(p+at+272);
            for (j=16; j<size; ++j)
                if ((j<272 || j>=280) && p[at+j]) return ATL_MACHO_ENTRY;
        } else if (cmd==0x32) { /* LC_BUILD_VERSION: informational, no OS services. */
            if (build || size<24 || le32(p+at+20)>16 || size!=24+8*le32(p+at+20))
                return ATL_MACHO_FORMAT;
            build=at;
        } else if (cmd==0x1b) {
            if (uuid || size!=24) return ATL_MACHO_FORMAT;
            uuid=at;
        } else return ATL_MACHO_UNSUPPORTED;
        at+=size;
    }
    if (at!=end || !sym || !dysym || !thread || !plan.segment_count || !plan.section_count)
        return ATL_MACHO_FORMAT;
    {
        const struct AtlanticMachoSegment *last=&plan.segments[plan.segment_count-1];
        if (!named((const uint8_t *)last->name,"__LINKEDIT")) return ATL_MACHO_LAYOUT;
        plan.virtual_span=last->virtual_address-plan.virtual_base+last->mapping_bytes;
        symoff=le32(p+sym+8); nsyms=le32(p+sym+12);
        stroff=le32(p+sym+16); strsize=le32(p+sym+20);
        indirect=le32(p+dysym+56); nindirect=le32(p+dysym+60);
        if (nsyms>ATL_MACHO_MAX_SYMBOLS || nindirect>ATL_MACHO_MAX_SYMBOLS) return ATL_MACHO_LIMIT;
        if (!nsyms || !strsize || (symoff&7) || (indirect&3) ||
            !inside(symoff,(uint64_t)nsyms*16,last->file_offset,last->file_bytes) ||
            !inside(stroff,strsize,last->file_offset,last->file_bytes) ||
            (nindirect && !inside(indirect,(uint64_t)nindirect*4,last->file_offset,last->file_bytes)) ||
            intersects(symoff,(uint64_t)nsyms*16,stroff,strsize) ||
            intersects(indirect,(uint64_t)nindirect*4,symoff,(uint64_t)nsyms*16) ||
            intersects(indirect,(uint64_t)nindirect*4,stroff,strsize) ||
            p[(uint64_t)stroff+strsize-1]) return ATL_MACHO_SYMBOL;
    }
    /* The final string byte is NUL: every in-range string index terminates.
     * No per-symbol scan of an attacker-controlled long string is necessary. */
    for (i=0; i<nsyms; ++i) {
        const uint8_t *q=p+symoff+16u*i;
        uint32_t type=q[4]&14, desc=(uint32_t)q[6] | (uint32_t)q[7]<<8;
        if (le32(q)>=strsize || (q[4]&0xe0) || (desc&~0xb0u)) return ATL_MACHO_SYMBOL;
        if (type==2) { if (q[5]) return ATL_MACHO_SYMBOL; }
        else if (type==14) {
            const struct Section *s;
            if (!q[5] || q[5]>plan.section_count) return ATL_MACHO_SYMBOL;
            s=&sections[q[5]-1];
            /* LLD associates __mh_execute_header with section 1 even though
             * its value precedes that section's first instruction. */
            if (!(q[5]==1 && le64(q+8)==plan.virtual_base) &&
                !inside(le64(q+8),0,s->address,s->bytes)) return ATL_MACHO_SYMBOL;
        } else return ATL_MACHO_SYMBOL;
    }
    /* Static local/external partitions cover the complete symbol table. */
    if (le32(p+dysym+8) || le32(p+dysym+12)>nsyms ||
        le32(p+dysym+16)!=le32(p+dysym+12) ||
        le32(p+dysym+20)!=nsyms-le32(p+dysym+12) ||
        le32(p+dysym+24)!=nsyms || le32(p+dysym+28)) return ATL_MACHO_SYMBOL;
    for (i=32; i<80; i+=4)
        if (i!=56 && i!=60 && le32(p+dysym+i)) return ATL_MACHO_UNSUPPORTED;
    for (i=0; i<nindirect; ++i) {
        uint32_t index=le32(p+indirect+4u*i);
        if (index>=nsyms && index!=0x80000000u && index!=0xc0000000u) return ATL_MACHO_SYMBOL;
    }
    at=32;
    for (i=0; i<count; ++i) {
        uint32_t size=le32(p+at+4);
        if (le32(p+at)==0x19) {
            uint32_t ns=le32(p+at+64), prot=le32(p+at+60);
            for (j=0; j<ns; ++j) {
                const uint8_t *q=p+at+72+80*j;
                uint64_t va=le64(q+32), n=le64(q+40);
                if ((le32(q+64)&255)==6 && !inside(le32(q+68),n/8,0,nindirect))
                    return ATL_MACHO_SYMBOL;
                if (prot==5 && (le32(q+64)&0x80000400u) && inside(entry,4,va,n)) entry_section=1;
            }
        }
        at+=size;
    }
    if ((entry&3) || !entry_section) return ATL_MACHO_ENTRY;
    plan.entry=entry; plan.symbol_count=nsyms;
    for (i=0; i<sizeof(plan); ++i) ((uint8_t *)out)[i]=((const uint8_t *)&plan)[i];
    return ATL_MACHO_OK;
}
