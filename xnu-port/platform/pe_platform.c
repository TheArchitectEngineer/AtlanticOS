/* SPDX-License-Identifier: MIT - Original AtlanticOS Platform Expert core.
 * Native XNU types and SecureDT remain the actual consumers/providers.
 * No Apple pe_init.c implementation, vendor BSP, or BootShim is included.
 */
#include <pexpert/atlantic.h>
#include <pexpert/arm64/board_config.h>
#include <pexpert/device_tree.h>
#include <kern/debug.h>
#include <libkern/section_keywords.h>
#include <stdint.h>
#include <string.h>

#if !CONFIG_ATLANTIC_FIRMWARE || !defined(__arm64__)
#error AtlanticOS PE core requires the explicit ARM64 firmware profile
#endif
#if defined(MACH_BSD) || defined(IOKIT)
#error AtlanticOS PE core has no BSD or IOKit platform backend
#endif

SECURITY_READ_ONLY_LATE(PE_state_t) PE_state;
clock_frequency_info_t gPEClockFrequencyInfo;
static timebase_callback_func timebase_callback;

static void
require_platform(void)
{
    if (atlantic_pe_platform.abi_version != ATLANTIC_PE_ABI ||
        atlantic_pe_platform.struct_bytes != sizeof(atlantic_pe_platform) ||
        !atlantic_pe_platform.validate_boot_record ||
        !atlantic_pe_platform.validate_tree_mapping ||
        !atlantic_pe_platform.initialize_interrupts) {
        panic("AtlanticOS: missing or incompatible original BSP platform provider");
    }
}

static void
require_tree_mapping(void const *tree, vm_size_t size)
{
    uintptr_t start = (uintptr_t)tree;
    if (!start || (start & 7) || size < 8 || size > ATLANTIC_PE_TREE_MAX ||
        size > UINTPTR_MAX - start ||
        atlantic_pe_platform.validate_tree_mapping(tree, size) != KERN_SUCCESS) {
        panic("AtlanticOS: bootstrap tree mapping is not owned and readable");
    }
}

static uint64_t
read_number(DTEntry entry, const char *name, unsigned int expected_size)
{
    const void *value;
    unsigned int size;
    uint64_t number = 0;
    if (SecureDTGetProperty(entry, name, &value, &size) != kSuccess || size != expected_size) {
        panic("AtlanticOS: missing or invalid native property %s", name);
    }
    /* GetProperty checks the native tree span. memcpy also permits properties
     * that have only the native four-byte structural alignment. */
    memcpy(&number, value, size);
    return number;
}

static void
validate_arguments(boot_args const *args)
{
    if (!args || args->Version != kBootArgsVersion2 || args->Revision != kBootArgsRevision2 ||
        args->machineType != ATLANTIC_PE_MACHINE_TYPE ||
        !args->memSize || !args->memSizeActual || args->memSize > args->memSizeActual ||
        (args->physBase & 0xfff) || (args->virtBase & 0xfff) ||
        args->memSize > UINT64_MAX - args->physBase ||
        args->memSize > UINT64_MAX - args->virtBase ||
        args->topOfKernelData < args->physBase ||
        args->topOfKernelData > args->physBase + args->memSize) {
        panic("AtlanticOS: invalid native boot_args contract");
    }
    unsigned int i;
    for (i = 0; i < sizeof(args->CommandLine) && args->CommandLine[i]; ++i) { }
    if (i == sizeof(args->CommandLine)) {
        panic("AtlanticOS: unterminated native boot command line");
    }
    /* Initial firmware profile is headless. A later verified framebuffer
     * provider must explicitly extend this contract, including ownership. */
    if (args->Video.v_baseAddr || args->Video.v_display || args->Video.v_rowBytes ||
        args->Video.v_width || args->Video.v_height || args->Video.v_depth) {
        panic("AtlanticOS: framebuffer boot contract is not implemented");
    }
    if (atlantic_pe_platform.validate_boot_record(args) != KERN_SUCCESS) {
        panic("AtlanticOS: BSP rejected image, memory or loader ownership");
    }
}

void
PE_init_platform(boolean_t vm_initialized, void *args)
{
    require_platform();
    if (vm_initialized) {
        if (!PE_state.initialized) {
            panic("AtlanticOS: interrupt phase before native boot-data phase");
        }
        /* XNU passes &BootCpuData initially and NULL on its secondary path.
         * This is not a boot_args pointer and must never be dereferenced here. */
        if (atlantic_pe_platform.initialize_interrupts(args) != KERN_SUCCESS) {
            panic("AtlanticOS: original BSP interrupt initialization failed");
        }
        return;
    }
    if (PE_state.initialized) {
        panic("AtlanticOS: duplicate native boot-data initialization");
    }
    boot_args const *boot = args;
    validate_arguments(boot);
    require_tree_mapping(boot->deviceTreeP, boot->deviceTreeLength);
    SecureDTInit(boot->deviceTreeP, boot->deviceTreeLength);
    DTEntry chosen, cpu;
    if (SecureDTLookupEntry(NULL, "/chosen", &chosen) != kSuccess ||
        SecureDTLookupEntry(NULL, "/cpus/cpu", &cpu) != kSuccess) {
        panic("AtlanticOS: native bootstrap tree lacks chosen or primary CPU");
    }
    uint64_t dram_base = read_number(chosen, "dram-base", sizeof(uint64_t));
    uint64_t dram_size = read_number(chosen, "dram-size", sizeof(uint64_t));
    if (!dram_size || dram_size > UINT64_MAX - dram_base ||
        dram_size != boot->memSizeActual || boot->physBase < dram_base ||
        boot->physBase - dram_base > dram_size ||
        boot->memSize > dram_size - (boot->physBase - dram_base)) {
        panic("AtlanticOS: native DRAM metadata disagrees with boot_args");
    }
    uint64_t affinity = __builtin_arm_rsr64("MPIDR_EL1") & UINT64_C(0x000000ff00ffffff);
    uint64_t frequency = __builtin_arm_rsr64("CNTFRQ_EL0");
    const void *state;
    unsigned int state_size;
    if (affinity > UINT32_MAX || !frequency || frequency > UINT32_MAX ||
        read_number(cpu, "reg", sizeof(uint32_t)) != affinity ||
        read_number(cpu, "timebase-frequency", sizeof(uint32_t)) != frequency ||
        SecureDTGetProperty(cpu, "state", &state, &state_size) != kSuccess ||
        state_size != sizeof("running") || memcmp(state, "running", sizeof("running"))) {
        panic("AtlanticOS: native primary CPU or counter does not match hardware");
    }
    gPEClockFrequencyInfo.timebase_frequency_hz = (uint32_t)frequency;
    gPEClockFrequencyInfo.timebase_frequency_num = (uint32_t)frequency;
    gPEClockFrequencyInfo.timebase_frequency_den = 1;
    gPEClockFrequencyInfo.dec_clock_rate_hz = (uint32_t)frequency;
    /* CPU/bus/memory frequencies stay unknown (zero); no Apple defaults. */
    PE_state.bootArgs = (void *)boot;
    PE_state.deviceTreeHead = boot->deviceTreeP;
    PE_state.deviceTreeSize = boot->deviceTreeLength;
    PE_state.initialized = TRUE;
}

void
PE_slide_devicetree(vm_offset_t slide)
{
    require_platform();
    if (!PE_state.initialized) {
        panic("AtlanticOS: tree slide before native boot-data initialization");
    }
    /* Match native vm_offset_t modulo arithmetic: a negative VM delta is
     * represented as unsigned. Permission/ownership is checked independently. */
    void *tree = (void *)((uintptr_t)PE_state.deviceTreeHead + slide);
    require_tree_mapping(tree, PE_state.deviceTreeSize);
    SecureDTInit(tree, PE_state.deviceTreeSize);
    PE_state.deviceTreeHead = tree;
}

void
PE_call_timebase_callback(void)
{
    if (!PE_state.initialized || !gPEClockFrequencyInfo.timebase_frequency_hz) {
        panic("AtlanticOS: timebase requested before native boot-data initialization");
    }
    struct timebase_freq_t frequency = { gPEClockFrequencyInfo.timebase_frequency_hz, 1 };
    if (timebase_callback) {
        timebase_callback(&frequency);
    }
}

void
PE_register_timebase_callback(timebase_callback_func callback)
{
    timebase_callback = callback;
    PE_call_timebase_callback();
}
