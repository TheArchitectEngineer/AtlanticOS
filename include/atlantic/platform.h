/* SPDX-License-Identifier: MIT - Original AtlanticOS interface draft. */
#ifndef ATLANTIC_PLATFORM_H
#define ATLANTIC_PLATFORM_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define ATLANTIC_BSP_ABI 1u
enum AtlanticStatus { ATL_OK = 0, ATL_UNSUPPORTED = -1, ATL_INVALID = -2,
                      ATL_IO_ERROR = -3, ATL_UNVERIFIED = -4 };
enum AtlanticKey { ATL_VOLUME_UP, ATL_VOLUME_DOWN, ATL_POWER };
enum AtlanticPowerRequest { ATL_POWER_OFF, ATL_RESTART, ATL_CANCEL };
enum AtlanticEvidence { ATL_NONE, ATL_HOST_TESTED, ATL_EMULATED,
                        ATL_BUILT_ARM64, ATL_DEVICE_VERIFIED };
struct AtlanticFramebuffer {
    uint64_t physical_base, reservation_bytes;
    uint32_t width, height, stride_bytes, pixel_format;
};
struct AtlanticBlockDevice { uint64_t id, sector_count; uint32_t sector_bytes, reserved; };
struct AtlanticBootSource { uint64_t id, required_capabilities; uint32_t kind, verified; };
struct AtlanticNetCapabilities { uint32_t host_role, bulk, ethernet, authenticated_channel; };
struct AtlanticBootTrust { uint32_t oem_locked, avb_state, payload_verified, rollback_available; };
struct AtlanticCapability { uint32_t id, evidence; uint8_t record_sha256[32]; };

/* This is an in-process C ABI, never cast from DTB or untrusted serialized bytes.
 * All implementations must check out pointers, lengths, media boundaries and
 * integer overflow. No write-block or set-slot callback exists in ABI v1. */
struct AtlanticPlatformOps {
    uint32_t abi_version, struct_bytes;
    const char *board_id;
    const struct AtlanticCapability *capabilities;
    size_t capability_count;
    int (*early_log)(const char *msg);
    int (*monotonic_us)(uint64_t *out);
    int (*get_key_state)(enum AtlanticKey key, bool *pressed);
    int (*framebuffer_acquire)(struct AtlanticFramebuffer *out);
    int (*power_request)(enum AtlanticPowerRequest request);
    int (*list_boot_sources)(struct AtlanticBootSource *out, size_t *count);
    int (*block_read)(const struct AtlanticBlockDevice *, uint64_t lba,
                      void *dst, size_t sectors);
    int (*network_probe)(struct AtlanticNetCapabilities *out);
    int (*secure_boot_context)(struct AtlanticBootTrust *out);
};
extern const struct AtlanticPlatformOps atlantic_moto_g20_ops;
_Static_assert(sizeof(uint64_t) == 8, "64-bit physical addresses required");
#endif
