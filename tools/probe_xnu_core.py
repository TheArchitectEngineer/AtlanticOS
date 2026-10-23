"""Record compilation of unresolved native core candidates without adding stubs.

Diagnostic probes only. A successful individual file is not integrated, linked,
or executed. Failing compilation is retained as evidence, not a passing test.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ['osfmk/ipc/ipc_policy.c', 'osfmk/ipc/mach_debug.c',
              'osfmk/arm64/sleh.c', 'osfmk/vm/vm_pageout.c']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    base = json.loads(args.build.read_text())
    lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if base['port_id'] != lock['port_id'] or base['failed_units'] or not base['layout_provider']:
        ap.error('Use a successful current experimental build')
    for rel, sha in base['inputs'].items():
        if digest(ROOT/rel) != sha:
            ap.error('Changed base input: '+rel)
    source = ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
    for item in lock['canonical_lf_files']:
        if digest(source/item['path']) != item['postimage_sha256']:
            ap.error('Changed prepared source: '+item['path'])
    for item in base['config_headers']+base['generated_headers']:
        path = (args.build.parent/item['path']).resolve()
        if not path.is_relative_to(args.build.parent.resolve()) or digest(path) != item['sha256']:
            ap.error('Changed or escaping generated header: '+item['path'])
    command = next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    if command[-4] != '-c':
        ap.error('Unexpected native target recipe')
    target = [s.replace('<ROOT>',str(ROOT)) for s in command[:-4]]
    if digest(target[0]) != base['layout_provider']['compiler_sha256']:
        ap.error('Changed experimental compiler')
    out = args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():
        ap.error('Use a new output directory under work/')
    out.mkdir(parents=True)
    units = []
    for rel in CANDIDATES:
        flags = ['-DVM_UNSAFE_TYPES'] if rel.startswith('osfmk/vm/') else []
        obj = out/(Path(rel).stem+'.o')
        cmd = [*target,*flags,'-c',str(source/rel),'-o',str(obj)]
        result = subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=60)
        log = out/(Path(rel).stem+'.log')
        log.write_text((result.stdout+result.stderr).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        units.append({'source':rel,'source_sha256':digest(source/rel),'exit_code':result.returncode,
            'log':log.name,'log_sha256':digest(log),'object_sha256':digest(obj) if obj.is_file() else None,
            'command':[s.replace(str(ROOT),'<ROOT>') for s in cmd],
            'diagnostics':[s.replace(str(ROOT),'<ROOT>') for s in result.stderr.splitlines() if 'error:' in s]})
    report = {'schema_version':1,'scope':'NATIVE_CORE_COMPILE_PROBES_ONLY_NOT_INTEGRATED_LINKED_OR_EXECUTED',
        'port_id':base['port_id'],'base_report_sha256':digest(args.build),'tool_sha256':digest(__file__),
        'units':units,'compiled_units':sum(u['exit_code']==0 for u in units),
        'failed_units':sum(u['exit_code']!=0 for u in units),'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'compiled_units':report['compiled_units'],'failed_units':report['failed_units'],
                      'diagnostic_only':True,'report':str(out/'report.json')}))


if __name__ == '__main__':
    main()
