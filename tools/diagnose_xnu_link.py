"""Attempt a strict static Mach-O link and preserve its actual rejection.

This diagnostic is not a kernel builder or boot-image producer. It forbids
undefined-symbol suppression, treats warnings as errors and never declares a
successful AtlanticOS kernel. Unexpected success requires a separate image audit.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--linker', type=Path)
    ap.add_argument('--output', type=Path, default=ROOT/'work/xnu-link-diagnostics')
    args = ap.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()):
        ap.error('Output must stay under work/')
    if out.exists():
        ap.error('Use a new output directory; preserve previous link attempts')
    linker = args.linker or shutil.which('ld64.lld') or shutil.which('ld64.lld-19')
    if not linker:
        ap.error('A real ld64.lld executable is required')
    linker = Path(linker).absolute()  # Retain its driver name when invoking a symlink.
    build = json.loads(args.build.read_text())
    lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if build['port_id'] != lock['port_id'] or build['failed_units']:
        ap.error('Use a successful build of the current patch series')
    for rel, expected in build['inputs'].items():
        if digest(ROOT/rel) != expected:
            ap.error('Changed build input: '+rel)
    source = ROOT/'work/xnu-lab-sources'/lock['port_id'][:16]
    objects = []
    for item in build['objects']:
        obj = (args.build.parent/item['object']).resolve()
        if (not obj.is_relative_to(args.build.parent.resolve()) or
            digest(obj) != item['object_sha256'] or
            digest(source/item['source']) != item['source_sha256']):
            ap.error('Changed or escaping XNU source/object: '+item['source'])
        objects.append(str(obj))
    out.mkdir(parents=True)
    image = out/'unvalidated.macho'
    cmd = [str(linker), '-arch', 'arm64', '-static', '-no_pie',
           '-platform_version', 'macos', '11.0', '11.0',
           '-e', '__start', '-image_base', build['virtual_link_address'],
           '-fatal_warnings', '-undefined', 'error', '--error-limit=0',
           '-o', str(image), *objects]
    r = subprocess.run(cmd, text=True, capture_output=True, timeout=120)
    log = out/'link.log'
    log.write_text((r.stdout+r.stderr).replace(str(ROOT), '<ROOT>'), encoding='utf-8', newline='\n')
    unsupported = "Option `-static' is not yet implemented" in r.stderr
    result = {'schema_version':1, 'label':'HOST_TESTED',
        'scope':'STRICT_STATIC_LINK_DIAGNOSTIC_ONLY_NOT_A_KERNEL_OR_BOOT_IMAGE',
        'port_id':lock['port_id'], 'build_report_sha256':digest(args.build),
        'tool_sha256':digest(__file__), 'linker_sha256':digest(linker),
        'linker_version':subprocess.check_output([str(linker), '--version'], text=True).strip(),
        'command':[s.replace(str(ROOT), '<ROOT>') for s in cmd],
        'link_exit_code':r.returncode, 'link_log_sha256':digest(log),
        'unsupported_static_option_diagnostic_found':unsupported,
        'rejected_option_diagnostics':[s for s in r.stderr.splitlines()
            if 'not yet implemented' in s or 'ignored for arm64' in s],
        'undefined_symbol_error_count':r.stderr.count('error: undefined symbol:'),
        'object_count':len(objects), 'warnings_are_errors':True,
        'undefined_symbols_must_error':True, 'dead_stripping_requested':False,
        'output_exists':image.exists(), 'output_sha256':digest(image) if image.exists() else None,
        'kernel_linked':False, 'xnu_executed':False, 'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k:result[k] for k in ['object_count','link_exit_code',
        'unsupported_static_option_diagnostic_found','output_exists','kernel_linked']}))
    # Failure is the observation being recorded. A produced image is never
    # accepted by this diagnostic; it must pass a separate kernel image audit.
    return 0 if r.returncode != 0 and not image.exists() else 1


if __name__ == '__main__':
    raise SystemExit(main())
