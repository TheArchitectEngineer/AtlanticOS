"""Audit native IPC component selection and actual ARM64 objects, not execution.

Process-identified CoreAnalytics is optional in Mach-only firmware. Message
validation, immovability, guards, diagnostic counts and registration stay native.
The BSD termination dependency in guard AST is deliberately still unresolved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from test_xnu_brk_scope import function,read_object,symbol_bytes

ROOT=Path(__file__).resolve().parents[1]
PATCH='0027-scope-ipc-process-analytics-sdk-and-iokit-descriptions.patch'
FILES=['osfmk/ipc/ipc_policy.c','osfmk/ipc/ipc_policy.h','osfmk/ipc/ipc_object.c',
       'osfmk/ipc/ipc_kmsg.c','osfmk/ipc/mach_debug.c']
CORE=['ipc_policy_for_task','ipc_current_msg_options','ipc_preflight_msg_option64',
      'ipc_should_apply_policy','ipc_validate_kmsg_header_schema_from_user',
      'ipc_validate_kmsg_schema_from_user','ipc_validate_kmsg_header_from_user',
      'ipc_move_receive_allowed','ipc_should_mark_immovable_send','ipc_entry_init',
      'mach_port_guard_exception','mach_port_guard_ast','ipc_kobject_register_startup',
      'ipc_policy_construct_entitlement_hardening','ipc_policy_set_defaults',
      'ipc_inc_telemetry_count','ipc_is_valid_exception_port']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def hashed(text):return hashlib.sha256(text.encode()).hexdigest()

def fragments(texts):
    policy,header,obj,kmsg,debug=[texts[p] for p in FILES]
    start=policy.index('#pragma mark ipc policy telemetry')
    end=policy.index('#if DEBUG || DEVELOPMENT\nvoid\nipc_inc_telemetry_count',start)
    a=policy[start:end]
    start=policy.index('#pragma mark MACH_SEND_MSG policies')
    end=policy.index('mach_msg_return_t\nipc_validate_kmsg_header_from_user',start)
    b=policy[start:end]
    start=header.index('/*!\n * @brief\n * Record ipc policy violations')
    end=header.index('#if DEBUG || DEVELOPMENT',start)
    return {'analytics':a,'send-policies':b,'reply-policies':function(policy,'ipc_validate_local_port'),
            'declaration':header[start:end],'copyin':function(obj,'ipc_object_copyin'),
            'kmsg-rights':function(kmsg,'ipc_kmsg_copyin_header_rights'),
            'descriptions':function(debug,'mach_port_kobject_description')}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    base=json.loads(args.build.read_text());lock=json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if base['port_id']!=lock['port_id'] or base['failed_units']:ap.error('Use a successful current build')
    for rel,expected in base['inputs'].items():
        if sha(ROOT/rel)!=expected:ap.error('Changed build input: '+rel)
    source=ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
    before={p:(ROOT/'xnu-upstream'/p).read_text() for p in FILES}
    after={p:(source/p).read_text() for p in FILES}
    for rel in FILES:
        record=next(i for i in lock['canonical_lf_files'] if i['path']==rel)
        assert hashed(before[rel])==record['preimage_sha256'] and sha(source/rel)==record['postimage_sha256']
    assert sha(ROOT/'xnu-port'/PATCH)==lock['patches'][PATCH]
    recipe=next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    assert recipe[-4]=='-c';target=[s.replace('<ROOT>',str(ROOT)) for s in recipe[:-4]]
    if base['layout_provider']:assert sha(target[0])==base['layout_provider']['compiler_sha256']
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():ap.error('Use a new output directory under work/')
    out.mkdir(parents=True)
    commands,outcomes=[],[]
    def run(name,cmd,data=None,expected=0,diagnostic=None,check=True):
        result=subprocess.run(cmd,input=data,cwd=ROOT,text=True,capture_output=True,timeout=60)
        commands.append([s.replace(str(ROOT),'<ROOT>') for s in cmd])
        log=result.stderr if data is not None else result.stdout+result.stderr
        (out/(name+'.log')).write_text(log.replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        assert result.returncode==expected and (not diagnostic or diagnostic in result.stderr),name+': '+result.stderr[-2500:]
        if check:outcomes.append({'name':name,'passed':True,'exit_code':result.returncode,'expected':expected})
        return result.stdout
    pair=[fragments(before),fragments(after)]
    for name,fw,bsd,iokit in [('outside-firmware-none',0,0,0),('outside-firmware-providers',0,1,1),
                             ('firmware-mach',1,0,0),('firmware-bsd',1,1,0),
                             ('firmware-iokit',1,0,1),('firmware-providers',1,1,1)]:
        prefix=(f'#define CONFIG_ATLANTIC_FIRMWARE {fw}\n#undef MACH_BSD\n#undef IOKIT\n'
                '#define XNU_TARGET_OS_OSX 0\n#define CONFIG_CSR 0\n#define DEBUG 1\n#define DEVELOPMENT 1\n')
        if bsd:prefix+='#define MACH_BSD 1\n'
        if iokit:prefix+='#define IOKIT 1\n'
        outputs=[]
        for role,parts in zip(['upstream','adapted'],pair):
            text='\n'.join('ATLANTIC_AUDIT_'+key.replace('-','_')+'\n'+value for key,value in parts.items())
            result=run(name+'-'+role,[target[0],'--target=arm64-apple-macos11','-E','-P','-x','c','-'],
                       prefix+text,check=False)
            processed={}
            for segment in result.split('ATLANTIC_AUDIT_')[1:]:
                key,_,value=segment.partition('\n');processed[key.strip().replace('_','-')]=value
            assert set(processed)==set(parts)
            outputs.append(processed)
        old,new=outputs;analytics=not fw or bool(bsd);descriptions=not fw or bool(iokit)
        assert ('ipc_stash_policy_violations_telemetry(' in new['analytics'])==analytics
        assert ('ipc_stash_policy_violations_telemetry(' in new['declaration'])==analytics
        for key in ['reply-policies','copyin','kmsg-rights']:
            assert ('ipc_stash_policy_violations_telemetry(' in new[key])==analytics
        assert ('ipc_policy_allow_send_only_kobject_calls(' in new['send-policies'])==analytics
        assert ('iokit_kobject_retain(' in new['descriptions'])==descriptions
        for key in new:
            if not fw or (iokit if key=='descriptions' else bsd):assert old[key]==new[key],(name,key)
        for name_core in ['mach_port_guard_exception','MACH_SEND_INVALID_REPLY']:
            assert name_core in new['reply-policies']
        for name_core in ['ipc_right_copyin(','is_write_unlock(']:
            assert name_core in new['copyin'] and name_core in new['kmsg-rights']
        assert 'ipc_right_copyin_cleanup_destroy(' in new['copyin']
        for name_core in ['IKOT_NAMED_ENTRY','mach_memory_entry_describe(','ipc_right_lookup_read(','io_unlock(']:
            assert name_core in new['descriptions']
        if fw and not bsd:
            dest=function(new['send-policies'],'ipc_validate_kmsg_dest_from_user')
            assert re.search(r'if \(__improbable\(\(opts & MACH64_RCV_MSG\) == 0\)\) \{\s*return MACH_SEND_INVALID_OPTIONS;\s*\}',dest)
        outcomes.append({'name':name,'passed':True,'process_analytics_selected':analytics,
            'legacy_sdk_exception_selected':analytics,'iokit_description_selected':descriptions,
            'fragment_sha256':{key:hashed(value) for key,value in new.items()}})
    native={}
    for name in CORE:
        old=function(before[FILES[0]],name);new=function(after[FILES[0]],name)
        assert old==new,name;native[name]=hashed(new)
    def array(text):return re.search(r'^struct ipc_object_policy ipc_policy_array\[IOT_UNKNOWN\] = \{.*?^\};',text,re.M|re.S)[0]
    assert array(before[FILES[0]])==array(after[FILES[0]])
    cleanup=function(before[FILES[3]],'ipc_kmsg_copyin_header_cleanup')
    assert cleanup==function(after[FILES[3]],'ipc_kmsg_copyin_header_cleanup')
    assert 'ipc_right_copyin_cleanup_destroy(' in cleanup
    outcomes.append({'name':'native-policy-array-and-17-core-bodies-intact','passed':True,
                     'function_sha256':native,'array_sha256':hashed(array(after[FILES[0]])),
                     'rights_cleanup_sha256':hashed(cleanup)})
    fixture=ROOT/'tests/xnu_port/ipc_policy_abi.c'
    run('native-policy-abi',[*target,'-fsyntax-only',str(fixture)])
    run('reject-truncated-option-abi',[*target,'-DATL_TEST_WRONG_POLICY_OPTIONS=1',
        '-Werror=incompatible-function-pointer-types','-fsyntax-only',str(fixture)],expected=1,diagnostic='incompatible function pointer types')
    run('reject-unselected-process-analytics-api',[*target,'-DATL_TEST_REQUIRE_PROCESS_ANALYTICS=1',
        '-fsyntax-only',str(fixture)],expected=1,diagnostic="use of undeclared identifier 'ipc_stash_policy_violations_telemetry'")
    selected=base['layout_provider'] is not None
    objects={}
    for rel in ['osfmk/ipc/ipc_policy.c','osfmk/ipc/mach_debug.c']:
        record=next((o for o in base['objects'] if o['source']==rel),None)
        assert (record is not None)==selected
        if record:
            obj=(args.build.parent/record['object']).resolve()
            assert obj.is_relative_to(args.build.parent.resolve()) and sha(obj)==record['object_sha256']
        else:
            obj=out/(Path(rel).stem+'-probe.o')
            if rel.endswith('/mach_debug.c'):
                run('standard-mach_debug-requires-native-layout-provider',
                    [*target,'-c',str(source/rel),'-o',str(obj)],expected=1,
                    diagnostic="unknown builtin '__builtin_xnu_type_summary'")
                assert not obj.exists()
                continue
            run('standard-'+Path(rel).stem+'-probe',[*target,'-c',str(source/rel),'-o',str(obj)])
        objects[rel]=obj
    imports={}
    for rel,obj in objects.items():
        names=set(run(Path(rel).stem+'-actual-imports',['llvm-nm','--undefined-only',str(obj)],check=False).split())
        assert not any(name.startswith(('_ca_','_csproc_','_iokit_','_proc_')) for name in names)
        imports[rel]=sorted(names)
    policy=read_object(objects[FILES[0]])
    assert {'_ipc_kobject_register_startup','_ipc_policy_array','_ipc_inc_telemetry_count'}<=set(policy[2])
    assert len(symbol_bytes(policy,'_ipc_kobject_register_startup'))>64
    registrations=['___startup_MACH_IPC_entry_ipc_policy_set_defaults_',
                   '___startup_TUNABLES_entry_ipc_policy_update_from_tunables_',
                   '___startup_TUNABLES_entry_ipc_policy_construct_entitlement_hardening_']
    assert all(any(name.startswith(prefix) for name in policy[2]) for prefix in registrations)
    assert {'_thread_guard_violation','_task_exception_notify','_exit_with_mach_exception','_task_violated_guard'}<=set(imports[FILES[0]])
    if selected:assert '_mach_memory_entry_describe' in imports[FILES[4]]
    outcomes.append({'name':'actual-native-policy-registration-and-strong-remaining-guard-dependencies','passed':True,
        'object_sha256':{rel:sha(obj) for rel,obj in objects.items()},'imports':imports,
        'bsd_guard_termination_dependency_remains':True})
    callers={}
    for rel in ['osfmk/ipc/ipc_object.c','osfmk/ipc/ipc_kmsg.c']:
        record=next((o for o in base['objects'] if o['source']==rel),None)
        if selected:
            assert record is not None
            obj=(args.build.parent/record['object']).resolve()
            assert obj.is_relative_to(args.build.parent.resolve()) and sha(obj)==record['object_sha256']
            actual=set(run(Path(rel).stem+'-actual-imports',['llvm-nm','--undefined-only',str(obj)],check=False).split())
            assert actual==set(record['undefined_symbols']) and '_ipc_stash_policy_violations_telemetry' not in actual
            callers[rel]=sha(obj)
    outcomes.append({'name':'optional-analytics-callers-keep-native-right-copying','passed':True,
                     'caller_objects_selected':selected,'actual_object_sha256':callers})
    report={'schema_version':1,'label':'HOST_TESTED',
        'scope':'NATIVE_IPC_POLICY_SELECTION_SOURCE_ABI_AND_TARGET_OBJECTS_ONLY_NO_IPC_OR_XNU_EXECUTION',
        'port_id':base['port_id'],'build_report_sha256':sha(args.build),
        'inputs':{rel:sha(ROOT/rel) for rel in ['tools/test_xnu_ipc_policy_scope.py','tools/test_xnu_brk_scope.py','tests/xnu_port/ipc_policy_abi.c']},
        'patch_sha256':sha(ROOT/'xnu-port'/PATCH),'objects_selected_in_base':selected,
        'standard_debug_probe_requires_layout_provider':not selected,
        'native_core_function_count':len(native),'process_analytics_selected':False,
        'legacy_sdk_exception_selected':False,'bsd_guard_termination_dependency_remains':True,
        'full_firmware_bsd_or_iokit_compositions_supported':False,'outcomes':outcomes,'commands':commands,
        'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':len(outcomes),'objects_selected_in_base':selected,'xnu_executed':False}))

if __name__=='__main__':main()
