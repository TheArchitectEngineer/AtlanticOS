"""Audit genuine MIG installed headers, native coalitions and bank field scopes.

Only preprocessing, target ABI and objects are checked. No coalition, persona,
process, voucher, UPL, VM debug, scheduler policy, notification or XNU execution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from build_xnu_lab import make_list
from xnu_selection import generated_cfiles
from test_xnu_brk_scope import function,read_object,symbol_bytes

ROOT=Path(__file__).resolve().parents[1]
PATCH='0029-match-bank-telemetry-uses-to-native-field-guard.patch'
NATIVE={'osfmk/kern/coalition.c':'_coalitions_init','osfmk/kern/mk_sp.c':'_thread_policy',
        'osfmk/vm/vm_pmap.c':'_unified_page_list_iterator_init',
        'osfmk/vm/vm_debug.c':'_host_virtual_physical_table_info'}
BANK='osfmk/bank/bank.c'
CORE=['bank_task_destroy','bank_task_initialize','bank_get_value','bank_release_value','bank_swap_thread_bank_ledger']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def hashed(text):return hashlib.sha256(text.encode()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();base=json.loads(args.build.read_text());lock=json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if base['port_id']!=lock['port_id'] or base['failed_units']:ap.error('Use a successful current build')
    for rel,expected in base['inputs'].items():
        if sha(ROOT/rel)!=expected:ap.error('Changed base input: '+rel)
    source=ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
    provenance={}
    for rel in NATIVE:
        assert hashed((ROOT/'xnu-upstream'/rel).read_text())==sha(source/rel)
        provenance[rel]={'source_sha256':sha(source/rel),'unchanged':True}
    before=(ROOT/'xnu-upstream'/BANK).read_text();after=(source/BANK).read_text()
    record=next(i for i in lock['canonical_lf_files'] if i['path']==BANK)
    assert hashed(before)==record['preimage_sha256'] and sha(source/BANK)==record['postimage_sha256']
    assert sha(ROOT/'xnu-port'/PATCH)==lock['patches'][PATCH]
    provenance[BANK]={'source_sha256':sha(source/BANK),'unchanged':False,'preimage_sha256':record['preimage_sha256']}
    header=(source/'osfmk/bank/bank_internal.h').read_text()
    assert hashed((ROOT/'xnu-upstream/osfmk/bank/bank_internal.h').read_text())==hashed(header)
    recipe=next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    assert recipe[-4]=='-c';target=[s.replace('<ROOT>',str(ROOT)) for s in recipe[:-4]]
    if base['layout_provider']:assert sha(target[0])==base['layout_provider']['compiler_sha256']
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():ap.error('Use a new output directory under work/')
    out.mkdir(parents=True);commands,outcomes=[],[]
    def run(name,cmd,data=None,expected=0,diagnostic=None,check=True):
        result=subprocess.run(cmd,input=data,cwd=ROOT,text=True,capture_output=True,timeout=60)
        commands.append([s.replace(str(ROOT),'<ROOT>') for s in cmd])
        log=result.stderr if data is not None else result.stdout+result.stderr
        (out/(name+'.log')).write_text(log.replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        assert result.returncode==expected and (not diagnostic or diagnostic in result.stderr),name+': '+result.stderr[-2500:]
        if check:outcomes.append({'name':name,'passed':True,'exit_code':result.returncode,'expected':expected})
        return result.stdout
    outcomes.append({'name':'four-native-units-intact-bank-field-guard-scoped-and-header-intact','passed':True,
                     'sources':provenance,'bank_internal_header_sha256':hashed(header)})
    mk=(source/'osfmk/mach/Makefile').read_text();servers=set(make_list(mk,'MIG_KSHDRS'))
    installed=set(make_list(mk,'MIG_USHDRS'));overlap=installed&servers;expected=installed-servers
    assert overlap=={'exc_server.h','mach_exc_server.h'} and len(expected)==13
    actual={i['path']:i for i in base['generated_headers']}
    assert len(actual)==len(base['generated_headers'])==70
    assert {Path(p).name for p,r in actual.items() if r['role']=='user-server'}==expected
    for name in overlap:assert actual['include/mach/'+name]['role']=='kernel-server'
    for item in base['generated_headers']:
        path=(args.build.parent/item['path']).resolve()
        assert path.is_relative_to(args.build.parent.resolve()) and sha(path)==item['sha256']
    assert actual['include/mach/coalition_notification_server.h']['role']=='user-server'
    assert actual['include/mach/coalition_notification.h']['role']=='kernel-sender'
    assert 'mach/coalition_notification_user.c' in generated_cfiles((args.build.parent/'config/Makefile').read_text())
    outcomes.append({'name':'13-genuine-installed-server-headers-with-internal-precedence-and-selected-kernel-sender','passed':True,
        'installed_headers':sorted(expected),'internal_overrides':sorted(overlap),'generated_header_count':70})
    start=header.index('struct bank_task {');end=header.index('\n};',start)+3;structure=header[start:end]+'\n'
    funcs=['bank_task_alloc_init','bank_get_bank_account_holder_resource_coalition_id']
    for coal,telemetry in [(0,0),(0,1),(1,0),(1,1)]:
        prefix=f'#define CONFIG_COALITIONS {coal}\n#define CONFIG_TELEMETRY {telemetry}\n#define DEVELOPMENT 1\n'
        name=f'coalitions-{coal}-telemetry-{telemetry}'
        field=run(name+'-struct',[target[0],'--target=arm64-apple-macos11','-E','-P','-x','c','-'],prefix+structure,check=False)
        present=bool(coal and telemetry);assert ('bt_rsrc_coal_id' in field)==present
        processed={}
        for func in funcs:
            outputs=[]
            for role,text in [('upstream',before),('adapted',after)]:
                result=run(name+'-'+func+'-'+role,[target[0],'--target=arm64-apple-macos11','-E','-P','-x','c','-'],
                    prefix+function(text,func),check=False);outputs.append(result)
            old,new=outputs;assert ('bt_rsrc_coal_id' in new)==present
            if not coal or telemetry:assert old==new
            if func=='bank_task_alloc_init':
                assert all(call+'(' in new for call in ['zalloc_flags','proc_uniqueid','proc_pid','proc_persona_get','lck_mtx_init'])
            else:assert 'return 0;' in new
            processed[func]=hashed(new)
        outcomes.append({'name':name,'passed':True,'native_field_present':present,'consumer_field_present':present,
                         'fragment_sha256':processed})
    core={}
    for name in CORE:
        original=function(before,name);adapted=function(after,name);assert original==adapted,name;core[name]=hashed(adapted)
    outcomes.append({'name':'five-native-bank-core-bodies-preserved','passed':True,'function_sha256':core})
    fixture=ROOT/'tests/xnu_port/coalition_bank_abi.c';ref=out/'native-abi.o'
    run('native-coalition-bank-abi',[*target,'-c',str(fixture),'-o',str(ref)])
    run('reject-absent-telemetry-field',[*target,'-DATL_TEST_ABSENT_TELEMETRY_FIELD=1','-fsyntax-only',str(fixture)],
        expected=1,diagnostic="no member named 'bt_rsrc_coal_id'")
    run('reject-wrong-bank-callback',[*target,'-DATL_TEST_WRONG_BANK_CALLBACK=1','-Werror=incompatible-function-pointer-types',
        '-fsyntax-only',str(fixture)],expected=1,diagnostic='incompatible function pointer types')
    selected=base['layout_provider'] is not None;objects,imports,records={},{},{}
    for rel,symbol in (NATIVE|{BANK:'_bank_task_initialize'}).items():
        item=next((o for o in base['objects'] if o['source']==rel),None)
        assert (item is not None)==selected
        if not item:continue
        obj=(args.build.parent/item['object']).resolve()
        assert obj.is_relative_to(args.build.parent.resolve()) and sha(obj)==item['object_sha256'] and sha(source/rel)==item['source_sha256']
        parsed=read_object(obj);assert symbol in parsed[2] and parsed[2][symbol]['type']&1
        names=set(run(Path(rel).stem+'-actual-imports',['llvm-nm','--undefined-only',str(obj)],check=False).split())
        assert names==set(item['undefined_symbols'])
        objects[rel]=parsed;imports[rel]=names;records[rel]={'source_sha256':item['source_sha256'],'object_sha256':sha(obj),'imports':sorted(names)}
    if selected:
        assert any(s.startswith('___startup_MACH_IPC_entry_bank_init_') for s in objects[BANK][2])
        outcomes.append({'name':'five-actual-native-objects-and-bank-startup-registration','passed':True,'objects':records})
        assert {'_coalition_notification','_ipc_port_release_send','_ledger_credit','_ledger_debit'}<=imports['osfmk/kern/coalition.c']
        assert {'_proc_persona_get','_proc_pid','_proc_uniqueid','_persona_get_id',
                '_ipc_register_well_known_mach_voucher_attr_manager'}<=imports[BANK]
        assert '_thread_set_mode_and_absolute_pri' in imports['osfmk/kern/mk_sp.c']
        outcomes.append({'name':'native-notification-ledger-voucher-and-remaining-identity-dependencies','passed':True,
                         'persona_provider_implemented':False,'notification_delivered':False})
        failure=symbol_bytes(read_object(ref),'_atl_native_failure_reference',8)
        for name in ['_host_virtual_physical_table_info','_vm32_mach_vm_region_info',
                     '_vm32_mach_vm_region_info_64','_vm32_vm_mapped_pages_info']:
            assert symbol_bytes(objects['osfmk/vm/vm_debug.c'],name,8)==failure
        outcomes.append({'name':'actual-disabled-vm-debug-returns-native-failure','passed':True,'vm_debug_active':False,
                         'return_reference_sha256':hashlib.sha256(failure).hexdigest()})
    else:outcomes.append({'name':'standard-selection-keeps-five-native-providers-unselected','passed':True,'base_object_count':len(base['objects'])})
    report={'schema_version':1,'label':'HOST_TESTED',
        'scope':'GENUINE_MIG_HEADER_ROLES_COALITION_BANK_SOURCE_ABI_AND_OBJECTS_ONLY_NO_XNU_OR_HARDWARE_EXECUTION',
        'port_id':base['port_id'],'build_report_sha256':sha(args.build),
        'inputs':{p:sha(ROOT/p) for p in ['tools/test_xnu_coalition_bank.py','tools/build_xnu_lab.py','tools/xnu_selection.py',
                                        'tools/test_xnu_brk_scope.py','tests/xnu_port/coalition_bank_abi.c']},
        'patch_sha256':sha(ROOT/'xnu-port'/PATCH),'native_units_unchanged':4,'native_units_scoped':1,
        'objects_selected_in_base':selected,'native_bank_core_function_count':len(core),'generated_header_count':70,
        'vm_debug_active':False,'notification_delivered':False,'persona_provider_implemented':False,
        'outcomes':outcomes,'commands':commands,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':len(outcomes),'objects_selected_in_base':selected,'generated_headers':70,'xnu_executed':False}))

if __name__=='__main__':main()
