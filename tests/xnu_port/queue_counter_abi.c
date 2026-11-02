/* SPDX-License-Identifier: MIT - Native XNU C/C++ queue and counter ABI probes. */
#include <kern/priority_queue.h>
#include <kern/counter.h>
#include <stdint.h>

#if !ATOMIC_COUNTER_USE_PERCPU
#error This ABI probe requires the selected native per-CPU counter profile
#endif

#ifdef __cplusplus
#define ATL_ASSERT static_assert
#define ATL_ALIGNOF alignof
#define ATL_CONST extern const
extern "C" {
#else
#define ATL_ASSERT _Static_assert
#define ATL_ALIGNOF _Alignof
#define ATL_CONST const
#endif

ATL_ASSERT(sizeof(struct priority_queue_entry) == 24, "generic entry");
ATL_ASSERT(sizeof(struct priority_queue_entry_sched) == 24, "sched entry");
ATL_ASSERT(sizeof(struct priority_queue_entry_deadline) == 32, "deadline entry");
ATL_ASSERT(sizeof(struct priority_queue_entry_stable) == 32, "stable entry");
ATL_ASSERT(ATL_ALIGNOF(struct priority_queue_entry_sched) == 8, "entry alignment");
ATL_ASSERT(sizeof(struct priority_queue_min) == 16, "generic queue and comparator");
ATL_ASSERT(sizeof(struct priority_queue_sched_max) == 8, "sched queue");
ATL_ASSERT(sizeof(struct priority_queue_deadline_min) == 8, "deadline queue");
ATL_ASSERT(sizeof(scalable_counter_t) == 8 && sizeof(uint64_t) == 8, "percpu counter widths");

bool (*atl_sched_insert)(struct priority_queue_sched_max *, priority_queue_entry_sched_t) = priority_queue_insert;
bool (*atl_deadline_insert)(struct priority_queue_deadline_min *, priority_queue_entry_deadline_t) = priority_queue_insert;
void (*atl_counter_add)(scalable_counter_t *, uint64_t) = counter_add;
void (*atl_counter_inc_disabled)(scalable_counter_t *) = counter_inc_preemption_disabled;

/* Synthetic wire fixtures, not pointers or measurements from a device. */
ATL_CONST struct priority_queue_entry_sched atl_sched_wire = {
    .next = 0, .prev = 0, .key = 0x1234, .child = -INT64_C(0x123456789a)
};
ATL_CONST struct priority_queue_entry_deadline atl_deadline_wire = {
    .next = 0, .prev = 0, .__key = 0, .child = 0, .deadline = UINT64_C(0x0123456789abcdef)
};

#if ATL_TEST_WRONG_QUEUE_ABI
bool (*atl_bad_queue)(struct priority_queue_sched_max *, priority_queue_entry_deadline_t) = priority_queue_insert;
#endif
#if ATL_TEST_WRONG_COUNTER_ABI
void (*atl_bad_counter)(scalable_counter_t *, uint32_t) = counter_add;
#endif
#ifdef __cplusplus
}
#endif
