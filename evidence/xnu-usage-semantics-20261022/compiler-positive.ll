; ModuleID = '/mnt/g/AtlanticOS/tests/clang_layout/positive.c'
source_filename = "/mnt/g/AtlanticOS/tests/clang_layout/positive.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx11.0.0"

@.str = private unnamed_addr constant [3 x i8] c"12\00", align 1
@atlantic_fixture_signature = global ptr @.str, align 8
@atlantic_fixture_summary = global i32 8, align 4
@.str.1 = private unnamed_addr constant [2 x i8] c"3\00", align 1
@atlantic_usage_fixture_signature = global ptr @.str.1, align 8

!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"frame-pointer", i32 1}
!3 = !{!"clang version 19.1.7"}
