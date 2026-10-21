# Experimental original C-layout compiler — 2026-10-21

HOST_TESTED: a complete LLVM/Clang compiler was built with the original
AtlanticOS C-layout frontend patch. 18 API checks passed: positive ARM64 object,
folded LLVM IR and 16 expected diagnostic rejections. No XNU code was executed.

The recorded build used verified LLVM 19.1.7 archive sources and checked the
seven patch postimages. The original files remain private in work/. Published
commands and logs replace the project root with <ROOT>; api-report.json is the
original fixture report with input and compiler hashes. Compiler binary is not
distributed; positive.o is our fixture, not an XNU object or a phone image.

The separate real thread.c probe selected four layout expressions through the
recorded experimental kalloc.h diff. Its compile failed with ten undeclared BSD
calls; that failure is preserved. It did not report layout metadata errors.
This is not successful compilation of thread.c or a complete kernel.

The public builder's end-to-end reproduction has not yet been verified; these
are the actual successful local configure/build/test commands. Full hardware
acceptance, allocator/thread runtime behavior, RAM and EDK2 handoff remain open.
