"""Audit intact XNU queues/counters and firmware VM wait scope; no execution.

C/C++ ABI, synthetic wire bytes, isolated conditional-region preprocessing,
native objects and relocations only. No scheduler, VM, CPU counter or IRQ runs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
from test_xnu_brk_scope import read_object, symbol_bytes, function
from test_xnu_platform import strong_external_import

ROOT = Path(__file__).resolve().parents[1]
CPPFLAGS = ['-x', 'c++', '-std=gnu++2b', '-fsized-deallocation', '-fapple-kext',
            '-DLIBKERN_KERNEL_PRIVATE=1', '-DOSALLOCDEBUG=1']
COUNTERS = ['__Z11counter_addPPyy', '__Z11counter_incPPy', '__Z11counter_decPPy',
    '__Z31counter_add_preemption_disabledPPyy', '__Z31counter_inc_preemption_disabledPPy',
    '__Z31counter_dec_preemption_disabledPPy']
VM = ['vm_object_sleep','vm_object_wakeup','vm_object_mapping_wait','vm_object_paging_wait',
      'vm_object_paging_only_wait','vm_object_paging_throttle_wait','vm_page_sleep','vm_page_wakeup',
      'vm_page_wakeup_done','vm_page_wakeup_done_with_inheritor','page_worker_init','page_worker_register_worker']
PQ_PREFIXES = ['__Z21priority_queue_insert', '__Z21priority_queue_remove', '__Z27_priority_queue_remove_root',
               '__Z30priority_queue_entry_decreased', '__Z30priority_queue_entry_increased', '__Z23_priority_queue_destroy']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def counter_atomic_words(code):
    words = struct.unpack('<'+'I'*(len(code)//4),code)
    loads = [i for i,w in enumerate(words) if w & 0xfffffc00 == 0xc85f7c00]
    stores = [i for i,w in enumerate(words) if w & 0xffe0fc00 == 0xc8007c00]
    assert len(loads)==len(stores)==1 and loads[0] < stores[0]
    branch_at = stores[0]+1
    branch = words[branch_at]
    assert branch & 0x7f000000 == 0x35000000
    offset = (branch >> 5) & 0x7ffff
    if offset & 0x40000: offset -= 0x80000
    assert branch_at+offset == loads[0]
    return {'load64':hex(words[loads[0]]),'store64':hex(words[stores[0]]),
            'retry_branch':hex(branch),'executed':False}


def region(text):
    # The actual upstream conditional region; headers/types are deliberately
    # not compiled by this isolated preprocessing test. Full native objects
    # and independent header probes validate the selected target separately.
    anchor = text.index('\nvoid\nkdp_vm_object_sleep_find_owner(')
    start = text.rfind('\n#if CONFIG_IOSCHED\n', 0, anchor)
    end = text.index('\n#if VM_OBJECT_ACCESS_TRACKING', anchor)
    assert start >= 0 and end > start
    return text[start:end]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    base = json.loads(args.build.read_text())
    lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    assert base['port_id'] == lock['port_id'] and not base['failed_units']
    for rel, digest in base['inputs'].items():
        assert sha(ROOT/rel) == digest, rel
    source = ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
    out = args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():
        ap.error('Use a new output directory under work/')
    out.mkdir(parents=True)
    commands, outcomes = [], []

    def check(name, **details):
        outcomes.append({'name':name, 'passed':True, **details})

    def run(name, command, expected=0, diagnostic=None, data=None):
        p = subprocess.run(command, cwd=ROOT, input=data, text=True, capture_output=True, timeout=90)
        commands.append([str(s).replace(str(ROOT), '<ROOT>') for s in command])
        (out/(name+'.log')).write_text((p.stdout+p.stderr).replace(str(ROOT), '<ROOT>'), encoding='utf-8', newline='\n')
        assert p.returncode == expected and (not diagnostic or diagnostic in p.stderr), name+': '+p.stderr[-2500:]
        return p.stdout

    recipe = next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    assert recipe[-4] == '-c'
    target = [s.replace('<ROOT>', str(ROOT)) for s in recipe[:-4]]
    cxx = [s for s in target if s != '-std=gnu11'] + CPPFLAGS
    if base['layout_provider']:
        assert sha(target[0]) == base['layout_provider']['compiler_sha256']
    hashes = {}
    for rel in ['osfmk/arm/counter.c','libkern/c++/priority_queue.cpp']:
        native = (ROOT/'xnu-upstream'/rel).read_text()
        hashes[rel] = hashlib.sha256(native.encode()).hexdigest()
        assert sha(source/rel) == hashes[rel]
    check('two-complete-native-provider-sources-unchanged', source_sha256=hashes)
    makeinc = (ROOT/'xnu-upstream/makedefs/MakeInc.def').read_text()
    template = (ROOT/'xnu-upstream/libkern/conf/Makefile.template').read_text()
    assert '-std=gnu++2b -fsized-deallocation $(CXXFLAGS_KERNEL)' in makeinc
    assert 'CXXFLAGS_KERNEL   = -fapple-kext' in makeinc
    assert '-DLIBKERN_KERNEL_PRIVATE -DOSALLOCDEBUG=1' in template
    filelist = (ROOT/'xnu-upstream/libkern/conf/files').read_text()
    assert re.search(r'^libkern/c\+\+/priority_queue\.cpp\s+standard\s*$', filelist, re.M)
    check('cpp-recipe-derived-from-native-kernel-and-libkern-component-flags')

    before = (ROOT/'xnu-upstream/osfmk/vm/vm_object.c').read_text()
    after = (source/'osfmk/vm/vm_object.c').read_text()
    first = '\n#endif /* CONFIG_IOSCHED */\n\n#if CONFIG_IOSCHED || CONFIG_ATLANTIC_FIRMWARE\n'
    second = '\n#endif /* CONFIG_IOSCHED || CONFIG_ATLANTIC_FIRMWARE */\n\n#if CONFIG_IOSCHED\n'
    assert after.count(first) == after.count(second) == 1
    assert after.replace(first, '', 1).replace(second, '', 1) == before
    bodies = {name:hashlib.sha256(function(after,name).encode()).hexdigest() for name in VM}
    assert all(function(after,name) == function(before,name) for name in VM)
    check('vm-patch-only-splits-guards-all-twelve-native-bodies-intact', function_sha256=bodies)
    for fw in [0,1]:
        for io in [0,1]:
            for inheritor in [0,1]:
                name = f'vm-region-fw{fw}-iosched{io}-inheritor{inheritor}'
                prefix = f'#define CONFIG_ATLANTIC_FIRMWARE {fw}\n#define CONFIG_IOSCHED {io}\n#define PAGE_SLEEP_WITH_INHERITOR {inheritor}\n#define DEVELOPMENT 1\n#define DEBUG 0\n'
                original = run(name+'-upstream', [target[0], '--target=arm64-apple-macos11', '-E','-P','-x','c','-'], data=prefix+region(before))
                modified = run(name+'-port', [target[0], '--target=arm64-apple-macos11', '-E','-P','-x','c','-'], data=prefix+region(after))
                present = lambda text,n: re.search(r'^'+re.escape(n)+r'\(',text,re.M) is not None
                if not fw or io:
                    assert original == modified
                else:
                    assert not present(original,'vm_object_sleep') and present(modified,'vm_object_sleep')
                    assert present(modified,'vm_page_wakeup_done')
                    assert present(modified,'page_worker_init') == bool(inheritor)
                    assert not present(modified,'vm_page_handle_prio_inversion')
                    assert not present(modified,'io_reprioritize')
                check(name, isolated_preprocessing_only=True, upstream_equal=not fw or bool(io))

    refs = {}
    for language, flags in [('c', target), ('cpp', cxx)]:
        obj = out/('queue-counter-'+language+'.o')
        fixture = ROOT/'tests/xnu_port/queue_counter_abi.c'
        run('queue-counter-'+language+'-abi', [*flags,'-c',str(fixture),'-o',str(obj)])
        refs[language] = read_object(obj)
        check('native-queue-counter-'+language+'-types-and-layouts')
        for kind, define in [('queue','ATL_TEST_WRONG_QUEUE_ABI'),('counter','ATL_TEST_WRONG_COUNTER_ABI')]:
            # Both languages must reject a mismatched overload; diagnostics
            # differ between C overloadable functions and native C++.
            run('reject-'+kind+'-'+language, [*flags,'-D'+define+'=1','-Werror=incompatible-function-pointer-types',
                                            '-fsyntax-only',str(fixture)], 1)
            check('reject-'+kind+'-'+language+'-overload-abi')
    expected_sched = bytes(16)+struct.pack('<Q', ((-0x123456789a & ((1<<48)-1))<<16)|0x1234)
    expected_deadline = bytes(24)+struct.pack('<Q',0x0123456789abcdef)
    for parsed in refs.values():
        assert symbol_bytes(parsed,'_atl_sched_wire',24) == expected_sched
        assert symbol_bytes(parsed,'_atl_deadline_wire',32) == expected_deadline
    check('actual-c-cpp-wire-identical-signed-child-48bit-and-deadline-64bit',
          sched_hex=expected_sched.hex(),deadline_hex=expected_deadline.hex(),synthetic_not_device=True)
    fixture = ROOT/'tests/xnu_port/vm_wait_abi.c'
    run('native-vm-wait-abi',[*target,'-fsyntax-only',str(fixture)])
    check('native-vm-wait-wakeup-and-page-worker-signatures')
    run('reject-vm-wait-abi',[*target,'-DATL_TEST_WRONG_VM_WAIT_ABI=1',
        '-Werror=incompatible-function-pointer-types','-fsyntax-only',str(fixture)],1,'incompatible function pointer types')
    check('reject-narrow-or-widened-vm-wait-argument')

    selected = base['layout_provider'] is not None
    objects = {}
    for rel,flags in [('osfmk/arm/counter.c',target),('libkern/c++/priority_queue.cpp',cxx)]:
        record = next((o for o in base['objects'] if o['source']==rel),None)
        assert (record is not None) == selected
        if record:
            obj = args.build.parent/record['object']
            assert sha(obj) == record['object_sha256']
            if rel.endswith('.cpp'):
                command = next(c for c in base['commands'] if len(c)>=4 and c[-3].endswith('/'+rel) and c[-2]=='-o')
                assert all(flag in command for flag in CPPFLAGS) and '-std=gnu11' not in command
        else:
            obj = out/(Path(rel).stem+'-probe.o')
            run('standard-'+Path(rel).stem+'-probe', [*flags,'-c',str(source/rel),'-o',str(obj)])
            check('standard-'+Path(rel).stem+'-isolated-native-probe')
        parsed = read_object(obj)
        imports = set(run(Path(rel).stem+'-imports',['llvm-nm','--undefined-only',str(obj)]).split())
        expected = {'_PAGE_SHIFT_CONST','_cpu_number'} if rel.endswith('counter.c') else {'_mach_assert_jump_key'}
        assert imports == expected and all(strong_external_import(obj,n) for n in imports)
        objects[rel] = {'object_sha256':sha(obj),'imports':sorted(imports)}
        if rel.endswith('counter.c'):
            assert set(COUNTERS) <= set(parsed[2])
            assert all(len(symbol_bytes(parsed,n))>=40 for n in COUNTERS)
            atomics = {n:counter_atomic_words(symbol_bytes(parsed,n)) for n in COUNTERS}
            # A 32-bit LDXR must fail this 64-bit counter audit. Inspect a copy;
            # never change the native object or its synchronization algorithm.
            damaged = bytearray(symbol_bytes(parsed,COUNTERS[0]))
            for offset in range(0,len(damaged),4):
                word = struct.unpack_from('<I',damaged,offset)[0]
                if word & 0xfffffc00 == 0xc85f7c00:
                    struct.pack_into('<I',damaged,offset,word & ~(1<<30))
                    break
            try:
                counter_atomic_words(damaged)
            except AssertionError:
                pass
            else:
                raise AssertionError('narrowed atomic load was accepted')
            check('six-genuine-scalable-counter-overloads-with-real-cpu-provider',imports=sorted(imports),
                  actual_atomic_words=atomics,narrowed_atomic_rejected=True)
        else:
            api = [n for n in parsed[2] if any(n.startswith(prefix) for prefix in PQ_PREFIXES)]
            assert len(api) == 48 and all(parsed[2][n]['type']&1 for n in api)
            check('forty-eight-native-queue-overloads-no-cxx-runtime-or-fake-comparator',api=sorted(api))
        run(Path(rel).stem+'-disassembly',['llvm-objdump','--macho','--disassemble',str(obj)])
    if selected:
        record = next(o for o in base['objects'] if o['source']=='osfmk/vm/vm_object.c')
        obj = args.build.parent/record['object']; assert sha(obj)==record['object_sha256']
        parsed = read_object(obj)
        assert all('_'+name in parsed[2] for name in VM)
        imports = set(run('vm-wait-imports',['llvm-nm','--undefined-only',str(obj)]).split())
        assert {'_lck_rw_sleep','_lck_rw_sleep_with_inheritor','_thread_wakeup_prim',
                '_zalloc_permanent_tag','_lck_ticket_lock','_lck_ticket_unlock'} <= imports
        assert not {'_vm_page_request_reprioritize','_vnode_pager_issue_reprioritize_io'} & imports
        check('actual-vm-wait-worker-providers-native-locks-and-no-iosched-callbacks',object_sha256=sha(obj))
    else:
        check('standard-keeps-full-vm-object-provider-unselected')
    check('source-api-selection-is-not-execution-or-physical-measurement')
    report = {'schema_version':1,'label':'HOST_TESTED',
        'scope':'NATIVE_C_CPP_QUEUE_COUNTER_VM_WAIT_SOURCE_ABI_AND_OBJECTS_ONLY_NO_KERNEL_EXECUTION',
        'build_report_sha256':sha(args.build),'port_id':base['port_id'],
        'inputs':{p:sha(ROOT/p) for p in ['tools/test_xnu_queue_vm.py','tests/xnu_port/queue_counter_abi.c',
            'tests/xnu_port/vm_wait_abi.c','tools/test_xnu_brk_scope.py','tools/test_xnu_platform.py']},
        'patch_sha256':sha(ROOT/'xnu-port/0031-retain-native-vm-wait-and-page-worker-synchronization.patch'),
        'native_sources':hashes,'objects':objects,'outcomes':outcomes,'commands':commands,
        'objects_selected_in_base':selected,'xnu_executed':False,'queue_executed':False,
        'cpu_counter_measured':False,'vm_wait_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':len(outcomes),'new_native_units_selected':selected,'xnu_executed':False}))


if __name__=='__main__':
    main()
