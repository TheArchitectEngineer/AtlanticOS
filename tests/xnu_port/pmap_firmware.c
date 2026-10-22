/* SPDX-License-Identifier: MIT
 * Header contract probes. No verifier, allocation, or page-table operation runs.
 */
#include <kern/cs_blobs.h>
#include <vm/pmap.h>

#ifdef ATL_TEST_STATIC_TRUST_CACHE
uint32_t atl_test_static_lookup(const uint8_t hash[CS_CDHASH_LEN])
{
    return pmap_lookup_in_static_trust_cache(hash);
}
#endif

#ifdef ATL_TEST_LOADED_TRUST_CACHE
bool atl_test_loaded_lookup(const uint8_t hash[CS_CDHASH_LEN])
{
    return pmap_lookup_in_loaded_trust_caches(hash);
}
#endif
