/* SPDX-License-Identifier: MIT - Host contract tests, never kernel execution. */
#include <atlantic/macho.h>
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BYTES 33024u
static unsigned cases, truncations, mutations, rejections;
static uint8_t image[BYTES], changed[BYTES];
static uint32_t thread_at, sym_at, dysym_at, build_at;
static void w32(uint8_t *p, uint32_t v) { for (unsigned i=0;i<4;++i) p[i]=(uint8_t)(v>>(i*8)); }
static void w64(uint8_t *p, uint64_t v) { for (unsigned i=0;i<8;++i) p[i]=(uint8_t)(v>>(i*8)); }
static void section(uint8_t *q, const char *name, const char *seg, uint64_t va,
                    uint64_t bytes, uint32_t offset, uint32_t align, uint32_t flags) {
    memcpy(q,name,strlen(name)); memcpy(q+16,seg,strlen(seg));
    w64(q+32,va); w64(q+40,bytes); w32(q+48,offset); w32(q+52,align); w32(q+64,flags);
}
static void segment(uint8_t *q, const char *name, uint64_t va, uint64_t bytes,
                    uint64_t offset, uint64_t filebytes, uint32_t prot, uint32_t nsects) {
    w32(q,0x19); w32(q+4,72+80*nsects); memcpy(q+8,name,strlen(name));
    w64(q+24,va); w64(q+32,bytes); w64(q+40,offset); w64(q+48,filebytes);
    w32(q+56,prot); w32(q+60,prot); w32(q+64,nsects);
}
static void fixture(uint64_t base) {
    uint32_t c=32;
    const char strings[]=" \0__start\0_data\0_zero\0__mh_execute_header\0";
    const unsigned names[]={2,10,16,22}, sects[]={1,2,3,1};
    const uint64_t values[]={base+4096,base+16384,base+32768,base};
    memset(image,0,sizeof(image));
    w32(image,0xfeedfacf); w32(image+4,0x100000c); w32(image+12,2);
    w32(image+16,7); w32(image+24,1);
    segment(image+c,"__TEXT",base,16384,0,16384,5,1);
    section(image+c+72,"__text","__TEXT",base+4096,4,4096,2,0x80000400); c+=152;
    segment(image+c,"__DATA",base+16384,32768,16384,16384,3,2);
    section(image+c+72,"__data","__DATA",base+16384,8,16384,3,0);
    section(image+c+152,"__bss","__DATA",base+32768,8192,0,3,1); c+=232;
    segment(image+c,"__LINKEDIT",base+49152,256,32768,256,1,0); c+=72;
    sym_at=c; w32(image+c,2); w32(image+c+4,24); w32(image+c+8,32768);
    w32(image+c+12,4); w32(image+c+16,32832); w32(image+c+20,128); c+=24;
    dysym_at=c; w32(image+c,11); w32(image+c+4,80); w32(image+c+20,4); w32(image+c+24,4); c+=80;
    build_at=c; w32(image+c,0x32); w32(image+c+4,24); w32(image+c+8,1); c+=24;
    thread_at=c; w32(image+c,5); w32(image+c+4,288);
    w32(image+c+8,6); w32(image+c+12,68); w64(image+c+272,base+4096); c+=288;
    w32(image+20,c-32);
    for (unsigned i=0;i<4;++i) {
        uint8_t *q=image+32768+16*i;
        w32(q,names[i]); q[4]=15; q[5]=(uint8_t)sects[i]; w64(q+8,values[i]);
    }
    memcpy(image+32832,strings,sizeof(strings));
}
static int check(const uint8_t *p, size_t bytes) {
    struct { uint64_t prefix; struct AtlanticMachoPlan plan; uint64_t suffix; } o;
    struct AtlanticMachoPlan before;
    int result;
    memset(&o,0xa5,sizeof(o)); before=o.plan;
    result=atl_macho_plan(p,bytes,&o.plan); ++cases;
    assert(o.prefix==UINT64_C(0xa5a5a5a5a5a5a5a5) && o.suffix==o.prefix);
    if (result) assert(!memcmp(&o.plan,&before,sizeof(before)));
    else {
        assert(o.plan.segment_count && o.plan.segment_count<=ATL_MACHO_MAX_SEGMENTS);
        assert(o.plan.virtual_span<=ATL_MACHO_MAX_BYTES && !(o.plan.entry&3));
        assert(o.plan.entry>=o.plan.virtual_base);
        for (unsigned i=0;i<o.plan.segment_count;++i) {
            struct AtlanticMachoSegment *s=&o.plan.segments[i];
            assert(s->file_offset<=bytes && s->file_bytes<=bytes-s->file_offset);
            assert(s->file_bytes<=s->virtual_bytes && s->virtual_bytes<=s->mapping_bytes);
            assert(!(s->mapping_bytes&16383) && (s->protection==1 || s->protection==3 || s->protection==5));
        }
    }
    return result;
}
static void reject32(uint32_t offset, uint32_t value, int error) {
    memcpy(changed,image,BYTES); w32(changed+offset,value);
    assert(check(changed,BYTES)==error); ++rejections;
}
static void reject64(uint32_t offset, uint64_t value, int error) {
    memcpy(changed,image,BYTES); w64(changed+offset,value);
    assert(check(changed,BYTES)==error); ++rejections;
}
static void contracts(void) {
    struct AtlanticMachoPlan plan;
    uint32_t random=0x51a7e123;
    fixture(0x40000000);
    assert(!check(image,BYTES));
    assert(!atl_macho_plan(image,BYTES,&plan));
    assert(plan.virtual_base==0x40000000 && plan.virtual_span==65536 && plan.entry==0x40001000);
    assert(plan.segment_count==3 && plan.section_count==3 && plan.symbol_count==4);
    assert(plan.segments[1].file_bytes==16384 && plan.segments[1].virtual_bytes==32768);
    assert(plan.segments[2].virtual_bytes==256 && plan.segments[2].mapping_bytes==16384);
    for (unsigned n=0;n<BYTES;++n) {
        /* Exact allocation makes every truncation's end visible to ASan. */
        uint8_t *shorter=malloc(n ? n:1); assert(shorter); memcpy(shorter,image,n);
        assert(check(shorter,n)); free(shorter); ++truncations;
    }
    reject32(0,0xcffaedfe,ATL_MACHO_UNSUPPORTED);
    reject32(4,0x1000007,ATL_MACHO_UNSUPPORTED);
    reject32(8,2,ATL_MACHO_UNSUPPORTED); /* arm64e/PAC not accepted. */
    reject32(12,1,ATL_MACHO_UNSUPPORTED);
    reject32(24,0x200005,ATL_MACHO_UNSUPPORTED);
    reject32(28,1,ATL_MACHO_UNSUPPORTED);
    reject32(16,65,ATL_MACHO_LIMIT);
    reject32(20,32769,ATL_MACHO_LIMIT);
    reject32(20,1,ATL_MACHO_BOUNDS);
    reject32(36,7,ATL_MACHO_BOUNDS);
    reject32(36,152+8,ATL_MACHO_FORMAT);
    reject32(32+64,129,ATL_MACHO_LIMIT);
    reject64(32+24,0x40000001,ATL_MACHO_LAYOUT);
    reject64(32+32,UINT64_MAX,ATL_MACHO_LAYOUT);
    reject64(32+48,BYTES+1,ATL_MACHO_LAYOUT);
    reject32(32+56,7,ATL_MACHO_LAYOUT);
    reject32(32+60,7,ATL_MACHO_LAYOUT);
    reject32(32+68,1,ATL_MACHO_FORMAT);
    memcpy(changed,image,BYTES); w32(changed+184+56,7); w32(changed+184+60,7);
    assert(check(changed,BYTES)==ATL_MACHO_LAYOUT); ++rejections; /* Actual W+X. */
    reject64(184+24,0x40000000,ATL_MACHO_LAYOUT); /* Overlapping virtual pages. */
    reject64(184+40,0,ATL_MACHO_LAYOUT); /* Overlapping file ranges. */
    reject32(104+48,4097,ATL_MACHO_LAYOUT); /* VA/file relation. */
    reject32(104+52,32,ATL_MACHO_LAYOUT);
    reject32(104+56,1,ATL_MACHO_LAYOUT); /* Residual relocation offset. */
    reject32(104+64,9,ATL_MACHO_UNSUPPORTED); /* Constructor section. */
    reject32(104+64,0x80000401,ATL_MACHO_LAYOUT); /* Instructions in zero-fill. */
    memcpy(changed,image,BYTES); w64(changed+184+152+32,0x40004008);
    w64(changed+184+152+40,24576);
    assert(!check(changed,BYTES)); /* BSS begins in zero file padding. */
    changed[16392]=1; assert(check(changed,BYTES)==ATL_MACHO_LAYOUT); ++rejections;
    reject32(sym_at+8,UINT32_MAX,ATL_MACHO_SYMBOL);
    reject32(sym_at+12,ATL_MACHO_MAX_SYMBOLS+1,ATL_MACHO_LIMIT);
    reject32(sym_at+16,32768,ATL_MACHO_SYMBOL); /* Metadata tables overlap. */
    reject32(sym_at+20,0,ATL_MACHO_SYMBOL);
    reject32(dysym_at+20,5,ATL_MACHO_SYMBOL);
    reject32(dysym_at+28,1,ATL_MACHO_SYMBOL);
    reject32(dysym_at+64,32768,ATL_MACHO_UNSUPPORTED); /* Runtime external relocation. */
    reject32(build_at,0x80000028,ATL_MACHO_UNSUPPORTED); /* LC_MAIN. */
    reject32(build_at,0xe,ATL_MACHO_UNSUPPORTED); /* LC_LOAD_DYLINKER. */
    reject32(build_at,0xc,ATL_MACHO_UNSUPPORTED); /* LC_LOAD_DYLIB. */
    reject32(build_at,0x80000022,ATL_MACHO_UNSUPPORTED); /* LC_DYLD_INFO_ONLY. */
    reject32(build_at+20,1,ATL_MACHO_FORMAT);
    reject32(build_at,2,ATL_MACHO_FORMAT); /* Duplicate LC_SYMTAB. */
    reject64(416+24,UINT64_C(0x50000000),ATL_MACHO_LIMIT); /* Page-rounded span. */
    reject32(thread_at+8,1,ATL_MACHO_ENTRY);
    reject32(thread_at+12,67,ATL_MACHO_ENTRY);
    reject64(thread_at+264,1,ATL_MACHO_ENTRY); /* SP is not loader authority. */
    reject64(thread_at+272,0x40001001,ATL_MACHO_ENTRY);
    reject64(thread_at+272,0x40004000,ATL_MACHO_ENTRY); /* Data. */
    reject64(thread_at+272,0x40008000,ATL_MACHO_ENTRY); /* BSS. */
    reject64(thread_at+272,0x40000000,ATL_MACHO_ENTRY); /* Header, outside instructions. */
    reject32(32768,128,ATL_MACHO_SYMBOL);
    reject32(32768+4,0x0101,ATL_MACHO_SYMBOL); /* N_UNDF despite MH_NOUNDEFS. */
    reject32(32768+4,0x40010f,ATL_MACHO_SYMBOL); /* Weak import. */
    memcpy(changed,image,BYTES); changed[32959]=1; assert(check(changed,BYTES)==ATL_MACHO_SYMBOL); ++rejections;
    /* Unaligned file bytes are legal: all fields are decoded byte by byte. */
    { uint8_t *unaligned=malloc(BYTES+1); assert(unaligned); memcpy(unaligned+1,image,BYTES);
      assert(!check(unaligned+1,BYTES)); free(unaligned); }
    memcpy(changed,image,BYTES);
    assert(atl_macho_plan(changed,BYTES,(struct AtlanticMachoPlan *)(void *)changed)==ATL_MACHO_BOUNDS);
    assert(!memcmp(changed,image,BYTES)); ++cases;
    assert(atl_macho_plan(NULL,BYTES,&plan)==ATL_MACHO_BOUNDS); ++cases;
    assert(atl_macho_plan(image,BYTES,NULL)==ATL_MACHO_BOUNDS); ++cases;
    for (unsigned i=0;i<12000;++i) {
        unsigned pos;
        random=random*1664525u+1013904223u;
        pos=(i&1) ? random%1024 : 32768+random%256;
        memcpy(changed,image,BYTES); changed[pos]^=(uint8_t)(1u<<((random>>24)&7));
        (void)check(changed,BYTES); ++mutations;
    }
    fixture(UINT64_C(0xfffffff007004000)); assert(!check(image,BYTES));
    reject64(32+24,UINT64_C(0xffffffffffffc000),ATL_MACHO_LAYOUT);
}
static void file_contract(const char *path) {
    FILE *f=fopen(path,"rb"); long n; uint8_t *data; struct AtlanticMachoPlan plan;
    assert(f && !fseek(f,0,SEEK_END)); n=ftell(f); assert(n>0 && n<=ATL_MACHO_MAX_BYTES);
    rewind(f); data=malloc((size_t)n); assert(data && fread(data,1,(size_t)n,f)==(size_t)n); fclose(f);
    { int result=check(data,(size_t)n);
      if (result) fprintf(stderr,"Rejected genuine fixture %s: %d\n",path,result);
      assert(!result); }
    assert(!atl_macho_plan(data,(size_t)n,&plan));
    printf("IMAGE {\"entry\":%" PRIu64 ",\"base\":%" PRIu64 ",\"span\":%" PRIu64
           ",\"segments\":%u,\"sections\":%u,\"symbols\":%u}\n",
           plan.entry,plan.virtual_base,plan.virtual_span,plan.segment_count,plan.section_count,plan.symbol_count);
    free(data);
}
int main(int argc, char **argv) {
    contracts();
    for (int i=1;i<argc;++i) file_contract(argv[i]);
    printf("PASS {\"cases\":%u,\"truncations\":%u,\"mutations\":%u,\"rejections\":%u,\"files\":%d}\n",
           cases,truncations,mutations,rejections,argc-1);
    return 0;
}
