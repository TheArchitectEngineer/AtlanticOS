# Native memory providers and original cache adapter â€” 2026-10-24

132 experimental / 13 standard base units compile. Six newly selected XNU sources are unchanged; loose_ends.c only guards its empty KDP fallback; one cache adapter is original MIT code.
42 RPC probes per lane compile; native CFILES selects 26. All 89/57 scope, object and ABI checks pass.
The experimental strict static link of 158 objects fails with 609 undefined diagnostics, zero duplicate diagnostics and no output.
Of 669 former undefined names, 60 are now resolved; 0 new dependencies appear.
Compiler API v2 (26 checks) and LLD v2 (54 checks, 15 images) proofs are reused by actual current hashes.
The cache adapter tail-branches through a strong native provider; actual DC/IC/barrier bytes and native CAS/pager dispatch are audited, not executed.
Coherent-IO C wrapper no-ops and the empty machine_task_init remain native behavior, not evidence of hardware capabilities.
The BSP descriptor remains a strong undefined import. No PE, SecureDT, physical copy, cache, atomic, pager, Mach or XNU execution.
Native tree ABI, ASan/UBSan boot-data and 78 host tests pass. Prior QEMU preflight evidence is not reassigned to these providers.
No hardware access, phone boot, EDK2 transfer or firmware RAM measurement.
