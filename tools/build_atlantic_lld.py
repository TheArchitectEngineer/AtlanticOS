"""Build the bounded static ARM64 LLD experiment from official pinned sources.

Linux x86_64 development tool only. Reuses an explicitly recorded LLVM 19.1.7
development installation, produces no XNU kernel, and never accesses a phone.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
COMMIT = 'cd708029e0b2869e80abe31ddb175f7c35361f90'
ARCHIVE_SHA256 = '05e6d7fe6d188dd4d33b812ab5cce7654b886b7c9ce405aa1d942c866bbe959f'
PATCH = 'linker-port/0001-add-bounded-static-arm64-link-mode.patch'


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as incoming:
        for block in iter(lambda: incoming.read(1024*1024), b''):
            result.update(block)
    return result.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cache', type=Path, required=True)
    ap.add_argument('--archive', type=Path, required=True)
    ap.add_argument('--llvm-config', type=Path, default=Path('/usr/bin/llvm-config-19'))
    ap.add_argument('--jobs', type=int, choices=range(1,9), default=4)
    ap.add_argument('--prepare-only', action='store_true')
    args = ap.parse_args()
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        ap.error('Linux x86_64 is required')
    cache = args.cache.resolve()
    if not cache.is_relative_to((ROOT/'work').resolve()):
        ap.error('Cache must stay under work/')
    for tool in ['git','cmake','ninja','clang-19','clang++-19','ld.lld-19']:
        if not shutil.which(tool):
            ap.error('Missing host dependency: '+tool)
    llvm_config = args.llvm_config.absolute()
    version = subprocess.check_output([str(llvm_config),'--version'], text=True).strip()
    if version != '19.1.7':
        ap.error('This recipe requires LLVM development libraries 19.1.7, got '+version)
    cmakedir = Path(subprocess.check_output([str(llvm_config),'--cmakedir'], text=True).strip()).resolve()
    libdir = Path(subprocess.check_output([str(llvm_config),'--libdir'], text=True).strip()).resolve()
    lock = json.loads((ROOT/'linker-port/patches.lock.json').read_text())
    if (lock['upstream_commit'] != COMMIT or lock['archive_sha256'] != ARCHIVE_SHA256 or
        lock['patch_sha256'] != digest(ROOT/PATCH) or digest(args.archive) != ARCHIVE_SHA256):
        ap.error('Archive or patch provenance mismatch')
    cache.mkdir(parents=True, exist_ok=True)
    source, stamp = cache/'source', cache/'source-record.json'
    if not source.exists():
        source.mkdir()
        # Upstream LLD spells its unwind include path llvm/../libunwind.
        # The intermediate directory must exist even in this partial checkout.
        (source/'llvm').mkdir()
        files = {}
        with tarfile.open(args.archive, 'r|gz') as tar:
            for item in tar:
                path = PurePosixPath(item.name)
                if path.is_absolute() or '..' in path.parts or path.parts[0] != 'llvm-project-'+COMMIT:
                    ap.error('Unexpected source archive path')
                rel = PurePosixPath(*path.parts[1:])
                selected = rel.parts and (rel.parts[0] in {'lld','cmake'} or
                            str(rel).startswith('libunwind/include/'))
                if not selected or item.isdir():
                    continue
                dest = source/str(rel)
                if not item.isfile() or not dest.resolve().is_relative_to(source) or dest.exists():
                    ap.error('Nonregular, duplicate or escaping archive member')
                dest.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(item) as incoming, dest.open('xb') as output:
                    shutil.copyfileobj(incoming, output)
                files[str(rel)] = digest(dest)
        for item in lock['files']:
            if files.get(item['path']) != item['preimage_sha256']:
                ap.error('Patch preimage mismatch: '+item['path'])
        subprocess.run(['git','init','--quiet',str(source)], check=True, timeout=30)
        subprocess.run(['git','apply','--check',str(ROOT/PATCH)], cwd=source, check=True, timeout=30)
        subprocess.run(['git','apply',str(ROOT/PATCH)], cwd=source, check=True, timeout=30)
        for item in lock['files']:
            files[item['path']] = item['postimage_sha256']
        stamp.write_text(json.dumps({'commit':COMMIT,'patch_sha256':lock['patch_sha256'],'files':files}, indent=2)+'\n', encoding='utf-8', newline='\n')
    if not stamp.is_file():
        ap.error('Incomplete source cache; preserve it and use a new cache')
    record = json.loads(stamp.read_text())
    if record['commit'] != COMMIT or record['patch_sha256'] != lock['patch_sha256']:
        ap.error('Cache belongs to another patch revision; use a new cache')
    for name, expected in record['files'].items():
        path = source/name
        if not path.resolve().is_relative_to(source) or path.is_symlink() or digest(path) != expected:
            ap.error('Changed or escaping prepared source: '+name)
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*')
              if p.is_file() and '.git' not in p.relative_to(source).parts}
    if actual != set(record['files']):
        ap.error('Unrecorded source file in prepared cache')
    inputs = {p:digest(ROOT/p) for p in ['tools/build_atlantic_lld.py', PATCH, 'linker-port/patches.lock.json']}
    report = {'schema_version':1,'label':'HOST_TESTED',
              'scope':'EXPERIMENTAL_LLD_TOOL_ONLY_NOT_KERNEL_OR_RUNTIME_VALIDATION',
              'upstream_commit':COMMIT,'archive_sha256':ARCHIVE_SHA256,'patch_sha256':lock['patch_sha256'],
              'inputs':inputs, 'source_files_verified':len(actual),
              'llvm_development_version':version,'llvm_config_sha256':digest(llvm_config),
              'llvm_cmake_config_sha256':digest(cmakedir/'LLVMConfig.cmake'),
              'xnu_linked':False,'xnu_executed':False,'phone_accessed':False}
    if args.prepare_only:
        (cache/'preparation-report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
        print(json.dumps({'source_files_verified':len(actual),'linker_built':False}))
        return
    build = cache/'build'
    build.mkdir(exist_ok=True)
    commands = []
    env = dict(os.environ)
    # Do not inherit Windows/MSYS CMake search paths into this Linux toolchain.
    for name in ['CMAKE_MODULE_PATH','CMAKE_PREFIX_PATH','CC','CXX','CFLAGS','CXXFLAGS','LDFLAGS']:
        env.pop(name, None)

    def run(name, cmd):
        print(name, flush=True)
        commands.append(cmd)
        with (build/(name+'.log')).open('w') as log:
            result = subprocess.run(cmd, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=3600)
        if result.returncode:
            print('\n'.join((build/(name+'.log')).read_text().splitlines()[-35:]))
            raise SystemExit(result.returncode)

    run('configure', ['cmake','-G','Ninja','-S',str(source/'lld'),'-B',str(build),
        '-DLLVM_DIR='+str(cmakedir),'-DCMAKE_MODULE_PATH=', '-DCMAKE_BUILD_TYPE=Release',
        '-DCMAKE_C_COMPILER='+shutil.which('clang-19'),'-DCMAKE_CXX_COMPILER='+shutil.which('clang++-19'),
        '-DCMAKE_C_FLAGS_RELEASE=-O1 -DNDEBUG','-DCMAKE_CXX_FLAGS_RELEASE=-O1 -DNDEBUG',
        '-DLLVM_INCLUDE_TESTS=OFF','-DLLVM_INCLUDE_DOCS=OFF','-DLLVM_ENABLE_ASSERTIONS=ON',
        '-DLLVM_LINK_LLVM_DYLIB=ON','-DLLVM_USE_LINKER='+shutil.which('ld.lld-19'),
        '-DLLD_VENDOR=AtlanticOS-static-arm64-v2'])
    run('build-lld', ['ninja','-C',str(build),'-j',str(args.jobs),'lld'])
    linker = build/'bin/ld64.lld'
    if not linker.exists():
        ap.error('Build did not produce the Mach-O linker driver')
    ldd = subprocess.check_output(['ldd',str(linker)], text=True)
    (build/'runtime-dependencies.log').write_text(ldd)
    dependencies = {}
    for line in ldd.splitlines():
        parts = line.strip().split()
        path = next((Path(s) for s in parts if s.startswith('/') and Path(s).is_file()), None)
        if path:
            dependencies[str(path)] = digest(path)
    llvm_shared = [p for p in dependencies if Path(p).name.startswith('libLLVM')]
    if len(llvm_shared) != 1 or digest(libdir/'libLLVM.so') != dependencies[llvm_shared[0]]:
        ap.error('Linked LLVM library does not match the selected development installation')
    report.update({'commands':[[s.replace(str(ROOT),'<ROOT>') for s in c] for c in commands],
                   'linker_sha256':digest(linker),
                   'linker_version':subprocess.check_output([str(linker),'--version'],text=True).strip(),
                   'runtime_dependencies':dependencies,
                   'host_compilers':{p:{'sha256':digest(shutil.which(p)), 'version':subprocess.check_output([p,'--version'],text=True).splitlines()[0]}
                                     for p in ['clang-19','clang++-19']}})
    (cache/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'linker':str(linker),'report':str(cache/'report.json'),'xnu_linked':False}))


if __name__ == '__main__':
    main()
