"""Audit native bootstrap component boundaries without executing XNU.

Checks real source preprocessing, retained Mach initialization order and the
actual startup.o imports. Feature combinations are fragment checks, not claims
that forbidden complete firmware compositions build or run.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from test_xnu_brk_scope import function

ROOT=Path(__file__).resolve().parents[1]
FUNCTIONS=['kernel_bootstrap','kernel_bootstrap_thread','scale_setup','load_context']
COMPONENTS={'workq_init':'bsd','bsd_scale_setup':'bsd',
            'device_service_create':'iokit','OSKextRemoveKextBootstrap':'iokit'}
MACH_IMPORTS={'_vm_mem_bootstrap','_sched_init','_task_init','_thread_init',
              '_kernel_thread_create','_machine_load_context','_vm_pageout',
              '_clock_init','_thread_daemon_init','_turnstiles_init'}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    base=json.loads(args.build.read_text());lock=json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if base['port_id']!=lock['port_id'] or base['failed_units']:ap.error('Use a successful current build')
    for rel,expected in base['inputs'].items():
        if sha(ROOT/rel)!=expected:ap.error('Changed build input: '+rel)
    rel='osfmk/kern/startup.c'
    source=ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
    before=(ROOT/'xnu-upstream'/rel).read_text();after=(source/rel).read_text()
    record=next(r for r in lock['canonical_lf_files'] if r['path']==rel)
    assert hashlib.sha256(before.encode()).hexdigest()==record['preimage_sha256']
    assert sha(source/rel)==record['postimage_sha256']
    patch='0025-scope-bootstrap-services-to-selected-firmware-components.patch'
    assert sha(ROOT/'xnu-port'/patch)==lock['patches'][patch]
    recipe=next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    assert recipe[-4]=='-c'
    compiler=recipe[0].replace('<ROOT>',str(ROOT))
    if base['layout_provider']:assert sha(compiler)==base['layout_provider']['compiler_sha256']
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():ap.error('Use a new output directory under work/')
    out.mkdir(parents=True)
    commands,outcomes,processed=[],[],{}
    fragments=['\n'.join(function(text,name) for name in FUNCTIONS) for text in [before,after]]
    for name,fw,bsd,iokit in [('outside-firmware-none',0,0,0),('outside-firmware-providers',0,1,1),
                             ('firmware-mach',1,0,0),('firmware-bsd',1,1,0),
                             ('firmware-iokit',1,0,1),('firmware-providers',1,1,1)]:
        prefix=f'#define CONFIG_ATLANTIC_FIRMWARE {fw}\n#undef MACH_BSD\n#undef IOKIT\n'
        if bsd:prefix+='#define MACH_BSD 1\n'
        if iokit:prefix+='#define IOKIT 1\n'
        outputs=[]
        for role,text in zip(['upstream','adapted'],fragments):
            cmd=[compiler,'--target=arm64-apple-macos11.0','-mcpu=cortex-a57','-E','-P','-x','c','-']
            result=subprocess.run(cmd,input=prefix+text,cwd=ROOT,text=True,capture_output=True,timeout=60)
            commands.append([s.replace(str(ROOT),'<ROOT>') for s in cmd])
            (out/(name+'-'+role+'.log')).write_text(result.stderr+result.stdout,encoding='utf-8',newline='\n')
            assert result.returncode==0,result.stderr
            outputs.append(result.stdout)
        actual={symbol:symbol+'(' in outputs[1] for symbol in COMPONENTS}
        expected={symbol:not fw or bool(bsd if component=='bsd' else iokit)
                  for symbol,component in COMPONENTS.items()}
        assert actual==expected,(name,actual,expected)
        if not fw:assert outputs[0]==outputs[1], 'Native behavior changed outside firmware'
        for core in MACH_IMPORTS:assert core[1:]+'(' in outputs[1], (name,core)
        assert 'task_max = MAX(task_max, task_max_base * scale);' in outputs[1]
        processed[name]=outputs[1]
        outcomes.append({'name':name,'passed':True,'component_calls':actual,
                         'upstream_byte_identical_required':not fw,'mach_calls_retained':sorted(MACH_IMPORTS)})
    def ordered(text,names):
        positions=[text.index(name+'(') for name in names]
        assert positions==sorted(positions) and len(set(positions))==len(positions)
    mach=processed['firmware-mach']
    ordered(function(mach,'kernel_bootstrap'),['vm_mem_bootstrap','sched_init','mapping_free_prime',
        'machine_init','clock_init','task_init','thread_init','turnstiles_init','kernel_thread_create','load_context'])
    ordered(function(mach,'kernel_bootstrap_thread'),['idle_thread_create','sched_startup','thread_daemon_init',
        'clock_service_create','machine_lockdown','vm_set_restrictions','vm_pageout'])
    ordered(function(mach,'load_context'),['stack_alloc_try','processor_up','machine_load_context'])
    outcomes.append({'name':'substantive-native-mach-bootstrap-order-retained','passed':True,'executed':False})
    native=next(o for o in base['objects'] if o['source']==rel)
    obj=(args.build.parent/native['object']).resolve()
    assert obj.is_relative_to(args.build.parent.resolve()) and sha(obj)==native['object_sha256']
    assert native['source_sha256']==record['postimage_sha256']
    cmd=['llvm-nm','--undefined-only',str(obj)]
    result=subprocess.run(cmd,capture_output=True,text=True,timeout=60,check=True)
    commands.append([s.replace(str(ROOT),'<ROOT>') for s in cmd])
    (out/'actual-startup-imports.log').write_text(result.stdout,encoding='utf-8',newline='\n')
    imports=set(result.stdout.split())
    assert imports==set(native['undefined_symbols']) and MACH_IMPORTS<=imports
    assert not {('_'+name) for name in COMPONENTS}&imports
    outcomes.append({'name':'actual-native-startup-mach-imports-without-unselected-services','passed':True,
                     'object_sha256':sha(obj),'required_mach_imports':sorted(MACH_IMPORTS)})
    report={'schema_version':1,'label':'HOST_TESTED',
        'scope':'NATIVE_BOOTSTRAP_SOURCE_PREPROCESSING_AND_OBJECT_IMPORTS_ONLY_NOT_MACH_OR_XNU_EXECUTION',
        'port_id':base['port_id'],'build_report_sha256':sha(args.build),
        'inputs':{p:sha(ROOT/p) for p in ['tools/test_xnu_startup_scope.py','tools/test_xnu_brk_scope.py']},
        'upstream_source_sha256':record['preimage_sha256'],'adapted_source_sha256':record['postimage_sha256'],
        'patch_sha256':sha(ROOT/'xnu-port'/patch),'outcomes':outcomes,'commands':commands,
        'full_firmware_bsd_or_iokit_compositions_supported':False,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':len(outcomes),'unselected_service_imports':0,'xnu_executed':False}))

if __name__=='__main__':main()
