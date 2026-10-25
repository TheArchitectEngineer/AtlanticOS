/* Original AtlanticOS fixture for genuine MIG/kernel declarations. MIT. */
#include <stddef.h>
#include <mach/mach_notify.h>
#include <mach/mach_notify_server.h>
#include <mach/coalition_notification.h>
#include <mach/coalition_notification_server.h>
#include <device/device_server.h>
#include <ipc/ipc_port.h>

#if !IMPORTANCE_INHERITANCE
#error AtlanticOS IPC core requires native importance inheritance
#endif
#ifdef MACH_BSD
#error This fixture does not enable BSD userland
#endif
#ifdef IOKIT
#error This fixture does not enable IOKit
#endif

_Static_assert(sizeof(mach_port_t) == 8, "kernel port pointer ABI");
_Static_assert(sizeof(mach_port_name_t) == 4, "port names remain 32-bit values");
_Static_assert(__builtin_types_compatible_p(__typeof__(&coalition_notification),
    kern_return_t (*)(ipc_port_t,uint64_t,uint32_t)), "native coalition sender ABI across both header roles");
_Static_assert(sizeof(((__Request__coalition_notification_t *)0)->id)==8, "native coalition ID width");
_Static_assert(sizeof(((__Request__coalition_notification_t *)0)->flags)==4, "native coalition flags width");
_Static_assert(__builtin_types_compatible_p(mach_port_t, ipc_port_t),
    "kernel sender must use port objects");
_Static_assert(__builtin_types_compatible_p(__typeof__(&mach_notify_port_deleted),
    kern_return_t (*)(mach_port_t, mach_port_name_t)), "native notification sender ABI");
_Static_assert(offsetof(__Request__mach_notify_port_deleted_t, name) ==
    sizeof(mach_msg_header_t) + sizeof(NDR_record_t), "native MIG request field offset");
_Static_assert(iokit_MSG_COUNT == 0, "disabled IOKit must export no device RPCs");
_Static_assert(sizeof(is_iokit_subsystem.kroutine) == 0, "native device server has no routines");
_Static_assert(__builtin_types_compatible_p(__typeof__(&iokit_server),
    boolean_t (*)(mach_msg_header_t *, void *, mach_msg_max_trailer_t *,
                  mach_msg_header_t *, void *)), "native kernel MIG server ABI");

#ifdef ATL_TEST_PORT_NAME_AS_OBJECT
kern_return_t atlantic_bad_kernel_sender(void)
{
    return mach_notify_port_deleted((mach_port_name_t)1, 1);
}
#endif

#ifdef ATL_TEST_COALITION_PORT_NAME
kern_return_t atlantic_bad_coalition_sender(void)
{
    return coalition_notification((mach_port_name_t)1, 1, 0);
}
#endif

#ifdef ATL_TEST_LEGACY_SERVER_ABI
boolean_t (*atlantic_bad_server)(mach_msg_header_t *, mach_msg_header_t *) = iokit_server;
#endif
