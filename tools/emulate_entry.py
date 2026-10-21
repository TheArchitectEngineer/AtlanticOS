"""Execute the preflight's AArch64 instructions under QEMU EL1 and EL2.

This is not execution of XNU. No disks, phone, network or EFI images are attached.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build',type=Path,default=ROOT/'work/entry-qemu')
    args=p.parse_args()
    folder=args.build.resolve()
    binary=folder/'entry.bin'
    meta=json.loads((folder/'build.json').read_text())
    if hashlib.sha256(binary.read_bytes()).hexdigest()!=meta['image_sha256']:
        raise SystemExit('Image differs from build report')
    qemu=shutil.which('qemu-system-aarch64')
    if not qemu:
        raise SystemExit('QEMU AArch64 not found')
    records=[]
    for el,virtualization in [(1,'off'),(2,'on')]:
        command=[qemu,'-machine','virt,virtualization='+virtualization,'-cpu','cortex-a57',
                 '-m','128M','-smp','1','-nographic','-monitor','none','-serial','stdio',
                 '-nic','none','-no-reboot','-semihosting-config','enable=on,target=native',
                 '-kernel',str(binary)]
        try:
            r=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=15)
            log=r.stdout+r.stderr
            (folder/f'qemu-el{el}.log').write_text(log,encoding='utf-8',newline='\n')
        except subprocess.TimeoutExpired as exc:
            log=(exc.stdout or b'').decode(errors='replace')+(exc.stderr or b'').decode(errors='replace')
            (folder/f'qemu-el{el}.log').write_text(log,encoding='utf-8',newline='\n')
            print(log)
            raise SystemExit(f'QEMU EL{el} timed out; no successful entry claim')
        print(log)
        observed=re.search(r'INITIAL_EL=0x([0-9A-F]+)',log)
        if r.returncode or not observed or int(observed[1],16)!=el or 'PASS:ENTRY_CAPTURE_DTB_TIMER' not in log or 'XNU_NOT_LINKED' not in log:
            raise SystemExit(f'EL{el} preflight failed (exit={r.returncode})')
        records.append({'expected_el':el,'observed_el':int(observed[1],16),'exit_code':r.returncode,
                        'log_sha256':hashlib.sha256((folder/f'qemu-el{el}.log').read_bytes()).hexdigest(),
                        'command':[Path(command[0]).name,*[s.replace(str(ROOT),'<ROOT>') for s in command[1:]]]})
    report={'schema_version':1,'label':'EMULATED','scope':'ORIGINAL_ARM64_ENTRY_ONLY_NOT_XNU_NOT_G20',
            'qemu_version':subprocess.check_output([qemu,'--version'],text=True).splitlines()[0],
            'image_sha256':meta['image_sha256'],'build_id':meta['build_id'],'runs':records,
            'xnu_executed':False,'phone_accessed':False,'network_enabled':False,'disks_attached':False}
    (folder/'emulation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
