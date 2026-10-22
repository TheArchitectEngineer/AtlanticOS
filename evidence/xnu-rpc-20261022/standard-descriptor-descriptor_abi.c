#include <stddef.h>
#include <mach/mig.h>
#include <mach/arcade_register_server.h>
#include <mach/clock_server.h>
#include <mach/exc_server.h>
#include <mach/host_priv_server.h>
#include <mach/mach_eventlink_server.h>
#include <mach/mach_exc_server.h>
#include <mach/mach_host_server.h>
#include <mach/mach_notify_server.h>
#include <mach/mach_port_server.h>
#include <mach/mach_vm_server.h>
#include <mach/mach_voucher_server.h>
#include <mach/memory_entry_server.h>
#include <mach/processor_server.h>
#include <mach/processor_set_server.h>
#include <mach/restartable_server.h>
#include <mach/task_server.h>
#include <mach/thread_act_server.h>
#include <mach/upl_server.h>
#include <mach/vm_map_server.h>
#include <mach/vm32_map_server.h>
#include <device/device_server.h>
#ifdef ATL_TEST_WRONG_DESCRIPTOR_PREFIX
_Static_assert(offsetof(struct mig_kern_subsystem, kroutine) ==
    offsetof(struct mig_kern_subsystem, kroutine) + 1,
    "AtlanticOS MIG descriptor prefix mismatch");
#endif
_Static_assert(offsetof(__typeof__(arcade_register_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "arcade_register_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(arcade_register_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "arcade_register_subsystem start offset");
_Static_assert(offsetof(__typeof__(arcade_register_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "arcade_register_subsystem end offset");
_Static_assert(offsetof(__typeof__(arcade_register_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "arcade_register_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(arcade_register_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "arcade_register_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(arcade_register_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "arcade_register_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(arcade_register_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(arcade_register_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(clock_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "clock_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(clock_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "clock_subsystem start offset");
_Static_assert(offsetof(__typeof__(clock_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "clock_subsystem end offset");
_Static_assert(offsetof(__typeof__(clock_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "clock_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(clock_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "clock_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(clock_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "clock_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(clock_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(clock_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(catch_exc_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "catch_exc_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(catch_exc_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "catch_exc_subsystem start offset");
_Static_assert(offsetof(__typeof__(catch_exc_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "catch_exc_subsystem end offset");
_Static_assert(offsetof(__typeof__(catch_exc_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "catch_exc_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(catch_exc_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "catch_exc_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(catch_exc_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "catch_exc_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(catch_exc_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(catch_exc_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(host_priv_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "host_priv_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(host_priv_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "host_priv_subsystem start offset");
_Static_assert(offsetof(__typeof__(host_priv_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "host_priv_subsystem end offset");
_Static_assert(offsetof(__typeof__(host_priv_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "host_priv_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(host_priv_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "host_priv_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(host_priv_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "host_priv_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(host_priv_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(host_priv_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(mach_eventlink_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "mach_eventlink_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(mach_eventlink_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "mach_eventlink_subsystem start offset");
_Static_assert(offsetof(__typeof__(mach_eventlink_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "mach_eventlink_subsystem end offset");
_Static_assert(offsetof(__typeof__(mach_eventlink_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "mach_eventlink_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(mach_eventlink_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "mach_eventlink_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(mach_eventlink_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "mach_eventlink_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(mach_eventlink_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(mach_eventlink_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(catch_mach_exc_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "catch_mach_exc_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(catch_mach_exc_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "catch_mach_exc_subsystem start offset");
_Static_assert(offsetof(__typeof__(catch_mach_exc_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "catch_mach_exc_subsystem end offset");
_Static_assert(offsetof(__typeof__(catch_mach_exc_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "catch_mach_exc_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(catch_mach_exc_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "catch_mach_exc_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(catch_mach_exc_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "catch_mach_exc_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(catch_mach_exc_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(catch_mach_exc_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(mach_host_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "mach_host_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(mach_host_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "mach_host_subsystem start offset");
_Static_assert(offsetof(__typeof__(mach_host_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "mach_host_subsystem end offset");
_Static_assert(offsetof(__typeof__(mach_host_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "mach_host_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(mach_host_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "mach_host_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(mach_host_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "mach_host_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(mach_host_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(mach_host_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(do_notify_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "do_notify_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(do_notify_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "do_notify_subsystem start offset");
_Static_assert(offsetof(__typeof__(do_notify_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "do_notify_subsystem end offset");
_Static_assert(offsetof(__typeof__(do_notify_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "do_notify_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(do_notify_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "do_notify_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(do_notify_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "do_notify_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(do_notify_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(do_notify_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(mach_port_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "mach_port_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(mach_port_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "mach_port_subsystem start offset");
_Static_assert(offsetof(__typeof__(mach_port_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "mach_port_subsystem end offset");
_Static_assert(offsetof(__typeof__(mach_port_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "mach_port_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(mach_port_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "mach_port_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(mach_port_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "mach_port_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(mach_port_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(mach_port_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(mach_vm_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "mach_vm_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(mach_vm_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "mach_vm_subsystem start offset");
_Static_assert(offsetof(__typeof__(mach_vm_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "mach_vm_subsystem end offset");
_Static_assert(offsetof(__typeof__(mach_vm_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "mach_vm_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(mach_vm_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "mach_vm_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(mach_vm_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "mach_vm_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(mach_vm_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(mach_vm_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(mach_voucher_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "mach_voucher_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(mach_voucher_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "mach_voucher_subsystem start offset");
_Static_assert(offsetof(__typeof__(mach_voucher_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "mach_voucher_subsystem end offset");
_Static_assert(offsetof(__typeof__(mach_voucher_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "mach_voucher_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(mach_voucher_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "mach_voucher_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(mach_voucher_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "mach_voucher_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(mach_voucher_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(mach_voucher_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(memory_entry_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "memory_entry_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(memory_entry_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "memory_entry_subsystem start offset");
_Static_assert(offsetof(__typeof__(memory_entry_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "memory_entry_subsystem end offset");
_Static_assert(offsetof(__typeof__(memory_entry_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "memory_entry_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(memory_entry_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "memory_entry_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(memory_entry_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "memory_entry_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(memory_entry_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(memory_entry_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(processor_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "processor_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(processor_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "processor_subsystem start offset");
_Static_assert(offsetof(__typeof__(processor_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "processor_subsystem end offset");
_Static_assert(offsetof(__typeof__(processor_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "processor_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(processor_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "processor_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(processor_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "processor_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(processor_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(processor_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(processor_set_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "processor_set_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(processor_set_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "processor_set_subsystem start offset");
_Static_assert(offsetof(__typeof__(processor_set_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "processor_set_subsystem end offset");
_Static_assert(offsetof(__typeof__(processor_set_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "processor_set_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(processor_set_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "processor_set_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(processor_set_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "processor_set_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(processor_set_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(processor_set_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(task_restartable_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "task_restartable_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(task_restartable_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "task_restartable_subsystem start offset");
_Static_assert(offsetof(__typeof__(task_restartable_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "task_restartable_subsystem end offset");
_Static_assert(offsetof(__typeof__(task_restartable_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "task_restartable_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(task_restartable_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "task_restartable_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(task_restartable_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "task_restartable_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(task_restartable_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(task_restartable_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(task_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "task_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(task_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "task_subsystem start offset");
_Static_assert(offsetof(__typeof__(task_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "task_subsystem end offset");
_Static_assert(offsetof(__typeof__(task_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "task_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(task_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "task_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(task_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "task_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(task_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(task_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(thread_act_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "thread_act_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(thread_act_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "thread_act_subsystem start offset");
_Static_assert(offsetof(__typeof__(thread_act_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "thread_act_subsystem end offset");
_Static_assert(offsetof(__typeof__(thread_act_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "thread_act_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(thread_act_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "thread_act_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(thread_act_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "thread_act_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(thread_act_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(thread_act_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(upl_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "upl_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(upl_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "upl_subsystem start offset");
_Static_assert(offsetof(__typeof__(upl_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "upl_subsystem end offset");
_Static_assert(offsetof(__typeof__(upl_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "upl_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(upl_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "upl_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(upl_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "upl_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(upl_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(upl_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(vm_map_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "vm_map_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(vm_map_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "vm_map_subsystem start offset");
_Static_assert(offsetof(__typeof__(vm_map_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "vm_map_subsystem end offset");
_Static_assert(offsetof(__typeof__(vm_map_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "vm_map_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(vm_map_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "vm_map_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(vm_map_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "vm_map_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(vm_map_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(vm_map_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(vm32_map_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "vm32_map_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(vm32_map_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "vm32_map_subsystem start offset");
_Static_assert(offsetof(__typeof__(vm32_map_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "vm32_map_subsystem end offset");
_Static_assert(offsetof(__typeof__(vm32_map_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "vm32_map_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(vm32_map_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "vm32_map_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(vm32_map_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "vm32_map_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(vm32_map_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(vm32_map_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
_Static_assert(offsetof(__typeof__(is_iokit_subsystem), kserver) == offsetof(struct mig_kern_subsystem, kserver), "is_iokit_subsystem kserver offset");
_Static_assert(offsetof(__typeof__(is_iokit_subsystem), start) == offsetof(struct mig_kern_subsystem, start), "is_iokit_subsystem start offset");
_Static_assert(offsetof(__typeof__(is_iokit_subsystem), end) == offsetof(struct mig_kern_subsystem, end), "is_iokit_subsystem end offset");
_Static_assert(offsetof(__typeof__(is_iokit_subsystem), maxsize) == offsetof(struct mig_kern_subsystem, maxsize), "is_iokit_subsystem maxsize offset");
_Static_assert(offsetof(__typeof__(is_iokit_subsystem), reserved) == offsetof(struct mig_kern_subsystem, reserved), "is_iokit_subsystem reserved offset");
_Static_assert(offsetof(__typeof__(is_iokit_subsystem), kroutine) == offsetof(struct mig_kern_subsystem, kroutine), "is_iokit_subsystem kroutine offset");
_Static_assert(__builtin_types_compatible_p(__typeof__(is_iokit_subsystem.kserver), mig_kern_server_routine_t), "native kernel demux type");
_Static_assert(sizeof(is_iokit_subsystem.kroutine[0]) == sizeof(struct kern_routine_descriptor), "native routine descriptor stride");
