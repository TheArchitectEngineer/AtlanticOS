"""Build/run host C tests; sanitizers supported on Linux/macOS Clang."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--sanitize',action='store_true')
args=p.parse_args()
out=ROOT/'work/freestanding-tests'
out.mkdir(parents=True,exist_ok=True)
cc=shutil.which('clang')
if not cc:
    raise SystemExit('clang required for C tests')
exe=out/('test-fdt.exe' if sys.platform=='win32' else 'test-fdt')
flags=['-std=c11','-Wall','-Wextra','-Werror','-O1','-g','-Iinclude']
if args.sanitize:
    flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
command=[cc,*flags,'tests/c/test_fdt.c','atlantic-core/fdt.c','-o',str(exe)]
build=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=30)
(out/'build.log').write_text(build.stdout+build.stderr,encoding='utf-8',newline='\n')
if build.returncode:
    print(build.stdout+build.stderr)
    raise SystemExit(build.returncode)
if sys.platform != 'win32':
    harness = subprocess.run([cc, *flags, '-D_POSIX_C_SOURCE=200809L',
                              'tools/fdt_check.c', 'atlantic-core/fdt.c',
                              '-o', str(out/'fdt-check')],
                             cwd=ROOT, capture_output=True, text=True, timeout=30)
    (out/'file-harness-build.log').write_text(harness.stdout+harness.stderr, encoding='utf-8', newline='\n')
    if harness.returncode:
        print(harness.stdout+harness.stderr)
        raise SystemExit(harness.returncode)
test=subprocess.run([str(exe)],cwd=ROOT,capture_output=True,text=True,timeout=20)
(out/'test.log').write_text(test.stdout+test.stderr,encoding='utf-8',newline='\n')
print(test.stdout+test.stderr)
report={'label':'HOST_TESTED','scope':'ORIGINAL_FREESTANDING_FDT_PARSER_NOT_HARDWARE',
        'sanitizers':args.sanitize,'exit_code':test.returncode,
        'compiler':subprocess.check_output([cc,'--version'],text=True).splitlines()[0]}
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
raise SystemExit(test.returncode)
