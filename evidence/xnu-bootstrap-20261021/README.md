# Eleven XNU ARM64 objects and target-generated offsets — 2026-10-21

BUILT_ARM64: eleven actual upstream translation units compiled, no link or runtime.
Command: python3 tools/build_xnu_lab.py --windows-git --probe-remaining
The extended probe returns exit 1 because thread.c and vm_map.c fail. These two
failures are preserved. A default invocation checks the eleven successful units.

The official genassym.c was cross-compiled, not executed. 137 values and aliases
were extracted from target assembly; target C layout assertions passed and an
offset displaced one byte was rejected. Eight extractor host tests passed.
The report records input/object hashes, actual commands and symbol inventories.
The virtual compilation address is not a physical image placement or link result.
Unprovided symbol names are not a linker/relocation test or proof of reachability.

Report commands use <ROOT>; compiler logs replace local project roots with it.
Empty logs reflect successful commands without diagnostics. Only error excerpts
of PMU/BSD/IOKit preprocessor guard output are retained; their complete output is
private under work/. The wrong-offset rejection log is retained in full.
No XNU object/source redistribution, phone access, firmware packaging or flashing.
The QEMU preflight does not execute these objects or a real context switch.
