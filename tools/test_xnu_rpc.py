"""Verify actual MIG objects, descriptor ABI and required kernel table providers.

Checks target compilation and symbol relationships only, never RPC execution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build',type=Path,required=True)
    ap.add_argument('--rpc',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=ROOT/'work/xnu-rpc-tests')
    args = ap.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()):
        ap.error('Output must stay under work/')
    base = json.loads(args.build.read_text())
    rpc = json.loads(args.rpc.read_text())
    lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if (rpc['base_build_report_sha256'] != digest(args.build) or rpc['port_id'] != lock['port_id'] or
        base['port_id'] != lock['port_id'] or base['failed_units'] or rpc['failed_units'] or rpc['generation_failures'] or
        len(rpc['objects']) != 42 or not all(c['passed'] for c in rpc['config_cases']+rpc['idl_scope_cases'])):
        ap.error('Use complete current native base/RPC builds')
    for rel,expected in {**base['inputs'],**rpc['inputs']}.items():
        if digest(ROOT/rel) != expected:
            ap.error('Changed input: '+rel)
    source = ROOT/'work/xnu-lab-sources'/lock['port_id'][:16]
    exports = set()
    for item in rpc['objects']:
        obj = (args.rpc.parent/item['object']).resolve()
        generated = (args.rpc.parent/item['source']).resolve()
        header = (args.rpc.parent/item['header']).resolve()
        if (not all(p.is_relative_to(args.rpc.parent.resolve()) for p in [obj,generated,header]) or
            digest(obj) != item['object_sha256'] or digest(generated) != item['source_sha256'] or
            digest(header) != item['header_sha256'] or
            digest(source/item['definition']) != item['definition_sha256']):
            ap.error('Changed RPC artifact: '+item['module'])
        lines = subprocess.check_output(['llvm-nm','--extern-only','--defined-only','--format=posix',str(obj)],text=True).splitlines()
        actual = {s.split()[0] for s in lines if s.split()}
        if actual != set(item['defined_external_symbols']):
            ap.error('RPC symbol inventory differs: '+item['module'])
        exports.update(actual)
    kobject = next((o for o in base['objects'] if o['source']=='osfmk/kern/ipc_kobject.c'),None)
    required = []
    if kobject:
        obj = args.build.parent/kobject['object']
        if digest(obj) != kobject['object_sha256']:
            ap.error('Changed real kobject object')
        required = sorted(s.strip() for s in subprocess.check_output(
            ['llvm-nm','--undefined-only',str(obj)],text=True).splitlines() if s.strip().endswith('_subsystem'))
        if not required or not set(required).issubset(exports):
            ap.error('Native kobject subsystem table still lacks generated providers')
    # Native ipc_kobject.c casts generated descriptor prefixes to this type.
    # Compile every emitted server header against that actual target ABI.
    out.mkdir(parents=True,exist_ok=True)
    fixture = out/'descriptor_abi.c'
    text = '#include <stddef.h>\n#include <mach/mig.h>\n'
    for item in rpc['objects']:
        if item['role']=='kernel-server':
            text += '#include <'+item['header'].removeprefix('include/')+'>\n'
    text += '''#ifdef ATL_TEST_WRONG_DESCRIPTOR_PREFIX
_Static_assert(offsetof(struct mig_kern_subsystem, kroutine) ==
    offsetof(struct mig_kern_subsystem, kroutine) + 1,
    "AtlanticOS MIG descriptor prefix mismatch");
#endif
'''
    for item in rpc['objects']:
        if item['role']!='kernel-server':
            continue
        symbol = item['required_descriptor'].removeprefix('_')
        for field in ['kserver','start','end','maxsize','reserved','kroutine']:
            text += ('_Static_assert(offsetof(__typeof__('+symbol+'), '+field+') == '
                'offsetof(struct mig_kern_subsystem, '+field+'), "'+symbol+' '+field+' offset");\n')
        text += ('_Static_assert(__builtin_types_compatible_p(__typeof__('+symbol+'.kserver), '
                 'mig_kern_server_routine_t), "native kernel demux type");\n')
        text += ('_Static_assert(sizeof('+symbol+'.kroutine[0]) == sizeof(struct kern_routine_descriptor), '
                 '"native routine descriptor stride");\n')
    fixture.write_text(text,encoding='utf-8',newline='\n')
    command = next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    if command[-4]!='-c':
        ap.error('Unexpected native target command')
    target = [s.replace('<ROOT>',str(ROOT)) for s in command[:-4]]
    outcomes = []
    for name,flags,expected in [('descriptor-layout',[],0),('reject-descriptor-prefix',['-DATL_TEST_WRONG_DESCRIPTOR_PREFIX=1'],1)]:
        cmd = [target[0],'-I'+str(args.rpc.parent/'include'),*target[1:],*flags,'-fsyntax-only',str(fixture)]
        r = subprocess.run(cmd,text=True,capture_output=True,timeout=60)
        (out/(name+'.log')).write_text((r.stdout+r.stderr).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        outcomes.append({'name':name,'exit_code':r.returncode,'expected':expected,
            'passed':r.returncode==expected and (expected==0 or 'AtlanticOS MIG descriptor prefix mismatch' in r.stderr),
            'command':[s.replace(str(ROOT),'<ROOT>') for s in cmd]})
    report = {'schema_version':1,'label':'HOST_TESTED',
        'scope':'NATIVE_RPC_OBJECTS_DESCRIPTOR_TARGET_ABI_AND_OPTIONAL_KOBJECT_TABLE_COVERAGE_NO_EXECUTION',
        'port_id':lock['port_id'],'base_report_sha256':digest(args.build),'rpc_report_sha256':digest(args.rpc),
        'tool_sha256':digest(__file__),'fixture_sha256':digest(fixture),'outcomes':outcomes,
        'descriptor_count':sum(i['role']=='kernel-server' for i in rpc['objects']),
        'kobject_table_checked':bool(kobject),'required_subsystem_symbols':required,
        'all_required_subsystems_have_native_generated_providers':bool(kobject),
        'kernel_linked':False,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':sum(c['passed'] for c in outcomes),'cases':len(outcomes),
        'descriptors':report['descriptor_count'],'required_subsystems':len(required),'kobject_table_checked':bool(kobject)}))
    return 0 if all(c['passed'] for c in outcomes) else 1


if __name__=='__main__':
    raise SystemExit(main())
