/* SPDX-License-Identifier: MIT - Original AtlanticOS freestanding primitives. */
#ifndef ATLANTIC_STRING_H
#define ATLANTIC_STRING_H
#include <stddef.h>

/* Callers provide valid readable spans / NUL-terminated strings and writable
 * destination capacity. Copy/append source and destination must not overlap.
 * Comparisons use unsigned bytes; only the sign of nonzero results is API.
 * Copy/append return the length attempted, including when truncated; capacity
 * counts the NUL slot. Capacity zero never reads/writes the destination.
 * Append scans the destination only within capacity; if no NUL is found it
 * writes nothing and returns capacity + source length (size_t arithmetic). */
int atl_memory_compare(const void *left, const void *right, size_t bytes);
int atl_string_compare(const char *left, const char *right);
size_t atl_string_copy(char *destination, const char *source, size_t capacity);
size_t atl_string_append(char *destination, const char *source, size_t capacity);
#endif
