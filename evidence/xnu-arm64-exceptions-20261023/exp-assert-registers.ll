; ModuleID = '/mnt/g/AtlanticOS/tests/xnu_port/brk_encoding.c'
source_filename = "/mnt/g/AtlanticOS/tests/xnu_port/brk_encoding.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx11.0.0"

@atl_native_assert.__desc = internal constant <{ <{ i8, i8, i8, i8, ptr }>, ptr }> <{ <{ i8, i8, i8, i8, ptr }> <{ i8 0, i8 21, i8 0, i8 0, ptr @.str }>, ptr @.str.1 }>, section "__DATA_CONST,__assert", align 4, !dbg !0
@.str = private unnamed_addr constant [15 x i8] c"brk_encoding.c\00", align 1, !dbg !20
@.str.1 = private unnamed_addr constant [2 x i8] c"0\00", align 1, !dbg !26
@atl_native_assert_values.__desc_3U = internal constant <{ <{ i8, i8, i8, i8, ptr }>, ptr, ptr, ptr }> <{ <{ i8, i8, i8, i8, ptr }> <{ i8 3, i8 24, i8 0, i8 0, ptr @.str }>, ptr @.str.2, ptr @.str.3, ptr @.str.4 }>, section "__DATA_CONST,__assert", align 4, !dbg !40
@.str.2 = private unnamed_addr constant [2 x i8] c"a\00", align 1, !dbg !31
@.str.3 = private unnamed_addr constant [3 x i8] c"==\00", align 1, !dbg !33
@.str.4 = private unnamed_addr constant [2 x i8] c"b\00", align 1, !dbg !38
@llvm.used = appending global [2 x ptr] [ptr @atl_native_assert.__desc, ptr @atl_native_assert_values.__desc_3U], section "llvm.metadata"

; Function Attrs: noredzone noreturn nounwind memory(inaccessiblemem: write)
define void @atl_builtin_trap() local_unnamed_addr #0 !dbg !89 {
entry:
  tail call void @llvm.trap(), !dbg !90
  unreachable, !dbg !91
}

; Function Attrs: cold noreturn nounwind memory(inaccessiblemem: write)
declare void @llvm.trap() #1

; Function Attrs: noredzone nounwind
define void @atl_debug_trap() local_unnamed_addr #2 !dbg !92 {
entry:
  tail call void @llvm.debugtrap(), !dbg !93
  ret void, !dbg !94
}

; Function Attrs: nounwind
declare void @llvm.debugtrap() #3

; Function Attrs: noredzone noreturn nounwind
define void @atl_native_assert() local_unnamed_addr #4 !dbg !2 {
entry:
    #dbg_value(i64 ptrtoint (ptr @atl_native_assert.__desc to i64), !72, !DIExpression(), !95)
  %0 = tail call i64 asm sideeffect "", "={x8},{x8}"(i64 ptrtoint (ptr @atl_native_assert.__desc to i64)) #3, !dbg !96, !srcloc !97
    #dbg_value(i64 %0, !72, !DIExpression(), !95)
  tail call void @llvm.aarch64.break(i32 49148), !dbg !98
  unreachable, !dbg !98
}

; Function Attrs: cold noreturn nounwind
declare void @llvm.aarch64.break(i32 immarg) #5

; Function Attrs: noredzone noreturn nounwind
define void @atl_native_assert_values(i64 noundef %a, i64 noundef %b) local_unnamed_addr #4 !dbg !42 {
entry:
    #dbg_value(i64 %a, !47, !DIExpression(), !100)
    #dbg_value(i64 %b, !48, !DIExpression(), !100)
    #dbg_value(i64 ptrtoint (ptr @atl_native_assert_values.__desc_3U to i64), !49, !DIExpression(), !101)
    #dbg_value(i64 %a, !53, !DIExpression(), !101)
    #dbg_value(i64 %b, !54, !DIExpression(), !101)
  %0 = tail call { i64, i64, i64 } asm sideeffect "", "={x8},={x16},={x17},{x8},{x16},{x17}"(i64 ptrtoint (ptr @atl_native_assert_values.__desc_3U to i64), i64 %a, i64 %b) #3, !dbg !102, !srcloc !103
    #dbg_value(i64 poison, !49, !DIExpression(), !101)
    #dbg_value(i64 poison, !53, !DIExpression(), !101)
    #dbg_value(i64 poison, !54, !DIExpression(), !101)
  tail call void @llvm.aarch64.break(i32 49148), !dbg !104
  unreachable, !dbg !104
}

attributes #0 = { noredzone noreturn nounwind memory(inaccessiblemem: write) "frame-pointer"="non-leaf" "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="cortex-a57" "target-features"="+aes,+crc,+fp-armv8,+neon,+perfmon,+sha2,+v8a" }
attributes #1 = { cold noreturn nounwind memory(inaccessiblemem: write) }
attributes #2 = { noredzone nounwind "frame-pointer"="non-leaf" "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="cortex-a57" "target-features"="+aes,+crc,+fp-armv8,+neon,+perfmon,+sha2,+v8a" }
attributes #3 = { nounwind }
attributes #4 = { noredzone noreturn nounwind "frame-pointer"="non-leaf" "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="cortex-a57" "target-features"="+aes,+crc,+fp-armv8,+neon,+perfmon,+sha2,+v8a" }
attributes #5 = { cold noreturn nounwind }

!llvm.dbg.cu = !{!6}
!llvm.module.flags = !{!84, !85, !86, !87}
!llvm.ident = !{!88}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "__desc", scope: !2, file: !3, line: 21, type: !79, isLocal: true, isDefinition: true)
!2 = distinct !DISubprogram(name: "atl_native_assert", scope: !3, file: !3, line: 21, type: !4, scopeLine: 21, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !6, retainedNodes: !71)
!3 = !DIFile(filename: "./tests/xnu_port/brk_encoding.c", directory: "")
!4 = !DISubroutineType(types: !5)
!5 = !{null}
!6 = distinct !DICompileUnit(language: DW_LANG_C11, file: !7, producer: "clang version 19.1.7", isOptimized: true, runtimeVersion: 0, emissionKind: FullDebug, enums: !8, retainedTypes: !17, globals: !19, splitDebugInlining: false, nameTableKind: Apple, sysroot: "/")
!7 = !DIFile(filename: "./tests/xnu_port/brk_encoding.c", directory: ".")
!8 = !{!9}
!9 = !DICompositeType(tag: DW_TAG_enumeration_type, file: !10, line: 96, baseType: !11, size: 8, elements: !12)
!10 = !DIFile(filename: "./work/xnu-lab-sources/b1325e485ebde996/osfmk/kern/assert.h", directory: "")
!11 = !DIBasicType(name: "unsigned char", size: 8, encoding: DW_ATE_unsigned_char)
!12 = !{!13, !14, !15, !16}
!13 = !DIEnumerator(name: "MACH_ASSERT_DEFAULT", value: 0, isUnsigned: true)
!14 = !DIEnumerator(name: "MACH_ASSERT_3P", value: 1, isUnsigned: true)
!15 = !DIEnumerator(name: "MACH_ASSERT_3S", value: 2, isUnsigned: true)
!16 = !DIEnumerator(name: "MACH_ASSERT_3U", value: 3, isUnsigned: true)
!17 = !{!18}
!18 = !DIBasicType(name: "long", size: 64, encoding: DW_ATE_signed)
!19 = !{!20, !26, !0, !31, !33, !38, !40}
!20 = !DIGlobalVariableExpression(var: !21, expr: !DIExpression())
!21 = distinct !DIGlobalVariable(scope: null, file: !3, line: 21, type: !22, isLocal: true, isDefinition: true)
!22 = !DICompositeType(tag: DW_TAG_array_type, baseType: !23, size: 120, elements: !24)
!23 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!24 = !{!25}
!25 = !DISubrange(count: 15)
!26 = !DIGlobalVariableExpression(var: !27, expr: !DIExpression())
!27 = distinct !DIGlobalVariable(scope: null, file: !3, line: 21, type: !28, isLocal: true, isDefinition: true)
!28 = !DICompositeType(tag: DW_TAG_array_type, baseType: !23, size: 16, elements: !29)
!29 = !{!30}
!30 = !DISubrange(count: 2)
!31 = !DIGlobalVariableExpression(var: !32, expr: !DIExpression())
!32 = distinct !DIGlobalVariable(scope: null, file: !3, line: 24, type: !28, isLocal: true, isDefinition: true)
!33 = !DIGlobalVariableExpression(var: !34, expr: !DIExpression())
!34 = distinct !DIGlobalVariable(scope: null, file: !3, line: 24, type: !35, isLocal: true, isDefinition: true)
!35 = !DICompositeType(tag: DW_TAG_array_type, baseType: !23, size: 24, elements: !36)
!36 = !{!37}
!37 = !DISubrange(count: 3)
!38 = !DIGlobalVariableExpression(var: !39, expr: !DIExpression())
!39 = distinct !DIGlobalVariable(scope: null, file: !3, line: 24, type: !28, isLocal: true, isDefinition: true)
!40 = !DIGlobalVariableExpression(var: !41, expr: !DIExpression())
!41 = distinct !DIGlobalVariable(name: "__desc_3U", scope: !42, file: !3, line: 24, type: !55, isLocal: true, isDefinition: true)
!42 = distinct !DISubprogram(name: "atl_native_assert_values", scope: !3, file: !3, line: 22, type: !43, scopeLine: 23, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !6, retainedNodes: !46)
!43 = !DISubroutineType(types: !44)
!44 = !{null, !45, !45}
!45 = !DIBasicType(name: "unsigned long", size: 64, encoding: DW_ATE_unsigned)
!46 = !{!47, !48, !49, !53, !54}
!47 = !DILocalVariable(name: "a", arg: 1, scope: !42, file: !3, line: 22, type: !45)
!48 = !DILocalVariable(name: "b", arg: 2, scope: !42, file: !3, line: 22, type: !45)
!49 = !DILocalVariable(name: "_a", scope: !50, file: !3, line: 24, type: !18)
!50 = distinct !DILexicalBlock(scope: !51, file: !3, line: 24, column: 5)
!51 = distinct !DILexicalBlock(scope: !52, file: !3, line: 24, column: 5)
!52 = distinct !DILexicalBlock(scope: !42, file: !3, line: 24, column: 5)
!53 = !DILocalVariable(name: "_b", scope: !50, file: !3, line: 24, type: !18)
!54 = !DILocalVariable(name: "_c", scope: !50, file: !3, line: 24, type: !18)
!55 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !56)
!56 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "mach_assert_3x", file: !10, line: 124, size: 288, align: 32, elements: !57)
!57 = !{!58, !68, !69, !70}
!58 = !DIDerivedType(tag: DW_TAG_member, name: "hdr", scope: !56, file: !10, line: 125, baseType: !59, size: 96, align: 32)
!59 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "mach_assert_hdr", file: !10, line: 113, size: 96, align: 32, elements: !60)
!60 = !{!61, !63, !65}
!61 = !DIDerivedType(tag: DW_TAG_member, name: "type", scope: !59, file: !10, line: 114, baseType: !62, size: 8)
!62 = !DIDerivedType(tag: DW_TAG_typedef, name: "mach_assert_type_t", file: !10, line: 96, baseType: !9)
!63 = !DIDerivedType(tag: DW_TAG_member, name: "lineno", scope: !59, file: !10, line: 115, baseType: !64, size: 24, offset: 8, flags: DIFlagBitField, extraData: i64 8)
!64 = !DIBasicType(name: "unsigned int", size: 32, encoding: DW_ATE_unsigned)
!65 = !DIDerivedType(tag: DW_TAG_member, name: "filename", scope: !59, file: !10, line: 116, baseType: !66, size: 64, offset: 32)
!66 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !67, size: 64)
!67 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !23)
!68 = !DIDerivedType(tag: DW_TAG_member, name: "a", scope: !56, file: !10, line: 126, baseType: !66, size: 64, offset: 96)
!69 = !DIDerivedType(tag: DW_TAG_member, name: "op", scope: !56, file: !10, line: 127, baseType: !66, size: 64, offset: 160)
!70 = !DIDerivedType(tag: DW_TAG_member, name: "b", scope: !56, file: !10, line: 128, baseType: !66, size: 64, offset: 224)
!71 = !{!72}
!72 = !DILocalVariable(name: "_a", scope: !73, file: !3, line: 21, type: !18)
!73 = distinct !DILexicalBlock(scope: !74, file: !3, line: 21, column: 32)
!74 = distinct !DILexicalBlock(scope: !75, file: !3, line: 21, column: 32)
!75 = distinct !DILexicalBlock(scope: !76, file: !3, line: 21, column: 32)
!76 = distinct !DILexicalBlock(scope: !77, file: !3, line: 21, column: 32)
!77 = distinct !DILexicalBlock(scope: !78, file: !3, line: 21, column: 32)
!78 = distinct !DILexicalBlock(scope: !2, file: !3, line: 21, column: 32)
!79 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !80)
!80 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "mach_assert_default", file: !10, line: 119, size: 160, align: 32, elements: !81)
!81 = !{!82, !83}
!82 = !DIDerivedType(tag: DW_TAG_member, name: "hdr", scope: !80, file: !10, line: 120, baseType: !59, size: 96, align: 32)
!83 = !DIDerivedType(tag: DW_TAG_member, name: "expr", scope: !80, file: !10, line: 121, baseType: !66, size: 64, offset: 96)
!84 = !{i32 7, !"Dwarf Version", i32 4}
!85 = !{i32 2, !"Debug Info Version", i32 3}
!86 = !{i32 1, !"wchar_size", i32 4}
!87 = !{i32 7, !"frame-pointer", i32 1}
!88 = !{!"clang version 19.1.7"}
!89 = distinct !DISubprogram(name: "atl_builtin_trap", scope: !3, file: !3, line: 19, type: !4, scopeLine: 19, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !6)
!90 = !DILocation(line: 19, column: 31, scope: !89)
!91 = !DILocation(line: 19, column: 49, scope: !89)
!92 = distinct !DISubprogram(name: "atl_debug_trap", scope: !3, file: !3, line: 20, type: !4, scopeLine: 20, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !6)
!93 = !DILocation(line: 20, column: 29, scope: !92)
!94 = !DILocation(line: 20, column: 52, scope: !92)
!95 = !DILocation(line: 0, scope: !73)
!96 = !DILocation(line: 21, column: 32, scope: !73)
!97 = !{i64 2155125676}
!98 = !DILocation(line: 21, column: 32, scope: !99)
!99 = distinct !DILexicalBlock(scope: !74, file: !3, line: 21, column: 32)
!100 = !DILocation(line: 0, scope: !42)
!101 = !DILocation(line: 0, scope: !50)
!102 = !DILocation(line: 24, column: 5, scope: !50)
!103 = !{i64 2155126962}
!104 = !DILocation(line: 24, column: 5, scope: !105)
!105 = distinct !DILexicalBlock(scope: !51, file: !3, line: 24, column: 5)
