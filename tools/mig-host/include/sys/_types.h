/* SPDX-License-Identifier: MIT - Isolate Mach metadata from Darwin libc types. */
#pragma once
#include <atl_mig_host_guard.h>
#include <stdint.h>
typedef uint32_t __darwin_mach_port_t;
typedef unsigned char __darwin_uuid_t[16];
