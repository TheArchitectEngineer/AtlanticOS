/* SPDX-License-Identifier: MIT - Original AtlanticOS, no host/kernel services. */
#include <atlantic/string.h>

int
atl_memory_compare(const void *left, const void *right, size_t bytes)
{
    const unsigned char *a = left, *b = right;
    for (size_t i = 0; i < bytes; ++i) {
        if (a[i] != b[i]) return (int)a[i] - (int)b[i];
    }
    return 0;
}

int
atl_string_compare(const char *left, const char *right)
{
    const unsigned char *a = (const unsigned char *)left;
    const unsigned char *b = (const unsigned char *)right;
    while (*a == *b) {
        if (!*a) return 0;
        ++a; ++b;
    }
    return (int)*a - (int)*b;
}

size_t
atl_string_copy(char *destination, const char *source, size_t capacity)
{
    size_t length = 0;
    while (source[length]) {
        if (capacity && length < capacity - 1) destination[length] = source[length];
        ++length;
    }
    if (capacity) destination[length < capacity ? length : capacity - 1] = 0;
    return length;
}

size_t
atl_string_append(char *destination, const char *source, size_t capacity)
{
    size_t used = 0;
    while (used < capacity && destination[used]) ++used;
    /* No destination terminator within capacity: do not access it again. */
    if (used == capacity) {
        size_t length = 0;
        while (source[length]) ++length;
        return capacity + length;
    }
    return used + atl_string_copy(destination + used, source, capacity - used);
}
