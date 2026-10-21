/* SPDX-License-Identifier: MIT - adversarial tests of original FDT parser. */
#include <atlantic/fdt.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static void put32(uint8_t *p,uint32_t v) { p[0]=v>>24;p[1]=v>>16;p[2]=v>>8;p[3]=v; }
static void put64(uint8_t *p,uint64_t v) { put32(p,v>>32);put32(p+4,v); }
static size_t fixture(uint8_t *p) {
    memset(p,0,512);
    put32(p,0xd00dfeed);put32(p+4,99);put32(p+8,56);put32(p+12,88);
    put32(p+16,40);put32(p+20,17);put32(p+24,16);put32(p+32,11);put32(p+36,32);
    put32(p+56,1); /* root node, empty name at 60 */
    put32(p+64,3);put32(p+68,4);put32(p+72,0);memcpy(p+76,"lab",4);
    put32(p+80,2);put32(p+84,9);memcpy(p+88,"compatible",11);
    return 99;
}
int main(void) {
    uint8_t original[512],p[512];
    struct AtlanticFdtView v;
    size_t bytes=fixture(original);
    assert(atl_fdt_open(original,bytes,&v)==0);
    assert(atl_fdt_validate_structure(&v)==0);
    assert(v.reservation_count==0);
    for (size_t cut=0;cut<bytes;++cut) assert(atl_fdt_open(original,cut,&v)!=0);
    memcpy(p,original,512);p[0]^=1;assert(atl_fdt_open(p,512,&v)==ATL_FDT_FORMAT);
    memcpy(p,original,512);put32(p+8,UINT32_MAX);assert(atl_fdt_open(p,512,&v)!=0);
    memcpy(p,original,512);put32(p+12,60);assert(atl_fdt_open(p,512,&v)!=0);
    memcpy(p,original,512);put32(p+20,18);assert(atl_fdt_open(p,512,&v)==ATL_FDT_VERSION);
    memcpy(p,original,512);put32(p+68,UINT32_MAX);
    assert(atl_fdt_open(p,512,&v)==0);assert(atl_fdt_validate_structure(&v)!=0);
    memcpy(p,original,512);p[98]='x';
    assert(atl_fdt_open(p,512,&v)==0);assert(atl_fdt_validate_structure(&v)!=0);
    memcpy(p,original,512);put32(p+80,1);
    assert(atl_fdt_open(p,512,&v)==0);assert(atl_fdt_validate_structure(&v)!=0);
    memcpy(p,original,512);put32(p+84,2);
    assert(atl_fdt_open(p,512,&v)==0);assert(atl_fdt_validate_structure(&v)!=0);
    memcpy(p,original,512);put64(p+40,UINT64_MAX);put64(p+48,2);
    assert(atl_fdt_open(p,512,&v)==ATL_FDT_OVERFLOW);
    /* A valid nonempty memreserve table, then terminator. */
    memset(p,0,512);
    memcpy(p,original,40);put32(p+4,115);put32(p+8,72);put32(p+12,104);
    put64(p+40,0x40000000);put64(p+48,0x1000);memcpy(p+72,original+56,43);
    assert(atl_fdt_open(p,115,&v)==0);assert(v.reservation_count==1);
    uint64_t start,size;
    assert(atl_fdt_reservation(&v,0,&start,&size)==0 && start==0x40000000 && size==0x1000);
    assert(atl_fdt_reservation(&v,1,&start,&size)!=0);
    assert(atl_fdt_validate_structure(&v)==0);
    /* Excessive depth is rejected before indexing beyond the bounded stack. */
    memset(p,0,512);memcpy(p,original,40);
    put32(p+12,500);put32(p+32,0);put32(p+4,500);
    unsigned cursor=56;
    put32(p+cursor,1);cursor+=8;
    for (unsigned i=0;i<32;++i) { put32(p+cursor,1);p[cursor+4]='n';cursor+=8; }
    put32(p+cursor,9);cursor+=4;
    put32(p+36,cursor-56);
    assert(atl_fdt_open(p,500,&v)==0);assert(atl_fdt_validate_structure(&v)==ATL_FDT_DEPTH);
    memcpy(p,original,512);put32(p+36,31);assert(atl_fdt_open(p,512,&v)!=0);
    /* Coverage of malformed inputs without requiring every mutation be invalid. */
    uint32_t seed=0x13579bdf;
    for (unsigned i=0;i<10000;++i) {
        memcpy(p,original,512);
        for (unsigned j=0;j<4;++j) {
            seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;
            p[seed%bytes]^=(uint8_t)(seed>>24);
        }
        if (atl_fdt_open(p,bytes,&v)==0) (void)atl_fdt_validate_structure(&v);
    }
    puts("PASS: bounded FDT fixtures, every truncation, reservation overflow and 10000 mutations");
    return 0;
}
