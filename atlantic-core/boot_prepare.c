/* SPDX-License-Identifier: MIT - Original preparation; not an XNU replacement. */
#include <atlantic/boot_prepare.h>

static int range(uint64_t a, uint64_t n) { return n && n<=UINT64_MAX-a; }
static int overlap(uint64_t a, uint64_t n, uint64_t b, uint64_t m) {
    return n && m && (a<=b ? b-a<n : a-b<m);
}
static int alias(const void *a, size_t n, const void *b, size_t m) {
    uintptr_t ap=(uintptr_t)a, bp=(uintptr_t)b;
    return n>UINTPTR_MAX-ap || m>UINTPTR_MAX-bp || overlap(ap,n,bp,m);
}
static void le16(uint8_t *p, uint16_t n) { p[0]=(uint8_t)n; p[1]=(uint8_t)(n>>8); }
static void le32(uint8_t *p, uint32_t n) {
    for (unsigned i=0;i<4;++i) p[i]=(uint8_t)(n>>(i*8));
}
static void le64(uint8_t *p, uint64_t n) {
    for (unsigned i=0;i<8;++i) p[i]=(uint8_t)(n>>(i*8));
}

int atl_xnu_boot_prepare(const struct AtlanticBootInventory *inventory,
                         const void *image, size_t image_bytes,
                         const struct AtlanticBootRequest *request,
                         struct AtlanticBootPreparation *out) {
    struct AtlanticMachoPlan image_plan;
    struct AtlanticBootPreparation result;
    const uint64_t block=ATL_XNU_BOOT_BLOCK_BYTES, aux=ATL_XNU_BOOT_AUX_PAGE_BYTES;
    uint64_t offset, end, covered_end, va_end;
    uint8_t *record;
    int status;
    if (!inventory || !image || !request || !out ||
        alias(out,sizeof(*out),inventory,sizeof(*inventory)) ||
        alias(out,sizeof(*out),request,sizeof(*request)) ||
        alias(out,sizeof(*out),image,image_bytes)) return ATL_PREPARE_ARGUMENT;
    if (request->command_bytes>=ATL_XNU_BOOT_COMMAND_BYTES ||
        (request->command_bytes && !request->command) ||
        alias(out,sizeof(*out),request->command,request->command_bytes)) return ATL_PREPARE_COMMAND;
    for (size_t i=0;i<request->command_bytes;++i)
        if ((unsigned char)request->command[i]<32 || (unsigned char)request->command[i]>126)
            return ATL_PREPARE_COMMAND;
    if (inventory->ram_count!=1 || inventory->reserved_count>ATL_BOOT_MAX_RESERVED ||
        !inventory->cpu_count || inventory->cpu_count>ATL_BOOT_MAX_CPUS ||
        !range(inventory->ram[0].start,inventory->ram[0].bytes)) return ATL_PREPARE_MEMORY;
    if (!range(request->managed_pa,request->managed_bytes) ||
        (request->managed_pa&(block-1)) || (request->managed_bytes&(block-1)) ||
        request->managed_bytes<2*block || request->managed_bytes>ATL_MACHO_MAX_BYTES ||
        request->managed_pa<inventory->ram[0].start ||
        request->managed_pa-inventory->ram[0].start>inventory->ram[0].bytes ||
        request->managed_bytes>inventory->ram[0].bytes-(request->managed_pa-inventory->ram[0].start))
        return ATL_PREPARE_MEMORY;
    end=request->managed_pa+request->managed_bytes;
    /* Identity mappings use T0SZ=25, even though TCR.IPS permits 40-bit PA. */
    if (end>UINT64_C(0x8000000000)) return ATL_PREPARE_PROFILE;
    for (uint32_t i=0;i<inventory->reserved_count;++i) {
        const struct AtlanticPhysicalRange *r=&inventory->reserved[i];
        if (!range(r->start,r->bytes) ||
            (i && r->start<inventory->reserved[i-1].start+inventory->reserved[i-1].bytes))
            return ATL_PREPARE_MEMORY;
        if (overlap(request->managed_pa,request->managed_bytes,r->start,r->bytes)) return ATL_PREPARE_RESERVED;
    }
    if (request->tree_bytes<8 || request->tree_bytes>ATL_XNU_TREE_MAX_BYTES ||
        !request->retained_bytes || request->retained_bytes>65536u) return ATL_PREPARE_ARGUMENT;
    status=atl_macho_plan(image,image_bytes,&image_plan);
    if (status) return status;
    if (image_plan.virtual_base!=ATL_XNU_BOOT_LINK_BASE) return ATL_PREPARE_PROFILE;
    for (size_t i=0;i<sizeof(result);++i) ((uint8_t *)&result)[i]=0;
    offset=image_plan.virtual_base&(block-1);
    result.managed_pa=request->managed_pa; result.managed_bytes=request->managed_bytes;
    result.dram_pa=inventory->ram[0].start; result.dram_bytes=inventory->ram[0].bytes;
    result.virtual_base=image_plan.virtual_base-offset;
    result.image_pa=request->managed_pa+offset;
    result.image_va=image_plan.virtual_base; result.image_bytes=image_plan.virtual_span;
    if (!range(result.virtual_base,result.managed_bytes)) return ATL_PREPARE_PROFILE;
    va_end=result.virtual_base+result.managed_bytes;
    if (result.virtual_base<UINT64_C(0xffffff8000000000) || !va_end) return ATL_PREPARE_PROFILE;
    /* start_first_cpu subtracts the PA prefix and floors the remaining bytes
     * to L2 entries. Its block mask also maps the prefix before the header. */
    result.bootstrap_pa=request->managed_pa; result.bootstrap_va=result.virtual_base;
    result.bootstrap_bytes=(request->managed_bytes-offset)&~(block-1);
    covered_end=result.bootstrap_pa+result.bootstrap_bytes;
    if (result.image_bytes>end-result.image_pa) return ATL_PREPARE_SPACE;
    result.context_pa=result.image_pa+result.image_bytes;
    result.context_bytes=((uint64_t)request->retained_bytes+aux-1)&~(aux-1);
    result.tree_pa=result.context_pa+result.context_bytes;
    result.boot_args_pa=result.tree_pa+aux;
    result.top_of_data=result.boot_args_pa+aux;
    /* Includes an unused maximum-size page. Actual native early allocations
     * still need an execution bound; this check does not assert their cost. */
    if (result.top_of_data>covered_end || covered_end-result.top_of_data<aux) return ATL_PREPARE_SPACE;
    result.tree_va=result.virtual_base+(result.tree_pa-result.managed_pa);
    result.tree_bytes=request->tree_bytes;
    result.entry_va=image_plan.entry;
    result.entry_pa=result.image_pa+(image_plan.entry-image_plan.virtual_base);
    result.bootstrap_table_pages=2u+
        (uint32_t)(1+(((result.bootstrap_pa&UINT64_C(0x3fffffff))+result.bootstrap_bytes-1)>>30))+
        (uint32_t)(1+(((result.bootstrap_va&UINT64_C(0x3fffffff))+result.bootstrap_bytes-1)>>30));
    if (result.bootstrap_table_pages>8) return ATL_PREPARE_PROFILE;
    record=result.boot_args;
    le16(record,2); le16(record+2,2);
    le64(record+8,result.virtual_base); le64(record+16,result.managed_pa);
    le64(record+24,result.managed_bytes); le64(record+32,result.top_of_data);
    le32(record+88,ATL_XNU_BOOT_MACHINE_TYPE);
    le64(record+96,result.tree_va); le32(record+104,result.tree_bytes);
    for (size_t i=0;i<request->command_bytes;++i) record[108+i]=(uint8_t)request->command[i];
    /* Video, all padding, remaining command bytes and bootFlags stay zero. */
    le64(record+1144,result.dram_bytes);
    for (size_t i=0;i<sizeof(result);++i) ((uint8_t *)out)[i]=((const uint8_t *)&result)[i];
    return 0;
}
