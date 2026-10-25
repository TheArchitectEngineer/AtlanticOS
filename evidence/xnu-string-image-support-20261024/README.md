# Original strings and native image support — 2026-10-24

136 experimental / 13 standard base units compile: two original support units and two unchanged native XNU units added.
Original memory/string comparison and bounded copy/append pass 79344 host contract cases with ASan/UBSan. Host libc is not interposed.
Native string types, 64-bit Mach-O layouts, negative ABIs and the actual strong ARM64 entry branches are audited.
The standard lane compiles two isolated support probes, which are not selected in its base/link.
42 RPC probes per lane compile; native CFILES selects 26. All 105/74 scope, object and ABI checks pass.
The experimental strict static link of 162 objects fails with 594 undefined diagnostics, zero duplicate diagnostics and no output.
Of 605 previous undefined names, 11 have providers; 0 new undefined names remain.
Compiler API v2 and LLD v2 proofs are reused by current hashes. Native tree ABI, ASan/UBSan boot-data and 78 Python tests pass.
Native Mach-O readers require an already validated, owned and mapped header. They are not an untrusted-image validator.
No native parser, tokenization, Mach bootstrap, BSP, PE, IRQ or XNU execution; no phone access, EDK2 handoff or firmware RAM measurement.
