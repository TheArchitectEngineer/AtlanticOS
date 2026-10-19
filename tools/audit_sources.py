"""Rebuild the audit source index from pinned Git objects, not working-tree text.

No repository scripts are executed. No submodules/binaries/boot images fetched.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
 ('S01','g20','README.md',r'UEFI DXE'),
 ('S02','g20','docs/STATUS.md',r'Actualizado'),
 ('S03','g20','docs/DEVELOPMENT.md',r'Fuente activa|fuente activa|entrada'),
 ('S04','g20','docs/BUILD.md',r'no reconstruye|No reconstruye'),
 ('S05','g20','MotoG20Pkg/Include/Platform.h',r'GICv3'),
 ('S06','g20','MotoG20Pkg/Include/Platform.h',r'MOTO_G20_FRAMEBUFFER_BASE'),
 ('S07','g20','MotoG20Pkg/Include/Platform.h',r'MOTO_G20_BOOT_EXCEPTION_LEVEL'),
 ('S08','g20','MotoG20Pkg/PrePi/Foundation/MotoG20FoundationBootstrap.h',r'DXE_MEMORY_SIZE'),
 ('S09','g20','MotoG20Pkg/Drivers/MotoG20SdDxe/sdhci_ro.c',r'.'),
 ('S10','g20','docs/evidence/microsd-v4-physical-result.json',r'android_return_after_v4'),
 ('S11','g20','docs/evidence/microsd-v1-physical-result.json',r'user_followup'),
 ('S12','g20','docs/evidence/motorola-source-manifest.json',r'CONFIG_KEXEC'),
 ('S13','g20','development/usb_ep0_v6/DIAGNOSTIC_GUIDE.md',r'.'),
 ('S14','g20','development/usb_ep0_v6/README.md',r'.'),
 ('S15','g20','development/microsd_v1/packaging/package_microsd_candidate.py',r'FV_SIZE, IMAGE_SIZE'),
 ('S16','g20','THIRD_PARTY_NOTICES.md',r'EDK2'),
 ('S17','g20','MotoG20Pkg/PrePi/EntryPoint.S',r'CurrentEL'),
 ('S18','g20','MotoG20Pkg/Drivers/MotoG20SdPlatformDxe/sd_platform_engine.c',r'.'),
 ('S19','g20','docs/evidence/IMG_1581.jpeg',None),
 ('X01','xnu','README.md',r'How to Build'),
 ('X02','xnu','makedefs/MakeInc.cmd',r'XCRUN = /usr/bin/xcrun'),
 ('X03','xnu','config/MASTER.arm64',r'BSD_BASE'),
 ('X04','xnu','osfmk/arm64/start.s',r'LEXT\(start_first_cpu\)'),
 ('X05','xnu','osfmk/arm/arm_init.c',r'^arm_init\('),
 ('X06','xnu','osfmk/kern/startup.c',r'^kernel_bootstrap\('),
 ('X07','xnu','pexpert/arm/pe_init.c',r'^PE_init_platform\('),
 ('X08','xnu','pexpert/pexpert/arm64/boot.h',r'typedef struct boot_args'),
 ('X09','xnu','pexpert/pexpert/arm64/VMAPPLE.h',r'HAS_GIC_V3'),
 ('X10','xnu','pexpert/arm/pe_fiq.c',r'HAS_GIC_V3'),
 ('X11','xnu','APPLE_LICENSE',r'Version 2.0'),
 ('X12','xnu','pexpert/arm/pe_identify_machine.c',r'SecureDTFindEntry'),
]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--g20', type=Path, default=ROOT/'work/references/g20')
    p.add_argument('--xnu', type=Path, default=ROOT/'xnu-upstream')
    args = p.parse_args()
    lock = json.loads((ROOT/'dependencies.lock.json').read_text())
    entries = []
    for ident, project, path, pattern in SOURCES:
        dep = lock['g20_reference' if project == 'g20' else 'xnu']
        folder = args.g20 if project == 'g20' else args.xnu
        commit = dep['commit']
        data = subprocess.check_output(['git','-C',str(folder),'show',f'{commit}:{path}'])
        lines = data.decode('utf-8', errors='replace').splitlines() if pattern else []
        matches = [i+1 for i,l in enumerate(lines) if re.search(pattern,l)] if pattern else []
        if pattern and not matches:
            raise ValueError(f'{ident}: anchor no longer present in pinned object')
        line = matches[0] if matches else None
        url = dep['url'].removesuffix('.git')+'/blob/'+commit+'/'+path
        if line:
            url += f'#L{line}'
        entries.append({'id':ident,'project':project,'commit':commit,'path':path,
                        'line':line,'url':url,'sha256_git_blob_bytes':hashlib.sha256(data).hexdigest(),
                        'bytes':len(data),'audit_date':'2026-10-19'})
    (ROOT/'docs/sources.lock.json').write_text(json.dumps(entries,indent=2)+'\n', encoding='utf-8', newline="\n")
    text = '# Índice de fuentes fijadas\n\nAuditoría 2026-10-19. Hashes sobre bytes originales del objeto Git, no CRLF del checkout.\n'
    text += 'No se ejecutaron scripts ni se integró código del repositorio de referencia.\n'
    for e in entries:
        text += f'\n## {e["id"]}\n\n[{e["project"]}: {e["path"]}, línea {e["line"] or "imagen"}]({e["url"]})\n\nSHA-256 `{e["sha256_git_blob_bytes"]}`; {e["bytes"]} bytes.\n'
    (ROOT/'docs/SOURCE_INDEX.md').write_text(text, encoding='utf-8', newline="\n")
    print(f'Indexed {len(entries)} pinned source objects')


if __name__ == '__main__':
    main()
