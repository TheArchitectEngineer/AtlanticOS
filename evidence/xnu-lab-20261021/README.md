# XNU ARM64 laboratory objects — 2026-10-21

BUILT_ARM64: five real XNU translation units compiled, not linked or executed.
Command: python3 tools/build_xnu_lab.py --windows-git --probe-remaining
Environment: Debian/WSL x86_64, Clang 19.1.7. See report for source/tool hashes.
The extended probe has two failures and therefore returns exit 1. This is not
a successful complete kernel build. No phone was accessed by this build.

report.json is the original build metadata; command paths already use <ROOT>.
Logs replace the local project root with <ROOT>. Empty logs record successful
commands without diagnostics. Negative guard output contains preprocessed source;
only actual error lines are included in negative-guards-excerpts.json. Those
excerpts are not full compiler logs. The original private logs remain in work/.
Generated headers, objects and unmodified upstream sources are not redistributed.
Object hashes and symbol lists identify the compiled artifacts; object sizes,
debug data and virtual reservations do not measure resident RAM.

The report inventories unresolved symbols. Real Mach initialization references
remain in bootstrap. There are no replacement implementations for those symbols.
thread.c and vm_map.c diagnostics remain visible. See docs/XNU_LAB_BUILD.md and
xnu-port/patches.lock.json for scope, reproduction and original patch provenance.
