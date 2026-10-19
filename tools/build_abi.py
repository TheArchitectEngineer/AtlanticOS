"""Compile an ORIGINAL unsupported BSP shell, not XNU or a bootable image."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'work/arm64-abi')
    args = parser.parse_args()
    compiler = shutil.which('clang')
    if not compiler:
        raise SystemExit('BLOCKED: clang unavailable; host policy tests do not require it')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    obj = out/'moto-g20-bsp.o'
    command = [compiler, '--target=aarch64-none-elf', '-std=c11', '-ffreestanding',
               '-fno-builtin', '-Wall', '-Wextra', '-Werror', '-Iinclude', '-c',
               'platforms/unisoc/ums512/moto-g20/bsp.c', '-o', str(obj)]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    log = result.stdout+result.stderr
    (out/'build.log').write_text(log, encoding='utf-8', newline="\n")
    if result.returncode:
        print(log)
        raise SystemExit(result.returncode)
    raw = obj.read_bytes()
    if raw[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H', raw, 18)[0] != 183:
        raise SystemExit('Not ELF64 little-endian AArch64')
    version = subprocess.check_output([compiler,'--version'],text=True).splitlines()[0]
    report = {'schema_version':1,'label':'BUILT_ARM64',
              'scope':'UNSUPPORTED_BSP_ABI_OBJECT_ONLY_NO_XNU_NO_ENTRY_NO_DRIVERS',
              'compiler':version, 'command':['clang',*command[1:-1], 'work/arm64-abi/moto-g20-bsp.o'],
              'elf_machine':183,'bytes':len(raw),'object_sha256':hashlib.sha256(raw).hexdigest(),
              'sources':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                         ['include/atlantic/platform.h','platforms/unisoc/ums512/moto-g20/bsp.c']}}
    (out/'build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8', newline="\n")
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
