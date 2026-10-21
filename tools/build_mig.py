"""Build genuine Apple MIG on Linux x86_64; generate ARM64 interfaces, not XNU.

Sources remain pristine. The small host bridge is never used by target builds.
No SDK/xcrun impersonation, kernel stubs, RPC execution, phone or network access.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'work/mig-host'
BOOTSTRAP = ROOT/'work/references/bootstrap_cmds'
XNU = ROOT/'xnu-upstream'
C_SOURCES = ['error.c', 'global.c', 'header.c', 'mig.c', 'routine.c', 'server.c',
             'statement.c', 'string.c', 'type.c', 'user.c', 'utils.c']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--windows-git', action='store_true',
                        help='WSL shared checkout: use git.exe for source integrity checks')
    args = parser.parse_args()
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise SystemExit('Use Linux x86_64 LP64, including Debian/WSL')
    for name in ['git', 'clang', 'bison', 'flex']:
        if not shutil.which(name):
            raise SystemExit('Required host tool missing: '+name)
    lock = json.loads((ROOT/'dependencies.lock.json').read_text())
    git_tool = 'git.exe' if args.windows_git else 'git'
    if not shutil.which(git_tool):
        raise SystemExit('Git integrity checker missing: '+git_tool)
    for folder, dep in [(BOOTSTRAP, lock['mig_host_tool']), (XNU, lock['xnu'])]:
        if not folder.is_dir():
            raise SystemExit('Run fetch_mig.py and fetch_xnu.py first')
        folder_arg = subprocess.check_output(['wslpath', '-w', str(folder)], text=True).strip() if args.windows_git else str(folder)
        head = subprocess.check_output([git_tool, '-C', folder_arg, 'rev-parse', 'HEAD'], text=True).strip()
        # Honor Git's CRLF normalization for a checkout shared with Windows Git.
        dirty = subprocess.check_output([git_tool, '-c', 'core.autocrlf=true', '-C', folder_arg, 'status', '--porcelain'], text=True)
        if head != dep['commit'] or dirty:
            raise SystemExit('Upstream must match its lock and remain pristine: '+str(folder))
    # Match the active official Xcode source list, excluding dormant handler.c.
    project = (BOOTSTRAP/'mig.xcodeproj/project.pbxproj').read_text()
    active = set(re.findall(r'/\* ([\w.]+) in Sources \*/', project))
    if active != set(C_SOURCES + ['parser.y', 'lexxer.l']):
        raise SystemExit('Official source list changed; review before building')
    OUT.mkdir(parents=True, exist_ok=True)
    commands, logs = [], []
    def run(command, input=None, expected=0, log_stdout=True):
        result = subprocess.run(command, cwd=ROOT, input=input, text=True,
                                capture_output=True, timeout=90)
        commands.append([str(s).replace(str(ROOT), '<ROOT>') for s in command])
        logs.append(f'STEP {len(commands)} EXPECTED_EXIT={expected} ACTUAL_EXIT={result.returncode}\n'
                    +(result.stdout if log_stdout else '')+result.stderr)
        (OUT/'build-and-test.log').write_text('\n'.join(log for log in logs if log), encoding='utf-8', newline='\n')
        if result.returncode != expected:
            raise SystemExit('Command failed: '+repr(commands[-1])+'\n'+result.stderr[-4000:])
        return result
    source = BOOTSTRAP/'migcom.tproj'
    run(['bison', '-y', '-d', '-o', str(OUT/'y.tab.c'), str(source/'parser.y')])
    run(['flex', '-o', str(OUT/'lex.yy.c'), str(source/'lexxer.l')])
    host_flags = ['-std=gnu11', '-DATL_MIG_HOST_TOOL=1', '-Ulinux', '-D__private_extern__=',
                  '-ffile-prefix-map='+str(ROOT)+'=.',
                  '-Itools/mig-host/include', '-Ixnu-upstream/osfmk',
                  '-Ixnu-upstream/EXTERNAL_HEADERS', '-Ixnu-upstream/libkern',
                  '-idirafter', 'xnu-upstream/bsd']
    run(['clang', *host_flags, 'tests/mig/abi.c', '-o', str(OUT/'abi-check')])
    run([str(OUT/'abi-check')])
    guard = run(['clang', '-DATL_MIG_HOST_TOOL=1', '-DKERNEL=1',
                 '-Itools/mig-host/include', '-E', '-x', 'c', '-'],
                input='#include <atl_mig_host_guard.h>\n', expected=1, log_stdout=False)
    if 'Never include the MIG host bridge' not in guard.stderr:
        raise SystemExit('Expected host bridge kernel-use rejection')
    version = 'bootstrap_cmds-138 AtlanticOS Linux host adapter'
    run(['clang', *host_flags, '-DMIG_VERSION="'+version+'"', '-I'+str(source),
         '-I'+str(OUT), *[str(source/p) for p in C_SOURCES],
         str(OUT/'y.tab.c'), str(OUT/'lex.yy.c'), '-o', str(OUT/'migcom')])
    run([str(OUT/'migcom'), '-version'])
    def generate(name, definitions, flags=()):
        run([str(OUT/'migcom'), *flags, '-header', str(OUT/(name+'.h')),
             '-sheader', str(OUT/(name+'Server.h')), '-dheader', str(OUT/(name+'Ids.h')),
             '-user', str(OUT/(name+'User.c')), '-server', str(OUT/(name+'Server.c'))], input=definitions)
        paths = [OUT/(name+suffix) for suffix in ['.h', 'Server.h', 'Ids.h', 'User.c', 'Server.c']]
        if any(not p.is_file() or not p.stat().st_size for p in paths):
            raise SystemExit('Incomplete MIG output')
        return paths
    probe_cpp = run(['clang', '--target=arm64-apple-darwin', '-E', '-x', 'c',
                     '-D__MIG__', 'tests/mig/probe.defs'], log_stdout=False)
    outputs = generate('probe', probe_cpp.stdout)
    if '44000' not in (OUT/'probeIds.h').read_text() or 'probe_ping' not in (OUT/'probeServer.c').read_text():
        raise SystemExit('Synthetic RPC ID/name mismatch')
    # Invalid syntax must fail. No malformed outputs are treated as valid code.
    run([str(OUT/'migcom')], input='this is not a subsystem;\n', expected=1)
    for module in ['clock', 'mach_host', 'mach_port']:
        source_path = 'xnu-upstream/osfmk/mach/'+module+'.defs'
        cpp = run(['clang', '--target=arm64-apple-darwin', '-E', '-x', 'c',
                   '-D__MIG__', '-DKERNEL_SERVER=1', '-DMACH_KERNEL_PRIVATE=1',
                   '-Ixnu-upstream/osfmk', '-Ixnu-upstream/bsd',
                   '-Ixnu-upstream/EXTERNAL_HEADERS', source_path], log_stdout=False)
        # The host-only bridge is intentionally absent from target preprocessing.
        (OUT/(module+'.preprocessed')).write_text(cpp.stdout, encoding='utf-8', newline='\n')
        outputs += generate(module, cpp.stdout, ['-novouchers', '-mach_msg2'])
        if 'KernelServer' not in (OUT/(module+'Server.c')).read_text():
            raise SystemExit('Expected genuine KernelServer generation')
    paths = [Path('tools/build_mig.py'), Path('tests/mig/abi.c'), Path('tests/mig/probe.defs')]
    paths += sorted(p.relative_to(ROOT) for p in (ROOT/'tools/mig-host/include').rglob('*.h'))
    report = {'label': 'HOST_TESTED', 'scope': 'OFFICIAL_MIG_HOST_TOOL_AND_ARM64_INTERFACE_GENERATION_ONLY',
              'bootstrap_commit': lock['mig_host_tool']['commit'], 'xnu_commit': lock['xnu']['commit'],
              'host_bridge_not_a_target_sdk': True, 'kernel_compiled_or_linked': False,
              'git_integrity_checker': git_tool,
              'generated_c_compiled_or_executed': False, 'phone_accessed': False,
              'source_sha256': {p.as_posix(): hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
              'tool_versions': {n: subprocess.check_output([n, '--version'], text=True).splitlines()[0]
                                for n in ['clang', 'bison', 'flex']},
              'commands': commands,
              'migcom_sha256': hashlib.sha256((OUT/'migcom').read_bytes()).hexdigest(),
              'generated': [{'path': p.name, 'bytes': p.stat().st_size,
                             'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in outputs]}
    (OUT/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'label': report['label'], 'generated_files': len(outputs),
                      'kernel_compiled_or_linked': False, 'report': str(OUT/'report.json')}))


if __name__ == '__main__':
    main()
