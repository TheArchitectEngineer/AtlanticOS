"""Check unavailable firmware APIs and, when present, the genuine pmap object.

These checks do not execute a kernel, MMU operation, verifier, or DMA backend.
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
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--output', type=Path, default=ROOT/'work/pmap-firmware-tests')
    args = ap.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()):
        ap.error('Output must stay under work/')
    report = json.loads(args.build.read_text())
    lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if report['port_id'] != lock['port_id']:
        ap.error('Build must match the current patch series')
    source = ROOT/'work/xnu-lab-sources'/lock['port_id'][:16]
    headers = {}
    for rel in ['osfmk/vm/pmap.h', 'osfmk/arm/pmap/pmap.c']:
        expected = next(c['postimage_sha256'] for c in lock['canonical_lf_files'] if c['path'] == rel)
        if digest(source/rel) != expected:
            ap.error('Changed prepared source: '+rel)
        headers[rel] = expected
    command = next(c for c in report['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    if command[-4] != '-c':
        ap.error('Unexpected compiler command; inspect before testing')
    base = [s.replace('<ROOT>', str(ROOT)) for s in command[:-4]]
    fixture = ROOT/'tests/xnu_port/pmap_firmware.c'
    out.mkdir(parents=True, exist_ok=True)
    outcomes = []
    cases = [('declarations', [], 0), ('static-unavailable', ['-DATL_TEST_STATIC_TRUST_CACHE=1'], 1),
             ('loaded-unavailable', ['-DATL_TEST_LOADED_TRUST_CACHE=1'], 1)]
    for name, flags, expected in cases:
        cmd = [*base, *flags, '-fsyntax-only', str(fixture)]
        r = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
        (out/(name+'.log')).write_text((r.stdout+r.stderr).replace(str(ROOT), '<ROOT>'), encoding='utf-8', newline='\n')
        passed = r.returncode == expected and (expected == 0 or
            'is unavailable: AtlanticOS firmware has no Apple trust-cache provider' in r.stderr)
        outcomes.append({'name':name, 'exit_code':r.returncode, 'expected':expected, 'passed':passed,
                         'command':[s.replace(str(ROOT), '<ROOT>') for s in cmd]})
    pmap = next((o for o in report['objects'] if o['source'] == 'osfmk/arm/pmap/pmap.c'), None)
    object_check = None
    if pmap:
        obj = args.build.parent/pmap['object']
        if digest(obj) != pmap['object_sha256']:
            ap.error('Pmap object changed since the build')
        defined = subprocess.check_output(['llvm-nm', '--defined-only', str(obj)], text=True)
        undefined = subprocess.check_output(['llvm-nm', '--undefined-only', str(obj)], text=True)
        required = ['_pmap_bootstrap', '_pmap_enter_options', '_pmap_page_protect', '_pmap_ro_zone_memcpy']
        if not all(any(line.split()[-2:] == ['T', name] for line in defined.splitlines()) for name in required):
            ap.error('Missing substantive pmap function definitions')
        if any(needle in defined+undefined for needle in ['trust_cache', '_amfi', '_sart_', '_ptep_get_iommu']):
            ap.error('Unexpected Apple monitor/trust-cache dependency or provider')
        (out/'pmap-defined.log').write_text(defined, encoding='utf-8', newline='\n')
        (out/'pmap-undefined.log').write_text(undefined, encoding='utf-8', newline='\n')
        object_check = {'sha256':digest(obj), 'required_external_text':required,
                        'apple_service_providers_or_dependencies_found':False}
    result = {'scope':'PMAP_FIRMWARE_API_AND_OPTIONAL_OBJECT_CHECKS_ONLY_NO_KERNEL_EXECUTION',
              'label':'HOST_TESTED', 'port_id':lock['port_id'], 'source_sha256':headers,
              'build_report_sha256':digest(args.build), 'fixture_sha256':digest(fixture), 'tool_sha256':digest(__file__),
              'outcomes':outcomes, 'pmap_object':object_check, 'kernel_linked':False,
              'xnu_executed':False, 'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'passed':sum(c['passed'] for c in outcomes), 'cases':len(cases),
                      'pmap_object_checked':bool(object_check), 'report':str(out/'report.json')}))
    return 0 if all(c['passed'] for c in outcomes) else 1


if __name__ == '__main__':
    raise SystemExit(main())
