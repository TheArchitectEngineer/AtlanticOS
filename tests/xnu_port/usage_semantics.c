/* SPDX-License-Identifier: MIT
 * Real native types: layout constants only; no allocator or XNU execution.
 */
#include <kern/kalloc.h>
#include <vm/vm_pageout_xnu.h>
#include <mach/shared_region.h>
#include <kern/lock_ptr.h>

#define VALUE(name, expression) const unsigned long atl_usage_##name = (expression)
VALUE(ppnum_bytes, sizeof(ppnum_t));
VALUE(ppnum_align, _Alignof(ppnum_t));
VALUE(page_info_bytes, sizeof(struct upl_page_info));
VALUE(page_info_align, _Alignof(struct upl_page_info));
VALUE(page_info_address_offset, __builtin_offsetof(struct upl_page_info, phys_addr));
VALUE(upl_bytes, sizeof(struct upl));
VALUE(upl_align, _Alignof(struct upl));
VALUE(upl_page_list_offset, __builtin_offsetof(struct upl, page_list));
VALUE(upl_object_offset, __builtin_offsetof(struct upl, map_object));
VALUE(slide_bytes, sizeof(struct shared_file_mapping_slide_np));
VALUE(slide_address_offset, __builtin_offsetof(struct shared_file_mapping_slide_np, sms_address));
VALUE(slide_offset_offset, __builtin_offsetof(struct shared_file_mapping_slide_np, sms_file_offset));
VALUE(lock_ptr_bytes, sizeof(hw_lck_ptr_t));
VALUE(ppnum_summary, __atlantic_layout_summary(ppnum_t));
VALUE(page_info_summary, __atlantic_layout_summary(struct upl_page_info));
VALUE(offset_summary, __atlantic_layout_summary(vm_offset_t));
VALUE(slide_summary, __atlantic_layout_summary(struct shared_file_mapping_slide_np));
VALUE(lock_ptr_summary, __atlantic_layout_summary(hw_lck_ptr_t));
