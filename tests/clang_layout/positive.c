/* SPDX-License-Identifier: MIT - hand-checked target layout fixtures. */
#if __ATLANTIC_XNU_LAYOUT__ != 2
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

/* Usage is a declaration annotation, independent of C type compatibility. */
#define PTR_USE __attribute__((annotate("atlantic.layout.pointer")))
#define DATA_USE __attribute__((annotate("atlantic.layout.data")))
#define DUAL_USE __attribute__((annotate("atlantic.layout.dual")))
typedef u64 pointer_usage_t PTR_USE;
typedef pointer_usage_t pointer_alias_t;
typedef pointer_usage_t data_override_t DATA_USE;
typedef u64 dual_usage_t DUAL_USE;
typedef unsigned int page_number_t PTR_USE;
typedef unsigned int pointer_array_usage_t[3] PTR_USE;
SIGNATURE(pointer_usage_t, "1");
SIGNATURE(const pointer_alias_t, "1");
SUMMARY(pointer_alias_t, 2);
SIGNATURE(data_override_t, "2");
SIGNATURE(dual_usage_t, "3");
SUMMARY(dual_usage_t, 8);
SIGNATURE(pointer_array_usage_t, "11");
SIGNATURE(_Atomic(pointer_alias_t), "1");
_Static_assert(!COMPAT(pointer_usage_t, u64), "C identity must not erase usage");
_Static_assert(!COMPAT(u64, pointer_usage_t), "usage compatibility is symmetric");
_Static_assert(COMPAT(pointer_usage_t, void *), "pointer usage layout");
_Static_assert(COMPAT(data_override_t, u64), "outer typedef usage overrides inner alias");
struct page_info_usage { page_number_t number; unsigned int flags; };
SIGNATURE(struct page_info_usage, "3");
SUMMARY(struct page_info_usage, 8);
struct field_usage {
  pointer_alias_t address DATA_USE;
  void *user_address DATA_USE;
  u64 encoded_address PTR_USE;
  pointer_alias_t opaque[2] DATA_USE;
};
SIGNATURE(struct field_usage, "22122");
struct bit_usage { unsigned int address : 16 PTR_USE; unsigned int flags : 16; };
SIGNATURE(struct bit_usage, "3");
struct bit_alias_usage { page_number_t address : 16; unsigned int flags : 16; };
SIGNATURE(struct bit_alias_usage, "3");
struct typedef_array_usage { pointer_alias_t values[2]; };
SIGNATURE(struct typedef_array_usage, "11");
typedef u64 unrelated_t __attribute__((annotate("some.other.annotation")));
SIGNATURE(unrelated_t, "2");
const char *atlantic_usage_fixture_signature = SIG(struct page_info_usage);
