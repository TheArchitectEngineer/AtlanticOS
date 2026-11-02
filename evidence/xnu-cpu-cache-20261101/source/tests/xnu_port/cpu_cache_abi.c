/* SPDX-License-Identifier: MIT - Genuine CPU/cache types; no hardware values. */
#include <stddef.h>
#include <stdint.h>
#include <pexpert/arm64/board_config.h>
#include <arm/cpuid.h>
#include <arm/cpuid_internal.h>
#if defined(HAS_APPLE_PAC)
#error Current non-PAC profile must not select native ARMv8E normalization
#endif
_Static_assert(CPU_ARCH_ARMv8==12 && CPU_ARCH_ARMv8E==13,"native architecture tags");
_Static_assert(sizeof(arm_cpu_info_t)==4,"native MIDR representation");
_Static_assert(sizeof(cache_info_t)==48,"native cache metadata");
_Static_assert(offsetof(cache_info_t,c_valid)==0 && sizeof(((cache_info_t *)0)->c_valid)==4,"boolean_t validity");
_Static_assert(offsetof(cache_info_t,c_linesz)==28 && offsetof(cache_info_t,c_inner_cache_size)==44,"cache fields");
_Static_assert(sizeof(csselr_cache_level)==4 && sizeof(csselr_cache_type)==4,"selector argument width");
_Static_assert(__builtin_types_compatible_p(__typeof__(&machine_read_midr),uint32_t (*)(void)),"native MIDR read");
_Static_assert(__builtin_types_compatible_p(__typeof__(&machine_read_clidr),uint32_t (*)(void)),"native CLIDR read");
_Static_assert(__builtin_types_compatible_p(__typeof__(&machine_read_ccsidr),uint32_t (*)(void)),"native CCSIDR read");
_Static_assert(__builtin_types_compatible_p(__typeof__(&machine_write_csselr),void (*)(csselr_cache_level,csselr_cache_type)),"native selector");
_Static_assert(__builtin_types_compatible_p(__typeof__(&cpuid_info),arm_cpu_info_t *(*)(void)),"native CPU pointer");
_Static_assert(__builtin_types_compatible_p(__typeof__(&cache_info_type),cache_info_t *(*)(cluster_type_t)),"native per-cluster pointer");
/* Synthetic field-layout fixture, never a measured CPU ID or kernel provider. */
const arm_cpu_info_t atl_native_cpuid_layout={.arm_info={
    .arm_rev=3,.arm_part=0xabc,.arm_arch=CPU_ARCH_ARMv8,.arm_variant=2,.arm_implementor=CPU_VID_ARM,
}};
#if ATL_TEST_WRONG_MIDR_WIDTH
uint64_t (*bad_midr)(void)=machine_read_midr;
#endif
#if ATL_TEST_WRONG_CACHE_POINTER
uint32_t (*bad_cache)(cluster_type_t)=cache_info_type;
#endif
