# Original boot-data bridge — 2026-10-23

Original portable inventory and native XNU bootstrap-tree serializer only. No XNU execution or phone IO.
Host ASan/UBSan pass with 504 insufficient-buffer cases and 5000 mutated FDT inputs; prior parser 10000 mutations and 78 Python tests pass.
Native device_tree.h ABI fixture compiles with standard and experimental ARM64 compilers. The native parser is not executed.
Four QEMU runs (EL1/EL2, normal/BRK) execute original entry and data code, retain XNU_NOT_LINKED, and build a 504-byte tree.
Image-owned memory is 96912 bytes; this is linker reservation for preflight, not firmware XNU RAM usage.
Stock candidate DTB declaration probe observes one 2-GiB RAM range, six reservation unions and eight affinities; no physical RAM or CPU verification.
No OEM binaries or generated phone payloads are distributed. Map text normalizes the workspace prefix to <ROOT>.
Full Platform Expert, boot_args, allocation/translation policy, native consumer execution, XNU image and EDK2 handoff remain pending.
