"""Audit native timer/scheduler providers, source scopes and actual target ABI.

This executes preprocessing and object inspection only. No timer, allocator,
task/thread policy, identity service, SFI, PMU or XNU runtime is executed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from test_xnu_brk_scope import function,read_object,symbol_bytes

ROOT=Path(__file__).resolve().parents[1]
PATCH='0028-scope-bsd-throttle-callbacks-and-fix-native-resource-failure-path.patch'
NATIVE={
    'osfmk/kern/mk_timer.c':'_mk_timer_port_label_dealloc',
    'osfmk/kern/syscall_subr.c':'_thread_depress_expire',
    'osfmk/kern/timeout.c':'_kern_timeout_start',
    'osfmk/kern/affinity.c':'_task_affinity_create',
    'osfmk/vm/vm_map_store_ll.c':'_vm_map_store_init_ll',
    'osfmk/kern/counter_common.c':'_scalable_counter_static_init',
    'osfmk/kern/task_ident.c':'_task_create_identity_token',
    'osfmk/kern/sfi.c':'_sfi_thread_classify'}
SCOPED={'osfmk/kern/thread_policy.c':'_thread_policy_create',
        'osfmk/kern/task_policy.c':'_task_policy_create'}
CORE={
    'osfmk/kern/thread_policy.c':['thread_policy_create','thread_policy_reset',
        'thread_recompute_priority','thread_recompute_kernel_promotion_locked',
        'thread_recompute_user_promotion_locked','proc_get_effective_thread_policy'],
    'osfmk/kern/task_policy.c':['task_policy_create','task_policy_get','task_policy_set',
        'proc_get_effective_task_policy','task_importance_init_from_parent',
        'task_policy_update_complete_unlocked']}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def hashed(text):return hashlib.sha256(text.encode()).hexdigest()

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
    before={rel:(ROOT/'xnu-upstream'/rel).read_text() for rel in NATIVE|SCOPED}
    after={rel:(source/rel).read_text() for rel in before}
    sources={}
    for rel in NATIVE:
        assert hashed(before[rel])==sha(source/rel)
        sources[rel]={'unchanged':True,'source_sha256':sha(source/rel)}
    for rel in SCOPED:
        record=next(i for i in lock['canonical_lf_files'] if i['path']==rel)
        assert hashed(before[rel])==record['preimage_sha256'] and sha(source/rel)==record['postimage_sha256']
        sources[rel]={'unchanged':False,'source_sha256':sha(source/rel),'preimage_sha256':record['preimage_sha256']}
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
    outcomes.append({'name':'eight-native-sources-intact-and-two-scoped-preimages-locked','passed':True,'sources':sources})
    t='osfmk/kern/thread_policy.c';p='osfmk/kern/task_policy.c'
    pieces=[('thread_policy_update_complete_unlocked',t),('set_thread_iotier_override',t),
            ('send_resource_violation_with_fatal_port',p)]
    for name,fw,bsd in [('outside-firmware-no-bsd',0,0),('outside-firmware-bsd',0,1),
                        ('firmware-mach',1,0),('firmware-bsd',1,1)]:
        prefix=f'#define CONFIG_ATLANTIC_FIRMWARE {fw}\n#undef MACH_BSD\n'
        if bsd:prefix+='#define MACH_BSD 1\n'
        records={}
        for func,rel in pieces:
            outputs=[]
            for role,texts in [('upstream',before),('adapted',after)]:
                result=run(name+'-'+func+'-'+role,[target[0],'--target=arm64-apple-macos11','-E','-P','-x','c','-'],
                    prefix+function(texts[rel],func),check=False)
                outputs.append(result)
            old,new=outputs
            if rel==t:
                assert ('rethrottle_thread(' in new)==(not fw or bool(bsd))
                if not fw or bsd:assert old==new
                if func=='set_thread_iotier_override':assert 'OSCompareAndSwap(' in new and 'thread->iotier_override' in new
                else:assert 'turnstile_update_thread_priority_chain(' in new and 'sfi_reevaluate(' in new
            elif bsd:assert old==new
            else:
                assert 'return KERN_NOT_SUPPORTED;' in new and 'kr' not in new and 'KERN_SUCCESS' not in new
            records[func]=hashed(new)
        outcomes.append({'name':name,'passed':True,'bsd_throttle_callback_selected':not fw or bool(bsd),
                         'resource_notification_supported_by_branch':bool(bsd),'fragment_sha256':records})
    core={}
    for rel,names in CORE.items():
        for name in names:
            original=function(before[rel],name);adapted=function(after[rel],name)
            assert original==adapted,name;core[name]=hashed(adapted)
    outcomes.append({'name':'12-native-scheduler-and-policy-bodies-intact','passed':True,'function_sha256':core})
    fixture=ROOT/'tests/xnu_port/scheduler_provider_abi.c';ref=out/'native-abi.o'
    run('native-timer-policy-counter-abi',[*target,'-c',str(fixture),'-o',str(ref)])
    run('reject-narrow-deadline',[*target,'-DATL_TEST_NARROW_TIMER_DEADLINE=1',
        '-Werror=incompatible-pointer-types','-fsyntax-only',str(fixture)],expected=1,diagnostic='incompatible pointer types')
    run('reject-wrong-label-callback',[*target,'-DATL_TEST_WRONG_LABEL_CALLBACK=1',
        '-Werror=incompatible-function-pointer-types','-fsyntax-only',str(fixture)],expected=1,diagnostic='incompatible function pointer types')
    selected=base['layout_provider'] is not None
    objects,imports,object_records={},{},{}
    for rel,symbol in (NATIVE|SCOPED).items():
        record=next((o for o in base['objects'] if o['source']==rel),None)
        assert (record is not None)==selected
        if not record:continue
        obj=(args.build.parent/record['object']).resolve()
        assert obj.is_relative_to(args.build.parent.resolve()) and sha(obj)==record['object_sha256']
        assert record['source_sha256']==sha(source/rel)
        parsed=read_object(obj);assert symbol in parsed[2] and parsed[2][symbol]['type']&1
        actual=set(run(Path(rel).stem+'-actual-imports',['llvm-nm','--undefined-only',str(obj)],check=False).split())
        assert actual==set(record['undefined_symbols'])
        objects[rel]=parsed;imports[rel]=actual;object_records[rel]={'source_sha256':sha(source/rel),'object_sha256':sha(obj),'imports':sorted(actual)}
    if selected:
        outcomes.append({'name':'ten-actual-native-provider-objects-and-strong-symbols','passed':True,'objects':object_records})
        timer_imports=imports['osfmk/kern/mk_timer.c']
        assert {'_thread_call_setup','_thread_call_cancel','_thread_call_enter_delayed_with_leeway',
                '_kernel_mach_msg_send_kmsg','_zalloc_flags','_zfree','_ipc_right_destroy'}<=timer_imports
        assert len(symbol_bytes(objects['osfmk/kern/mk_timer.c'],'_mk_timer_expire'))>64
        policy=next(o for o in base['objects'] if o['source']=='osfmk/ipc/ipc_policy.c')
        assert '_mk_timer_port_label_dealloc' in policy['undefined_symbols']
        assert '_zalloc_percpu_permanent' in imports['osfmk/kern/counter_common.c']
        assert not {'_rethrottle_thread','_get_bsdthread_info'}&imports[t]
        assert {'_proc_find_ident','_proc_ident_with_policy','_proc_rele','_proc_task'}<=imports['osfmk/kern/task_ident.c']
        outcomes.append({'name':'genuine-timer-lifecycle-counter-allocation-and-remaining-identity-dependencies','passed':True,
                         'bsd_io_callback_implemented':False,'identity_process_provider_implemented':False})
        assert not any(s.startswith('-DCONFIG_SCHED_SFI') for s in base['selected_defines'])
        reference=symbol_bytes(read_object(ref),'_atl_native_unsupported_reference',8)
        for name in ['_sfi_set_window','_sfi_window_cancel','_sfi_set_class_offtime']:
            assert symbol_bytes(objects['osfmk/kern/sfi.c'],name,8)==reference
        assert symbol_bytes(objects[p],'_send_resource_violation_with_fatal_port',8)==reference
        outcomes.append({'name':'actual-native-disabled-sfi-and-resource-notification-return-not-supported','passed':True,
                         'return_reference_sha256':hashlib.sha256(reference).hexdigest(),'sfi_active':False})
    else:
        outcomes.append({'name':'standard-selection-keeps-all-ten-providers-unselected','passed':True,'base_object_count':len(base['objects'])})
    report={'schema_version':1,'label':'HOST_TESTED',
        'scope':'NATIVE_SCHEDULER_TIMER_SOURCE_ABI_AND_OBJECTS_ONLY_NO_KERNEL_OR_HARDWARE_EXECUTION',
        'port_id':base['port_id'],'build_report_sha256':sha(args.build),
        'inputs':{rel:sha(ROOT/rel) for rel in ['tools/test_xnu_scheduler_providers.py','tools/test_xnu_brk_scope.py','tests/xnu_port/scheduler_provider_abi.c']},
        'patch_sha256':sha(ROOT/'xnu-port'/PATCH),'native_units_unchanged':8,'native_units_scoped':2,
        'objects_selected_in_base':selected,'native_core_function_count':len(core),'outcomes':outcomes,'commands':commands,
        'sfi_active':False,'pmu_measured':False,'timers_executed':False,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':len(outcomes),'objects_selected_in_base':selected,'timers_executed':False}))

if __name__=='__main__':main()
