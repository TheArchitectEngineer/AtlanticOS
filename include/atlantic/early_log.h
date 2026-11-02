/* SPDX-License-Identifier: MIT - Original AtlanticOS early RAM diagnostics. */
#ifndef ATLANTIC_EARLY_LOG_H
#define ATLANTIC_EARLY_LOG_H
#include <stddef.h>
#include <stdint.h>

#define ATL_EARLY_LOG_CAPACITY 16384u
#define ATL_EARLY_LOG_RECORD_CAPACITY 1024u
#define ATL_EARLY_LOG_SNAPSHOT_ABI 1u

enum AtlanticEarlyLogStatus {
    ATL_LOG_OK = 0, ATL_LOG_INVALID = -1, ATL_LOG_BUSY = -2,
    ATL_LOG_BUFFER_SMALL = -3
};

/* Zero-initialize once, before concurrent access; never reset a live instance.
 * All storage must be owned, mapped normal/shareable RAM supporting exclusive
 * accesses. This is NOT a logger for an MMU-off/device-memory entry path.
 * Fields are private to these functions after publication. Counters wrap mod
 * 2^64. contention_seen is a sticky observation, not an exact drop counter. */
struct AtlanticEarlyLog {
    uint32_t gate, contention_seen, head, size;
    uint64_t records, accepted_bytes, overwritten_bytes, truncated_bytes;
    unsigned char data[ATL_EARLY_LOG_CAPACITY];
};

struct AtlanticEarlyLogSnapshot {
    uint32_t abi_version, struct_bytes, data_bytes, contention_seen;
    uint64_t records, accepted_bytes, overwritten_bytes, truncated_bytes;
};

/* Formatter callback context, initialized to zero for each record. No NUL
 * terminator is inserted: these are bytes, including any embedded NUL. */
struct AtlanticEarlyLogRecord {
    size_t bytes;
    uint64_t truncated_bytes;
    unsigned char data[ATL_EARLY_LOG_RECORD_CAPACITY];
};
void atl_early_log_capture(int character, void *record);

/* One weak compare-exchange attempt; no spin, wait, allocation, I/O or drain.
 * Contention (including a spurious weak-CAS failure) returns BUSY and marks
 * contention_seen. Records are committed as a unit; old bytes may be evicted.
 * bytes must be <= CAPACITY. Source must not overlap the instance. A NULL
 * source is allowed only for zero bytes. truncated_bytes describes formatter
 * omissions for this accepted record; rejected records do not add counters.
 * Callers supply valid objects/readable spans; pointer checks do not map RAM. */
enum AtlanticEarlyLogStatus atl_early_log_append(struct AtlanticEarlyLog *log,
    const void *source, size_t bytes, uint64_t truncated_bytes);

/* Copies retained bytes oldest-first and metadata under the same gate.
 * A CAPACITY-byte destination is always large enough. Smaller buffers can
 * return BUFFER_SMALL. On failure, destination and metadata are unchanged.
 * Writable outputs must not overlap each other or the instance. Metadata must
 * be naturally aligned; destination is a byte buffer. NULL/zero is valid for
 * the destination of an empty snapshot. Reading does not consume or clear.
 * contention_seen is sampled atomically and may change during a snapshot. */
enum AtlanticEarlyLogStatus atl_early_log_snapshot(struct AtlanticEarlyLog *log,
    void *destination, size_t capacity, struct AtlanticEarlyLogSnapshot *metadata);
#endif
