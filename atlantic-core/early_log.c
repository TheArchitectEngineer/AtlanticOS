/* SPDX-License-Identifier: MIT - Original AtlanticOS; no host/kernel services. */
#include <atlantic/early_log.h>

_Static_assert(__atomic_always_lock_free(sizeof(uint32_t), 0), "inline 32-bit atomics required");

static int
span_valid(const void *pointer, size_t bytes)
{
    return !bytes || (pointer && bytes <= UINTPTR_MAX - (uintptr_t)pointer);
}

static int
overlap(const void *a, size_t na, const void *b, size_t nb)
{
    return na && nb && (uintptr_t)a < (uintptr_t)b + nb &&
           (uintptr_t)b < (uintptr_t)a + na;
}

static int
log_valid(struct AtlanticEarlyLog *log)
{
    return log && !((uintptr_t)log % _Alignof(struct AtlanticEarlyLog)) &&
           span_valid(log, sizeof(*log));
}

static int
enter(struct AtlanticEarlyLog *log)
{
    uint32_t expected = 0;
    if (__atomic_compare_exchange_n(&log->gate, &expected, 1, 1,
            __ATOMIC_ACQUIRE, __ATOMIC_RELAXED)) return 1;
    /* A single store avoids an unbounded atomic-increment retry loop. */
    __atomic_store_n(&log->contention_seen, 1, __ATOMIC_RELAXED);
    return 0;
}

static void
leave(struct AtlanticEarlyLog *log)
{
    __atomic_store_n(&log->gate, 0, __ATOMIC_RELEASE);
}

void
atl_early_log_capture(int character, void *context)
{
    struct AtlanticEarlyLogRecord *record = context;
    if (record->bytes < sizeof(record->data)) {
        record->data[record->bytes++] = (unsigned char)character;
    } else {
        ++record->truncated_bytes;
    }
}

enum AtlanticEarlyLogStatus
atl_early_log_append(struct AtlanticEarlyLog *log, const void *source, size_t bytes,
    uint64_t truncated_bytes)
{
    if (!log_valid(log) || bytes > ATL_EARLY_LOG_CAPACITY ||
        !span_valid(source, bytes) || overlap(log, sizeof(*log), source, bytes)) {
        return ATL_LOG_INVALID;
    }
    if (!enter(log)) return ATL_LOG_BUSY;
    if (log->head >= ATL_EARLY_LOG_CAPACITY || log->size > ATL_EARLY_LOG_CAPACITY) {
        leave(log);
        return ATL_LOG_INVALID;
    }
    size_t excess = log->size + bytes > ATL_EARLY_LOG_CAPACITY ?
        log->size + bytes - ATL_EARLY_LOG_CAPACITY : 0;
    size_t next = (log->head + log->size) % ATL_EARLY_LOG_CAPACITY;
    const unsigned char *input = source;
    for (size_t i = 0; i < bytes; ++i) {
        log->data[next] = input[i];
        if (++next == ATL_EARLY_LOG_CAPACITY) next = 0;
    }
    log->head = (uint32_t)((log->head + excess) % ATL_EARLY_LOG_CAPACITY);
    log->size = (uint32_t)(log->size + bytes - excess);
    ++log->records;
    log->accepted_bytes += bytes;
    log->overwritten_bytes += excess;
    log->truncated_bytes += truncated_bytes;
    leave(log);
    return ATL_LOG_OK;
}

enum AtlanticEarlyLogStatus
atl_early_log_snapshot(struct AtlanticEarlyLog *log, void *destination, size_t capacity,
    struct AtlanticEarlyLogSnapshot *metadata)
{
    if (!log_valid(log) || !metadata ||
        (uintptr_t)metadata % _Alignof(struct AtlanticEarlyLogSnapshot) ||
        !span_valid(metadata, sizeof(*metadata)) || !span_valid(destination, capacity) ||
        overlap(log, sizeof(*log), destination, capacity) ||
        overlap(log, sizeof(*log), metadata, sizeof(*metadata)) ||
        overlap(destination, capacity, metadata, sizeof(*metadata))) return ATL_LOG_INVALID;
    if (!enter(log)) return ATL_LOG_BUSY;
    if (log->head >= ATL_EARLY_LOG_CAPACITY || log->size > ATL_EARLY_LOG_CAPACITY) {
        leave(log);
        return ATL_LOG_INVALID;
    }
    if (capacity < log->size) {
        leave(log);
        return ATL_LOG_BUFFER_SMALL;
    }
    unsigned char *output = destination;
    size_t next = log->head;
    for (size_t i = 0; i < log->size; ++i) {
        output[i] = log->data[next];
        if (++next == ATL_EARLY_LOG_CAPACITY) next = 0;
    }
    metadata->abi_version = ATL_EARLY_LOG_SNAPSHOT_ABI;
    metadata->struct_bytes = sizeof(*metadata);
    metadata->data_bytes = log->size;
    metadata->contention_seen = __atomic_load_n(&log->contention_seen, __ATOMIC_RELAXED);
    metadata->records = log->records;
    metadata->accepted_bytes = log->accepted_bytes;
    metadata->overwritten_bytes = log->overwritten_bytes;
    metadata->truncated_bytes = log->truncated_bytes;
    leave(log);
    return ATL_LOG_OK;
}
