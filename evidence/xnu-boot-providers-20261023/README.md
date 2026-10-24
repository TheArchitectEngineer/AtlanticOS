# Native boot and scheduling providers — 2026-10-23

123 experimental / 13 standard native XNU-derived units compile; 16 newly selected sources are upstream unchanged.
42 RPC probes per lane compile; native CFILES selects 26. All 51/45 scope and ABI checks pass.
The experimental strict static link of 149 objects fails with 672 undefined diagnostics, zero duplicate diagnostics and no output.
Of 765 former undefined names, 109 are now resolved; 16 new dependencies appear.
Compiler API v2 (26 checks) and LLD v2 (54 checks, 15 images) proofs are reused by actual current hashes.
No XNU execution, hardware access, phone boot, EDK2 transfer or firmware RAM measurement.
SecureDT consumes the native XNU tree representation, not an unconverted Linux FDT.
Native cpu_bootstrap is empty upstream; cpu_data_init and other substantive definitions remain required.
