/* Original AtlanticOS check of the native MIG runtime configuration. MIT. */
#include <mach/mig.h>

_Static_assert(__MigTypeCheck == 1, "MIG runtime type checks must remain enabled");
_Static_assert(__MigKernelSpecificCode == 1, "MIG must retain native kernel message semantics");
_Static_assert(sizeof(mach_port_t) == 8, "MIG kernel ports are objects");
_Static_assert(sizeof(mach_port_name_t) == 4, "MIG port names remain 32-bit");
