/* Original AtlanticOS layout fixture; uses genuine pinned XNU types. MIT. */
#include <stddef.h>
#ifdef MACH_KERNEL_PRIVATE
#include <kern/task.h>
#else
#include <sys/proc_internal.h>
#endif
#include <sys/proc_ro.h>

#ifdef MACH_BSD
#error This fixture requires firmware without BSD userland
#endif
#if !CONFIG_ATLANTIC_FIRMWARE
#error This fixture requires the AtlanticOS firmware profile
#endif

#define VALUE(name, expr) const unsigned long atl_meta_ ## name = (expr)
_Static_assert(sizeof(void *) == 8, "ARM64 pointer ABI");
_Static_assert(sizeof(security_token_t) == 8, "Mach security token ABI");
_Static_assert(sizeof(audit_token_t) == 32, "Mach audit token ABI");
VALUE(ro_bytes, sizeof(struct proc_ro));
VALUE(ro_align, _Alignof(struct proc_ro));
VALUE(owner_offset, offsetof(struct proc_ro, pr_task));
VALUE(proc_offset, offsetof(struct proc_ro, pr_proc));
VALUE(tokens_offset, offsetof(struct proc_ro, task_tokens));
VALUE(flags_offset, offsetof(struct proc_ro, t_flags_ro));
VALUE(ports_offset, offsetof(struct proc_ro, task_control_port_options));
VALUE(payload_offset, offsetof(struct proc_ro, task_data));
VALUE(payload_bytes, sizeof(struct task_ro_data));
#ifdef MACH_KERNEL_PRIVATE
VALUE(task_bytes, sizeof(struct task));
VALUE(task_align, _Alignof(struct task));
VALUE(task_ro_pointer_offset, offsetof(struct task, bsd_info_ro));
_Static_assert(sizeof(((struct task *)0)->bsd_info_ro) == 8, "real metadata pointer");
#else
VALUE(proc_bytes, sizeof(struct proc));
VALUE(proc_align, _Alignof(struct proc));
VALUE(refcount_offset, offsetof(struct proc, p_refcount));
#endif

#ifdef ATL_TEST_WRONG_OWNER_OFFSET
_Static_assert(offsetof(struct proc_ro, pr_task) == ATL_TEST_WRONG_OWNER_OFFSET,
    "AtlanticOS metadata owner offset mismatch");
#endif
