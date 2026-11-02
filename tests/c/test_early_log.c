/* SPDX-License-Identifier: MIT - Original AtlanticOS RAM transport tests. */
#include <atlantic/early_log.h>
#include <assert.h>
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <string.h>

static struct AtlanticEarlyLog log_state;
static unsigned char output[ATL_EARLY_LOG_CAPACITY];
static struct AtlanticEarlyLogSnapshot info;
static unsigned checks;
#define CHECK(x) do { assert(x); ++checks; } while (0)

static void
snapshot(void)
{
    enum AtlanticEarlyLogStatus status;
    do { status = atl_early_log_snapshot(&log_state, output, sizeof(output), &info); }
    while (status == ATL_LOG_BUSY);
    CHECK(status == ATL_LOG_OK);
    CHECK(info.abi_version == 1 && info.struct_bytes == sizeof(info));
}

static void
contracts(void)
{
    struct AtlanticEarlyLogSnapshot before;
    unsigned char saved[sizeof(output)];
    CHECK(atl_early_log_snapshot(&log_state, NULL, 0, &info) == ATL_LOG_OK);
    CHECK(info.data_bytes == 0 && info.records == 0);
    CHECK(atl_early_log_append(&log_state, "abc", 3, 7) == ATL_LOG_OK);
    snapshot();
    CHECK(info.data_bytes == 3 && !memcmp(output, "abc", 3));
    CHECK(info.records == 1 && info.accepted_bytes == 3 && info.truncated_bytes == 7);
    memset(output, 0xa5, sizeof(output)); memset(&info, 0x5a, sizeof(info));
    memcpy(saved, output, sizeof(output)); before = info;
    CHECK(atl_early_log_snapshot(&log_state, output, 2, &info) == ATL_LOG_BUFFER_SMALL);
    CHECK(!memcmp(output, saved, sizeof(output)) && !memcmp(&info, &before, sizeof(info)));
    CHECK(atl_early_log_append(NULL, "x", 1, 0) == ATL_LOG_INVALID);
    CHECK(atl_early_log_append((void *)((unsigned char *)&log_state + 1), "x", 1, 0) == ATL_LOG_INVALID);
    CHECK(atl_early_log_append(&log_state, NULL, 1, 0) == ATL_LOG_INVALID);
    CHECK(atl_early_log_append(&log_state, "x", ATL_EARLY_LOG_CAPACITY + 1, 0) == ATL_LOG_INVALID);
    CHECK(atl_early_log_append(&log_state, log_state.data, 1, 0) == ATL_LOG_INVALID);
    CHECK(atl_early_log_append(&log_state, (void *)(UINTPTR_MAX - 2), 4, 0) == ATL_LOG_INVALID);
    CHECK(atl_early_log_snapshot(&log_state, output, sizeof(output), NULL) == ATL_LOG_INVALID);
    CHECK(atl_early_log_snapshot(&log_state, NULL, 1, &info) == ATL_LOG_INVALID);
    CHECK(atl_early_log_snapshot(&log_state, output, sizeof(output), (void *)(output + 1)) == ATL_LOG_INVALID);
    CHECK(atl_early_log_snapshot(&log_state, log_state.data, 1, &info) == ATL_LOG_INVALID);
    CHECK(atl_early_log_snapshot(&log_state, output, sizeof(output), (void *)&log_state) == ATL_LOG_INVALID);
    CHECK(atl_early_log_snapshot(&log_state, output, sizeof(output), (void *)output) == ATL_LOG_INVALID);
    CHECK(atl_early_log_snapshot(&log_state, (void *)(UINTPTR_MAX - 2), 4, &info) == ATL_LOG_INVALID);
    CHECK(!memcmp(output, saved, sizeof(output)) && !memcmp(&info, &before, sizeof(info)));
    __atomic_store_n(&log_state.gate, 1, __ATOMIC_RELAXED);
    CHECK(atl_early_log_append(&log_state, "busy", 4, 19) == ATL_LOG_BUSY);
    CHECK(atl_early_log_snapshot(&log_state, output, sizeof(output), &info) == ATL_LOG_BUSY);
    CHECK(!memcmp(output, saved, sizeof(output)) && !memcmp(&info, &before, sizeof(info)));
    CHECK(__atomic_load_n(&log_state.contention_seen, __ATOMIC_RELAXED) == 1);
    __atomic_store_n(&log_state.gate, 0, __ATOMIC_RELEASE);
    snapshot();
    CHECK(info.records == 1 && info.truncated_bytes == 7 && info.contention_seen == 1);
    log_state.head = ATL_EARLY_LOG_CAPACITY;
    CHECK(atl_early_log_append(&log_state, "x", 1, 0) == ATL_LOG_INVALID);
    CHECK(atl_early_log_snapshot(&log_state, output, sizeof(output), &info) == ATL_LOG_INVALID);
    log_state.head = 0; log_state.size = ATL_EARLY_LOG_CAPACITY + 1;
    CHECK(atl_early_log_append(&log_state, "x", 1, 0) == ATL_LOG_INVALID);
    CHECK(atl_early_log_snapshot(&log_state, output, sizeof(output), &info) == ATL_LOG_INVALID);
    memset(&log_state, 0, sizeof(log_state)); /* Quiescent fixture only. */
    log_state.records = UINT64_MAX; log_state.accepted_bytes = UINT64_MAX;
    log_state.truncated_bytes = UINT64_MAX;
    CHECK(atl_early_log_append(&log_state, "x", 1, 1) == ATL_LOG_OK);
    snapshot();
    CHECK(info.records == 0 && info.accepted_bytes == 0 && info.truncated_bytes == 0);
}

static uint32_t random_state = 0x19382abcu;
static uint32_t
random_value(void)
{
    random_state ^= random_state << 13;
    random_state ^= random_state >> 17;
    random_state ^= random_state << 5;
    return random_state;
}

static void
model(void)
{
    unsigned char reference[ATL_EARLY_LOG_CAPACITY], input[ATL_EARLY_LOG_CAPACITY];
    size_t size = 0;
    uint64_t total = 0, overwritten = 0, truncated = 0;
    memset(&log_state, 0, sizeof(log_state));
    for (unsigned iteration = 0; iteration < 6000; ++iteration) {
        size_t bytes = random_value() % (sizeof(input) + 1);
        if (iteration % 17 == 0) bytes = 0;
        if (iteration % 31 == 0) bytes = sizeof(input);
        uint64_t omitted = random_value() % 2048;
        for (size_t i = 0; i < bytes; ++i) input[i] = (unsigned char)random_value();
        size_t evicted = size + bytes > sizeof(reference) ? size + bytes - sizeof(reference) : 0;
        memmove(reference, reference + evicted, size - evicted);
        memcpy(reference + size - evicted, input, bytes);
        size += bytes - evicted; total += bytes; overwritten += evicted; truncated += omitted;
        CHECK(atl_early_log_append(&log_state, input, bytes, omitted) == ATL_LOG_OK);
        snapshot();
        CHECK(info.records == iteration + 1 && info.accepted_bytes == total);
        CHECK(info.overwritten_bytes == overwritten && info.truncated_bytes == truncated);
        CHECK(info.data_bytes == size && !memcmp(output, reference, size));
    }
}

static void
capture(void)
{
    struct AtlanticEarlyLogRecord record = { 0 };
    for (unsigned i = 0; i < 3000; ++i) atl_early_log_capture((int)i, &record);
    CHECK(record.bytes == 1024 && record.truncated_bytes == 1976);
    for (size_t i = 0; i < record.bytes; ++i) CHECK(record.data[i] == (unsigned char)i);
    memset(&log_state, 0, sizeof(log_state));
    CHECK(atl_early_log_append(&log_state, record.data, record.bytes, record.truncated_bytes) == ATL_LOG_OK);
    snapshot();
    CHECK(info.data_bytes == 1024 && info.truncated_bytes == 1976);
    CHECK(!memcmp(output, record.data, 1024));
}

enum { THREADS = 4, WRITES = 4000, RECORD_BYTES = 32 };
static uint32_t start, finished, first_accepted;
struct Writer { unsigned id, accepted, busy; };

static void
make_record(unsigned char *record, unsigned id, unsigned sequence)
{
    record[0] = 0xa7; record[1] = (unsigned char)id;
    record[2] = (unsigned char)sequence; record[3] = (unsigned char)(sequence >> 8);
    for (unsigned i = 4; i < RECORD_BYTES; ++i)
        record[i] = (unsigned char)(id * 17 + sequence * 31 + i);
}

static void *
writer(void *context)
{
    struct Writer *state = context;
    while (!__atomic_load_n(&start, __ATOMIC_ACQUIRE)) sched_yield();
    for (unsigned sequence = 0; sequence < WRITES; ++sequence) {
        unsigned char record[RECORD_BYTES]; make_record(record, state->id, sequence);
        enum AtlanticEarlyLogStatus status = atl_early_log_append(&log_state, record, sizeof(record), 0);
        assert(status == ATL_LOG_OK || status == ATL_LOG_BUSY);
        if (status == ATL_LOG_OK) {
            ++state->accepted;
            __atomic_store_n(&first_accepted, 1, __ATOMIC_RELEASE);
        } else ++state->busy;
    }
    __atomic_fetch_add(&finished, 1, __ATOMIC_RELEASE); /* Host test only. */
    return NULL;
}

static void
check_records(void)
{
    int last[THREADS] = { -1, -1, -1, -1 };
    CHECK(info.data_bytes % RECORD_BYTES == 0);
    CHECK(info.accepted_bytes == info.records * RECORD_BYTES);
    CHECK(info.overwritten_bytes == info.accepted_bytes - info.data_bytes);
    for (size_t offset = 0; offset < info.data_bytes; offset += RECORD_BYTES) {
        unsigned char expected[RECORD_BYTES];
        unsigned id = output[offset + 1];
        unsigned sequence = output[offset + 2] | (unsigned)output[offset + 3] << 8;
        CHECK(id < THREADS && sequence < WRITES);
        CHECK((int)sequence > last[id]); last[id] = (int)sequence;
        make_record(expected, id, sequence);
        CHECK(!memcmp(output + offset, expected, sizeof(expected)));
    }
}

static void
concurrent(void)
{
    pthread_t threads[THREADS]; struct Writer states[THREADS] = { 0 };
    memset(&log_state, 0, sizeof(log_state));
    for (unsigned i = 0; i < THREADS; ++i) {
        states[i].id = i; CHECK(pthread_create(&threads[i], NULL, writer, &states[i]) == 0);
    }
    __atomic_store_n(&start, 1, __ATOMIC_RELEASE);
    while (!__atomic_load_n(&first_accepted, __ATOMIC_ACQUIRE) &&
        __atomic_load_n(&finished, __ATOMIC_ACQUIRE) < THREADS) sched_yield();
    CHECK(__atomic_load_n(&first_accepted, __ATOMIC_ACQUIRE));
    while (__atomic_load_n(&finished, __ATOMIC_ACQUIRE) < THREADS) {
        enum AtlanticEarlyLogStatus status = atl_early_log_snapshot(&log_state, output, sizeof(output), &info);
        CHECK(status == ATL_LOG_OK || status == ATL_LOG_BUSY);
        if (status == ATL_LOG_OK) check_records();
    }
    uint64_t accepted = 0, busy = 0;
    for (unsigned i = 0; i < THREADS; ++i) {
        CHECK(pthread_join(threads[i], NULL) == 0);
        accepted += states[i].accepted; busy += states[i].busy;
    }
    snapshot(); check_records();
    CHECK(accepted > 0 && accepted + busy == THREADS * WRITES);
    CHECK(info.records == accepted && info.accepted_bytes == accepted * RECORD_BYTES);
    CHECK(info.overwritten_bytes == accepted * RECORD_BYTES - info.data_bytes);
    CHECK(info.truncated_bytes == 0 && (!busy || info.contention_seen));
    printf("STRESS: %llu accepted, %llu busy, %u bytes retained; no torn records\n",
        (unsigned long long)accepted, (unsigned long long)busy, info.data_bytes);
}

int
main(void)
{
    contracts(); model(); capture(); concurrent();
    printf("PASS: %u checks, 6000 model records and 16000 concurrent attempts; RAM transport only\n", checks);
    return 0;
}
