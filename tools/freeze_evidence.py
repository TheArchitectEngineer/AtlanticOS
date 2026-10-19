"""Freeze a bounded set of already-run reports; never execute or promote tests.

Run validate.py and build_abi.py first, inspect results, then this tool. Re-running
updates historical host evidence; review the diff before committing.
"""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
FILES = ['tests.log','summary.json','host-memory.json','source-hashes.json',
         'realtime-timer.json','tk-smoke.json','config-integration.json',
         'countdown.json','held-volume-down.json','menu.json','safe-recovery.json',
         'menu.png','safe-recovery.png','countdown-5.png','setup.png','power-confirmation.png']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(folder, label, scope, files):
    data = {'schema_version':1,'audit_date':'2026-10-19','label':label,'scope':scope,
            'artifacts':[{'path':name,'sha256':sha(folder/name)} for name in files]}
    (folder/'manifest.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8', newline="\n")


def main():
    src = ROOT/'work/validation'
    summary = json.loads((src/'summary.json').read_text())
    if summary.get('unit_exit_code') != 0 or summary.get('device_verified') is not False:
        raise SystemExit('Refusing invalid or mislabeled host summary')
    dest = ROOT/'evidence/host'
    dest.mkdir(parents=True,exist_ok=True)
    for name in FILES:
        shutil.copyfile(src/name,dest/name)
    spec = ROOT/'work/ATLANTICOS_CODEX_HANDOFF.md'
    lock = json.loads((ROOT/'dependencies.lock.json').read_text())
    provenance = {'audit_date':'2026-10-19','label':'HOST_TESTED',
                  'scope':'SOURCE_AUDIT_AND_HOST_ONLY_POLICY',
                  'main_spec_sha256':sha(spec) if spec.exists() else None,
                  'xnu_commit':lock['xnu']['commit'],'xnu_patchset':'EMPTY',
                  'g20_reference_commit':lock['g20_reference']['commit'],
                  'reference_code_imported':False,'reference_binary_downloaded_or_used':False,
                  'device_connected':False,'flashed':False,'android_modified':False,
                  'reference_photo':{'source':'docs/evidence/IMG_1581.jpeg',
                    'sha256':'4c1970360c053d001925fc1186e520966904949dd11b523241170d5b777d8be3',
                    'ownership':'EXTERNAL_G20_UEFI_PROJECT','inspection':'visual source audit only; not redistributed'}}
    (dest/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8', newline="\n")
    manifest(dest,'HOST_TESTED','Host policy, renderer and audits only; no XNU execution',FILES+['provenance.json'])
    arm = ROOT/'evidence/arm64'
    arm.mkdir(parents=True,exist_ok=True)
    for name in ['build.json','build.log','moto-g20-bsp.o']:
        shutil.copyfile(ROOT/'work/arm64-abi'/name,arm/name)
    manifest(arm,'BUILT_ARM64','Original unsupported BSP shell ELF object only; no XNU, entry or hardware drivers',
             ['build.json','build.log','moto-g20-bsp.o'])
    print('Frozen host and ARM64 ABI evidence; no device claims')


if __name__ == '__main__':
    main()
