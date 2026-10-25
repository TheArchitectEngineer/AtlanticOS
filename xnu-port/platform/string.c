/* SPDX-License-Identifier: MIT - Original AtlanticOS providers of native ABI.
 * Unique C names avoid collisions with XNU's inline overloads. The assembly
 * names are the exact external ABI those native headers and callers require.
 * The actual implementations are the original freestanding primitives.
 */
#include <string.h>
#include <atlantic/string.h>

#if !CONFIG_ATLANTIC_FIRMWARE || !defined(__arm64__)
#error AtlanticOS string providers require the explicit ARM64 firmware profile
#endif

int atlantic_xnu_strcmp(const char *, const char *) __asm("_strcmp");
int atlantic_xnu_memcmp(const void *, const void *, size_t) __asm("_memcmp");
size_t atlantic_xnu_strlcpy(char *, const char *, size_t) __asm("_strlcpy");
size_t atlantic_xnu_strlcat(char *, const char *, size_t) __asm("_strlcat");

_Static_assert(__builtin_types_compatible_p(__typeof__(&atlantic_xnu_strcmp), __typeof__(&strcmp)), "native strcmp ABI");
_Static_assert(__builtin_types_compatible_p(__typeof__(&atlantic_xnu_memcmp), __typeof__(&memcmp)), "native memcmp ABI");
_Static_assert(__builtin_types_compatible_p(__typeof__(&atlantic_xnu_strlcpy), __typeof__(&strlcpy)), "native strlcpy ABI");
_Static_assert(__builtin_types_compatible_p(__typeof__(&atlantic_xnu_strlcat), __typeof__(&strlcat)), "native strlcat ABI");

int atlantic_xnu_strcmp(const char *a, const char *b) { return atl_string_compare(a, b); }
int atlantic_xnu_memcmp(const void *a, const void *b, size_t n) { return atl_memory_compare(a, b, n); }
size_t atlantic_xnu_strlcpy(char *dst, const char *src, size_t n) { return atl_string_copy(dst, src, n); }
size_t atlantic_xnu_strlcat(char *dst, const char *src, size_t n) { return atl_string_append(dst, src, n); }
