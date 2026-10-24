/* SPDX-License-Identifier: MIT - native target wire layout, no redefined XNU types. */
#include <stddef.h>
#include <stdint.h>
#include <pexpert/device_tree.h>
#include <sys/types.h>
_Static_assert(sizeof(void *)==8 && sizeof(unsigned long)==8,"native ARM64 DRAM fields");
_Static_assert(sizeof(DeviceTreeNode)==8,"native tree node bytes");
_Static_assert(offsetof(DeviceTreeNode,nProperties)==0,"native property count");
_Static_assert(offsetof(DeviceTreeNode,nChildren)==4,"native child count");
_Static_assert(sizeof(DeviceTreeNodeProperty)==36,"native property header bytes");
_Static_assert(offsetof(DeviceTreeNodeProperty,length)==32,"native property length");
_Static_assert(kPropNameLength==32 && kDTMaxPropertyNameLength==31,"native property name capacity");
_Static_assert(__alignof__(DeviceTreeNode)==4 && __alignof__(DeviceTreeNodeProperty)==4,"native header alignment");
_Static_assert(__builtin_types_compatible_p(__typeof__(&SecureDTInit),void (*)(void const *,size_t)),"native initializer ABI");
