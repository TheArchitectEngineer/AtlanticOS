/* SPDX-License-Identifier: MIT - Genuine XNU VM sleep/wakeup ABI only. */
#include <vm/vm_object_internal.h>
#include <vm/vm_page.h>
#include <vm/vm_page_internal.h>

wait_result_t (*atl_object_sleep)(vm_object_t, vm_object_wait_reason_t,
    wait_interrupt_t, lck_sleep_action_t) = vm_object_sleep;
wait_result_t (*atl_object_wait)(vm_object_t, wait_interrupt_t) = vm_object_paging_wait;
void (*atl_object_wakeup)(vm_object_t, vm_object_wait_reason_t) = vm_object_wakeup;
wait_result_t (*atl_page_sleep)(vm_object_t, vm_page_t,
    wait_interrupt_t, lck_sleep_action_t) = vm_page_sleep;
void (*atl_page_wakeup)(vm_object_t, vm_page_t) = vm_page_wakeup;
void (*atl_page_wakeup_done)(vm_object_t, vm_page_t) = vm_page_wakeup_done;
void (*atl_worker_register)(event_t, page_worker_token_t *) = page_worker_register_worker;

#if ATL_TEST_WRONG_VM_WAIT_ABI
wait_result_t (*atl_bad_vm_sleep)(vm_object_t, vm_object_wait_reason_t,
    uint64_t, lck_sleep_action_t) = vm_object_sleep;
#endif
