"""Build original ARM64 entry preflight for the laboratory BSP, NOT an XNU kernel.

No phone packaging, bootloader commands, device access or foreign loader binary.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCES=['atlantic-entry/entry.S','atlantic-entry/preflight.c','atlantic-entry/link.ld',
         'atlantic-core/fdt.c','include/atlantic/entry.h','include/atlantic/fdt.h',
         'platforms/qemu-virt/early.c','platforms/qemu-virt/board.json',
         'platforms/qemu-virt/el1.S']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board',choices=['qemu-virt'],default='qemu-virt')
    parser.add_argument('--output',type=Path,default=ROOT/'work/entry-qemu')
    parser.add_argument('--probe',choices=['normal','el1-trap'],default='normal')
    args=parser.parse_args()
    cc,ld,objcopy=(shutil.which(x) for x in ['clang','ld.lld','llvm-objcopy'])
    if not all((cc,ld,objcopy)):
        raise SystemExit('clang, ld.lld and llvm-objcopy required')
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()):
        raise SystemExit('Build output must remain under work/')
    out.mkdir(parents=True,exist_ok=True)
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}
    build_id=hashlib.sha256(json.dumps({'sources':hashes,'probe':args.probe},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    flags=['--target=aarch64-none-elf','-mcpu=cortex-a57','-mgeneral-regs-only',
           '-std=c11','-ffreestanding','-fno-builtin','-fno-stack-protector',
           '-fno-unwind-tables','-fno-asynchronous-unwind-tables','-O2','-g',
           '-Wall','-Wextra','-Werror','-Iinclude',f'-DATL_BUILD_ID="{build_id}"',
           '-ffile-prefix-map='+str(ROOT)+'=.', '-DATL_TEST_EL1_TRAP='+str(int(args.probe=='el1-trap'))]
    commands=[]
    logs=[]
    def run(command):
        r=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=30)
        commands.append([Path(command[0]).name,*[str(s).replace(str(ROOT),'<ROOT>') for s in command[1:]]])
        logs.append(r.stdout+r.stderr)
        if r.returncode:
            (out/'build.log').write_text('\n'.join(log for log in logs if log),encoding='utf-8',newline='\n')
            print(r.stdout+r.stderr)
            raise SystemExit(r.returncode)
    objects=[]
    for source in [SOURCES[0],SOURCES[1],SOURCES[3],SOURCES[6],SOURCES[8]]:
        obj=out/(Path(source).stem+'.o')
        run([cc,*flags,'-c',source,'-o',str(obj)])
        objects.append(str(obj))
    elf,binary=out/'entry.elf',out/'entry.bin'
    run([ld,'--defsym=ATL_LINK_BASE=0x40080000','-T','atlantic-entry/link.ld',
         '-Map='+str(out/'entry.map'),'-o',str(elf),*objects])
    run([objcopy,'-O','binary',str(elf),str(binary)])
    data=binary.read_bytes()
    if len(data)<64 or data[56:60]!=b'ARM\x64' or struct.unpack_from('<Q',data,8)[0]!=0x80000:
        raise SystemExit('Invalid self-built AArch64 Image header')
    memory_bytes=struct.unpack_from('<Q',data,16)[0]
    if not len(data)<=memory_bytes<2*1024*1024:
        raise SystemExit('Invalid image file/memory bounds')
    raw_elf=elf.read_bytes()
    if raw_elf[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',raw_elf,18)[0]!=183:
        raise SystemExit('Invalid AArch64 ELF')
    report={'schema_version':1,'label':'BUILT_ARM64','scope':'ORIGINAL_ENTRY_PREFLIGHT_ONLY_XNU_NOT_LINKED',
            'board_id':'qemu,virt-laboratory','build_id':build_id,'sources':hashes,'probe':args.probe,
            'compiler':subprocess.check_output([cc,'--version'],text=True).splitlines()[0],
            'linker':subprocess.check_output([ld,'--version'],text=True).strip(),
            'commands':commands,'image_file_bytes':len(data),'image_memory_bytes':memory_bytes,
            'image_sha256':hashlib.sha256(data).hexdigest(),'elf_sha256':hashlib.sha256(raw_elf).hexdigest(),
            'phone_packaged':False,'xnu_linked':False,'bootshim_used':False}
    (out/'build.log').write_text('\n'.join(log for log in logs if log),encoding='utf-8',newline='\n')
    (out/'build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
