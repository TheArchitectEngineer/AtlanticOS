"""Fetch pinned official Apple MIG sources, preserving any existing checkout."""
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
dep = json.loads((root/'dependencies.lock.json').read_text())['mig_host_tool']
dest = root/'work/references/bootstrap_cmds'
if not dest.exists():
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', str(dest)], check=True)
    subprocess.run(['git', '-C', str(dest), 'remote', 'add', 'origin', dep['url']], check=True)
    subprocess.run(['git', '-C', str(dest), 'fetch', '--depth', '1', 'origin', dep['commit']], check=True)
    subprocess.run(['git', '-C', str(dest), 'checkout', '--detach', dep['commit']], check=True)
head = subprocess.check_output(['git', '-C', str(dest), 'rev-parse', 'HEAD'], text=True).strip()
dirty = subprocess.check_output(['git', '-c', 'core.autocrlf=true', '-C', str(dest), 'status', '--porcelain'], text=True)
if head != dep['commit'] or dirty:
    raise SystemExit('Preserve existing MIG checkout: revision mismatch or local changes')
print('Pinned official MIG sources present:', head)
