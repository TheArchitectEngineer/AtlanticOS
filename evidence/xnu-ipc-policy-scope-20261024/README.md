# Native IPC policy and component scope — 2026-10-24

138 experimental / 13 standard base units compile; native ipc_policy.c and mach_debug.c are selected experimentally.
Only process-identified CoreAnalytics, legacy process SDK exceptions and unavailable IOKit descriptions are scoped.
Native Mach policy, 17 core bodies, the policy array, right cleanup and kobject startup registration remain genuine.
All 117/88 source, ABI and object checks pass. Standard policy probe compiles; mach_debug correctly rejects missing native allocator builtins.
The isolated standard probes are not selected in its base/link. 42 RPC probes per lane compile; CFILES selects 26.
The experimental strict static link of 164 objects fails with 561 undefined diagnostics, zero duplicates and no output.
Of 594 prior undefined names, 33 have providers; 1 are no longer referenced; 1 new dependencies remain.
CA call removal is not described as an implemented telemetry service. exit_with_mach_exception remains strong and unresolved; task_violated_guard has its native provider.
Original strings pass 79344 host ASan/UBSan contracts; native tree ABI, boot-data sanitizers and 78 Python tests pass.
Clang API v2 and LLD v2 proofs are reused by verified hashes. No native IPC, exception, parser, Mach bootstrap, BSP, PE or XNU execution.
No phone access, EDK2 handoff or firmware RAM measurement.
