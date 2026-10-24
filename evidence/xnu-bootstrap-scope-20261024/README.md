# Native Mach bootstrap component scope — 2026-10-24

132 experimental / 13 standard base units compile, with no units added or removed.
The native bootstrap excludes only four calls owned by unselected BSD/IOKit components. No substitute providers are defined.
VM, scheduler, task, thread, clock, pageout and context loading retain genuine native calls and source order.
42 RPC probes per lane compile; native CFILES selects 26. All 97/65 scope, object and ABI checks pass.
The experimental strict static link of 158 objects fails with 605 undefined diagnostics, zero duplicate diagnostics and no output.
Four former undefined names disappear because their unselected callers are excluded; no new undefined names or implementations.
Compiler API v2 (26 checks) and LLD v2 (54 checks, 15 images) proofs are reused by current hashes.
Native tree ABI, ASan/UBSan boot-data and 78 host tests pass.
Source-fragment BSD/IOKit combinations do not enable forbidden complete firmware profiles.
No native bootstrap, scheduler, thread, cache, PE, SecureDT, IRQ, Mach or XNU execution.
No phone access, physical boot, EDK2 handoff or firmware RAM measurement.
