"""Exercise the real TrustCache include boundary using a completed XNU build.

No replacement header, verifier, kernel execution or phone access.
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
    ap.add_argument('--build', type=Path, required=True, help='build_xnu_lab.py report.json')
    ap.add_argument('--output', type=Path, default=ROOT/'work/pmap-cs-scope-tests')
    args = ap.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()):
        ap.error('Output must stay under work/')
    report = json.loads(args.build.read_text())
    lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    header = ROOT/'work/xnu-lab-sources'/lock['port_id'][:16]/'osfmk/vm/pmap_cs.h'
    expected_header = next(i['postimage_sha256'] for i in lock['canonical_lf_files']
                           if i['path'] == 'osfmk/vm/pmap_cs.h')
    if report['port_id'] != lock['port_id'] or digest(header) != expected_header:
        ap.error('Build and actual header must match the current patch lock')
    fixture = ROOT/'tests/xnu_port/pmap_cs_scope.c'
    abi_command = next(c for c in report['commands']
                       if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    if abi_command[-4] != '-c':
        ap.error('Unrecognized build command; inspect rather than guessing')
    base = [s.replace('<ROOT>', str(ROOT)) for s in abi_command[:-4]]
    out.mkdir(parents=True, exist_ok=True)
    cases = [('no-monitor', [], 0), ('ppl-requires-real-api', ['-DATL_TEST_REQUIRE_PPL_MONITOR=1'], 1),
             ('upstream-keeps-include', ['-DATL_TEST_UPSTREAM_INCLUDE=1'], 1)]
    outcomes = []
    for name, flags, expected in cases:
        command = [*base, *flags, '-fsyntax-only', str(fixture)]
        r = subprocess.run(command, text=True, capture_output=True, timeout=30)
        diagnostic = r.stdout+r.stderr
        (out/(name+'.log')).write_text(diagnostic.replace(str(ROOT), '<ROOT>'), encoding='utf-8', newline='\n')
        passed = r.returncode == expected and (expected == 0 or "'TrustCache/API.h' file not found" in r.stderr)
        outcomes.append({'name': name, 'exit_code': r.returncode, 'expected': expected, 'passed': passed,
                         'command': [s.replace(str(ROOT), '<ROOT>') for s in command]})
    result = {'scope': 'REAL_HEADER_DEPENDENCY_SELECTION_ONLY_NOT_SIGNATURE_VALIDATION',
              'label': 'HOST_TESTED', 'port_id': lock['port_id'], 'header_sha256': digest(header),
              'build_report_sha256': digest(args.build), 'fixture_sha256': digest(fixture),
              'tool_sha256': digest(__file__), 'outcomes': outcomes,
              'xnu_executed': False, 'phone_accessed': False}
    (out/'report.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'passed': sum(c['passed'] for c in outcomes), 'cases': len(cases),
                      'report': str(out/'report.json')}))
    return 0 if all(c['passed'] for c in outcomes) else 1


if __name__ == '__main__':
    raise SystemExit(main())
