/* SPDX-License-Identifier: MIT - Real native ABI, with no kernel providers. */
#include <stdint.h>
#include <mach/kern_return.h>
#include <mach/coalition_notification.h>
#include <mach/coalition_notification_server.h>
#include <kern/coalition.h>
#include <bank/bank_internal.h>
#if !CONFIG_COALITIONS || CONFIG_TELEMETRY || MACH_VM_DEBUG
#error This audit requires the selected coalitions/no-telemetry/no-VM-debug profile
#endif
_Static_assert(__builtin_types_compatible_p(__typeof__(&coalition_notification),
    kern_return_t (*)(ipc_port_t,uint64_t,uint32_t)), "native coalition notification ABI");
_Static_assert(__builtin_types_compatible_p(__typeof__(&bank_task_initialize),
    void (*)(task_t)), "native bank task context ABI");
_Static_assert(__builtin_types_compatible_p(__typeof__(&coalition_id),
    uint64_t (*)(coalition_t)), "native coalition ID ABI");
/* Reference fixture only: never selected as a kernel service or linked unit. */
kern_return_t atl_native_failure_reference(void) { return KERN_FAILURE; }
#if ATL_TEST_ABSENT_TELEMETRY_FIELD
uint64_t bad_telemetry_field(bank_task_t task) { return task->bt_rsrc_coal_id; }
#endif
#if ATL_TEST_WRONG_BANK_CALLBACK
void (*bad_bank_callback)(uint32_t) = bank_task_initialize;
#endif
