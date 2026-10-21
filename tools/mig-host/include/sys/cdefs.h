/* SPDX-License-Identifier: MIT - Preserve native libc; host-only annotations. */
#pragma once
#include <atl_mig_host_guard.h>
#include_next <sys/cdefs.h>
#define __kernel_ptr_semantics
#define __enum_decl(name, type, ...) typedef type name; enum __VA_ARGS__
#define __options_decl(name, type, ...) typedef type name; enum __VA_ARGS__
#define __header_always_inline static inline __attribute__((always_inline))
#define __swift_unavailable(message)
