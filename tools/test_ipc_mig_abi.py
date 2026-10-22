"""Check genuine MIG header roles and the ARM64 kernel port-object ABI.

The negative fixture rejects a 32-bit name passed as a kernel port object.
No message delivery, importance propagation, IOKit or kernel execution is tested.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--output', type=Path, default=ROOT/'work/ipc-mig-abi-tests')
    args = ap.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()):
        ap.error('Output must stay under work/')
    build = json.loads(args.build.read_text())
    lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if build['port_id'] != lock['port_id'] or build['failed_units']:
        ap.error('Use a successful build of the current patch series')
    for rel, expected in build['inputs'].items():
        if digest(ROOT/rel) != expected:
            ap.error('Changed build input: '+rel)
    headers = build['generated_headers']
    if len(headers) != 57 or len({h['path'] for h in headers}) != 57:
        ap.error('Pinned recipes require 57 unique selected headers, including native source side effects')
    roles = Counter(h['role'] for h in headers)
    if dict(roles) != {'sender':14, 'kernel-server':22, 'kernel-sender':21}:
        ap.error('Unexpected MIG role counts')
    selected = {h['path']:h['role'] for h in headers}
    for name in ['mach_notify', 'task_access', 'upl', 'vm_map', 'ktrace_background', 'vfs_nspace']:
        if selected.get('include/mach/'+name+'.h') != 'kernel-sender':
            ap.error('Kernel sender precedence lost: '+name)
    if selected.get('include/device/device_server.h') != 'kernel-server':
        ap.error('Native device kernel-server header missing')
    for item in headers:
        path = (args.build.parent/item['path']).resolve()
        if not path.is_relative_to(args.build.parent.resolve()) or digest(path) != item['sha256']:
            ap.error('Changed or escaping generated header: '+item['path'])
    commands = [c for c in build['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c)]
    if len(commands) != 1 or commands[0][-4] != '-c':
        ap.error('Unexpected target ABI command')
    base = [s.replace('<ROOT>',str(ROOT)) for s in commands[0][:-4]]
    fixture = ROOT/'tests/xnu_port/ipc_mig_abi.c'
    out.mkdir(parents=True, exist_ok=True)
    outcomes = []
    for name,flags,expected,diagnostic in [('declarations',[],0,None),
        ('reject-port-name',['-DATL_TEST_PORT_NAME_AS_OBJECT=1'],1,'incompatible integer to pointer conversion'),
        ('reject-legacy-server',['-DATL_TEST_LEGACY_SERVER_ABI=1'],1,'incompatible function pointer types')]:
        cmd = [*base,*flags,'-Werror=int-conversion','-Werror=incompatible-function-pointer-types',
               '-fsyntax-only',str(fixture)]
        r = subprocess.run(cmd,text=True,capture_output=True,timeout=60)
        (out/(name+'.log')).write_text((r.stdout+r.stderr).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        passed = r.returncode == expected and (diagnostic is None or diagnostic in r.stderr)
        outcomes.append({'name':name,'exit_code':r.returncode,'expected':expected,'passed':passed,
            'command':[s.replace(str(ROOT),'<ROOT>') for s in cmd]})
    report = {'schema_version':1,'label':'HOST_TESTED',
        'scope':'GENERATED_MIG_ROLES_AND_KERNEL_PORT_ABI_ONLY_NO_RPC_OR_KERNEL_EXECUTION',
        'port_id':lock['port_id'],'build_report_sha256':digest(args.build),
        'tool_sha256':digest(__file__),'fixture_sha256':digest(fixture),
        'header_count':len(headers),'header_roles':dict(roles),'outcomes':outcomes,
        'device_rpc_count':0,'kernel_linked':False,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':sum(c['passed'] for c in outcomes),'cases':len(outcomes),
        'header_count':len(headers),'report':str(out/'report.json')}))
    return 0 if all(c['passed'] for c in outcomes) else 1


if __name__ == '__main__':
    raise SystemExit(main())
