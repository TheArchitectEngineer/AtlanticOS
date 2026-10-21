"""Check the experimental original C-layout compiler API, not XNU execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--compiler', type=Path, required=True)
    ap.add_argument('--output', type=Path, default=ROOT/'work/clang-layout-tests')
    args = ap.parse_args()
    compiler = args.compiler.resolve()
    out = args.output.resolve()
    if not compiler.is_file() or not out.is_relative_to((ROOT/'work').resolve()):
        ap.error('Compiler must exist; output must be under work/')
    out.mkdir(parents=True, exist_ok=True)
    base = [str(compiler), '--target=arm64-apple-macos11', '-mcpu=cortex-a57', '-std=gnu11',
            '-ffreestanding', '-nostdinc', '-fblocks', '-Wall', '-Wextra', '-Werror']
    commands, outcomes = [], []
    def run(name, command, *, code=None, expected=0, diagnostic=None):
        r = subprocess.run(command, input=code, text=True, capture_output=True, timeout=30)
        (out/(name+'.log')).write_text(r.stdout+r.stderr, encoding='utf-8', newline='\n')
        commands.append([s.replace(str(ROOT),'<ROOT>') for s in command])
        passed = r.returncode == expected and (diagnostic is None or diagnostic in r.stderr)
        outcomes.append({'name':name,'exit_code':r.returncode,'expected':expected,'passed':passed,
                         'required_diagnostic':diagnostic})
        if not passed:
            print(r.stdout+r.stderr)
            raise RuntimeError(name+' failed its compiler contract check')
    fixture = ROOT/'tests/clang_layout/positive.c'
    run('positive', [*base,'-c',str(fixture),'-o',str(out/'positive.o')])
    run('llvm-ir', [*base,'-S','-emit-llvm',str(fixture),'-o',str(out/'positive.ll')])
    ir = (out/'positive.ll').read_text()
    if '__atlantic_layout_' in ir or 'c"12\\00"' not in ir:
        raise RuntimeError('Expected folded static metadata, not runtime calls')
    for case in json.loads((ROOT/'tests/clang_layout/negative.json').read_text()):
        flags = case.get('flags', [])
        selected = [s for s in base if not s.startswith('-mcpu=')] if any(s.startswith('--target=') for s in flags) else base
        command = [*selected, '-fsyntax-only', '-x','c', *flags, '-']
        run(case['name'], command, code=case['code'], expected=1, diagnostic=case['diagnostic'])
    inputs = ['compiler-port/SemaAtlanticLayout.cpp','compiler-port/ParseAtlanticLayout.inc',
              'compiler-port/patches.lock.json','tests/clang_layout/positive.c','tests/clang_layout/negative.json',
              'tools/test_atlantic_clang.py']
    report = {'scope':'EXPERIMENTAL_C_LAYOUT_COMPILER_API_ONLY_NOT_XNU_OR_PHONE_EXECUTION',
              'label':'HOST_TESTED','compiler_sha256':hashlib.sha256(compiler.read_bytes()).hexdigest(),
              'compiler_version':subprocess.check_output([str(compiler),'--version'],text=True).splitlines()[0],
              'inputs':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},
              'outcomes':outcomes,'commands':commands,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':len(outcomes),'report':str(out/'report.json'),'xnu_executed':False}))


if __name__ == '__main__':
    main()
