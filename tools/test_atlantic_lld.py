"""Audit fixed-load Mach-O ARM64 link fixtures; does not execute XNU or firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_image(path, base):
    """Read only the bounded fixture format, including its full static contract."""
    data = path.read_bytes()
    magic, cpu, sub, filetype, count, size, flags, reserved = struct.unpack_from('<8I', data)
    assert (magic, cpu, sub, filetype, reserved) == (0xfeedfacf, 0x100000c, 0, 2, 0)
    assert flags == 1, ('Expected only MH_NOUNDEFS', flags)
    assert 0 < count < 50 and 32 + size <= len(data)
    segments, symbols, descriptions, commands, pc = [], {}, {}, [], None
    cursor, symtab = 32, None
    for _ in range(count):
        cmd, cmdsize = struct.unpack_from('<II', data, cursor)
        assert cmdsize >= 8 and cmdsize % 8 == 0 and cursor + cmdsize <= 32 + size
        # SEGMENT_64, SYMTAB, DYSYMTAB, UUID, BUILD_VERSION, UNIXTHREAD only.
        assert cmd in {0x19, 0x2, 0xb, 0x1b, 0x32, 0x5}, hex(cmd)
        commands.append(hex(cmd))
        if cmd == 0x19:
            name, va, vmsize, off, filesize, maxprot, prot, nsects, segflags = struct.unpack_from('<16s4Q4I', data, cursor+8)
            name = name.rstrip(b'\0').decode('ascii')
            assert cmdsize == 72 + 80*nsects
            assert va % 0x4000 == 0 and va >= base and vmsize >= filesize
            assert off + filesize <= len(data)
            assert prot == maxprot and prot & 1 and not (prot & 2 and prot & 4)
            sections = []
            for i in range(nsects):
                values = struct.unpack_from('<16s16s2Q8I', data, cursor+72+80*i)
                sect, seg, addr, length, sectoff, align, reloff, nreloc, sf, r1, r2, r3 = values
                assert seg.rstrip(b'\0').decode() == name
                assert va <= addr <= va + vmsize and length <= va+vmsize-addr
                assert reloff == nreloc == 0
                if sf & 0xff not in {1, 12, 18}:
                    assert off <= sectoff <= off+filesize and length <= off+filesize-sectoff
                if sf & 0x80000400:
                    assert prot & 4
                sections.append({'name':sect.rstrip(b'\0').decode(), 'address':hex(addr), 'size':length, 'flags':hex(sf)})
            segments.append({'name':name, 'address':va, 'virtual_size':vmsize, 'file_offset':off,
                             'file_size':filesize, 'protection':prot, 'sections':sections})
        elif cmd == 0x5:
            assert pc is None and cmdsize == 288
            assert struct.unpack_from('<II', data, cursor+8) == (6, 68)
            state = bytearray(data[cursor+16:cursor+cmdsize])
            pc = struct.unpack_from('<Q', state, 256)[0]
            state[256:264] = b'\0'*8
            assert state == b'\0'*272, 'SP and other state are zero; bootstrap owns them'
        elif cmd == 0x2:
            assert symtab is None
            symtab = struct.unpack_from('<4I', data, cursor+8)
        elif cmd == 0xb:
            fields = struct.unpack_from('<18I', data, cursor+8)
            assert fields[5] == 0 and fields[15] == 0 and fields[17] == 0, 'No undefined symbols or runtime relocations'
        cursor += cmdsize
    assert cursor == 32+size and symtab is not None and pc is not None
    assert segments[0]['name'] == '__TEXT' and segments[0]['address'] == base and segments[0]['file_offset'] == 0
    for a, b in zip(segments, segments[1:]):
        assert a['address']+a['virtual_size'] <= b['address']
        assert a['file_offset']+a['file_size'] <= b['file_offset']
    symoff, nsyms, stroff, strsize = symtab
    assert symoff+16*nsyms <= len(data) and stroff+strsize <= len(data)
    strings = data[stroff:stroff+strsize]
    for i in range(nsyms):
        nameoff, stype, section, desc, value = struct.unpack_from('<IBBHQ', data, symoff+16*i)
        assert nameoff < len(strings)
        end = strings.index(0, nameoff)
        name = strings[nameoff:end].decode()
        if stype & 0xe0:  # Debug STABS are not definitions.
            continue
        assert stype & 0xe != 0, ('No N_UNDF allowed', name)
        assert name not in symbols
        symbols[name] = value
        descriptions[name] = {'description':desc, 'type':stype}
    assert pc == symbols['__start'] and pc % 4 == 0
    assert any(s['address'] <= pc < s['address']+s['virtual_size'] and s['protection'] == 5 for s in segments)

    def read_at(va, fmt):
        width = struct.calcsize(fmt)
        for seg in segments:
            delta = va-seg['address']
            if 0 <= delta <= seg['file_size']-width:
                return struct.unpack_from(fmt, data, seg['file_offset']+delta)[0]
        raise AssertionError('Address has no file-backed bytes: '+hex(va))

    result = {'commands':commands, 'entry':hex(pc), 'base':hex(base), 'segments':segments,
              'symbol_count':len(symbols), 'file_sha256':digest(path)}
    return result, symbols, descriptions, read_at


def adrp_address(read_at, at):
    inst = read_at(at, '<I')
    assert inst & 0x9f000000 == 0x90000000
    imm = ((inst >> 29) & 3) | (((inst >> 5) & 0x7ffff) << 2)
    if imm & 0x100000:
        imm -= 1 << 21
    return (at & ~0xfff) + (imm << 12)


def branch_address(read_at, at):
    branch = read_at(at, '<I')
    assert branch & 0xfc000000 == 0x94000000
    imm = branch & 0x3ffffff
    if imm & 0x2000000:
        imm -= 1 << 26
    return at + 4*imm


def inspect_image(path, base):
    """Independent byte-level checks, including actual relocated instructions."""
    result, symbols, descriptions, read_at = read_image(path, base)
    pc, segments = symbols['__start'], result['segments']

    assert read_at(symbols['_value'], '<Q') == 0x1122334455667788
    assert read_at(symbols['_pointer'], '<Q') == symbols['_value']+8
    assert read_at(symbols['_entry_pointer'], '<Q') == pc
    assert read_at(symbols['_delta'], '<Q') == symbols['_zero']-symbols['_value']
    assert symbols['__mh_execute_header'] == base
    assert read_at(symbols['_header_pointer'], '<Q') == base
    got_delta = read_at(symbols['_got_delta'], '<i')
    assert read_at(symbols['_got_delta']+got_delta, '<Q') == symbols['_value']
    assert read_at(symbols['_readonly'], '<Q') == 0xa1b2c3d4e5f6071
    assert next(s for s in segments if s['name'] == '__DATA_CONST')['protection'] == 1
    ds = next(s for s in segments if s['name'] == '__DATA')
    assert ds['protection'] == 3 and ds['virtual_size'] > ds['file_size']
    assert ds['address'] <= symbols['_zero'] < ds['address']+ds['virtual_size']
    assert symbols['_zero']+0x5000 <= ds['address']+ds['virtual_size']
    assert branch_address(read_at, pc) == symbols['_helper']

    for offset, symbol in [(4, '_value'), (12, '_zero')]:
        add = read_at(pc+offset+4, '<I')
        assert add & 0xffc00000 == 0x91000000
        assert adrp_address(read_at, pc+offset) + ((add >> 10) & 0xfff) == symbols[symbol]
    load = read_at(pc+32, '<I')
    if load & 0xffc00000 == 0xf9400000:
        got = adrp_address(read_at, pc+28) + (((load >> 10) & 0xfff) << 3)
        assert read_at(got, '<Q') == symbols['_value']
    else:
        # Upstream legally relaxes a resolved GOT load into ADRP + ADD.
        assert load & 0xffc00000 == 0x91000000
        assert adrp_address(read_at, pc+28) + ((load >> 10) & 0xfff) == symbols['_value']
    result['relocations_checked'] = ['BRANCH26','PAGE21','PAGEOFF12','GOT_LOAD_PAGE21',
                                   'GOT_LOAD_PAGEOFF12','POINTER_TO_GOT','UNSIGNED64','SUBTRACTOR64']
    return result


def inspect_weak_image(path, base, expected_return, expected_data, expected_weak, expected_private=False):
    result, symbols, descriptions, read_at = read_image(path, base)
    selected, value, pc = symbols['_selected'], symbols['_selected_value'], symbols['__start']
    # Preserve N_WEAK_DEF for selected weak definitions; no runtime binding.
    for name in ['_selected', '_selected_value']:
        assert bool(descriptions[name]['description'] & 0x80) == (expected_weak and not expected_private)
        assert bool(descriptions[name]['type'] & 0x10) == expected_private
    assert read_at(selected, '<I') == 0xd2800000 | (expected_return << 5)
    assert read_at(selected+4, '<I') == 0xd65f03c0  # RET.
    assert read_at(value, '<Q') == expected_data
    assert branch_address(read_at, pc) == selected
    assert read_at(symbols['_selected_pointer'], '<Q') == selected
    assert read_at(symbols['_selected_value_pointer'], '<Q') == value
    for name, expected in [('_selected_got', selected), ('_selected_value_got', value)]:
        got = symbols[name] + read_at(symbols[name], '<i')
        assert read_at(got, '<Q') == expected
    load = read_at(pc+8, '<I')
    if load & 0xffc00000 == 0x91000000:
        destination = adrp_address(read_at, pc+4) + ((load >> 10) & 0xfff)
    else:
        assert load & 0xffc00000 == 0xf9400000
        got = adrp_address(read_at, pc+4) + (((load >> 10) & 0xfff) << 3)
        destination = read_at(got, '<Q')
    assert destination == selected
    add = read_at(pc+20, '<I')
    assert add & 0xffc00000 == 0x91000000
    assert adrp_address(read_at, pc+16) + ((add >> 10) & 0xfff) == value
    result.update({'scope':'WEAK_DEFINITION_SELECTION_AND_STATIC_RELOCATIONS_ONLY',
                   'selected_return':expected_return, 'selected_data':hex(expected_data),
                   'selected_definition_is_weak':expected_weak,
                   'selected_definition_is_private_external':expected_private})
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--linker', type=Path, required=True)
    ap.add_argument('--compiler', type=Path, default=Path('/usr/bin/clang-19'))
    ap.add_argument('--ar', type=Path, default=Path('/usr/bin/llvm-ar-19'))
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    # Preserve the ld64.lld driver symlink name.
    linker, compiler, out = args.linker.absolute(), args.compiler.absolute(), args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():
        ap.error('Use a new output directory under work/')
    out.mkdir(parents=True)
    outcomes, commands, images = [], [], []

    def run(name, cmd, *, code=None, success=True, diagnostic=None):
        result = subprocess.run([str(s) for s in cmd], input=code, text=True, capture_output=True, timeout=60)
        (out/(name+'.log')).write_text((result.stdout+result.stderr).replace(str(ROOT), '<ROOT>'), encoding='utf-8', newline='\n')
        passed = (result.returncode == 0) == success and (diagnostic is None or diagnostic in result.stderr)
        outcomes.append({'name':name, 'exit_code':result.returncode, 'passed':passed, 'required_diagnostic':diagnostic})
        commands.append([str(s).replace(str(ROOT),'<ROOT>') for s in cmd])
        if not passed:
            raise RuntimeError(name+' failed: '+result.stdout+result.stderr)

    cc = [compiler, '--target=arm64-apple-macos11', '-mcpu=cortex-a57', '-ffreestanding', '-c']
    for name in ['entry', 'data']:
        run('compile-'+name, [*cc, ROOT/'tests/lld_static'/(name+'.s'), '-o', out/(name+'.o')])
    objects = [out/'entry.o', out/'data.o']
    shared = ['-arch','arm64','-platform_version','macos','11.0','11.0','-e','__start',
              '-fatal_warnings','-undefined','error','--error-limit=0','-no_uuid',
              '-segprot','__DATA_CONST','r--','r--']
    for name, base in [('low',0x40000000), ('high',0xfffffff007004000)]:
        image = out/(name+'.macho')
        run('link-'+name, [linker, '--atlantic-static-arm64='+hex(base), *shared, '-o', image, *objects])
        images.append(inspect_image(image, base))
    negative = [
        ('unaligned-base', '--atlantic-static-arm64=40000001', [], '16 KiB aligned'),
        ('zero-base', '--atlantic-static-arm64=0', [], '16 KiB aligned'),
        ('noncanonical-base', '--atlantic-static-arm64=1111000040000000', [], 'canonical'),
        ('overflow-base', '--atlantic-static-arm64=ffffffffffffc000', [], '256 MiB'),
        ('invalid-base', '--atlantic-static-arm64=not-hex', [], 'unsigned 64-bit'),
        ('base-too-wide', '--atlantic-static-arm64=10000000000000000', [], 'unsigned 64-bit'),
        ('wrong-architecture', '--atlantic-static-arm64=40000000', ['-arch','x86_64'], 'requires arm64'),
        ('pie-option', '--atlantic-static-arm64=40000000', ['-pie'], 'option not supported'),
        ('legacy-static-option', '--atlantic-static-arm64=40000000', ['-static'], 'option not supported'),
        ('dynamic-lookup', '--atlantic-static-arm64=40000000', ['-undefined','dynamic_lookup'], '-undefined error'),
        ('writable-executable', '--atlantic-static-arm64=40000000', ['-segprot','__TEXT','rwx','rwx'], 'writable executable'),
        ('nonexecute-text', '--atlantic-static-arm64=40000000', ['-segprot','__TEXT','r--','r--'], 'lacks execute permission'),
        ('data-entry', '--atlantic-static-arm64=40000000', ['-e','_value'], 'instruction symbol'),
    ]
    for name, mode, extra, diagnostic in negative:
        image = out/(name+'.macho')
        run(name, [linker, mode, *shared, *extra, '-o', image, *objects], success=False, diagnostic=diagnostic)
        assert not image.exists(), 'Rejected links must not publish a file'
    fixtures = [
        ('undefined', '.text\n.globl __start\n__start: bl _missing\n', 'undefined symbol: _missing'),
        ('weak-undefined', '.text\n.globl __start\n.weak_reference _missing\n__start: bl _missing\n', 'undefined symbol: _missing'),
        ('tls', '.text\n.globl __start\n__start: ret\n.section __DATA,__thread_vars,thread_local_variables\n.quad 0,0,0\n', 'unsupported runtime section'),
        ('unreferenced-undefined', '.text\n.globl __start, _unprovided\n__start: ret\n', 'unresolved or dynamic symbol'),
        ('constructor', '.text\n.globl __start\n__start: ret\n.section __DATA,__mod_init_func,mod_init_funcs\n.quad __start\n', 'unsupported runtime section'),
    ]
    for name, code, diagnostic in fixtures:
        src, obj, image = out/(name+'.s'), out/(name+'.o'), out/(name+'.macho')
        src.write_text(code)
        run('compile-'+name, [*cc, src, '-o', obj])
        run('reject-'+name, [linker,'--atlantic-static-arm64=40000000',*shared,'-o',image,obj], success=False, diagnostic=diagnostic)
        assert not image.exists()
    bitcode = out/'bitcode.o'
    run('compile-bitcode', [*cc,'-emit-llvm','-x','c','-','-o',bitcode], code='void _start(void) {}\n')
    rejected = out/'bitcode.macho'
    run('reject-bitcode', [linker,'--atlantic-static-arm64=40000000',*shared,'-o',rejected,bitcode],
        success=False, diagnostic='requires native Mach-O objects')
    assert not rejected.exists()
    archive = out/'data.a'
    run('archive-native-object', [args.ar,'rcs',archive,out/'data.o'])
    archived = out/'archive.macho'
    run('link-native-archive', [linker,'--atlantic-static-arm64=40000000',*shared,'-o',archived,out/'entry.o',archive])
    images.append(inspect_image(archived, 0x40000000))
    run('compile-weak-entry', [*cc,ROOT/'tests/lld_static/weak-entry.s','-o',out/'weak-entry.o'])
    definitions = [('weak-a',17,0x1111,False), ('weak-b',34,0x2222,False),
                   ('strong-c',51,0x3333,True), ('strong-d',68,0x4444,True),
                   ('weak-private-a',85,0x5555,False), ('weak-private-b',102,0x6666,False)]
    for name, returned, value, strong in definitions:
        flags = ['-DSELECTED_RETURN='+str(returned),'-DSELECTED_DATA='+hex(value)]
        if strong:
            flags.append('-DSTRONG_DEFINITION=1')
        if name.startswith('weak-private-'):
            flags.append('-DPRIVATE_DEFINITION=1')
        run('compile-'+name, [*cc,*flags,ROOT/'tests/lld_static/weak-definition.S','-o',out/(name+'.o')])
    for name in ['weak-a', 'strong-c']:
        run('archive-'+name, [args.ar,'rcs',out/(name+'.a'),out/(name+'.o')])
    weak_cases = [
        ('weak-a', ['weak-a.o'],17,0x1111,True,0x40000000),
        ('weak-ab', ['weak-a.o','weak-b.o'],17,0x1111,True,0x40000000),
        ('weak-ba', ['weak-b.o','weak-a.o'],34,0x2222,True,0x40000000),
        ('weak-then-strong', ['weak-a.o','weak-b.o','strong-c.o'],51,0x3333,False,0x40000000),
        ('strong-then-weak', ['strong-c.o','weak-a.o','weak-b.o'],51,0x3333,False,0x40000000),
        ('weak-strong-weak', ['weak-a.o','strong-c.o','weak-b.o'],51,0x3333,False,0x40000000),
        ('high-weak', ['weak-b.o','weak-a.o'],34,0x2222,True,0xfffffff007004000),
        ('archive-weak', ['weak-a.a'],17,0x1111,True,0x40000000),
        ('archive-weak-then-strong', ['weak-a.a','strong-c.o'],51,0x3333,False,0x40000000),
        # A lazy archive member is not extracted just to supersede a resolved weak.
        ('weak-then-strong-archive', ['weak-a.o','strong-c.a'],17,0x1111,True,0x40000000),
        ('weak-private-ab', ['weak-private-a.o','weak-private-b.o'],85,0x5555,True,0x40000000),
        ('weak-private-ba', ['weak-private-b.o','weak-private-a.o'],102,0x6666,True,0xfffffff007004000),
    ]
    for name, names, returned, value, weak, base in weak_cases:
        image = out/(name+'.macho')
        run('link-'+name,[linker,'--atlantic-static-arm64='+hex(base),*shared,'-o',image,
                         out/'weak-entry.o',*[out/p for p in names]])
        images.append(inspect_weak_image(image, base, returned, value, weak, name.startswith('weak-private-')))
    duplicate = out/'duplicate-strong.macho'
    run('reject-duplicate-strong',[linker,'--atlantic-static-arm64=40000000',*shared,'-o',duplicate,
                                  out/'weak-entry.o',out/'strong-c.o',out/'strong-d.o'],
        success=False, diagnostic='duplicate symbol')
    assert not duplicate.exists()
    # Ordinary upstream dynamic output must keep its original entry/dyld behavior.
    normal = out/'normal.macho'
    run('normal-dynamic-link', [linker,*shared,'-o',normal,*objects])
    data = normal.read_bytes()
    assert struct.unpack_from('<I', data, 24)[0] & 0x4  # MH_DYLDLINK.
    cmds, pos = [], 32
    for _ in range(struct.unpack_from('<I',data,16)[0]):
        cmd, size = struct.unpack_from('<II',data,pos)
        cmds.append(cmd); pos += size
    assert 0xe in cmds and 0x80000028 in cmds and 0x5 not in cmds
    inputs = ['tools/test_atlantic_lld.py','tests/lld_static/entry.s','tests/lld_static/data.s',
              'tests/lld_static/weak-entry.s','tests/lld_static/weak-definition.S',
              'linker-port/0001-add-bounded-static-arm64-link-mode.patch','linker-port/patches.lock.json']
    report = {'schema_version':1, 'label':'HOST_TESTED',
              'scope':'STATIC_ARM64_LINK_FIXTURES_ONLY_NOT_XNU_KERNEL_OR_EXECUTION',
              'linker_sha256':digest(linker),'compiler_sha256':digest(compiler),
              'archive_tool_sha256':digest(args.ar),
              'linker_version':subprocess.check_output([str(linker),'--version'], text=True).strip(),
              'inputs':{p:digest(ROOT/p) for p in inputs}, 'outcomes':outcomes, 'commands':commands, 'images':images,
              'weak_definition_image_audits':len(weak_cases),
              'xnu_linked':False,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'passed':len(outcomes),'relocation_audits':len(images),'xnu_linked':False,'report':str(out/'report.json')}))


if __name__ == '__main__':
    main()
