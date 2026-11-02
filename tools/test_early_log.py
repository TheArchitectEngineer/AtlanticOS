"""Test original RAM diagnostics; audit native formatter ABI without executing XNU.

Linux/WSL pthread host tests, ARM64 objects and native-header probes only.
The MMU-off entry must not execute this normal/shareable-memory transport.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import struct
import subprocess
from test_xnu_brk_scope import read_object, symbol_bytes
from test_xnu_memory_providers import imported_name
from test_xnu_platform import strong_external_import

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = {
    'atlantic-core/early_log.c': 'osfmk/atlantic/early_log.c',
    'include/atlantic/early_log.h': 'osfmk/atlantic/early_log.h',
    'xnu-port/platform/atlantic_log.h': 'pexpert/pexpert/atlantic_log.h',
    'xnu-port/platform/pe_early_log.c': 'osfmk/kern/atlantic_early_log.c'}
STRICT = ['-mstrict-align', '-mno-outline-atomics']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def audit_gate(code):
    words = struct.unpack('<' + 'I' * (len(code) // 4), code)
    loads = [i * 4 for i, w in enumerate(words) if w & 0xfffffc00 == 0x885ffc00]
    stores = [i * 4 for i, w in enumerate(words) if w & 0xffe0fc00 == 0x88007c00]
    releases = [i * 4 for i, w in enumerate(words) if w & 0xfffffc00 == 0x889ffc00]
    if len(loads) != 1 or len(stores) != 1 or not releases or loads[0] >= stores[0]:
        raise ValueError('expected one inline acquire/exclusive attempt and release stores')
    for i, word in enumerate(words):
        pc = i * 4
        if word & 0xfc000000 == 0x14000000:
            target = pc + 4 * signed(word & 0x3ffffff, 26)
        elif word & 0xff000010 == 0x54000000 or word & 0x7e000000 == 0x34000000:
            target = pc + 4 * signed((word >> 5) & 0x7ffff, 19)
        elif word & 0x7e000000 == 0x36000000:
            target = pc + 4 * signed((word >> 5) & 0x3fff, 14)
        else:
            continue
        if pc >= loads[0] and loads[0] <= target <= min(pc, stores[0]):
            raise ValueError('backward branch retries the exclusive gate')
    return {'acquire_offset': loads[0], 'exclusive_store_offset': stores[0],
            'release_store_offsets': releases, 'retry_branch_found': False}


def relocations(parsed, name, width=None):
    raw, sections, symbols = parsed
    symbol = symbols[name]
    section = sections[symbol['section'] - 1]
    start = symbol['value'] - section['address']
    size = len(symbol_bytes(parsed, name, width))
    defined_names = {value['index']: key for key, value in symbols.items()}
    found = []
    for i in range(section['relocation_count']):
        address, info = struct.unpack_from('<iI', raw, section['relocation_offset'] + 8 * i)
        if start <= address < start + size:
            assert (info >> 27) & 1
            index = info & 0xffffff
            target = defined_names[index] if index in defined_names else imported_name(raw, index)
            found.append({'offset': address - start, 'type': info >> 28,
                          'target': target})
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sanitize', action='store_true')
    ap.add_argument('--thread-sanitize', action='store_true',
                    help='also run a separate host executable under ThreadSanitizer')
    ap.add_argument('--xnu-build', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if platform.system() != 'Linux':
        ap.error('Run the pthread host checks under Linux or WSL')
    out = args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():
        ap.error('Use a new output directory under work/')
    compiler = shutil.which('clang')
    if not compiler:
        ap.error('clang is required')
    out.mkdir(parents=True)
    commands, outcomes = [], []

    def check(name, **details):
        outcomes.append({'name': name, 'passed': True, **details})

    def run(name, command, expected=0, diagnostic=None):
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=90)
        commands.append([str(s).replace(str(ROOT), '<ROOT>') for s in command])
        (out/(name+'.log')).write_text((result.stdout + result.stderr).replace(str(ROOT), '<ROOT>'),
                                      encoding='utf-8', newline='\n')
        assert result.returncode == expected and (not diagnostic or diagnostic in result.stderr), name + ': ' + result.stderr[-2500:]
        return result.stdout

    flags = ['-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-fno-builtin', '-I'+str(ROOT/'include')]
    plain_flags = flags.copy()
    if args.sanitize:
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    host = out/'test-early-log'
    run('host-build', [compiler, *flags, '-pthread', str(ROOT/'atlantic-core/early_log.c'),
                      str(ROOT/'tests/c/test_early_log.c'), '-o', str(host)])
    result = run('host-contracts', [str(host)])
    match = re.fullmatch(r'STRESS: (\d+) accepted, (\d+) busy, (\d+) bytes retained; no torn records\n'
                         r'PASS: (\d+) checks, 6000 model records and 16000 concurrent attempts; RAM transport only\n', result)
    assert match
    accepted, busy, retained, checks = map(int, match.groups())
    assert accepted > 0 and accepted + busy == 16000 and retained <= 16384 and checks >= 37000
    tsan = None
    if args.thread_sanitize:
        executable = out/'test-early-log-tsan'
        run('thread-sanitizer-build', [compiler, *plain_flags, '-fsanitize=thread', '-fno-omit-frame-pointer',
            '-pthread', str(ROOT/'atlantic-core/early_log.c'), str(ROOT/'tests/c/test_early_log.c'), '-o', str(executable)])
        tsan_result = run('thread-sanitizer-contracts', [str(executable)])
        tsan_match = re.fullmatch(match.re.pattern, tsan_result)
        assert tsan_match and 'ThreadSanitizer' not in (out/'thread-sanitizer-contracts.log').read_text()
        ta, tb, tr, tc = map(int, tsan_match.groups())
        assert ta > 0 and ta + tb == 16000 and tr <= 16384 and tc >= 37000
        tsan = {'host_checks': tc, 'concurrent_accepted': ta, 'concurrent_busy': tb,
                'host_executable_sha256': sha(executable), 'race_reported': False}
    elf = out/'early-log-arm64.o'
    run('portable-arm64-compile', [compiler, '--target=aarch64-none-elf', *STRICT, '-std=c11',
        '-O1', '-ffreestanding', '-fno-builtin', '-fno-stack-protector', '-I'+str(ROOT/'include'),
        '-c', str(ROOT/'atlantic-core/early_log.c'), '-o', str(elf)])
    raw = elf.read_bytes()
    assert raw[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', raw, 18)[0] == 183
    assert not run('portable-elf-imports', ['llvm-nm', '--undefined-only', str(elf)]).strip()
    native = None
    inputs = [*ORIGINAL, 'tests/c/test_early_log.c', 'tests/xnu_port/early_log_abi.c',
              'tools/test_early_log.py', 'tools/test_xnu_brk_scope.py',
              'tools/test_xnu_memory_providers.py', 'tools/test_xnu_platform.py']
    if args.xnu_build:
        base = json.loads(args.xnu_build.read_text())
        lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
        assert base['port_id'] == lock['port_id'] and not base['failed_units']
        for rel, expected in base['inputs'].items():
            assert sha(ROOT/rel) == expected, rel
        source = ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
        for rel, dest in ORIGINAL.items():
            item = next(i for i in lock['canonical_lf_files'] if i['path'] == dest)
            assert item['preimage_sha256'] is None and item['postimage_sha256'] == sha(source/dest) == sha(ROOT/rel)
        check('four-original-added-files-match-locked-patch')
        recipe = next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
        assert recipe[-4] == '-c'
        target = [s.replace('<ROOT>', str(ROOT)) for s in recipe[:-4]] + STRICT
        if base['layout_provider']:
            assert sha(target[0]) == base['layout_provider']['compiler_sha256']
        fixture = ROOT/'tests/xnu_port/early_log_abi.c'
        run('native-abi', [*target, '-fsyntax-only', str(fixture)])
        check('native-formatter-putc-snapshot-types-and-fixed-struct-sizes')
        for name, define in [('reject-putc-type', 'ATL_TEST_WRONG_PUTC_ABI'),
                             ('reject-snapshot-capacity', 'ATL_TEST_WRONG_LOG_SNAPSHOT_ABI')]:
            run(name, [*target, '-D'+define+'=1', '-Werror=incompatible-function-pointer-types',
                       '-fsyntax-only', str(fixture)], 1, 'incompatible function pointer types')
            check(name)
        objects = []
        for rel in ['osfmk/atlantic/early_log.c', 'osfmk/kern/atlantic_early_log.c']:
            record = next((i for i in base['objects'] if i['source'] == rel), None)
            assert (record is not None) == (base['layout_provider'] is not None)
            if record:
                obj = args.xnu_build.parent/record['object']
                assert sha(obj) == record['object_sha256']
                command = next(c for c in base['commands'] if len(c) >= 4 and c[-3].endswith('/'+rel) and c[-2] == '-o')
                assert all(flag in command for flag in STRICT)
            else:
                obj = out/(Path(rel).stem+'-probe.o')
                run('standard-'+Path(rel).stem, [*target, '-c', str(source/rel), '-o', str(obj)])
                check('standard-'+Path(rel).stem+'-compile-probe')
            objects.append(obj)
        core, adapter = map(read_object, objects)
        assert not run('native-core-imports', ['llvm-nm', '--undefined-only', str(objects[0])]).strip()
        imports = run('native-adapter-imports', ['llvm-nm', '--undefined-only', str(objects[1])]).split()
        assert set(imports) == {'___doprnt', '_atl_early_log_append', '_atl_early_log_capture', '_atl_early_log_snapshot', '_bzero'}
        assert all(strong_external_import(objects[1], name) for name in imports)
        check('no-atomic-runtime-or-hardware-imports-and-only-real-strong-dependencies')
        assert all('_'+name in core[2] for name in ['atl_early_log_capture', 'atl_early_log_append', 'atl_early_log_snapshot'])
        gate_audits = {}
        for name in ['_atl_early_log_append', '_atl_early_log_snapshot']:
            code = symbol_bytes(core, name)
            gate = audit_gate(code); gate_audits[name] = gate
            mutated = bytearray(code)
            retry_at = gate['exclusive_store_offset'] + 4
            struct.pack_into('<I', mutated, retry_at, 0x14000000 |
                (((gate['acquire_offset'] - retry_at) // 4) & 0x3ffffff))
            try:
                audit_gate(mutated)
            except ValueError:
                pass
            else:
                raise AssertionError('corrupted gate was accepted')
        check('native-single-attempt-exclusive-gates-release-and-mutated-retry-rejection', functions=gate_audits)
        refs = {name: relocations(adapter, name) for name in ['_kprintf', '_memory_putc', '_atlantic_xnu_log_snapshot']}
        assert any(r['target'] == '___doprnt' and r['type'] == 2 for r in refs['_kprintf'])
        assert any(r['target'] == '_atl_early_log_capture' for r in refs['_kprintf'])
        assert any(r['target'] == '_atl_early_log_append' and r['type'] == 2 for r in refs['_kprintf'])
        assert any(r['target'] == '_atl_early_log_append' and r['type'] == 2 for r in refs['_memory_putc'])
        assert any(r['target'] == '_atl_early_log_snapshot' and r['type'] == 2 for r in refs['_atlantic_xnu_log_snapshot'])
        check('actual-native-formatter-and-ram-transport-relocation-chains', relocations=refs)
        for name in ['_PE_kputc', '_PE_putc']:
            assert symbol_bytes(adapter, name, 8) == bytes(8)
            assert relocations(adapter, name, 8) == [{'offset': 0, 'type': 0, 'target': '_memory_putc'}]
        check('native-putc-variables-have-real-function-pointer-relocations')
        bss = adapter[1][adapter[2]['_boot_log']['section']-1]
        assert bss['flags'] & 0xff == 1 and bss['size'] == 16432
        check('real-owned-16432-byte-bss-instance-not-a-runtime-ram-measurement')
        ll = out/'adapter.ll'
        run('native-adapter-ir', [*target, '-S', '-emit-llvm', str(source/'osfmk/kern/atlantic_early_log.c'), '-o', str(ll)])
        ir = ll.read_text()
        assert re.search(r'call i32 @__doprnt\([^\n]*@atl_early_log_capture[^\n]*i32 noundef 16, i32 noundef 1\)', ir)
        check('native-formatter-call-preserves-radix-16-and-is-log-true')
        for name, flags, diagnostic in [
            ('reject-outside-firmware', ['-UCONFIG_ATLANTIC_FIRMWARE'], 'require the explicit ARM64 firmware profile'),
            ('reject-bsd-log-service', ['-DMACH_BSD=1'], 'do not implement the BSD or IOKit log service'),
            ('reject-iokit-log-service', ['-DIOKIT=1'], 'do not implement the BSD or IOKit log service')]:
            run(name, [*target, *flags, '-E', str(source/'osfmk/kern/atlantic_early_log.c')], 1, diagnostic)
            check(name)
        formatter_hash = hashlib.sha256((ROOT/'xnu-upstream/osfmk/kern/printf.c').read_text().encode()).hexdigest()
        assert sha(source/'osfmk/kern/printf.c') == formatter_hash
        if base['layout_provider']:
            formatter = next(o for o in base['objects'] if o['source'] == 'osfmk/kern/printf.c')
            assert formatter['source_sha256'] == formatter_hash
            assert '___doprnt' in formatter['defined_external_symbols']
        check('whole-native-formatter-source-unchanged', source_sha256=formatter_hash,
              formatter_selected_in_base=base['layout_provider'] is not None)
        run('native-core-disassembly', ['llvm-objdump', '--macho', '--disassemble', str(objects[0])])
        run('native-adapter-disassembly', ['llvm-objdump', '--macho', '--disassemble', str(objects[1])])
        native = {'build_report_sha256': sha(args.xnu_build), 'port_id': base['port_id'],
                  'objects_selected_in_base': base['layout_provider'] is not None,
                  'object_sha256': [sha(p) for p in objects], 'formatter_source_sha256': formatter_hash}
    report = {'schema_version': 1, 'label': 'HOST_TESTED',
        'scope': 'ORIGINAL_RAM_TRANSPORT_HOST_EXECUTION_AND_NATIVE_ABI_OBJECTS_ONLY_NO_NATIVE_FORMATTER_OR_XNU_EXECUTION',
        'inputs': {rel: sha(ROOT/rel) for rel in inputs}, 'commands': commands,
        'sanitizers': args.sanitize, 'thread_sanitizer': tsan,
        'host_compiler': subprocess.check_output([compiler, '--version'], text=True).splitlines()[0],
        'host_executable_sha256': sha(host), 'host_checks': checks, 'host_model_records': 6000,
        'host_concurrent_attempts': 16000, 'host_concurrent_accepted': accepted, 'host_concurrent_busy': busy,
        'portable_arm64_elf_sha256': sha(elf), 'native_xnu_abi': native, 'outcomes': outcomes,
        'transport_is_memory_only': True, 'native_formatter_executed': False,
        'xnu_executed': False, 'phone_accessed': False, 'physical_memory_measured': False}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'host_model_records': 6000, 'host_concurrent_attempts': 16000,
                      'host_checks': checks, 'native_checks': len(outcomes)}))


if __name__ == '__main__':
    main()
