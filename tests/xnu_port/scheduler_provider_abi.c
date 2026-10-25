/* SPDX-License-Identifier: MIT - Contracts against genuine XNU target headers. */
#include <stddef.h>
#include <stdint.h>
#include <mach/kern_return.h>
#include <mach/mach_traps.h>
#include <ipc/ipc_policy.h>
#include <mach/mk_timer.h>
#include <kern/thread.h>
#include <kern/policy_internal.h>
#include <kern/timeout.h>
#include <kern/counter.h>
#if CONFIG_SCHED_SFI
#error This audit requires the selected profile with SFI disabled
#endif
_Static_assert(sizeof(struct mk_timer_arm_trap_args)==16, "native padded arm arguments");
_Static_assert(offsetof(struct mk_timer_arm_trap_args,expire_time)==8, "native deadline slot");
_Static_assert(sizeof(struct mk_timer_arm_leeway_trap_args)==32, "native leeway arguments");
_Static_assert(offsetof(struct mk_timer_arm_leeway_trap_args,mk_leeway)==24, "native leeway slot");
_Static_assert(sizeof(struct mk_timer_cancel_trap_args)==16, "native cancel arguments");
_Static_assert(sizeof(((struct mk_timer_cancel_trap_args *)0)->result_time)==8, "native output address width");
_Static_assert(__builtin_types_compatible_p(__typeof__(&mk_timer_port_label_dealloc),
    void (*)(ipc_object_label_t)), "native timer label callback");
_Static_assert(__builtin_types_compatible_p(__typeof__(&task_policy_create),
    void (*)(task_t,task_t)), "native task policy creation");
_Static_assert(__builtin_types_compatible_p(__typeof__(&thread_policy_create),
    void (*)(thread_t)), "native thread policy creation");
_Static_assert(__builtin_types_compatible_p(__typeof__(&scalable_counter_static_init),
    void (*)(scalable_counter_t *)), "native per-CPU counter initialization");
/* This reference fixture is never selected in the kernel build or link. */
kern_return_t atl_native_unsupported_reference(void) { return KERN_NOT_SUPPORTED; }
#if ATL_TEST_NARROW_TIMER_DEADLINE
uint32_t *bad_deadline(struct mk_timer_arm_trap_args *args) { return &args->expire_time; }
#endif
#if ATL_TEST_WRONG_LABEL_CALLBACK
void (*bad_label_callback)(uintptr_t) = mk_timer_port_label_dealloc;
#endif
