# Native scheduler and timer providers — 2026-10-24

148 experimental / 13 standard base units compile: eight added native sources intact and two scoped.
Native timer ports, scheduling policies, affinity, VM list storage, per-CPU counters and identity-token bodies are selected.
Two BSD rethrottle callbacks are excluded in firmware without BSD; native priority, CAS and turnstile updates remain.
The broken no-BSD resource branch returns its intended KERN_NOT_SUPPORTED. BSD behavior is retained.
SFI stays disabled with native unsupported returns; task identity still requires real process/corpse providers. PMU fallback zeros are not measurements.
All 129/98 source, ABI and object checks pass. Timer deadlines/output addresses are 64-bit; incorrect deadlines/callbacks reject.
Original strings pass 79344 host ASan/UBSan cases; boot-data sanitizers/native tree ABI and 78 Python tests pass.
42 RPC probes per lane compile and native CFILES selects 26. The standard base remains 13 units.
The experimental strict static link of 174 objects fails with 502 undefined diagnostics, zero duplicates and no output.
From 561 prior undefined names, 76 have providers; 0 are no longer referenced; 17 new dependencies remain.
Initial native thread/task policy failures and missing coalition MIG header are preserved as earlier candidate diagnostics.
Clang API v2 and LLD v2 proofs are reused by verified hashes. No native timer, policy, allocator, IPC, BSP, PE, IRQ or XNU execution.
No phone access, EDK2 handoff or firmware RAM measurement.
