/* SPDX-License-Identifier: MIT - hand-checked target layout fixtures. */
#if __ATLANTIC_XNU_LAYOUT__ != 1
#error AtlanticOS layout compiler extension is required
#endif
#define SIG(T) __atlantic_layout_signature(T)
#define SUM(T) __atlantic_layout_summary(T)
#define COMPAT(A, B) __atlantic_layout_compatible(A, B)
#define SIGNATURE(T, S) _Static_assert(__builtin_strcmp(SIG(T), S) == 0, #T " signature")
#define SUMMARY(T, S) _Static_assert(SUM(T) == (S), #T " summary")
typedef __UINT64_TYPE__ u64;
_Static_assert(sizeof(void *) == 8 && sizeof(u64) == 8, "AArch64 LP64 fixture");
SIGNATURE(unsigned char, "2");
SIGNATURE(u64, "2");
SIGNATURE(__int128, "22");
SIGNATURE(double, "2");
SIGNATURE(void *, "1");
SIGNATURE(void (*)(void), "1");
typedef void (^block_t)(void);
SIGNATURE(block_t, "1");
SIGNATURE(_Atomic(void *), "1");
SIGNATURE(_Atomic(u64), "2");
SUMMARY(u64, 4);
SUMMARY(void *, 2);

struct pointer_data { void *pointer; u64 data; };
struct same_shape { int *other_pointer; double other_data; };
struct reversed { u64 data; void *pointer; };
SIGNATURE(struct pointer_data, "12");
SIGNATURE(struct same_shape, "12");
SIGNATURE(struct reversed, "21");
SUMMARY(struct pointer_data, 6);
_Static_assert(COMPAT(struct pointer_data, struct same_shape), "distinct records with equal signature");
_Static_assert(!COMPAT(struct pointer_data, struct reversed), "pointer/data order matters");
typedef struct pointer_data alias_t;
_Static_assert(COMPAT(const alias_t, struct pointer_data), "aliases and top qualifiers");
_Static_assert(COMPAT(void, const void), "void identity for caller wildcard check");
_Static_assert(!COMPAT(void, u64), "void is not directly a layout wildcard");

struct packed_pair { unsigned char data; void *pointer; } __attribute__((packed));
_Static_assert(__builtin_offsetof(struct packed_pair, pointer) == 1, "packed pointer offset");
_Static_assert(sizeof(struct packed_pair) == 9, "packed object size");
SIGNATURE(struct packed_pair, "31");
SUMMARY(struct packed_pair, 10);
typedef struct packed_pair packed_array_t[2];
SIGNATURE(packed_array_t, "331");
typedef void *pointer_array_t[3];
SIGNATURE(pointer_array_t, "111");
typedef unsigned char data_array_t[17];
SIGNATURE(data_array_t, "222");

struct padded_data { unsigned char data __attribute__((aligned(16))); };
struct padded_pointer { void *pointer __attribute__((aligned(16))); };
_Static_assert(sizeof(struct padded_data) == 16 && sizeof(struct padded_pointer) == 16, "full padding granule");
SIGNATURE(struct padded_data, "20");
SIGNATURE(struct padded_pointer, "10");
SUMMARY(struct padded_data, 5);
SUMMARY(struct padded_pointer, 3);

union mixed { void *pointer; u64 data; };
SIGNATURE(union mixed, "3");
SUMMARY(union mixed, 8);
struct anonymous_union { union { void *pointer; u64 data; }; unsigned char end; };
SIGNATURE(struct anonymous_union, "32");
struct bits { unsigned data : 1; unsigned : 0; void *pointer; };
_Static_assert(__builtin_offsetof(struct bits, pointer) == 8, "bitfield boundary");
SIGNATURE(struct bits, "21");
union bit_union { unsigned data : 1; void *pointer; };
SIGNATURE(union bit_union, "3");
struct flexible { u64 length; void *items[]; };
_Static_assert(sizeof(struct flexible) == 8, "flexible payload is not stored in header");
SIGNATURE(struct flexible, "2");
typedef double double3_t __attribute__((ext_vector_type(3)));
_Static_assert(sizeof(double3_t) == 32, "vector storage includes tail padding");
SIGNATURE(double3_t, "2220");

/* These are compiler-generated static metadata, with no runtime implementation. */
const char *atlantic_fixture_signature = SIG(struct pointer_data);
unsigned atlantic_fixture_summary = SUM(union mixed);
