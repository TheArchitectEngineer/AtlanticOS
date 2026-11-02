/* SPDX-License-Identifier: MIT - Original AtlanticOS/XNU RAM trace boundary. */
#ifndef _PEXPERT_ATLANTIC_LOG_H_
#define _PEXPERT_ATLANTIC_LOG_H_
#include <atlantic/early_log.h>

/* Private boot diagnostics, not native console initialization or serial I/O.
 * The caller must satisfy the normal-RAM and writable-buffer contract of
 * atl_early_log_snapshot. No address/ownership proof is implied by this API. */
enum AtlanticEarlyLogStatus atlantic_xnu_log_snapshot(void *destination,
    size_t capacity, struct AtlanticEarlyLogSnapshot *metadata);
#endif
