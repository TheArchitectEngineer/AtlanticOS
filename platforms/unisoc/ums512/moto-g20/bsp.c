/* SPDX-License-Identifier: MIT
 * Original capability shell, NOT a hardware driver. No MMIO or OEM calls.
 * Compile validation only; all callbacks fail closed until device bring-up.
 */
#include <atlantic/platform.h>
static int log_unavailable(const char *msg) { (void)msg; return ATL_UNSUPPORTED; }
static int clock_unavailable(uint64_t *out) { if (!out) return ATL_INVALID; *out = 0; return ATL_UNSUPPORTED; }
static int key_unavailable(enum AtlanticKey key, bool *out) { (void)key; if (!out) return ATL_INVALID; *out = false; return ATL_UNSUPPORTED; }
static int fb_unavailable(struct AtlanticFramebuffer *out) { if (!out) return ATL_INVALID; *out = (struct AtlanticFramebuffer){0}; return ATL_UNSUPPORTED; }
static int power_unavailable(enum AtlanticPowerRequest req) { (void)req; return ATL_UNSUPPORTED; }
static int sources_unavailable(struct AtlanticBootSource *out, size_t *count) { (void)out; if (!count) return ATL_INVALID; *count = 0; return ATL_UNSUPPORTED; }
static int read_unavailable(const struct AtlanticBlockDevice *d, uint64_t lba, void *dst, size_t n) { (void)d; (void)lba; (void)dst; (void)n; return ATL_UNSUPPORTED; }
static int net_unavailable(struct AtlanticNetCapabilities *out) { if (!out) return ATL_INVALID; *out = (struct AtlanticNetCapabilities){0}; return ATL_UNSUPPORTED; }
static int trust_unavailable(struct AtlanticBootTrust *out) { if (!out) return ATL_INVALID; *out = (struct AtlanticBootTrust){0}; return ATL_UNSUPPORTED; }
const struct AtlanticPlatformOps atlantic_moto_g20_ops = {
    .abi_version = ATLANTIC_BSP_ABI, .struct_bytes = sizeof(struct AtlanticPlatformOps),
    .board_id = "motorola,java-xt2128", .capabilities = NULL, .capability_count = 0,
    .early_log = log_unavailable, .monotonic_us = clock_unavailable,
    .get_key_state = key_unavailable, .framebuffer_acquire = fb_unavailable,
    .power_request = power_unavailable, .list_boot_sources = sources_unavailable,
    .block_read = read_unavailable, .network_probe = net_unavailable,
    .secure_boot_context = trust_unavailable
};
