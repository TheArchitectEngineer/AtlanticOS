/* SPDX-License-Identifier: MIT - Original host preparation contracts only. */
#include <atlantic/boot_prepare.h>
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned cases, directed, mutations;
static uint8_t *image; static size_t image_bytes;
static struct AtlanticBootInventory inventory;
static struct AtlanticBootRequest request;
static char command[1024];
static void defaults(void) {
    memset(&inventory,0,sizeof(inventory));
    inventory.ram_count=1; inventory.cpu_count=1;
    inventory.ram[0]=(struct AtlanticPhysicalRange){0x40000000,0x8000000};
    inventory.reserved_count=2;
    inventory.reserved[0]=(struct AtlanticPhysicalRange){0x40080000,0x200000};
    inventory.reserved[1]=(struct AtlanticPhysicalRange){0x44000000,0x100000};
    memset(command,' ',sizeof(command)); command[0]='-'; command[1]='v';
    request=(struct AtlanticBootRequest){0x42000000,0x2000000,504,4096,command,2};
}
static int check(void) {
    struct { uint64_t head; struct AtlanticBootPreparation value; uint64_t tail; } guarded;
    struct AtlanticBootPreparation before;
    int status;
    memset(&guarded,0xa5,sizeof(guarded)); before=guarded.value;
    status=atl_xnu_boot_prepare(&inventory,image,image_bytes,&request,&guarded.value); ++cases;
    assert(guarded.head==UINT64_C(0xa5a5a5a5a5a5a5a5) && guarded.tail==guarded.head);
    if (status) assert(!memcmp(&before,&guarded.value,sizeof(before)));
    else {
        const struct AtlanticBootPreparation *v=&guarded.value;
        assert(v->image_pa>=v->managed_pa && v->top_of_data<=v->bootstrap_pa+v->bootstrap_bytes);
        assert(v->bootstrap_pa==v->managed_pa && v->bootstrap_bytes<=v->managed_bytes);
        assert(v->tree_va-v->virtual_base==v->tree_pa-v->managed_pa);
        assert(v->context_pa==v->image_pa+v->image_bytes);
        assert(v->tree_pa==v->context_pa+v->context_bytes && v->boot_args_pa==v->tree_pa+16384);
        assert(!(v->top_of_data&16383) && v->bootstrap_table_pages<=8);
    }
    return status;
}
static uint8_t *read_file(const char *path, size_t *bytes) {
    FILE *f=fopen(path,"rb"); long size; uint8_t *p;
    assert(f && !fseek(f,0,SEEK_END)); size=ftell(f); assert(size>0 && size<=ATL_MACHO_MAX_BYTES);
    rewind(f); *bytes=(size_t)size; p=malloc(*bytes); assert(p && fread(p,1,*bytes,f)==*bytes); fclose(f);
    return p;
}
#define BAD(statement, error) do { defaults(); statement; assert(check()==(error)); ++directed; } while (0)
int main(int argc, char **argv) {
    struct AtlanticBootPreparation prepared;
    assert(argc==4); image=read_file(argv[1],&image_bytes); defaults(); assert(!check());
    assert(!atl_xnu_boot_prepare(&inventory,image,image_bytes,&request,&prepared));
    assert(prepared.virtual_base==UINT64_C(0xfffffff007000000));
    assert(prepared.image_pa==0x42004000 && prepared.image_bytes==0x14000);
    assert(prepared.context_pa==0x42018000 && prepared.context_bytes==0x4000);
    assert(prepared.tree_pa==0x4201c000 && prepared.tree_va==UINT64_C(0xfffffff00701c000));
    assert(prepared.boot_args_pa==0x42020000 && prepared.top_of_data==0x42024000);
    assert(prepared.bootstrap_bytes==0x1e00000 && prepared.bootstrap_table_pages==4);
    { FILE *f=fopen(argv[2],"wb"); assert(f && fwrite(prepared.boot_args,1,1152,f)==1152); fclose(f); }
    BAD(request.managed_pa++,ATL_PREPARE_MEMORY);
    BAD(request.managed_bytes--,ATL_PREPARE_MEMORY);
    BAD(request.managed_bytes=2097152,ATL_PREPARE_MEMORY);
    BAD(request.managed_bytes=0,ATL_PREPARE_MEMORY);
    BAD(request.managed_bytes=UINT64_MAX,ATL_PREPARE_MEMORY);
    BAD(request.managed_bytes=0x4000000,ATL_PREPARE_RESERVED); /* QEMU DTB reach. */
    BAD(request.managed_pa=0x3fe00000,ATL_PREPARE_MEMORY);
    BAD(request.managed_pa=0x47000000,ATL_PREPARE_MEMORY);
    BAD(inventory.ram_count=2,ATL_PREPARE_MEMORY);
    BAD(inventory.ram_count=0,ATL_PREPARE_MEMORY);
    BAD(inventory.cpu_count=0,ATL_PREPARE_MEMORY);
    BAD(inventory.reserved_count=65,ATL_PREPARE_MEMORY);
    BAD(inventory.reserved[1].bytes=0,ATL_PREPARE_MEMORY);
    BAD(inventory.reserved[1].start=UINT64_MAX,ATL_PREPARE_MEMORY);
    BAD(inventory.reserved[1].start=inventory.reserved[0].start,ATL_PREPARE_MEMORY);
    BAD((inventory.reserved[1]=(struct AtlanticPhysicalRange){0x42000000,4096}),ATL_PREPARE_RESERVED);
    BAD((inventory.reserved[1]=(struct AtlanticPhysicalRange){0x43fff000,4096}),ATL_PREPARE_RESERVED);
    BAD((inventory.reserved[1]=(struct AtlanticPhysicalRange){0x41ffffff,2}),ATL_PREPARE_RESERVED);
    BAD(request.tree_bytes=0,ATL_PREPARE_ARGUMENT);
    BAD(request.tree_bytes=16385,ATL_PREPARE_ARGUMENT);
    BAD(request.retained_bytes=0,ATL_PREPARE_ARGUMENT);
    BAD(request.retained_bytes=65537,ATL_PREPARE_ARGUMENT);
    BAD(request.command_bytes=1024,ATL_PREPARE_COMMAND);
    BAD(request.command=NULL,ATL_PREPARE_COMMAND);
    BAD(command[0]=0,ATL_PREPARE_COMMAND);
    BAD(command[0]='\n',ATL_PREPARE_COMMAND);
    BAD(inventory.ram[0].start=UINT64_C(0x8000000000); request.managed_pa=UINT64_C(0x8000000000),ATL_PREPARE_PROFILE);
    defaults(); request.command_bytes=1023; assert(!check());
    defaults(); request.command=NULL; request.command_bytes=0; assert(!check());
    defaults(); request.managed_bytes=4194304; assert(!check());
    defaults(); inventory.reserved[1]=(struct AtlanticPhysicalRange){0x44000000,4096}; assert(!check());
    defaults(); inventory.reserved[1]=(struct AtlanticPhysicalRange){0x100000000,4096}; assert(!check());
    /* A low linked image remains a valid parser fixture, but is not this XNU profile. */
    { uint8_t *high=image; size_t high_bytes=image_bytes;
      image=read_file(argv[3],&image_bytes); assert(check()==ATL_PREPARE_PROFILE); ++directed;
      free(image); image=high; image_bytes=high_bytes; }
    defaults(); image[24]=5; assert(check()==ATL_MACHO_UNSUPPORTED); ++directed; image[24]=1;
    /* A structurally valid larger link span still must fit the selected RAM. */
    { size_t at=32; uint8_t saved[8];
      while (memcmp(image+at+8,"__LINKEDIT",10))
          at+=(size_t)image[at+4] | (size_t)image[at+5]<<8 | (size_t)image[at+6]<<16 | (size_t)image[at+7]<<24;
      memcpy(saved,image+at+24,8);
      for (unsigned i=0;i<8;++i) image[at+24+i]=(uint8_t)((ATL_XNU_BOOT_LINK_BASE+0x1000000)>>(i*8));
      request.managed_bytes=4194304; assert(check()==ATL_PREPARE_SPACE); ++directed;
      memcpy(image+at+24,saved,8); defaults(); }
    { uint8_t *area=malloc(sizeof(prepared)); uint8_t *before=malloc(sizeof(prepared));
      assert(area && before); memset(area,0xa5,sizeof(prepared));
      memcpy(area,&request,sizeof(request)); memcpy(before,area,sizeof(prepared));
      assert(atl_xnu_boot_prepare(&inventory,image,image_bytes,(const void *)area,(void *)area)==ATL_PREPARE_ARGUMENT);
      assert(!memcmp(area,before,sizeof(prepared))); free(area); free(before); ++cases; }
    { struct AtlanticBootPreparation before; memset(&prepared,0xa5,sizeof(prepared)); before=prepared;
      assert(atl_xnu_boot_prepare(NULL,image,image_bytes,&request,&prepared)==ATL_PREPARE_ARGUMENT);
      assert(!memcmp(&before,&prepared,sizeof(before))); ++cases; }
    { uint32_t random=0xa719ef3;
      for (unsigned i=0;i<10000;++i) {
        defaults(); random=random*1664525u+1013904223u;
        switch (i%8) {
        case 0: request.managed_pa^=(uint64_t)random<<12; break;
        case 1: request.managed_bytes=(uint64_t)random<<12; break;
        case 2: request.tree_bytes=random%20000; break;
        case 3: request.retained_bytes=random%80000; break;
        case 4: request.command_bytes=random%1025; break;
        case 5: inventory.reserved_count=random%66; break;
        case 6: inventory.reserved[1]=(struct AtlanticPhysicalRange){0x41e00000+random%0x8000000,random%0x800000}; break;
        default: inventory.ram[0].bytes=random; break;
        }
        (void)check(); ++mutations;
      }
    }
    printf("PASS {\"cases\":%u,\"directed_rejections\":%u,\"mutations\":%u,\"record_bytes\":1152}\n",cases,directed,mutations);
    free(image); return 0;
}
