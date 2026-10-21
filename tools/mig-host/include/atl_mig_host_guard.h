/* SPDX-License-Identifier: MIT - AtlanticOS host-tool adaptation only. */
#pragma once
#if !defined(ATL_MIG_HOST_TOOL) || !defined(__linux__) || !defined(__x86_64__) || !defined(__LP64__)
#error "This bridge is only for the Linux x86_64 LP64 MIG host tool"
#endif
#if defined(KERNEL) || defined(MACH_KERNEL_PRIVATE) || defined(XNU_KERNEL_PRIVATE)
#error "Never include the MIG host bridge in a kernel or target build"
#endif
