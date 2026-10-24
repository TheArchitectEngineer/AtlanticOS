"""Verify original typed boot-data code; host execution and target ABI only.

No kernel execution, image of a phone, physical RAM measurement, or device IO.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCES=['include/atlantic/fdt.h','include/atlantic/boot_tree.h','atlantic-core/fdt.c',
         'atlantic-core/boot_tree.c','tests/c/test_boot_tree.c','tests/xnu_port/boot_tree_abi.c',
         'tools/test_boot_tree.py','tools/boot_tree_check.c']

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--sanitize',action='store_true')
    ap.add_argument('--xnu-build',type=Path)
    ap.add_argument('--dtb',type=Path,action='append',default=[],help='Read-only declaration probe, never a physical RAM test')
    args=ap.parse_args()
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():
        ap.error('Use a new output directory under work/')
    cc=shutil.which('clang')
    if not cc:ap.error('A real Clang compiler is required')
    if platform.system()!='Linux':ap.error('Use Linux/WSL for target builds and the POSIX inspection harness')
    out.mkdir(parents=True)
    commands=[]
    def run(name,cmd):
        r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=60)
        commands.append([str(s).replace(str(ROOT),'<ROOT>') for s in cmd])
        (out/(name+'.log')).write_text((r.stdout+r.stderr).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        if r.returncode:raise RuntimeError(name+' failed: '+r.stderr[-3000:])
        return r.stdout
    flags=['-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-I'+str(ROOT/'include')]
    if args.sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
    exe=out/'host-tests'
    run('host-build',[cc,*flags,str(ROOT/'tests/c/test_boot_tree.c'),str(ROOT/'atlantic-core/fdt.c'),
                      str(ROOT/'atlantic-core/boot_tree.c'),'-o',str(exe)])
    result=run('host-tests',[str(exe)])
    if 'PASS: boot inventory' not in result:raise RuntimeError('Missing actual test completion')
    run('file-harness-build',[cc,*flags,'-D_POSIX_C_SOURCE=200809L',str(ROOT/'tools/boot_tree_check.c'),
         str(ROOT/'atlantic-core/fdt.c'),str(ROOT/'atlantic-core/boot_tree.c'),'-o',str(out/'inspect-dtb')])
    samples=[]
    for i,path in enumerate(args.dtb):
        if not path.is_file() or path.is_symlink():ap.error('Use a regular DTB file')
        before=digest(path)
        cmd=[str(out/'inspect-dtb'),str(path.resolve())]
        r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=30)
        commands.append([s.replace(str(ROOT),'<ROOT>') for s in cmd])
        (out/('sample-'+str(i)+'.log')).write_text(r.stdout+r.stderr,encoding='utf-8',newline='\n')
        if r.returncode not in {0,1} or digest(path)!=before:raise RuntimeError('Input changed or inspection failed')
        decoded=json.loads(r.stdout)
        if decoded['accepted']!=(r.returncode==0):raise RuntimeError('Inconsistent inspection result')
        samples.append({'input_sha256':before,'exit_code':r.returncode,'declarations':decoded})
    target=[cc,'--target=aarch64-none-elf','-mcpu=cortex-a57','-mgeneral-regs-only',
            '-std=c11','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector',
            '-Wall','-Wextra','-Werror','-I'+str(ROOT/'include')]
    for rel in ['atlantic-core/fdt.c','atlantic-core/boot_tree.c']:
        run(Path(rel).stem+'-arm64',[*target,'-c',str(ROOT/rel),'-o',str(out/(Path(rel).stem+'.o'))])
    abi=None
    if args.xnu_build:
        base=json.loads(args.xnu_build.read_text())
        lock=json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
        if base['port_id']!=lock['port_id'] or base['failed_units']:ap.error('Use a successful current XNU build')
        for rel,sha in base['inputs'].items():
            if digest(ROOT/rel)!=sha:ap.error('Changed XNU build input: '+rel)
        command=next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
        if command[-4]!='-c':ap.error('Unexpected target recipe')
        native=[s.replace('<ROOT>',str(ROOT)) for s in command[:-4]]
        if base['layout_provider'] and digest(native[0])!=base['layout_provider']['compiler_sha256']:
            ap.error('Changed experimental compiler')
        tree=ROOT/'work/xnu-lab-sources'/base['port_id'][:16]/'pexpert/pexpert/device_tree.h'
        upstream=ROOT/'xnu-upstream/pexpert/pexpert/device_tree.h'
        if digest(tree)!=hashlib.sha256(upstream.read_text().encode()).hexdigest():ap.error('Native tree header changed')
        for item in base['config_headers']+base['generated_headers']:
            if digest(args.xnu_build.parent/item['path'])!=item['sha256']:ap.error('Changed generated header')
        run('native-xnu-tree-abi',[*native,'-UMACH_KERNEL_PRIVATE','-DPEXPERT_KERNEL_PRIVATE=1',
                                  '-c',str(ROOT/'tests/xnu_port/boot_tree_abi.c'),'-o',str(out/'native-tree-abi.o')])
        abi={'build_report_sha256':digest(args.xnu_build),'header_sha256':digest(tree),
             'object_sha256':digest(out/'native-tree-abi.o'),'xnu_executed':False}
    report={'schema_version':1,'label':'HOST_TESTED',
        'scope':'ORIGINAL_BOOT_TREE_HOST_EXECUTION_AND_ARM64_OBJECTS_ONLY_NOT_XNU_OR_PHONE_EXECUTION',
        'inputs':{p:digest(ROOT/p) for p in SOURCES},'commands':commands,'sanitizers':args.sanitize,
        'host_exit_code':0,'buffer_truncations':504,'fdt_mutations':5000,'native_xnu_abi':abi,
        'compiler_version':subprocess.check_output([cc,'--version'],text=True).splitlines()[0],
        'objects':{p.name:digest(p) for p in sorted(out.glob('*.o'))},'declaration_probes':samples,
        'kernel_linked':False,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'host_passed':True,'sanitizers':args.sanitize,'native_abi_checked':abi is not None}))

if __name__=='__main__':main()
