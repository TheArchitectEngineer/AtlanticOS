"""Fetch only locked official XNU. Never a bootloader, BootShim or device image."""
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
dep = json.loads((root/'dependencies.lock.json').read_text())['xnu']
dest = root/'xnu-upstream'
if dest.exists():
    head = subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()
    dirty = subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True)
    if head != dep['commit'] or dirty:
        raise SystemExit('Existing XNU does not match lock or has changes; preserve and inspect it manually')
else:
    subprocess.run(['git','init',str(dest)],check=True)
    subprocess.run(['git','-C',str(dest),'remote','add','origin',dep['url']],check=True)
    subprocess.run(['git','-C',str(dest),'fetch','--depth','1','origin',dep['commit']],check=True)
    subprocess.run(['git','-C',str(dest),'checkout','--detach',dep['commit']],check=True)
print('Pinned official XNU present:', dep['commit'])
