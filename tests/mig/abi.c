/* SPDX-License-Identifier: MIT - Validate the host generator's Mach metadata. */
#include <mach/message.h>
#include <mach/ndr.h>
#include <stddef.h>
#include <stdio.h>
_Static_assert(sizeof(void *) == 8, "LP64 host required");
_Static_assert(sizeof(natural_t) == 4 && sizeof(boolean_t) == 4, "Mach integers");
_Static_assert(sizeof(mach_port_t) == 4 && sizeof(user_addr_t) == 8, "Mach port/address");
_Static_assert(sizeof(vm_offset_t) == 8 && sizeof(NDR_record_t) == 8, "Mach VM/NDR");
_Static_assert(sizeof(mach_msg_header_t) == 24, "Mach message header");
_Static_assert(offsetof(mach_msg_header_t, msgh_id) == 20, "Mach message ID offset");
_Static_assert(sizeof(mach_msg_body_t) == 4, "Mach descriptor count");
_Static_assert(sizeof(mach_msg_port_descriptor_t) == 12, "Port descriptor");
_Static_assert(sizeof(mach_msg_ool_descriptor_t) == 16, "OOL descriptor");
_Static_assert(sizeof(mach_msg_ool_ports_descriptor_t) == 16, "OOL ports descriptor");
_Static_assert(sizeof(mach_msg_guarded_port_descriptor_t) == 16, "Guarded descriptor");
int main(void) {
    puts("PASS: host MIG metadata widths and message layouts; not runtime IPC");
    return 0;
}
