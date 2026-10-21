"""Compile real XNU core objects using original AtlanticOS laboratory patches.

This is an incremental port build, not a linked kernel, boot image, or execution.
No fake SDK, simulator macros, host MIG bridge in target flags, or phone IO.
Requires pinned sources and the genuine MIG build from tools/build_mig.py.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import struct
import subprocess
from xnu_assym import parse_assym, render_assym

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT/'xnu-port/config/MASTER.arm64.atlanticlab.AtlanticOS'
UNITS = {'osfmk/kern/startup.c': '_kernel_bootstrap',
         'osfmk/kern/sched_prim.c': '_sched_init',
         'osfmk/kern/clock.c': '_clock_init',
         'osfmk/vm/vm_init.c': '_vm_mem_bootstrap',
         'osfmk/vm/vm_kern.c': '_kmem_alloc_guard',
         'osfmk/arm64/cswitch.s': '_Switch_context',
         'osfmk/arm64/start.s': '_start_first_cpu',
         'osfmk/arm64/locore.s': '_ExceptionVectorsBase',
         'osfmk/arm64/machine_routines_asm.s': '_set_mmu_ttb',
         'osfmk/arm/arm_init.c': '_arm_init',
         'osfmk/arm64/arm_vm_init.c': '_arm_vm_init'}
EXTRA_SYMBOLS = {'osfmk/arm64/cswitch.s': ['_machine_load_context', '_Call_continuation'],
                 'osfmk/arm64/start.s': ['__start', '_LowResetVectorBase'],
                 'osfmk/arm64/locore.s': ['_fleh_synchronous', '_fleh_irq'],
                 'osfmk/arm64/machine_routines_asm.s': ['_set_mmu_ttb_alternate'],
                 'osfmk/arm/arm_init.c': ['_arm_init_cpu', '_arm_init_idle_cpu', '_const_boot_args'],
                 'osfmk/arm64/arm_vm_init.c': ['_bootstrap_pagetables']}
PROBES = ['osfmk/kern/thread.c', 'osfmk/vm/vm_map.c']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_list(text, name):
    flat = text.replace('\\\n', ' ')
    match = re.search(r'^'+re.escape(name)+r'\s*=\s*([^\n]+)', flat, re.M)
    if not match:
        raise ValueError('Missing upstream literal list: '+name)
    values = match.group(1).split()
    if not values or any(not re.fullmatch(r'[A-Za-z0-9_.-]+', v) for v in values):
        raise ValueError('Nonliteral upstream list requires review: '+name)
    return values


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--windows-git', action='store_true')
    ap.add_argument('--probe-remaining', action='store_true',
                    help='Also compile thread.c and vm_map.c; any failure returns nonzero')
    args = ap.parse_args()
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        ap.error('Use Linux x86_64 or Debian/WSL')
    git = 'git.exe' if args.windows_git else 'git'
    for tool in [git, 'clang', 'bison', 'flex', 'csh', 'unifdef', 'perl', 'llvm-nm', 'llvm-size']:
        if not shutil.which(tool):
            ap.error('Missing build tool: '+tool)
    capability = subprocess.run(['clang', '--target=arm64-apple-macos11.0', '-nostdinc', '-fsyntax-only', '-x', 'c', '-'],
        input='#if !__has_builtin(__builtin_clzg) || !__has_builtin(__builtin_ctzg)\n'
              '#error This XNU revision requires generic count-leading/trailing-zero builtins (Clang 19+)\n#endif\n',
        text=True, capture_output=True, timeout=10)
    if capability.returncode:
        ap.error('Selected clang lacks required target builtins. Use Clang 19 or newer: '+capability.stderr)
    def path_arg(p):
        return subprocess.check_output(['wslpath', '-w', str(p)], text=True).strip() if args.windows_git else str(p)
    def scm(folder, *argv):
        return subprocess.check_output([git, '-c', 'core.autocrlf=true', '-C', path_arg(folder), *argv], timeout=60)
    lock = json.loads((ROOT/'dependencies.lock.json').read_text())
    pristine = ROOT/'xnu-upstream'
    if scm(pristine, 'rev-parse', 'HEAD').decode().strip() != lock['xnu']['commit'] or scm(pristine, 'status', '--porcelain'):
        ap.error('Preserve upstream: source must match its lock and be pristine')
    series = [s.strip() for s in (ROOT/'xnu-port/series').read_text().splitlines() if s.strip() and not s.startswith('#')]
    if not series or any(not re.fullmatch(r'[a-z0-9-]+\.patch', s) for s in series):
        ap.error('Invalid patch series')
    patches = {s: digest(ROOT/'xnu-port'/s) for s in series}
    port_id = hashlib.sha256(json.dumps({'upstream': lock['xnu']['commit'], 'series': list(patches.items())}, sort_keys=True).encode()).hexdigest()
    source = ROOT/'work/xnu-lab-sources'/port_id[:16]
    stamp = source.parent/(source.name+'.json')
    source.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        subprocess.run([git, 'clone', '--shared', '--no-checkout', path_arg(pristine), path_arg(source)], check=True, timeout=60)
        subprocess.run([git, '-C', path_arg(source), 'config', 'core.autocrlf', 'false'], check=True, timeout=10)
        subprocess.run([git, '-C', path_arg(source), 'checkout', '--detach', lock['xnu']['commit']], check=True, timeout=60)
        for name in series:
            subprocess.run([git, '-C', path_arg(source), 'apply', '--index', '--whitespace=nowarn', path_arg(ROOT/'xnu-port'/name)], check=True, timeout=15)
        diff_hash = hashlib.sha256(scm(source, 'diff', '--cached', '--binary', 'HEAD')).hexdigest()
        stamp.write_text(json.dumps({'port_id': port_id, 'diff_sha256': diff_hash})+'\n', encoding='utf-8', newline='\n')
    if not stamp.is_file():
        ap.error('Preserve incomplete source preparation; inspect it manually')
    prepared = json.loads(stamp.read_text())
    if (prepared['port_id'] != port_id or
        scm(source, 'rev-parse', 'HEAD').decode().strip() != lock['xnu']['commit'] or
        hashlib.sha256(scm(source, 'diff', '--cached', '--binary', 'HEAD')).hexdigest() != prepared['diff_sha256'] or
        scm(source, 'diff', '--name-only') or b'?? ' in scm(source, 'status', '--porcelain')):
        ap.error('Preserve prepared source: unexpected local changes')
    patch_lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if patch_lock['port_id'] != port_id or patch_lock['patches'] != patches or patch_lock['upstream_commit'] != lock['xnu']['commit']:
        ap.error('Patch provenance lock does not match this series')
    for item in patch_lock['canonical_lf_files']:
        if digest(source/item['path']) != item['postimage_sha256']:
            ap.error('Patched file differs from recorded postimage: '+item['path'])
        if item['preimage_sha256'] is not None and hashlib.sha256(scm(source, 'show', 'HEAD:'+item['path'])).hexdigest() != item['preimage_sha256']:
            ap.error('Upstream preimage mismatch: '+item['path'])
    mig_dir = ROOT/'work/mig-host'
    mig_report = json.loads((mig_dir/'report.json').read_text())
    if mig_report['bootstrap_commit'] != lock['mig_host_tool']['commit'] or digest(mig_dir/'migcom') != mig_report['migcom_sha256']:
        ap.error('Rebuild the pinned official MIG host tool')
    for name, sha in mig_report['source_sha256'].items():
        if digest(ROOT/name) != sha:
            ap.error('MIG host adaptation changed; rebuild it first')
    build_inputs = {'tools/build_xnu_lab.py': digest(__file__),
                    'tools/xnu_assym.py': digest(ROOT/'tools/xnu_assym.py'),
                    'xnu-port/patches.lock.json': digest(ROOT/'xnu-port/patches.lock.json'),
                    'xnu-port/config/'+PROFILE.name: digest(PROFILE),
                    'tests/xnu_port/boot_abi.c': digest(ROOT/'tests/xnu_port/boot_abi.c'),
                    'tests/xnu_port/assym_abi.c': digest(ROOT/'tests/xnu_port/assym_abi.c')}
    build_id = hashlib.sha256(json.dumps({'port_id': port_id, 'inputs': build_inputs}, sort_keys=True).encode()).hexdigest()
    out = ROOT/'work/xnu-lab-builds'/build_id[:16]
    out.mkdir(parents=True, exist_ok=True)
    commands, steps = [], []
    def run(command, *, cwd=ROOT, env=None, data=None, expected=0, name='step'):
        r = subprocess.run(command, cwd=cwd, env=env, input=data, text=True, capture_output=True, timeout=60)
        commands.append([str(s).replace(str(ROOT), '<ROOT>') for s in command])
        log = out/(name+'.log')
        log.write_text(r.stdout+r.stderr, encoding='utf-8', newline='\n')
        steps.append({'name': name, 'exit_code': r.returncode, 'expected': expected, 'log': log.name})
        if r.returncode != expected:
            raise RuntimeError(name+' failed: '+r.stderr[-2000:])
        return r
    # Build the official config program, retaining its source and license notices.
    host = out/'config-host';host.mkdir(exist_ok=True)
    conf_src = source/'SETUP/config'
    run(['bison', '-y', '-d', '-o', str(host/'parser.c'), str(conf_src/'parser.y')], name='config-bison')
    run(['flex', '--header-file='+str(host/'lexer.yy.h'), '-o', str(host/'lexer.yy.c'), str(conf_src/'lexer.l')], name='config-flex')
    csrc = [str(conf_src/n) for n in ['externs.c','main.c','mkheaders.c','mkioconf.c','mkmakefile.c','openp.c','searchp.c']]
    csrc += [str(host/'parser.c'), str(host/'lexer.yy.c')]
    program = out/'obj/SETUP/config/config';program.parent.mkdir(parents=True, exist_ok=True)
    run(['clang', '-std=gnu11', '-DYY_NO_INPUT', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
         '-I'+str(conf_src), '-I'+str(host), *csrc, '-o', str(program)], name='config-build')
    masters = out/'masters';masters.mkdir(exist_ok=True)
    shutil.copyfile(source/'config/MASTER', masters/'MASTER')
    shutil.copyfile(PROFILE, masters/PROFILE.name)
    config = out/'config';config.mkdir(exist_ok=True)
    # doconf can mask config failures; do not accept these outputs from an old run.
    for name in ['meta_features.h', 'Makefile']:
        (config/name).unlink(missing_ok=True)
    env = dict(os.environ, OBJROOT=str(out/'obj'), SRCROOT=str(source), SOURCE=str(source/'osfmk/conf')+'/', ASAN_OPTIONS='detect_leaks=0')
    run(['csh', '-f', str(conf_src/'doconf'), '-c', '-cpu', 'arm64', '-soc', 'atlanticlab', '-platform', 'AtlanticOS',
         '-d', str(config), '-s', str(source/'osfmk/conf'), '-m', str(masters), 'ATLANTIC'], env=env, name='config-generate')
    if not (config/'meta_features.h').is_file() or not (config/'Makefile').is_file():
        raise RuntimeError('doconf can mask config failures; required outputs are missing')
    line = next(s for s in (config/'Makefile').read_text().splitlines() if s.startswith('export CONFIG_DEFINES ='))
    defines = shlex.split(line.split('=',1)[1])
    if '-DCONFIG_ATLANTIC_FIRMWARE' not in defines or any(v in defines for v in ['-DMACH_BSD','-DIOKIT','-DLIBKERNCPP']):
        raise RuntimeError('Unexpected firmware feature selection')
    inc = out/'include';(inc/'mach').mkdir(parents=True, exist_ok=True)
    for sub in ['memory', 'coverage']:
        (inc/'san').mkdir(exist_ok=True)
        for h in (source/'san'/sub).glob('*.h'):
            shutil.copyfile(h, inc/'san'/h.name)
    # Match actual upstream MIG sender and kernel-server header roles.
    base = ['clang', '--target=arm64-apple-macos11.0', '-E', '-x', 'c', '-D__MIG__', '-DAPPLE', '-DKERNEL',
            '-DPRIVATE', '-DKERNEL_PRIVATE', '-DXNU_KERNEL_PRIVATE', '-DMACH_KERNEL_PRIVATE', *defines]
    base += ['-I'+str(source/p) for p in ['osfmk','bsd','EXTERNAL_HEADERS']]
    mk = (source/'osfmk/mach/Makefile').read_text()
    generated = []
    groups = [('MIG_UUHDRS', 'sender'), ('MIG_KSHDRS', 'kernel-server')]
    for variable, role in groups:
        for header in make_list(mk, variable):
            module = header.removesuffix('_server.h') if role == 'kernel-server' else header.removesuffix('.h')
            flags = ['-DKERNEL_SERVER=1'] if role == 'kernel-server' else []
            cpp = run([*base, *flags, str(source/('osfmk/mach/'+module+'.defs'))], name='cpp-'+header)
            destination = inc/'mach'/header
            opts = ['-mach_msg2'] if role == 'kernel-server' else []
            run([str(mig_dir/'migcom'), '-novouchers', *opts, '-header', str(destination) if role=='sender' else '/dev/null',
                 '-sheader', str(destination) if role=='kernel-server' else '/dev/null', '-server', '/dev/null', '-user', '/dev/null'],
                cwd=out, data=cpp.stdout, name='mig-'+header)
            generated.append(destination)
    # resource_notify is a kernel sender header, not one of MIG_UUHDRS.
    if 'resource_notify.h' not in make_list(mk, 'MIG_KUHDRS'):
        raise RuntimeError('Upstream resource_notify role changed')
    cpp = run([*base, '-DKERNEL_USER=1', str(source/'osfmk/mach/resource_notify.defs')], name='cpp-resource-notify')
    resource = inc/'mach/resource_notify.h'
    run([str(mig_dir/'migcom'), '-novouchers', '-maxonstack', '1024', '-header', str(resource), '-server', '/dev/null', '-user', '/dev/null'],
        cwd=out, data=cpp.stdout, name='mig-resource-notify')
    generated.append(resource)
    # Use upstream's real version template/generator with explicit build metadata.
    version = inc/'libkern/version.h';version.parent.mkdir(exist_ok=True)
    shutil.copyfile(source/'libkern/libkern/version.h.template', version)
    (out/'xnuVersion').write_text('25.0.0\n', encoding='utf-8', newline='\n')
    venv = dict(os.environ, SRCROOT=str(source), OBJROOT=str(out), TARGET=str(out), CURRENT_KERNEL_CONFIG_LC='atlantic-lab',
                KERNEL_BUILD_DATE='SOURCE_DATE_EPOCH=0', KERNEL_BUILD_OBJROOT='AtlanticOS-laboratory')
    run(['perl', str(source/'config/newvers.pl'), str(version)], cwd=out, env=venv, name='version-generate')
    clang_resource = subprocess.check_output(['clang','-print-resource-dir'], text=True).strip()
    target = ['clang', '--target=arm64-apple-macos11.0', '-mcpu=cortex-a57', '-std=gnu11', '-ffreestanding', '-nostdinc',
              '-fno-builtin', '-fno-stack-protector', '-mkernel', '-fblocks', '-O1', '-g', '-Darm64', '-DARM64', '-D__ARM64__',
              '-DLP64', '-DPAGE_SIZE_FIXED', '-DVM_KERNEL_LINK_ADDRESS=0xfffffff007004000',
              '-DPRIVATE', '-DAPPLE', '-D__MACHO__=1', '-DXNU_KERN_EVENT_DATA_IS_VLA',
              '-DKERNEL', '-DKERNEL_PRIVATE', '-DXNU_KERNEL_PRIVATE', '-DMACH_KERNEL_PRIVATE', '-DMACH_KERNEL',
              '-DARM64_BOARD_CONFIG_ATLANTIC_LAB', '-include', str(config/'meta_features.h'),
              '-ffile-prefix-map='+str(ROOT)+'=.', '-fdebug-compilation-dir=.', '-I'+str(config), '-I'+str(inc)]
    target += ['-I'+str(source/p) for p in ['osfmk','bsd','pexpert','libkern','iokit','osfmk/libsa','libsa','EXTERNAL_HEADERS','.']]
    target += ['-isystem', clang_resource+'/include', *defines]
    abi = run([*target, '-c', str(ROOT/'tests/xnu_port/boot_abi.c'), '-o', str(out/'boot-abi.o')], name='boot-abi')
    # Generate assembler offsets with the target compiler, never a host ABI.
    genassym = out/'genassym.s'
    run([*target, '-fno-integrated-as', '-S', str(source/'osfmk/arm64/genassym.c'), '-o', str(genassym)], name='genassym')
    assym_values = parse_assym(genassym.read_text(), required=['TH_KSTACKPTR','ACT_CPUDATAP','CPU_ACTIVE_THREAD',
        'SS64_KERNEL_SP','NS64_KERNEL_D8','BA_VIRT_BASE','BA_PHYS_BASE','BA_BOOT_FLAGS'])
    assym = inc/'assym.s'
    assym.write_text(render_assym(assym_values), encoding='utf-8', newline='\n')
    (inc/'assym-check.h').write_text(render_assym(assym_values, prefix='ATL_ASSYM_'), encoding='utf-8', newline='\n')
    run([*target, '-c', str(ROOT/'tests/xnu_port/assym_abi.c'), '-o', str(out/'assym-abi.o')], name='assym-abi')
    bad_assym = out/'invalid-assym';bad_assym.mkdir(exist_ok=True)
    wrong = dict(assym_values);wrong['TH_KSTACKPTR'] += 1
    (bad_assym/'assym-check.h').write_text(render_assym(wrong, prefix='ATL_ASSYM_'), encoding='utf-8', newline='\n')
    rejection = run([target[0], '-I'+str(bad_assym), *target[1:], '-c', str(ROOT/'tests/xnu_port/assym_abi.c'),
                     '-o', str(out/'invalid-assym.o')], expected=1, name='reject-assym-offset')
    if 'TH_KSTACKPTR target layout' not in rejection.stderr:
        raise RuntimeError('Wrong generated-offset rejection reason')
    # Reject accidental PMU enablement and forbidden BSD/IOKit composition.
    bad = '#undef CONFIG_CPU_COUNTERS\n#define CONFIG_CPU_COUNTERS 1\n#include <pexpert/arm64/board_config.h>\n'
    rejection = run([*target, '-E', '-x', 'c', '-'], data=bad, expected=1, name='reject-pmu')
    if 'laboratory PMU backend is not implemented' not in rejection.stderr:
        raise RuntimeError('Wrong PMU rejection reason')
    for feature in ['MACH_BSD','IOKIT']:
        rejection = run([*target, '-E', '-x', 'c', '-'], data='#define '+feature+' 1\n#include <kern/startup.c>\n',
                        expected=1, name='reject-'+feature.lower())
        if 'firmware profile excludes BSD userland and IOKit' not in rejection.stderr:
            raise RuntimeError('Wrong forbidden composition rejection reason')
    objects, failures = [], []
    units = list(UNITS) + (PROBES if args.probe_remaining else [])
    for rel in units:
        obj = out/(Path(rel).stem+'.o')
        # This flag is mandated for VM sources by upstream Makefile.template.
        per_file = ['-DVM_UNSAFE_TYPES'] if rel.startswith('osfmk/vm/') else []
        if rel.endswith('.s'):
            # Match upstream SFLAGS_GEN, including the non-Clang ASSEMBLER guard.
            per_file += ['-DASSEMBLER', '-D__ASSEMBLER__', '-x', 'assembler-with-cpp']
        cmd = [*target, *per_file, '-c', str(source/rel), '-o', str(obj)]
        r = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=60)
        commands.append([str(s).replace(str(ROOT),'<ROOT>') for s in cmd])
        log = out/(obj.stem+'.log');log.write_text(r.stdout+r.stderr, encoding='utf-8', newline='\n')
        if r.returncode:
            failures.append({'source':rel,'exit_code':r.returncode,'log':log.name,
                             'diagnostics':[s.replace(str(ROOT),'<ROOT>') for s in r.stderr.splitlines() if 'error:' in s]})
            print(json.dumps(failures[-1]), flush=True)
            continue
        raw = obj.read_bytes()
        if len(raw)<32 or struct.unpack_from('<4I',raw) != (0xfeedfacf,0x100000c,0,1):
            raise RuntimeError('Expected AArch64 Mach-O object, not a kernel image')
        nm = run(['llvm-nm','--defined-only',str(obj)],name=obj.stem+'-defined').stdout
        required_symbols = ([UNITS[rel]]+EXTRA_SYMBOLS.get(rel, [])) if rel in UNITS else []
        if rel in UNITS and not any(line.split()[-2:]==['T', UNITS[rel]] for line in nm.splitlines()):
            raise RuntimeError('Expected real external text symbol: '+UNITS[rel])
        for symbol in required_symbols:
            if not any(line.split()[-1:]==[symbol] for line in nm.splitlines()):
                raise RuntimeError('Missing real XNU function: '+symbol)
        undefined = run(['llvm-nm','--undefined-only',str(obj)],name=obj.stem+'-undefined').stdout.splitlines()
        exported = run(['llvm-nm','--extern-only','--defined-only','--format=posix',str(obj)],
                       name=obj.stem+'-exports').stdout.splitlines()
        exported = [s.split()[0] for s in exported if s.split()]
        if rel.endswith('/startup.c') and not {'_vm_mem_bootstrap','_sched_init','_task_init','_thread_init'}.issubset(set(undefined)):
            raise RuntimeError('Bootstrap no longer references substantive Mach initialization')
        if rel.endswith('/startup.c') and any('trust_cache' in s or 'code_signing_init' in s for s in undefined):
            raise RuntimeError('Unexpected Apple userland trust-cache dependency in firmware bootstrap')
        objects.append({'source':rel,'source_sha256':digest(source/rel),'object':obj.name,'object_sha256':digest(obj),
                        'object_file_bytes':len(raw),'required_symbol':UNITS.get(rel),'required_symbols':required_symbols,
                        'defined_external_symbols':exported,'undefined_symbols':undefined})
    selected_definitions = {s for item in objects for s in item['defined_external_symbols']}
    missing_symbols = sorted({s for item in objects for s in item['undefined_symbols']} - selected_definitions)
    report = {'schema_version':1,'label':'BUILT_ARM64','scope':'REAL_XNU_CORE_OBJECTS_ONLY_NOT_LINKED_OR_EXECUTED',
              'upstream_commit':lock['xnu']['commit'],'patches':patches,'port_id':port_id,'build_id':build_id,
              'inputs':build_inputs,'profile':'atlanticlab','kernel_linked':False,'xnu_executed':False,'phone_accessed':False,
              'object_sizes_are_not_runtime_ram':True,'host_generator_sanitizers':['address','undefined'],
              'host_generator_leak_check':False,'selected_defines':defines,'commands':commands,'steps':steps,
              'compiler':subprocess.check_output(['clang','--version'],text=True).splitlines()[0],
              'generator_versions':{name:subprocess.check_output([name,'--version'],text=True).splitlines()[0]
                                    for name in ['bison','flex','csh']},
              'config_headers':[{'path':p.relative_to(out).as_posix(),'sha256':digest(p)} for p in sorted(config.glob('*.h'))],
              'version_header_sha256':digest(version),
              'assym':{'source_sha256':digest(source/'osfmk/arm64/genassym.c'),'assembly_sha256':digest(genassym),
                       'header_sha256':digest(assym),'definitions':assym_values,'extraction':'strict-decimal-ascii-no-fallback',
                       'target_layout_assertions_passed':True},
              'virtual_link_address':'0xfffffff007004000','physical_link_or_load_address':None,
              'selected_object_symbol_inventory':{'scope':'NAME_INVENTORY_ONLY_NOT_A_LINK_OR_RELOCATION_CHECK',
                  'defined_external_count':len(selected_definitions),'unprovided_symbols':missing_symbols},
              'generated_headers':[{'path':p.relative_to(out).as_posix(),'sha256':digest(p)} for p in generated],
              'objects':objects,'failed_units':failures}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'label':report['label'],'compiler':report['compiler'],'compiled_units':len(objects),'failed_units':len(failures),
                      'kernel_linked':False,'xnu_executed':False,'report':str(out/'report.json')}))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
