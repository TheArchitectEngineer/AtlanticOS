"""Compare genuine ARM64 metadata layouts across native Mach/BSD header contexts.

Only target compilation, negative ABI checks and optional object inspection.
Does not execute allocation, reference counting, credentials, RO writes or XNU.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
COMMON = {'ro_bytes', 'ro_align', 'owner_offset', 'proc_offset', 'tokens_offset',
          'flags_offset', 'ports_offset', 'payload_offset', 'payload_bytes'}
CONTEXT_FIELDS = {'mach': {'task_bytes', 'task_align', 'task_ro_pointer_offset',
                  'thread_ro_bytes', 'thread_ro_align', 'thread_owner_offset',
                  'thread_task_offset', 'thread_ro_pointer_offset'},
                  'bsd': {'proc_bytes', 'proc_align', 'refcount_offset'}}
REQUIRED = {
    'osfmk/kern/task.c': ['_task_init', '_task_create_internal', '_task_get_ro', '_task_info'],
    'osfmk/kern/task_ref.c': ['_task_ref_init', '_task_ref_count_init', '_task_ref_count_fini'],
    'osfmk/kern/atlantic_task_metadata.c': ['_proc_ro_alloc', '_proc_ro_ref_task',
        '_proc_ro_erase_task', '_proc_require', '_task_ref_hold_proc_task_struct',
        '_task_release_proc_task_struct'],
    'osfmk/kern/atlantic_task_process.c': ['_get_bsdtask_info'],
    'osfmk/kern/atlantic_thread_metadata.c': ['_get_thread_ro', '_current_thread_ro',
        '_get_threadtask', '_get_threadtask_early']}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--output', type=Path, default=ROOT/'work/task-metadata-tests')
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
    source = ROOT/'work/xnu-lab-sources'/lock['port_id'][:16]
    source_hashes = {}
    for item in lock['canonical_lf_files']:
        if digest(source/item['path']) != item['postimage_sha256']:
            ap.error('Changed prepared source: '+item['path'])
        source_hashes[item['path']] = item['postimage_sha256']
    for rel in ['bsd/sys/proc_ro.h', 'bsd/sys/proc_internal.h', 'bsd/sys/proc_require.h']:
        source_hashes[rel] = digest(source/rel)
    commands = [c for c in build['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c)]
    if len(commands) != 1 or commands[0][-4] != '-c':
        ap.error('Unexpected target command; inspect before testing')
    base = [s.replace('<ROOT>', str(ROOT)) for s in commands[0][:-4]]
    provider = build.get('layout_provider')
    if provider and digest(base[0]) != provider['compiler_sha256']:
        ap.error('Experimental compiler differs from build')
    fixture = ROOT/'tests/xnu_port/task_metadata_abi.c'
    out.mkdir(parents=True, exist_ok=True)
    outcomes, layouts = [], {}
    for context in CONTEXT_FIELDS:
        flags = [] if context == 'mach' else ['-UMACH_KERNEL_PRIVATE', '-DBSD_KERNEL_PRIVATE=1']
        ir = out/(context+'.ll')
        cmd = [*base, *flags, '-S', '-emit-llvm', str(fixture), '-o', str(ir)]
        r = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
        (out/(context+'.log')).write_text((r.stdout+r.stderr).replace(str(ROOT), '<ROOT>'), encoding='utf-8', newline='\n')
        record = {'name':context, 'exit_code':r.returncode, 'expected':0, 'passed':r.returncode == 0,
                  'command':[s.replace(str(ROOT), '<ROOT>') for s in cmd]}
        outcomes.append(record)
        if r.returncode:
            continue
        values = {}
        for line in ir.read_text().splitlines():
            if not line.startswith('@atl_meta_'):
                continue
            match = re.fullmatch(r'@atl_meta_(\w+) = .*constant i64 (\d+),.*', line)
            if match is None or match[1] in values:
                ap.error('Unexpected or duplicate target constant: '+line)
            values[match[1]] = int(match[2])
        if set(values) != COMMON | CONTEXT_FIELDS[context]:
            ap.error('Missing or unexpected target ABI constants in '+context)
        layouts[context] = values
        record['llvm_ir_sha256'] = digest(ir)
        # Corrupt only the expected owner offset. Real types remain unchanged.
        cmd = [*base, *flags, '-DATL_TEST_WRONG_OWNER_OFFSET='+str(values['owner_offset']+1),
               '-fsyntax-only', str(fixture)]
        r = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
        (out/(context+'-reject-owner.log')).write_text((r.stdout+r.stderr).replace(str(ROOT), '<ROOT>'), encoding='utf-8', newline='\n')
        outcomes.append({'name':context+'-reject-owner', 'exit_code':r.returncode, 'expected':1,
            'passed':r.returncode == 1 and 'AtlanticOS metadata owner offset mismatch' in r.stderr,
            'command':[s.replace(str(ROOT), '<ROOT>') for s in cmd]})
        if context == 'mach':
            cmd = [*base, '-DATL_TEST_WRONG_THREAD_OWNER_OFFSET='+str(values['thread_owner_offset']+1),
                   '-fsyntax-only', str(fixture)]
            r = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
            (out/'mach-reject-thread-owner.log').write_text((r.stdout+r.stderr).replace(str(ROOT), '<ROOT>'), encoding='utf-8', newline='\n')
            outcomes.append({'name':'mach-reject-thread-owner', 'exit_code':r.returncode, 'expected':1,
                'passed':r.returncode == 1 and 'AtlanticOS thread metadata owner offset mismatch' in r.stderr,
                'command':[s.replace(str(ROOT), '<ROOT>') for s in cmd]})
    same = len(layouts) == 2 and all(layouts['mach'][k] == layouts['bsd'][k] for k in COMMON)
    object_checks = []
    for item in build['objects']:
        if item['source'] not in REQUIRED:
            continue
        obj = args.build.parent/item['object']
        if digest(obj) != item['object_sha256'] or digest(source/item['source']) != item['source_sha256']:
            ap.error('Changed task source/object: '+item['source'])
        defined = subprocess.check_output(['llvm-nm', '--defined-only', str(obj)], text=True)
        undefined = subprocess.check_output(['llvm-nm', '--undefined-only', str(obj)], text=True)
        if not all(any(line.split()[-2:] == ['T', name] for line in defined.splitlines()) for name in REQUIRED[item['source']]):
            ap.error('Missing genuine external task function: '+item['source'])
        stem = Path(item['source']).stem
        (out/(stem+'-defined.log')).write_text(defined, encoding='utf-8', newline='\n')
        (out/(stem+'-undefined.log')).write_text(undefined, encoding='utf-8', newline='\n')
        object_checks.append({'source':item['source'], 'object_sha256':digest(obj),
                              'required_external_text':REQUIRED[item['source']]})
    if object_checks and len(object_checks) != len(REQUIRED):
        ap.error('Partial task object set; inspect before accepting')
    result = {'schema_version':1, 'label':'HOST_TESTED',
        'scope':'TARGET_LAYOUT_COMPARISON_NEGATIVE_ABI_AND_OPTIONAL_TASK_OBJECTS_ONLY',
        'port_id':lock['port_id'], 'build_report_sha256':digest(args.build),
        'fixture_sha256':digest(fixture), 'tool_sha256':digest(__file__),
        'native_function_lock_sha256':digest(ROOT/'xnu-port/task-metadata-native.lock.json'),
        'source_sha256':source_hashes, 'outcomes':outcomes, 'layouts':layouts,
        'shared_field_count':len(COMMON), 'shared_fields_match':same,
        'objects':object_checks, 'kernel_linked':False, 'xnu_executed':False,
        'allocation_or_reference_operations_executed':False, 'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'passed':sum(c['passed'] for c in outcomes), 'cases':len(outcomes),
                     'shared_fields_match':same, 'task_objects_checked':len(object_checks),
                     'report':str(out/'report.json')}))
    return 0 if same and len(outcomes) == 5 and all(c['passed'] for c in outcomes) else 1


if __name__ == '__main__':
    raise SystemExit(main())
