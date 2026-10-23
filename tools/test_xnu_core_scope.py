"""Check ARM64 dependencies, native panic scope and retained printf ABI.

Target compilation and preprocessing only; no panic, formatter or XNU execution.
The negative ABI case changes a declaration, never a native type or function.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def panic_function(text):
    match = re.search(r'^boolean_t\npanic_get_thread_proc_task\(.*?^\}', text, re.M|re.S)
    if not match:
        raise ValueError('Expected native panic context function')
    return match[0]+'\n'


def kperf_block(text):
    start = text.index('\tif (reasons & AST_KPERF) {')
    end = text.index('\n\tif (reasons & AST_RESET_PCS)', start)
    return text[start:end]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    build = json.loads(args.build.read_text())
    lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if build['port_id'] != lock['port_id'] or build['failed_units']:
        ap.error('Use a successful current build')
    for rel, sha in build['inputs'].items():
        if digest(ROOT/rel) != sha:
            ap.error('Changed build input: '+rel)
    source = ROOT/'work/xnu-lab-sources'/lock['port_id'][:16]
    source_hashes = {}
    texts = {}
    for rel in ['osfmk/arm64/pcb.c', 'osfmk/arm/machine_routines_common.c',
                'osfmk/kern/ast.c', 'osfmk/kern/debug.c']:
        record = next(i for i in lock['canonical_lf_files'] if i['path'] == rel)
        before = (ROOT/'xnu-upstream'/rel).read_text()
        if (hashlib.sha256(before.encode()).hexdigest() != record['preimage_sha256'] or
            digest(source/rel) != record['postimage_sha256']):
            ap.error('Changed native source pre/postimage: '+rel)
        texts[rel] = (before, (source/rel).read_text())
        source_hashes[rel] = {'upstream':record['preimage_sha256'], 'adapted':record['postimage_sha256']}
    command = next(c for c in build['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    if command[-4] != '-c':
        ap.error('Unexpected target recipe')
    target = [s.replace('<ROOT>',str(ROOT)) for s in command[:-4]]
    if build['layout_provider'] and digest(target[0]) != build['layout_provider']['compiler_sha256']:
        ap.error('Changed experimental compiler')
    out = args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():
        ap.error('Use a new output directory under work/')
    out.mkdir(parents=True)
    outcomes, commands = [], []

    def run(name, cmd, data=None, expected=0, diagnostic=None):
        result = subprocess.run(cmd,input=data,text=True,capture_output=True,timeout=60)
        passed = result.returncode == expected and (diagnostic is None or diagnostic in result.stderr)
        (out/(name+'.log')).write_text((result.stdout+result.stderr).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        commands.append([s.replace(str(ROOT),'<ROOT>') for s in cmd])
        if not passed:
            raise RuntimeError(name+' failed: '+result.stderr[-2000:])
        return result.stdout

    def preprocess(name, fragment, prefix):
        cmd = [target[0], '--target=arm64-apple-macos11.0', '-E', '-P', '-x', 'c', '-']
        return run(name, cmd, data=prefix+fragment)

    for rel in ['osfmk/arm64/pcb.c', 'osfmk/arm/machine_routines_common.c']:
        name = Path(rel).stem+'-dependencies'
        dependencies = run(name, [*target, '-M', str(source/rel)])
        assert 'apple_arm64_cpu.h' not in dependencies, 'Unexpected Apple CPU header in lab'
        before, after = texts[rel]
        include = '#include <pexpert/arm64/apple_arm64_cpu.h>'
        assert include in before and '#if !defined(ARM64_BOARD_CONFIG_ATLANTIC_LAB)\n'+include+'\n#endif' in after
        outcomes.append({'name':name,'passed':True,'apple_cpu_header_in_lab_dependencies':False,
                         'outside_lab_include_retained_in_source':True})

    before, after = map(kperf_block, texts['osfmk/kern/ast.c'])
    for enabled in [0,1]:
        prefix = '#define CONFIG_CPU_COUNTERS 1\n#define CONFIG_KPERF '+str(enabled)+'\n'
        old = preprocess('kperf-'+str(enabled)+'-upstream',before,prefix)
        new = preprocess('kperf-'+str(enabled)+'-adapted',after,prefix)
        assert 'thread_ast_clear(thread, AST_KPERF);' in new
        assert 'kpc_thread_ast_handler(thread);' in new and 'kperf_thread_ast_handler(thread);' in new
        assert ('thread->kperf_ast = 0;' in new) == bool(enabled)
        if enabled:
            assert old == new, 'Enabled KPERF behavior changed'
        outcomes.append({'name':'kperf-'+str(enabled),'passed':True,
                         'native_handlers_and_ast_clear_retained':True,'upstream_byte_identical':old==new})

    before, after = map(panic_function, texts['osfmk/kern/debug.c'])
    for name, fw, bsd in [('outside-firmware',0,0), ('firmware-bsd',1,1), ('firmware-mach',1,0)]:
        prefix = '#define CONFIG_ATLANTIC_FIRMWARE '+str(fw)+'\n#define MACH_BSD '+str(bsd)+'\n'
        old = preprocess(name+'-upstream',before,prefix)
        new = preprocess(name+'-adapted',after,prefix)
        if not fw or bsd:
            assert old == new, 'Other native panic context changed'
        else:
            assert 'tro_proc' not in new and '*proc = NULL;' in new and 'if (proc)' in new
            assert '*task = thread->t_tro->tro_task;' in new
            for ptr in ['thread', 'thread->t_tro', 'thread->t_tro->tro_task']:
                assert 'if (!PANIC_VALIDATE_PTR('+ptr+'))' in new
            assert new.count('return false;') == 3, 'Native Mach validation must still fail'
        outcomes.append({'name':name,'passed':True,'upstream_byte_identical':old==new,
                         'bsd_process_context_available':bool(not fw or bsd)})

    # Compile the complete original BSD file with the firmware declaration forced
    # in. This checks the declaration against its actual definitions, including
    # size_t and va_list from the pinned native headers.
    native = source/'bsd/kern/subr_prf.c'
    header = source/'osfmk/kern/atlantic_printf.h'
    flags = ['-UMACH_KERNEL_PRIVATE', '-DBSD_KERNEL_PRIVATE=1']
    run('printf-native-abi', [*target,*flags,'-include',str(header),'-fsyntax-only',str(native)])
    outcomes.append({'name':'printf-native-abi','passed':True,'full_original_definitions_checked':True})
    wrong = out/'wrong-printf.h'
    wrong.write_text(header.read_text().replace('extern int vsnprintf(', 'extern long vsnprintf('),encoding='utf-8',newline='\n')
    run('printf-reject-return-type', [*target,*flags,'-include',str(wrong),'-fsyntax-only',str(native)],
        expected=1, diagnostic="conflicting types for 'vsnprintf'")
    outcomes.append({'name':'printf-reject-return-type','passed':True,'wrong_return_type_rejected':True})
    report = {'schema_version':1,'label':'HOST_TESTED',
        'scope':'NATIVE_SOURCE_PREPROCESSOR_SCOPE_AND_TARGET_PRINTF_ABI_ONLY_NOT_RUNTIME_EXECUTION',
        'port_id':build['port_id'],'build_report_sha256':digest(args.build),'tool_sha256':digest(__file__),
        'native_sources':source_hashes,'full_printf_source_sha256':digest(native),'printf_header_sha256':digest(header),
        'outcomes':outcomes,'commands':commands,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':len(outcomes),'scope':report['scope']}))


if __name__ == '__main__':
    main()
