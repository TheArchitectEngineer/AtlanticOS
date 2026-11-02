; ModuleID = '/mnt/g/AtlanticOS/work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/kern/atlantic_early_log.c'
source_filename = "/mnt/g/AtlanticOS/work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/kern/atlantic_early_log.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx11.0.0"

%struct.AtlanticEarlyLog = type { i32, i32, i32, i32, i64, i64, i64, i64, [16384 x i8] }
%struct.AtlanticEarlyLogRecord = type { i64, i64, [1024 x i8] }

@PE_kputc = global ptr @memory_putc, section "__DATA,__const", align 8, !dbg !0
@PE_putc = global ptr @memory_putc, section "__DATA,__const", align 8, !dbg !14
@boot_log = internal global %struct.AtlanticEarlyLog zeroinitializer, align 8, !dbg !22
@llvm.used = appending global [2 x ptr] [ptr @PE_kputc, ptr @PE_putc], section "llvm.metadata"

; Function Attrs: noredzone nounwind
define internal void @memory_putc(i8 noundef signext %character) #0 !dbg !53 {
entry:
  %character.addr = alloca i8, align 1
    #dbg_value(i8 %character, !55, !DIExpression(), !56)
  store i8 %character, ptr %character.addr, align 1, !tbaa !57
    #dbg_value(ptr %character.addr, !55, !DIExpression(DW_OP_deref), !56)
  %call = call i32 @atl_early_log_append(ptr noundef nonnull @boot_log, ptr noundef nonnull %character.addr, i64 noundef 1, i64 noundef 0) #6, !dbg !60
  ret void, !dbg !61
}

; Function Attrs: noinline noredzone nounwind
define void @kprintf(ptr noundef %format, ...) local_unnamed_addr #1 !dbg !62 {
entry:
  %record = alloca %struct.AtlanticEarlyLogRecord, align 8
  %arguments = alloca ptr, align 8
    #dbg_value(ptr %format, !68, !DIExpression(), !86)
  call void @llvm.lifetime.start.p0(i64 1040, ptr nonnull %record) #7, !dbg !87
    #dbg_declare(ptr %record, !69, !DIExpression(), !88)
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 8 dereferenceable(1040) %record, i8 0, i64 1040, i1 false), !dbg !88
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %arguments) #7, !dbg !89
    #dbg_value(ptr %arguments, !81, !DIExpression(DW_OP_deref), !86)
  call void @llvm.va_start.p0(ptr nonnull %arguments), !dbg !90
  %0 = load ptr, ptr %arguments, align 8, !dbg !91, !tbaa !92
    #dbg_value(ptr %0, !81, !DIExpression(), !86)
  %call = call i32 @__doprnt(ptr noundef %format, ptr noundef %0, ptr noundef nonnull @atl_early_log_capture, ptr noundef nonnull %record, i32 noundef 16, i32 noundef 1) #6, !dbg !94
    #dbg_value(ptr %arguments, !81, !DIExpression(DW_OP_deref), !86)
  call void @llvm.va_end.p0(ptr %arguments), !dbg !95
  %data = getelementptr inbounds i8, ptr %record, i64 16, !dbg !96
  %1 = load i64, ptr %record, align 8, !dbg !97, !tbaa !98
  %truncated_bytes = getelementptr inbounds i8, ptr %record, i64 8, !dbg !102
  %2 = load i64, ptr %truncated_bytes, align 8, !dbg !102, !tbaa !103
  %call1 = call i32 @atl_early_log_append(ptr noundef nonnull @boot_log, ptr noundef nonnull %data, i64 noundef %1, i64 noundef %2) #6, !dbg !104
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %arguments) #7, !dbg !105
  call void @llvm.lifetime.end.p0(i64 1040, ptr nonnull %record) #7, !dbg !105
  ret void, !dbg !105
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #2

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn
declare void @llvm.va_start.p0(ptr) #4

; Function Attrs: noredzone
declare !dbg !106 i32 @__doprnt(ptr noundef, ptr noundef, ptr noundef, ptr noundef, i32 noundef, i32 noundef) local_unnamed_addr #5

; Function Attrs: noredzone
declare void @atl_early_log_capture(i32 noundef, ptr noundef) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn
declare void @llvm.va_end.p0(ptr) #4

; Function Attrs: noredzone
declare !dbg !114 i32 @atl_early_log_append(ptr noundef, ptr noundef, i64 noundef, i64 noundef) local_unnamed_addr #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #2

; Function Attrs: noredzone nounwind
define i32 @atlantic_xnu_log_snapshot(ptr noundef %destination, i64 noundef %capacity, ptr noundef %metadata) local_unnamed_addr #0 !dbg !120 {
entry:
    #dbg_value(ptr %destination, !135, !DIExpression(), !138)
    #dbg_value(i64 %capacity, !136, !DIExpression(), !138)
    #dbg_value(ptr %metadata, !137, !DIExpression(), !138)
  %call = tail call i32 @atl_early_log_snapshot(ptr noundef nonnull @boot_log, ptr noundef %destination, i64 noundef %capacity, ptr noundef %metadata) #6, !dbg !139
  ret i32 %call, !dbg !140
}

; Function Attrs: noredzone
declare !dbg !141 i32 @atl_early_log_snapshot(ptr noundef, ptr noundef, i64 noundef, ptr noundef) local_unnamed_addr #5

attributes #0 = { noredzone nounwind "frame-pointer"="non-leaf" "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="cortex-a57" "target-features"="+aes,+crc,+fp-armv8,+neon,+perfmon,+sha2,+strict-align,+v8a,-outline-atomics" }
attributes #1 = { noinline noredzone nounwind "frame-pointer"="non-leaf" "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="cortex-a57" "target-features"="+aes,+crc,+fp-armv8,+neon,+perfmon,+sha2,+strict-align,+v8a,-outline-atomics" }
attributes #2 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #4 = { mustprogress nocallback nofree nosync nounwind willreturn }
attributes #5 = { noredzone "frame-pointer"="non-leaf" "no-builtins" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="cortex-a57" "target-features"="+aes,+crc,+fp-armv8,+neon,+perfmon,+sha2,+strict-align,+v8a,-outline-atomics" }
attributes #6 = { nobuiltin noredzone nounwind "no-builtins" }
attributes #7 = { nounwind }

!llvm.dbg.cu = !{!2}
!llvm.module.flags = !{!48, !49, !50, !51}
!llvm.ident = !{!52}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "PE_kputc", scope: !2, file: !16, line: 30, type: !17, isLocal: false, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C11, file: !3, producer: "clang version 19.1.7", isOptimized: true, runtimeVersion: 0, emissionKind: FullDebug, enums: !4, globals: !13, splitDebugInlining: false, nameTableKind: Apple, sysroot: "/")
!3 = !DIFile(filename: "./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/kern/atlantic_early_log.c", directory: ".")
!4 = !{!5}
!5 = !DICompositeType(tag: DW_TAG_enumeration_type, name: "AtlanticEarlyLogStatus", file: !6, line: 11, baseType: !7, size: 32, elements: !8)
!6 = !DIFile(filename: "./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/atlantic/early_log.h", directory: "")
!7 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!8 = !{!9, !10, !11, !12}
!9 = !DIEnumerator(name: "ATL_LOG_OK", value: 0)
!10 = !DIEnumerator(name: "ATL_LOG_INVALID", value: -1)
!11 = !DIEnumerator(name: "ATL_LOG_BUSY", value: -2)
!12 = !DIEnumerator(name: "ATL_LOG_BUFFER_SMALL", value: -3)
!13 = !{!0, !14, !22}
!14 = !DIGlobalVariableExpression(var: !15, expr: !DIExpression())
!15 = distinct !DIGlobalVariable(name: "PE_putc", scope: !2, file: !16, line: 31, type: !17, isLocal: false, isDefinition: true)
!16 = !DIFile(filename: "./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/kern/atlantic_early_log.c", directory: "")
!17 = !DIDerivedType(tag: DW_TAG_typedef, name: "atlantic_putc_t", file: !16, line: 29, baseType: !18)
!18 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !19, size: 64)
!19 = !DISubroutineType(types: !20)
!20 = !{null, !21}
!21 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!22 = !DIGlobalVariableExpression(var: !23, expr: !DIExpression())
!23 = distinct !DIGlobalVariable(name: "boot_log", scope: !2, file: !16, line: 21, type: !24, isLocal: true, isDefinition: true)
!24 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "AtlanticEarlyLog", file: !6, line: 21, size: 131456, elements: !25)
!25 = !{!26, !32, !33, !34, !35, !40, !41, !42, !43}
!26 = !DIDerivedType(tag: DW_TAG_member, name: "gate", scope: !24, file: !6, line: 22, baseType: !27, size: 32)
!27 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint32_t", file: !28, line: 40, baseType: !29)
!28 = !DIFile(filename: "./work/xnu-lab-sources/5647a1f4c6efdb54/EXTERNAL_HEADERS/stdint.h", directory: "")
!29 = !DIDerivedType(tag: DW_TAG_typedef, name: "u_int32_t", file: !30, line: 30, baseType: !31)
!30 = !DIFile(filename: "./work/xnu-lab-sources/5647a1f4c6efdb54/bsd/sys/_types/_u_int32_t.h", directory: "")
!31 = !DIBasicType(name: "unsigned int", size: 32, encoding: DW_ATE_unsigned)
!32 = !DIDerivedType(tag: DW_TAG_member, name: "contention_seen", scope: !24, file: !6, line: 22, baseType: !27, size: 32, offset: 32)
!33 = !DIDerivedType(tag: DW_TAG_member, name: "head", scope: !24, file: !6, line: 22, baseType: !27, size: 32, offset: 64)
!34 = !DIDerivedType(tag: DW_TAG_member, name: "size", scope: !24, file: !6, line: 22, baseType: !27, size: 32, offset: 96)
!35 = !DIDerivedType(tag: DW_TAG_member, name: "records", scope: !24, file: !6, line: 23, baseType: !36, size: 64, offset: 128)
!36 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint64_t", file: !28, line: 41, baseType: !37)
!37 = !DIDerivedType(tag: DW_TAG_typedef, name: "u_int64_t", file: !38, line: 30, baseType: !39)
!38 = !DIFile(filename: "./work/xnu-lab-sources/5647a1f4c6efdb54/bsd/sys/_types/_u_int64_t.h", directory: "")
!39 = !DIBasicType(name: "unsigned long long", size: 64, encoding: DW_ATE_unsigned)
!40 = !DIDerivedType(tag: DW_TAG_member, name: "accepted_bytes", scope: !24, file: !6, line: 23, baseType: !36, size: 64, offset: 192)
!41 = !DIDerivedType(tag: DW_TAG_member, name: "overwritten_bytes", scope: !24, file: !6, line: 23, baseType: !36, size: 64, offset: 256)
!42 = !DIDerivedType(tag: DW_TAG_member, name: "truncated_bytes", scope: !24, file: !6, line: 23, baseType: !36, size: 64, offset: 320)
!43 = !DIDerivedType(tag: DW_TAG_member, name: "data", scope: !24, file: !6, line: 24, baseType: !44, size: 131072, offset: 384)
!44 = !DICompositeType(tag: DW_TAG_array_type, baseType: !45, size: 131072, elements: !46)
!45 = !DIBasicType(name: "unsigned char", size: 8, encoding: DW_ATE_unsigned_char)
!46 = !{!47}
!47 = !DISubrange(count: 16384)
!48 = !{i32 7, !"Dwarf Version", i32 4}
!49 = !{i32 2, !"Debug Info Version", i32 3}
!50 = !{i32 1, !"wchar_size", i32 4}
!51 = !{i32 7, !"frame-pointer", i32 1}
!52 = !{!"clang version 19.1.7"}
!53 = distinct !DISubprogram(name: "memory_putc", scope: !16, file: !16, line: 24, type: !19, scopeLine: 25, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !54)
!54 = !{!55}
!55 = !DILocalVariable(name: "character", arg: 1, scope: !53, file: !16, line: 24, type: !21)
!56 = !DILocation(line: 0, scope: !53)
!57 = !{!58, !58, i64 0}
!58 = !{!"omnipotent char", !59, i64 0}
!59 = !{!"Simple C/C++ TBAA"}
!60 = !DILocation(line: 26, column: 11, scope: !53)
!61 = !DILocation(line: 27, column: 1, scope: !53)
!62 = distinct !DISubprogram(name: "kprintf", scope: !16, file: !16, line: 34, type: !63, scopeLine: 35, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !67)
!63 = !DISubroutineType(types: !64)
!64 = !{null, !65, null}
!65 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !66, size: 64)
!66 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !21)
!67 = !{!68, !69, !81}
!68 = !DILocalVariable(name: "format", arg: 1, scope: !62, file: !16, line: 34, type: !65)
!69 = !DILocalVariable(name: "record", scope: !62, file: !16, line: 36, type: !70)
!70 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "AtlanticEarlyLogRecord", file: !6, line: 34, size: 8320, elements: !71)
!71 = !{!72, !76, !77}
!72 = !DIDerivedType(tag: DW_TAG_member, name: "bytes", scope: !70, file: !6, line: 35, baseType: !73, size: 64)
!73 = !DIDerivedType(tag: DW_TAG_typedef, name: "size_t", file: !74, line: 57, baseType: !75)
!74 = !DIFile(filename: "./work/xnu-lab-sources/5647a1f4c6efdb54/EXTERNAL_HEADERS/stddef.h", directory: "")
!75 = !DIBasicType(name: "unsigned long", size: 64, encoding: DW_ATE_unsigned)
!76 = !DIDerivedType(tag: DW_TAG_member, name: "truncated_bytes", scope: !70, file: !6, line: 36, baseType: !36, size: 64, offset: 64)
!77 = !DIDerivedType(tag: DW_TAG_member, name: "data", scope: !70, file: !6, line: 37, baseType: !78, size: 8192, offset: 128)
!78 = !DICompositeType(tag: DW_TAG_array_type, baseType: !45, size: 8192, elements: !79)
!79 = !{!80}
!80 = !DISubrange(count: 1024)
!81 = !DILocalVariable(name: "arguments", scope: !62, file: !16, line: 37, type: !82)
!82 = !DIDerivedType(tag: DW_TAG_typedef, name: "va_list", file: !83, line: 12, baseType: !84)
!83 = !DIFile(filename: "./work/llvm-toolchain/native-active/clang-layout-usage-v2/build/lib/clang/19/include/__stdarg_va_list.h", directory: "")
!84 = !DIDerivedType(tag: DW_TAG_typedef, name: "__builtin_va_list", file: !3, baseType: !85)
!85 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !21, size: 64)
!86 = !DILocation(line: 0, scope: !62)
!87 = !DILocation(line: 36, column: 5, scope: !62)
!88 = !DILocation(line: 36, column: 35, scope: !62)
!89 = !DILocation(line: 37, column: 5, scope: !62)
!90 = !DILocation(line: 38, column: 5, scope: !62)
!91 = !DILocation(line: 41, column: 22, scope: !62)
!92 = !{!93, !93, i64 0}
!93 = !{!"any pointer", !58, i64 0}
!94 = !DILocation(line: 41, column: 5, scope: !62)
!95 = !DILocation(line: 42, column: 5, scope: !62)
!96 = !DILocation(line: 43, column: 50, scope: !62)
!97 = !DILocation(line: 43, column: 63, scope: !62)
!98 = !{!99, !100, i64 0}
!99 = !{!"AtlanticEarlyLogRecord", !100, i64 0, !101, i64 8, !58, i64 16}
!100 = !{!"long", !58, i64 0}
!101 = !{!"long long", !58, i64 0}
!102 = !DILocation(line: 43, column: 77, scope: !62)
!103 = !{!99, !101, i64 8}
!104 = !DILocation(line: 43, column: 11, scope: !62)
!105 = !DILocation(line: 44, column: 1, scope: !62)
!106 = !DISubprogram(name: "__doprnt", scope: !107, file: !107, line: 218, type: !108, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!107 = !DIFile(filename: "./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/kern/misc_protos.h", directory: "")
!108 = !DISubroutineType(types: !109)
!109 = !{!7, !65, !82, !110, !113, !7, !7}
!110 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !111, size: 64)
!111 = !DISubroutineType(types: !112)
!112 = !{null, !7, !113}
!113 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!114 = !DISubprogram(name: "atl_early_log_append", scope: !6, file: !6, line: 48, type: !115, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!115 = !DISubroutineType(types: !116)
!116 = !{!5, !117, !118, !73, !36}
!117 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !24, size: 64)
!118 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !119, size: 64)
!119 = !DIDerivedType(tag: DW_TAG_const_type, baseType: null)
!120 = distinct !DISubprogram(name: "atlantic_xnu_log_snapshot", scope: !16, file: !16, line: 47, type: !121, scopeLine: 49, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !134)
!121 = !DISubroutineType(types: !122)
!122 = !{!5, !113, !73, !123}
!123 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !124, size: 64)
!124 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "AtlanticEarlyLogSnapshot", file: !6, line: 27, size: 384, elements: !125)
!125 = !{!126, !127, !128, !129, !130, !131, !132, !133}
!126 = !DIDerivedType(tag: DW_TAG_member, name: "abi_version", scope: !124, file: !6, line: 28, baseType: !27, size: 32)
!127 = !DIDerivedType(tag: DW_TAG_member, name: "struct_bytes", scope: !124, file: !6, line: 28, baseType: !27, size: 32, offset: 32)
!128 = !DIDerivedType(tag: DW_TAG_member, name: "data_bytes", scope: !124, file: !6, line: 28, baseType: !27, size: 32, offset: 64)
!129 = !DIDerivedType(tag: DW_TAG_member, name: "contention_seen", scope: !124, file: !6, line: 28, baseType: !27, size: 32, offset: 96)
!130 = !DIDerivedType(tag: DW_TAG_member, name: "records", scope: !124, file: !6, line: 29, baseType: !36, size: 64, offset: 128)
!131 = !DIDerivedType(tag: DW_TAG_member, name: "accepted_bytes", scope: !124, file: !6, line: 29, baseType: !36, size: 64, offset: 192)
!132 = !DIDerivedType(tag: DW_TAG_member, name: "overwritten_bytes", scope: !124, file: !6, line: 29, baseType: !36, size: 64, offset: 256)
!133 = !DIDerivedType(tag: DW_TAG_member, name: "truncated_bytes", scope: !124, file: !6, line: 29, baseType: !36, size: 64, offset: 320)
!134 = !{!135, !136, !137}
!135 = !DILocalVariable(name: "destination", arg: 1, scope: !120, file: !16, line: 47, type: !113)
!136 = !DILocalVariable(name: "capacity", arg: 2, scope: !120, file: !16, line: 47, type: !73)
!137 = !DILocalVariable(name: "metadata", arg: 3, scope: !120, file: !16, line: 48, type: !123)
!138 = !DILocation(line: 0, scope: !120)
!139 = !DILocation(line: 50, column: 12, scope: !120)
!140 = !DILocation(line: 50, column: 5, scope: !120)
!141 = !DISubprogram(name: "atl_early_log_snapshot", scope: !6, file: !6, line: 58, type: !142, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!142 = !DISubroutineType(types: !143)
!143 = !{!5, !117, !113, !73, !123}
