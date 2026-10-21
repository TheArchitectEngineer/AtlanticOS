"""Build the experimental C-layout compiler from a pinned LLVM archive.

Linux development only; produces no firmware or phone image. Sources, build and
download stay under work/. This tool never formats or mounts a filesystem.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
COMMIT = 'cd708029e0b2869e80abe31ddb175f7c35361f90'
ARCHIVE_SHA256 = '05e6d7fe6d188dd4d33b812ab5cce7654b886b7c9ce405aa1d942c866bbe959f'
URL = 'https://codeload.github.com/llvm/llvm-project/tar.gz/'+COMMIT
EXCLUDED = {'llvm/test','llvm/unittests','llvm/docs','llvm/benchmarks',
            'clang/test','clang/unittests','clang/docs'}


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as source:
        for data in iter(lambda: source.read(1024*1024), b''):
            result.update(data)
    return result.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cache', type=Path, default=ROOT/'work/clang-layout-build')
    ap.add_argument('--archive', type=Path)
    ap.add_argument('--jobs', type=int, default=4, choices=range(1, 17))
    ap.add_argument('--prepare-only', action='store_true', help='Verify/extract/apply sources without compiling')
    args = ap.parse_args()
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        ap.error('Linux/WSL x86_64 is required')
    cache = args.cache.resolve()
    if not cache.is_relative_to((ROOT/'work').resolve()):
        ap.error('Cache must stay under work/')
    cache.mkdir(parents=True, exist_ok=True)
    for tool in ['cmake','ninja','git','clang-19','clang++-19','ld.lld-19']:
        if not shutil.which(tool):
            ap.error('Missing host dependency: '+tool)
    lock = json.loads((ROOT/'compiler-port/patches.lock.json').read_text())
    patch = ROOT/'compiler-port/0001-add-atlantic-c-layout-primitives.patch'
    if (lock['upstream_commit'] != COMMIT or lock['archive_sha256'] != ARCHIVE_SHA256 or
        lock['patch_sha256'] != digest(patch)):
        ap.error('Compiler patch provenance mismatch')
    inputs = {p:digest(ROOT/p) for p in ['tools/build_atlantic_clang.py','compiler-port/patches.lock.json',
              'compiler-port/ParseAtlanticLayout.inc','compiler-port/SemaAtlanticLayout.cpp']}
    archive = args.archive.resolve() if args.archive else cache/'llvm-source.tar.gz'
    if args.archive and not archive.is_file():
        ap.error('The supplied archive does not exist')
    if not archive.exists():
        partial = archive.with_suffix('.partial')
        with urllib.request.urlopen(URL,timeout=60) as incoming, partial.open('xb') as output:
            shutil.copyfileobj(incoming,output,1024*1024)
        if digest(partial) != ARCHIVE_SHA256:
            ap.error('Archive digest mismatch; preserve partial file for inspection')
        partial.rename(archive)
    if digest(archive) != ARCHIVE_SHA256:
        ap.error('Archive digest mismatch')
    source = cache/'source'
    stamp = cache/'source-record.json'
    if not source.exists():
        source.mkdir()
        files = {}
        with tarfile.open(archive,'r|gz') as tar:
            for item in tar:
                path = PurePosixPath(item.name)
                if path.is_absolute() or '..' in path.parts or path.parts[0] != 'llvm-project-'+COMMIT:
                    ap.error('Unexpected archive path')
                relative = PurePosixPath(*path.parts[1:])
                name = str(relative)
                if not relative.parts or relative.parts[0] not in {'llvm','clang','cmake','third-party'}:
                    continue
                if any(name==p or name.startswith(p+'/') for p in EXCLUDED) or item.isdir():
                    continue
                dest = source/name
                if not item.isfile() or not dest.resolve().is_relative_to(source) or dest.exists():
                    ap.error('Nonregular, duplicate or escaping source member')
                dest.parent.mkdir(parents=True,exist_ok=True)
                with tar.extractfile(item) as incoming, dest.open('xb') as output:
                    shutil.copyfileobj(incoming,output,1024*1024)
                files[name] = digest(dest)
        for entry in lock['files']:
            if entry['preimage_sha256'] is not None and files.get(entry['path']) != entry['preimage_sha256']:
                ap.error('Unexpected upstream patch preimage: '+entry['path'])
        # Use an isolated repository boundary even when the cache is below this
        # project's checkout; git apply must not skip paths outside its prefix.
        subprocess.run(['git','init','--quiet',str(source)],check=True,timeout=15)
        subprocess.run(['git','apply','--check',str(patch)],cwd=source,check=True,timeout=30)
        subprocess.run(['git','apply',str(patch)],cwd=source,check=True,timeout=30)
        for entry in lock['files']:
            files[entry['path']] = entry['postimage_sha256']
        stamp.write_text(json.dumps({'commit':COMMIT,'patch_sha256':lock['patch_sha256'],'files':files},indent=2)+'\n',
                         encoding='utf-8',newline='\n')
    if not stamp.is_file():
        ap.error('Incomplete source preparation; preserve it and inspect manually')
    record = json.loads(stamp.read_text())
    if record['commit'] != COMMIT or record['patch_sha256'] != lock['patch_sha256']:
        ap.error('Existing cache is for a different compiler patch; use a new cache')
    for name, expected in record['files'].items():
        if digest(source/name) != expected:
            ap.error('Prepared compiler source changed: '+name)
    actual_files = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()
                    and '.git' not in p.relative_to(source).parts
                    and '__pycache__' not in p.relative_to(source).parts}
    if actual_files != set(record['files']):
        ap.error('Unexpected files in the prepared compiler source tree')
    if (source/'clang/lib/Sema/SemaAtlanticLayout.cpp').read_bytes() != (ROOT/'compiler-port/SemaAtlanticLayout.cpp').read_bytes():
        ap.error('Compiler implementation and patch disagree')
    if (ROOT/'compiler-port/ParseAtlanticLayout.inc').read_text() not in (source/'clang/lib/Parse/ParseExpr.cpp').read_text():
        ap.error('Compiler parser fragment and patch disagree')
    if args.prepare_only:
        report = {'scope':'PINNED_COMPILER_SOURCE_PREPARATION_ONLY_NOT_COMPILER_BUILD',
                  'upstream_commit':COMMIT,'archive_sha256':ARCHIVE_SHA256,'patch_sha256':lock['patch_sha256'],
                  'inputs':inputs,'source_files_verified':len(record['files']),'xnu_executed':False}
        (cache/'preparation-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({'source_files_verified':len(record['files']),'compiler_built':False,
                          'report':str(cache/'preparation-report.json')}))
        return
    build = cache/'build';build.mkdir(exist_ok=True)
    commands = []
    def run(name, command):
        print(name,flush=True)
        commands.append([s.replace(str(ROOT),'<ROOT>') for s in command])
        with (build/(name+'.log')).open('w') as log:
            result = subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=7200)
        if result.returncode:
            print('\n'.join((build/(name+'.log')).read_text().splitlines()[-30:]))
            raise SystemExit(result.returncode)
    run('configure',['cmake','-G','Ninja','-S',str(source/'llvm'),'-B',str(build),
        '-DCMAKE_BUILD_TYPE=Release','-DCMAKE_C_COMPILER='+shutil.which('clang-19'),
        '-DCMAKE_CXX_COMPILER='+shutil.which('clang++-19'),'-DCMAKE_CXX_FLAGS_RELEASE=-O1 -DNDEBUG',
        '-DCMAKE_C_FLAGS_RELEASE=-O1 -DNDEBUG','-DLLVM_ENABLE_PROJECTS=clang',
        '-DLLVM_TARGETS_TO_BUILD=AArch64;X86','-DLLVM_INCLUDE_TESTS=OFF','-DLLVM_INCLUDE_BENCHMARKS=OFF',
        '-DLLVM_INCLUDE_DOCS=OFF','-DCLANG_INCLUDE_TESTS=OFF','-DLLVM_ENABLE_ASSERTIONS=ON',
        '-DLLVM_APPEND_VC_REV=OFF','-DLLVM_ENABLE_ZSTD=OFF','-DLLVM_ENABLE_ZLIB=OFF',
        '-DLLVM_ENABLE_LIBXML2=OFF','-DCLANG_ENABLE_STATIC_ANALYZER=OFF','-DCLANG_ENABLE_ARCMT=OFF',
        '-DLLVM_USE_LINKER='+shutil.which('ld.lld-19'),'-DLLVM_PARALLEL_LINK_JOBS=1'])
    run('build-clang',['ninja','-C',str(build),'-j',str(args.jobs),'clang','clang-resource-headers'])
    compiler = build/'bin/clang'
    run('test-api',['python3',str(ROOT/'tools/test_atlantic_clang.py'),'--compiler',str(compiler),
                    '--output',str(cache/'tests')])
    report = {'scope':'EXPERIMENTAL_HOST_COMPILER_ONLY_NOT_A_KERNEL_OR_HARDWARE_PORT','label':'HOST_TESTED',
              'upstream_commit':COMMIT,'archive_sha256':ARCHIVE_SHA256,'patch_sha256':lock['patch_sha256'],
              'inputs':inputs,'commands':commands,'compiler_sha256':digest(compiler),
              'source_files_verified':len(record['files']),'xnu_executed':False,'phone_accessed':False}
    (cache/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'compiler':str(compiler),'report':str(cache/'report.json')}))


if __name__ == '__main__':
    main()
