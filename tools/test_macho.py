"""Test original static-image plans on host; no loading, XNU or device execution."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ['include/atlantic/macho.h', 'atlantic-core/macho.c',
          'tests/c/test_macho.c', 'tests/xnu_port/macho_format_abi.c', 'tools/test_macho.py']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--sanitize', action='store_true')
    ap.add_argument('--lld-fixtures', type=Path, help='Existing genuine Atlantic LLD v2 test directory')
    ap.add_argument('--xnu-build', type=Path, help='Successful native build for official header ABI checks')
    args = ap.parse_args()
    out = args.output.resolve()
    cc = shutil.which('clang')
    if platform.system() != 'Linux' or not cc:
        ap.error('Use Linux/WSL with real Clang')
    if out.exists() or not out.is_relative_to((ROOT/'work').resolve()):
        ap.error('Use a new output directory under work/')
    fixtures, expected, fixture_proof = [], [], None
    if args.lld_fixtures:
        folder = args.lld_fixtures.resolve()
        proof = json.loads((folder/'report.json').read_text())
        assert proof['linker_version'] == 'AtlanticOS-static-arm64-v2 LLD 19.1.7'
        assert all(i['passed'] for i in proof['outcomes']) and len(proof['outcomes']) == 54
        for rel, digest in proof['inputs'].items():
            assert sha(ROOT/rel) == digest, 'Changed LLD fixture input: '+rel
        expected = proof['images']
        assert proof['weak_definition_image_audits'] == 12
        remaining = list(folder.glob('*.macho'))
        for record in expected:
            matches = [f for f in remaining if sha(f) == record['file_sha256']]
            assert matches, 'Missing original LLD output bytes'
            fixtures.append(matches[0])
            remaining.remove(matches[0])
        assert len(fixtures) == 15
        fixture_proof = {'report_sha256': sha(folder/'report.json'),
                         'linker_sha256': proof['linker_sha256'], 'source_inputs': proof['inputs']}
    out.mkdir(parents=True)
    commands = []

    def run(name, cmd):
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=60)
        commands.append([str(s).replace(str(ROOT), '<ROOT>') for s in cmd])
        (out/(name+'.log')).write_text((result.stdout+result.stderr).replace(str(ROOT), '<ROOT>'),
                                      encoding='utf-8', newline='\n')
        if result.returncode:
            raise RuntimeError(name+' failed: '+result.stderr[-2500:])
        return result.stdout

    flags = ['-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-I'+str(ROOT/'include')]
    if args.sanitize:
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    exe = out/'host-tests'
    run('host-build', [cc, *flags, str(ROOT/'atlantic-core/macho.c'),
                       str(ROOT/'tests/c/test_macho.c'), '-o', str(exe)])
    stdout = run('host-tests', [str(exe), *map(str, fixtures)])
    stats = json.loads(next(s[5:] for s in stdout.splitlines() if s.startswith('PASS ')))
    assert stats['truncations'] == 33024 and stats['mutations'] == 12000 and stats['rejections'] >= 48
    images = [json.loads(s[6:]) for s in stdout.splitlines() if s.startswith('IMAGE ')]
    audits = []
    for image, record, path in zip(images, expected, fixtures, strict=True):
        segs = record['segments']
        assert image == {'entry': int(record['entry'], 16), 'base': int(record['base'], 16),
                         'span': segs[-1]['address']-segs[0]['address']+
                                 ((segs[-1]['virtual_size']+16383)//16384)*16384,
                         'segments': len(segs), 'sections': sum(len(s['sections']) for s in segs),
                         'symbols': record['symbol_count']}
        audits.append({'file': path.name, 'sha256': sha(path), 'plan': image})
    obj = out/'macho-arm64.o'
    run('arm64-build', [cc, '--target=aarch64-none-elf', '-std=c11', '-O2', '-ffreestanding',
                        '-fno-builtin', '-fno-stack-protector', '-Wall', '-Wextra', '-Werror',
                        '-I'+str(ROOT/'include'), '-c', str(ROOT/'atlantic-core/macho.c'), '-o', str(obj)])
    data = obj.read_bytes()
    assert data[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', data, 18)[0] == 183
    assert not run('arm64-imports', ['llvm-nm', '--undefined-only', str(obj)]).strip()
    native = None
    if args.xnu_build:
        base = json.loads(args.xnu_build.read_text())
        lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
        assert not base['failed_units'] and base['port_id'] == lock['port_id']
        for rel, digest in base['inputs'].items():
            assert sha(ROOT/rel) == digest, 'Changed native input: '+rel
        recipe = next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
        assert recipe[-4] == '-c'
        target = [s.replace('<ROOT>', str(ROOT)) for s in recipe[:-4]]
        if base['layout_provider']:
            assert sha(target[0]) == base['layout_provider']['compiler_sha256']
        for item in base['config_headers']+base['generated_headers']:
            assert sha(args.xnu_build.parent/item['path']) == item['sha256'], 'Changed generated header'
        source = ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
        headers = ['EXTERNAL_HEADERS/mach-o/loader.h', 'EXTERNAL_HEADERS/mach-o/nlist.h',
                   'osfmk/mach/arm/thread_status.h', 'osfmk/mach/arm/_structs.h']
        for rel in headers:
            assert sha(source/rel) == hashlib.sha256((ROOT/'xnu-upstream'/rel).read_text().encode()).hexdigest()
        native_obj = out/'native-format-abi.o'
        run('native-format-abi', [*target, '-c', str(ROOT/'tests/xnu_port/macho_format_abi.c'), '-o', str(native_obj)])
        native = {'build_report_sha256': sha(args.xnu_build), 'object_sha256': sha(native_obj),
                  'headers': {p: sha(source/p) for p in headers}, 'xnu_executed': False}
    report = {'schema_version': 1, 'label': 'HOST_TESTED',
              'scope': 'ORIGINAL_STATIC_MACHO_PLAN_ONLY_NO_LOADING_OR_XNU_OR_DEVICE_EXECUTION',
              'inputs': {p: sha(ROOT/p) for p in INPUTS}, 'commands': commands,
              'sanitizers': args.sanitize, 'host_contracts': stats, 'lld_fixture_audits': audits,
              'lld_fixture_proof': fixture_proof,
              'native_header_abi': native, 'arm64_object_sha256': sha(obj),
              'compiler_version': subprocess.check_output([cc, '--version'], text=True).splitlines()[0],
              'kernel_linked': False, 'xnu_executed': False, 'phone_accessed': False,
              'image_loaded': False, 'signature_checked': False, 'physical_memory_measured': False}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'host_passed': True, **stats, 'lld_images': len(audits), 'native_abi': native is not None}))


if __name__ == '__main__':
    main()
