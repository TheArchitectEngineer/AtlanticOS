/* SPDX-License-Identifier: MIT - Contract boundaries and independent libc comparisons. */
#include <atlantic/string.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static size_t cases;
static uint32_t state = 0x41544c53u;
static uint32_t next(void) { state = state * 1664525u + 1013904223u; return state; }
static int sign(int value) { return (value > 0) - (value < 0); }

static void
boundaries(void)
{
    char dst[12] = "XXXXXXXXXXX";
    assert(atl_string_copy(dst, "abcde", 5) == 5 && !strcmp(dst, "abcd"));
    assert(dst[5] == 'X');
    assert(atl_string_copy(dst, "abcde", 1) == 5 && dst[0] == 0 && dst[1] == 'b');
    strcpy(dst, "keep");
    assert(atl_string_copy(dst, "", 0) == 0 && !strcmp(dst, "keep"));
    assert(atl_string_append(dst, "abc", 0) == 3 && !strcmp(dst, "keep"));
    assert(atl_string_append(dst, "more", 4) == 8 && !strcmp(dst, "keep"));
    strcpy(dst, "abc");
    assert(atl_string_append(dst, "XYZ", 4) == 6 && !strcmp(dst, "abc"));
    assert(atl_string_append(dst, "XYZ", 6) == 6 && !strcmp(dst, "abcXY"));
    assert(atl_string_compare("\x80", "\x7f") > 0);
    assert(atl_memory_compare("\xff", "\x01", 1) > 0);
    assert(atl_memory_compare("a", "b", 0) == 0);
    cases += 10;

    /* Exact malloc extents let ASan catch reads past an unterminated destination. */
    for (size_t cap = 1; cap < 65; ++cap) {
        char *exact = malloc(cap);
        assert(exact);
        memset(exact, 'q', cap);
        assert(atl_string_append(exact, "XY", cap) == cap + 2);
        for (size_t j = 0; j < cap; ++j) assert(exact[j] == 'q');
        free(exact); ++cases;
    }
}

static void
differential(void)
{
    for (unsigned round = 0; round < 10000; ++round) {
        unsigned char a[65], b[65];
        for (size_t i = 0; i < sizeof(a); ++i) { a[i] = (unsigned char)next(); b[i] = (unsigned char)next(); }
        size_t n = next() % sizeof(a);
        assert(sign(atl_memory_compare(a, b, n)) == sign(memcmp(a, b, n)));
        assert(atl_memory_compare(a, a, n) == 0);
        a[next() % sizeof(a)] = 0; b[next() % sizeof(b)] = 0;
        a[64] = b[64] = 0;
        assert(sign(atl_string_compare((char *)a, (char *)b)) == sign(strcmp((char *)a, (char *)b)));
        assert(atl_string_compare((char *)a, (char *)a) == 0);
        cases += 4;
    }
}

static void
capacity_matrix(void)
{
    for (size_t src_length = 0; src_length < 33; ++src_length) {
        char *src = malloc(src_length + 1);
        assert(src);
        for (size_t i = 0; i < src_length; ++i) src[i] = (char)(1 + next() % 255);
        src[src_length] = 0;
        for (size_t cap = 0; cap < 35; ++cap) {
            unsigned char actual[52], expected[52];
            memset(actual, 0xa7, sizeof(actual)); memcpy(expected, actual, sizeof(actual));
            size_t copied = cap ? (src_length < cap - 1 ? src_length : cap - 1) : 0;
            if (cap) { memcpy(expected + 8, src, copied); expected[8 + copied] = 0; }
            assert(atl_string_copy((char *)actual + 8, src, cap) == src_length);
            assert(!memcmp(actual, expected, sizeof(actual))); ++cases;
            for (size_t dst_length = 0; dst_length < 33; ++dst_length) {
                memset(actual, 0xa7, sizeof(actual));
                memset(actual + 8, 'd', dst_length); actual[8 + dst_length] = 0;
                memcpy(expected, actual, sizeof(actual));
                size_t attempted;
                if (dst_length >= cap) attempted = cap + src_length;
                else {
                    attempted = dst_length + src_length;
                    size_t room = cap - dst_length - 1;
                    copied = src_length < room ? src_length : room;
                    memcpy(expected + 8 + dst_length, src, copied);
                    expected[8 + dst_length + copied] = 0;
                }
                assert(atl_string_append((char *)actual + 8, src, cap) == attempted);
                assert(!memcmp(actual, expected, sizeof(actual))); ++cases;
            }
        }
        free(src);
    }
}

int main(void)
{
    boundaries(); differential(); capacity_matrix();
    printf("PASS: %zu original string contract cases; no kernel or hardware execution\n", cases);
    return 0;
}
