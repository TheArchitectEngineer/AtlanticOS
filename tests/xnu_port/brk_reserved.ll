; SPDX-License-Identifier: MIT
; Backend encoding fixture, not Apple bounds-safety instrumentation support.
target triple = "arm64-apple-macosx11.0.0"
declare void @llvm.ubsantrap(i8 immarg)
define void @atl_reserved_trap_25() {
  call void @llvm.ubsantrap(i8 25)
  unreachable
}
