/* SPDX-License-Identifier: MIT
 * Verify dependency selection with the actual patched header, not its text.
 * These are compile probes, never signature verification or monitor execution.
 */
#if defined(ATL_TEST_REQUIRE_PPL_MONITOR)
#define XNU_MONITOR 1
#define PMAP_CS 1
#endif
#if defined(ATL_TEST_UPSTREAM_INCLUDE)
#undef CONFIG_ATLANTIC_FIRMWARE
#endif
#include <vm/pmap_cs.h>

_Static_assert(PMAP_CS_PPL_MONITOR == 0, "laboratory has no PPL monitor");
#if PMAP_CS_INCLUDE_CODE_SIGNING
#error laboratory does not select PMAP code signing
#endif
