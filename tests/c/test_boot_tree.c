/* SPDX-License-Identifier: MIT - independent wire checks and adversarial fixtures. */
#include <atlantic/boot_tree.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>

static void put32(uint8_t *p,uint32_t n) { p[0]=n>>24;p[1]=n>>16;p[2]=n>>8;p[3]=n; }
static void put64(uint8_t *p,uint64_t n) { put32(p,n>>32);put32(p+4,n); }
static uint32_t u32(const uint8_t *p) { return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24; }
static uint64_t u64(const uint8_t *p) { return u32(p)|(uint64_t)u32(p+4)<<32; }
enum Mode { NORMAL, CELLS_ONE, GAP, OVERLAP, DYNAMIC, BAD_RANGES, DUP_CELLS, DUP_CPU,
            RESERVED_OVERFLOW, RAM_OVERFLOW, DISABLED_CPU, AFF3, BAD_REG, MISSING_RAM,
            BAD_CELLS, BAD_RES_CELLS, TOO_MANY_RAM, TOO_MANY_RESERVED, TOO_MANY_CPUS };
struct Fixture { uint8_t p[4096]; uint32_t at,strings; };
static void word(struct Fixture *f,uint32_t n) { put32(f->p+f->at,n);f->at+=4; }
static void begin(struct Fixture *f,const char *name) {
    word(f,1);size_t n=strlen(name)+1;memcpy(f->p+f->at,name,n);f->at+=(n+3)&~3u;
}
static void prop(struct Fixture *f,const char *name,const void *data,uint32_t n) {
    uint32_t index=f->strings;
    size_t len=strlen(name)+1;memcpy(f->p+3072+f->strings,name,len);f->strings+=len;
    word(f,3);word(f,n);word(f,index);if(n)memcpy(f->p+f->at,data,n);f->at+=(n+3)&~3u;
}
static void scalar(struct Fixture *f,const char *name,uint32_t n) { uint8_t p[4];put32(p,n);prop(f,name,p,4); }
static void reg(struct Fixture *f,uint64_t base,uint64_t size,unsigned width) {
    uint8_t p[16];
    if(width==2) { put64(p,base);put64(p+8,size);prop(f,"reg",p,16); }
    else { put32(p,(uint32_t)base);put32(p+4,(uint32_t)size);prop(f,"reg",p,8); }
}
static void cpu(struct Fixture *f,enum Mode mode,uint64_t affinity) {
    uint8_t p[8];char name[32];snprintf(name,sizeof(name),"cpu@%llx",(unsigned long long)affinity);
    begin(f,name);prop(f,"device_type","cpu",4);
    put64(p,mode==AFF3?UINT64_C(0x100000100):affinity);prop(f,"reg",p,8);
    if(mode==DISABLED_CPU)prop(f,"status","disabled",9);
    word(f,2);
}
static size_t fixture(struct Fixture *f,enum Mode mode) {
    memset(f,0,sizeof(*f));f->at=96;
    unsigned width=mode==CELLS_ONE?1:2;
    uint64_t base=width==1?0x40000000:UINT64_C(0x100000000);
    put64(f->p+40,base+0x1000);put64(f->p+48,0x2000); /* memreserve */
    begin(f,"");scalar(f,"#address-cells",mode==BAD_CELLS?3:width);scalar(f,"#size-cells",width);
    if(mode==DUP_CELLS)scalar(f,"#address-cells",width);
    if(mode!=MISSING_RAM) {
        begin(f,"memory");prop(f,"device_type","memory",7);
        if(mode==BAD_REG)scalar(f,"reg",1);
        else reg(f,mode==RAM_OVERFLOW?UINT64_MAX-3:base,0x2000000,width);
        word(f,2);
    }
    if(mode==GAP || mode==OVERLAP) {
        begin(f,"memory@2");prop(f,"device_type","memory",7);
        reg(f,base+(mode==GAP?0x4000000:0x1000000),0x2000000,width);word(f,2);
    }
    if(mode==TOO_MANY_RAM)for(unsigned i=0;i<16;++i) {
        char name[32];snprintf(name,sizeof(name),"memory@extra%x",i);begin(f,name);
        prop(f,"device_type","memory",7);reg(f,base+0x4000000+i*0x2000000,0x1000000,width);word(f,2);
    }
    begin(f,"reserved-memory");scalar(f,"#address-cells",mode==BAD_RES_CELLS?1:width);scalar(f,"#size-cells",width);
    if(mode==BAD_RANGES)scalar(f,"ranges",0);else prop(f,"ranges",0,0);
    begin(f,"firmware@2000");
    if(mode==DYNAMIC)scalar(f,"size",4096);
    else if(mode==TOO_MANY_RESERVED) {
        uint8_t many[64*16];
        for(unsigned i=0;i<64;++i) { put64(many+i*16,base+i*0x2000);put64(many+i*16+8,0x1000); }
        prop(f,"reg",many,sizeof(many)); /* plus the memreserve entry = 65 */
    }
    else reg(f,mode==RESERVED_OVERFLOW?UINT64_MAX-2:base+0x2000,0x2000,width);
    word(f,2);word(f,2);
    begin(f,"cpus");scalar(f,"#address-cells",2);scalar(f,"#size-cells",0);
    cpu(f,mode,0x100);if(mode==DUP_CPU)cpu(f,mode,0x100);
    if(mode==TOO_MANY_CPUS)for(unsigned i=0;i<32;++i)cpu(f,mode,i);
    word(f,2);word(f,2);word(f,9);
    put32(f->p,0xd00dfeed);put32(f->p+4,3072+f->strings);put32(f->p+8,96);
    put32(f->p+12,3072);put32(f->p+16,40);put32(f->p+20,17);put32(f->p+24,16);
    put32(f->p+32,f->strings);put32(f->p+36,f->at-96);
    assert(f->at<3072 && f->strings<1024);
    return 3072+f->strings;
}
static int inventory(struct Fixture *f,enum Mode mode,struct AtlanticBootInventory *m) {
    struct AtlanticFdtView v;
    size_t n=fixture(f,mode);
    assert(atl_fdt_open(f->p,n,&v)==0);
    return atl_boot_inventory(&v,m);
}
static int events(void *context,const struct AtlanticFdtEvent *e) {
    unsigned *count=context;++*count;assert(e->depth<ATL_FDT_MAX_DEPTH);return 0;
}
static int stop(void *context,const struct AtlanticFdtEvent *e) { (void)e;++*(unsigned *)context;return -99; }
/* Independent traversal of the emitted native format, not FDT. */
static size_t native_node(const uint8_t *tree,size_t limit,size_t at,const char *expected,unsigned depth) {
    assert(at+8<=limit && depth<4);
    uint32_t props=u32(tree+at),children=u32(tree+at+4);at+=8;
    unsigned named=0;
    assert(props<=8 && children<=3);
    for(uint32_t i=0;i<props;++i) {
        assert(at+36<=limit && memchr(tree+at,0,32));
        const char *name=(const char *)tree+at;uint32_t n=u32(tree+at+32);at+=36;
        assert(n<=limit-at && ((n+3)&~3u)<=limit-at);
        if(!strcmp(name,"name")) { assert(!named++);assert(n==strlen(expected)+1);assert(!strcmp((const char *)tree+at,expected)); }
        else if(!strcmp(name,"dram-base")) { assert(n==8 && !(at&7));assert(u64(tree+at)==UINT64_C(0x100000000)); }
        else if(!strcmp(name,"dram-size")) { assert(n==8 && !(at&7));assert(u64(tree+at)==0x2000000); }
        else if(!strcmp(name,"reg")) { assert(n==4 && u32(tree+at)==0x100); }
        else if(!strcmp(name,"timebase-frequency")) { assert(n==4 && u32(tree+at)==62500000); }
        else if(!strcmp(name,"state")) { assert(n==8 && !memcmp(tree+at,"running",8)); }
        else { assert(!strcmp(name,"atlantic,padding") && !n); }
        for(uint32_t j=n;j<((n+3)&~3u);++j)assert(tree[at+j]==0);
        at+=(n+3)&~3u;
    }
    assert(named==1);
    if(!depth) {
        assert(children==3);
        at=native_node(tree,limit,at,"chosen",1);
        at=native_node(tree,limit,at,"defaults",1);
        at=native_node(tree,limit,at,"cpus",1);
    } else if(!strcmp(expected,"cpus")) { assert(children==1);at=native_node(tree,limit,at,"cpu",2); }
    else assert(children==0);
    return at;
}
int main(void) {
    struct Fixture f;
    struct AtlanticBootInventory m,empty;
    memset(&empty,0,sizeof(empty));
    assert(inventory(&f,NORMAL,&m)==0 && m.ram_count==1 && m.cpu_count==1);
    assert(m.ram[0].start==UINT64_C(0x100000000) && m.ram[0].bytes==0x2000000);
    assert(m.reserved_count==1 && m.reserved[0].start==m.ram[0].start+0x1000 && m.reserved[0].bytes==0x3000);
    struct AtlanticFdtView v;
    assert(atl_fdt_open(f.p,4096,&v)==0);
    unsigned count=0;assert(atl_fdt_walk(&v,events,&count)==0 && count>10);
    count=0;assert(atl_fdt_walk(&v,stop,&count)==-99 && count==1);
    put32(f.p+f.at-4,2);count=0;assert(atl_fdt_walk(&v,events,&count)!=0 && !count);
    assert(inventory(&f,CELLS_ONE,&m)==0 && m.ram[0].start==0x40000000);
    struct {enum Mode mode;int expected;} failures[]={
        {OVERLAP,ATL_BOOT_AMBIGUOUS},{DYNAMIC,ATL_BOOT_DYNAMIC_RESERVATION},
        {BAD_RANGES,ATL_BOOT_SCHEMA},{DUP_CELLS,ATL_BOOT_AMBIGUOUS},{DUP_CPU,ATL_BOOT_AMBIGUOUS},
        {RESERVED_OVERFLOW,ATL_FDT_OVERFLOW},{RAM_OVERFLOW,ATL_FDT_OVERFLOW},
        {BAD_REG,ATL_BOOT_SCHEMA},{MISSING_RAM,ATL_BOOT_NO_RAM},
        {BAD_CELLS,ATL_BOOT_SCHEMA},{BAD_RES_CELLS,ATL_BOOT_SCHEMA},
        {TOO_MANY_RAM,ATL_BOOT_LIMIT},{TOO_MANY_RESERVED,ATL_BOOT_LIMIT},{TOO_MANY_CPUS,ATL_BOOT_LIMIT}};
    for(size_t i=0;i<sizeof(failures)/sizeof(*failures);++i) {
        memset(&m,0xa5,sizeof(m));assert(inventory(&f,failures[i].mode,&m)==failures[i].expected);
        assert(!memcmp(&m,&empty,sizeof(m)));
    }
    _Alignas(8) uint8_t out[1024];size_t used=0;
    assert(inventory(&f,NORMAL,&m)==0);
    assert(atl_boot_exclude(&m,m.ram[0].start+0x8000,4096)==0 && m.reserved_count==2);
    assert(atl_boot_exclude(&m,0,4096)==ATL_BOOT_SCHEMA);
    assert(atl_xnu_boot_tree(&m,0x80000100,62500000,out,sizeof(out),&used)==0);
    assert(used==504 && native_node(out,used,0,"/",0)==used);
    struct AtlanticBootInventory saved=m;
    assert(atl_xnu_boot_tree(&m,0x100,62500000,out,sizeof(out),&used)==0 && !memcmp(&m,&saved,sizeof(m)));
    assert(atl_xnu_boot_tree(&m,0x100,62500000,&m,sizeof(m),&used)==ATL_BOOT_BUFFER && !memcmp(&m,&saved,sizeof(m)));
    assert(atl_xnu_boot_tree(&m,0x100,62500000,out,sizeof(out),(size_t *)&m)==ATL_BOOT_BUFFER && !memcmp(&m,&saved,sizeof(m)));
    assert(atl_xnu_boot_tree(&m,0x100,UINT64_C(0x100000000),out,sizeof(out),&used)==ATL_BOOT_CPU);
    used=504;
    for(size_t n=0;n<used;++n) {
        size_t wrote=123;memset(out,0xa5,sizeof(out));
        assert(atl_xnu_boot_tree(&m,0x100,62500000,out,n,&wrote)==ATL_BOOT_BUFFER && wrote==0);
        for(size_t j=0;j<sizeof(out);++j)assert(out[j]==0xa5);
    }
    used=123;assert(atl_xnu_boot_tree(&m,0x100,0,out,sizeof(out),&used)==ATL_BOOT_CPU && !used);
    assert(atl_xnu_boot_tree(&m,0x200,62500000,out,sizeof(out),&used)==ATL_BOOT_CPU);
    used=123;assert(atl_xnu_boot_tree(&m,0x100,62500000,out+1,sizeof(out)-1,&used)==ATL_BOOT_BUFFER && !used);
    assert(inventory(&f,GAP,&m)==0 && m.ram_count==2);
    assert(atl_xnu_boot_tree(&m,0x100,62500000,out,sizeof(out),&used)==ATL_BOOT_NOT_CONTIGUOUS);
    assert(inventory(&f,DISABLED_CPU,&m)==0 && !m.cpu_count);
    assert(atl_xnu_boot_tree(&m,0x100,62500000,out,sizeof(out),&used)==ATL_BOOT_CPU);
    assert(inventory(&f,AFF3,&m)==0);
    assert(atl_xnu_boot_tree(&m,UINT64_C(0x100000100),62500000,out,sizeof(out),&used)==ATL_BOOT_CPU);
    assert(atl_fdt_open(f.p,4096,&v)==0);
    uint8_t original[4096];memcpy(original,f.p,sizeof(original));
    assert(atl_boot_inventory(&v,(struct AtlanticBootInventory *)f.p)==ATL_BOOT_BUFFER && !memcmp(original,f.p,sizeof(original)));
    uint32_t seed=0x81fd2311;
    for(unsigned i=0;i<5000;++i) {
        size_t n=fixture(&f,NORMAL);
        for(unsigned j=0;j<4;++j) { seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;f.p[seed%n]^=(uint8_t)(seed>>24); }
        if(atl_fdt_open(f.p,n,&v)==0)(void)atl_boot_inventory(&v,&m);
    }
    puts("PASS: boot inventory, reservation union, native tree wire, all 504 buffer truncations, 5000 FDT mutations");
    return 0;
}
