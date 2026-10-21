/* SPDX-License-Identifier: MIT - AtlanticOS internal producer/consumer ABI. */
#include <stddef.h>
#include <pexpert/boot.h>
_Static_assert(sizeof(void *) == 8, "ARM64 pointers");
_Static_assert(BOOT_LINE_LENGTH == 1024, "AtlanticOS boot line capacity");
_Static_assert(sizeof(Boot_Video) == 48, "Video metadata ABI");
_Static_assert(sizeof(boot_args) == 1152, "AtlanticOS boot_args size");
_Static_assert(offsetof(boot_args, virtBase) == 8, "virtBase offset");
_Static_assert(offsetof(boot_args, physBase) == 16, "physBase offset");
_Static_assert(offsetof(boot_args, Video) == 40, "Video offset");
_Static_assert(offsetof(boot_args, deviceTreeP) == 96, "tree pointer offset");
_Static_assert(offsetof(boot_args, CommandLine) == 108, "command line offset");
_Static_assert(offsetof(boot_args, bootFlags) == 1136, "flags offset");
_Static_assert(offsetof(boot_args, memSizeActual) == 1144, "actual memory offset");
