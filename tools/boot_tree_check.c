/* SPDX-License-Identifier: MIT - host-only inspection of regular FDT files. */
#include <atlantic/boot_tree.h>
#include <inttypes.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
static uint8_t blob[ATL_FDT_MAX_BYTES];
int main(int argc,char **argv) {
    if(argc!=2)return 2;
    FILE *f=fopen(argv[1],"rb");if(!f)return 2;
    struct stat st;
    if(fstat(fileno(f),&st) || !S_ISREG(st.st_mode) || st.st_size<40 ||
       (uint64_t)st.st_size>sizeof(blob)) { fclose(f);return 2; }
    size_t bytes=fread(blob,1,(size_t)st.st_size,f);
    int extra=fgetc(f),bad=ferror(f);fclose(f);
    if(bytes!=(size_t)st.st_size || extra!=EOF || bad)return 2;
    struct AtlanticFdtView v;
    struct AtlanticBootInventory m;
    int status=atl_fdt_open(blob,bytes,&v);
    if(!status)status=atl_boot_inventory(&v,&m);
    if(status) { printf("{\"accepted\":false,\"error\":%d}\n",status);return 1; }
    printf("{\"accepted\":true,\"scope\":\"FDT_DECLARATIONS_ONLY_NOT_PHYSICAL_RAM\",\"bytes\":%zu,\"ram\":[",bytes);
    for(uint32_t i=0;i<m.ram_count;++i)printf("%s{\"start\":%" PRIu64 ",\"bytes\":%" PRIu64 "}",i?",":"",m.ram[i].start,m.ram[i].bytes);
    printf("],\"reserved_union\":[");
    for(uint32_t i=0;i<m.reserved_count;++i)printf("%s{\"start\":%" PRIu64 ",\"bytes\":%" PRIu64 "}",i?",":"",m.reserved[i].start,m.reserved[i].bytes);
    printf("],\"cpu_affinities\":[");
    for(uint32_t i=0;i<m.cpu_count;++i)printf("%s%" PRIu64,i?",":"",m.cpu_affinity[i]);
    printf("]}\n");return 0;
}
