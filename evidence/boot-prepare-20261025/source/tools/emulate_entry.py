"""Execute the preflight's AArch64 instructions under QEMU EL1 and EL2.

This is not execution of XNU. No disks, phone, network or EFI images are attached.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
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
    for rel,expected in meta['sources'].items():
        if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=expected:
            raise SystemExit('Build input changed: '+rel)
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
        execution=re.search(r'EXECUTION_EL=0x([0-9A-F]+)',log)
        is_trap=meta.get('probe')=='el1-trap'
        expected_exit=1 if is_trap else 0
        esr=re.search(r'ESR=0x([0-9A-F]+)',log)
        tree=re.search(r'XNU_TREE_BYTES=0x([0-9A-F]+)',log)
        data_ok=bool(tree and int(tree[1],16)==504 and 'PASS:BOOT_DATA_DECLARATIONS_XNU_TREE_ONLY' in log)
        candidate=None
        if meta.get('probe')=='boot-args':
            wire=re.search(r'^CANDIDATE_BOOT_ARGS_HEX=([0-9a-f]{2304})$',log,re.M)
            expected=bytearray(1152)
            struct.pack_into('<HH',expected,0,2,2)
            struct.pack_into('<4Q',expected,8,0xfffffff007000000,0x42000000,0x2000000,0x42024000)
            struct.pack_into('<I',expected,88,0x41544c31)
            struct.pack_into('<QI',expected,96,0xfffffff00701c000,504)
            expected[108:110]=b'-v';struct.pack_into('<Q',expected,1144,0x8000000)
            if (not wire or bytes.fromhex(wire[1])!=expected or
                'PASS:BOOT_ARGS_CANDIDATE_ONLY' not in log or 'CANDIDATE_NOT_PLACED_OR_MAPPED' not in log or
                'PASS:BOOT_ARGS_RESERVED_WINDOW_REJECTED' not in log or
                'CANDIDATE_BOOTSTRAP_BYTES=0x0000000001E00000' not in log):
                raise SystemExit('Candidate record/block reach differs from independent expected bytes')
            candidate=hashlib.sha256(expected).hexdigest()
        result_ok = (esr and int(esr[1],16)==0xf2000a71 and 'TEST:EL1_BRK_EXPECTED' in log
                     and 'ATLANTIC_ENTRY_EXCEPTION' in log) if is_trap else 'PASS:ENTRY_CAPTURE_DTB_TIMER' in log
        if (r.returncode!=expected_exit or not observed or int(observed[1],16)!=el or not execution or int(execution[1],16)!=1
            or 'PASS:EL1_STACK_VECTORS_COUNTER' not in log or not result_ok or not data_ok or 'FAIL:' in log or 'XNU_NOT_LINKED' not in log):
            raise SystemExit(f'EL{el} preflight failed (exit={r.returncode})')
        records.append({'expected_el':el,'observed_el':int(observed[1],16),'execution_el':int(execution[1],16),
                        'expected_exit_code':expected_exit,'exit_code':r.returncode,'probe':meta.get('probe'),
                        'boot_data_checked':True,'native_tree_bytes':int(tree[1],16),
                        'candidate_boot_args_sha256':candidate,
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
