/* SPDX-License-Identifier: MIT - Check declarations from real XNU headers. */
#include <ipc/ipc_policy.h>
#include <kern/ipc_kobject.h>
_Static_assert(sizeof(mach_msg_option64_t)==8, "native option width");
_Static_assert(IPC_HAS_LEGACY_MACH_MSG_TRAP==0, "selected ARM64 profile has no legacy trap");
_Static_assert(__builtin_types_compatible_p(__typeof__(&ipc_kobject_register_startup),
    void (*)(ipc_kobject_ops_t)), "native registration ABI");
_Static_assert(__builtin_types_compatible_p(__typeof__(&ipc_validate_kmsg_header_from_user),
    mach_msg_return_t (*)(mach_msg_header_t *, mach_msg_send_uctx_t *, mach_msg_option64_t)),
    "native message validation ABI");
#if ATL_TEST_WRONG_POLICY_OPTIONS
mach_msg_return_t (*bad_options)(mach_msg_header_t *,mach_msg_send_uctx_t *,uint32_t) = ipc_validate_kmsg_header_from_user;
#endif
#if ATL_TEST_REQUIRE_PROCESS_ANALYTICS
__typeof__(&ipc_stash_policy_violations_telemetry) unavailable_process_analytics;
#endif
