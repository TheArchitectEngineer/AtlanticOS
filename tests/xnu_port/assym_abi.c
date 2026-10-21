/* SPDX-License-Identifier: MIT - independent target checks of generated offsets. */
#include <stddef.h>
#include <kern/thread.h>
#include <arm/thread.h>
#include <arm/cpu_data_internal.h>
#include <pexpert/boot.h>
#include <arm64/proc_reg.h>
#include "assym-check.h"
#define CHECK(name, expression) _Static_assert(ATL_ASSYM_##name == (expression), #name " target layout")
CHECK(TH_KSTACKPTR, offsetof(struct thread, machine.kstackptr));
CHECK(TH_THREAD_ID, offsetof(struct thread, thread_id));
CHECK(ACT_CPUDATAP, offsetof(struct thread, machine.CpuDatap));
CHECK(CPU_ACTIVE_THREAD, offsetof(cpu_data_t, cpu_active_thread));
CHECK(SS64_KERNEL_X19, offsetof(arm_kernel_context_t, ss.x[0]));
CHECK(SS64_KERNEL_LR, offsetof(arm_kernel_context_t, ss.lr));
CHECK(SS64_KERNEL_SP, offsetof(arm_kernel_context_t, ss.sp));
CHECK(NS64_KERNEL_D8, offsetof(arm_kernel_context_t, ns.d[0]));
CHECK(BA_VIRT_BASE, offsetof(boot_args, virtBase));
CHECK(BA_PHYS_BASE, offsetof(boot_args, physBase));
CHECK(BA_BOOT_FLAGS, offsetof(boot_args, bootFlags));
/* PAGE_SHIFT is initialized at runtime by arm_init for this upstream profile. */
_Static_assert(ARM_PGSHIFT == 12, "laboratory 4 KiB hardware translation granule");
_Static_assert(VM_KERNEL_LINK_ADDRESS == 0xfffffff007004000ULL, "declared compilation link address");
