"""Query ONLY enumerated fastboot metadata after a human reaches bootloader.

No reboot, boot, flash, erase, set_active, OEM, unlock or getvar all operations.
The user controls physical mode changes; this command never enters/leaves a mode.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

VARIABLES = (
    'product', 'version', 'version-bootloader', 'secure', 'unlocked',
    'is-userspace', 'current-slot', 'slot-count',
    'has-slot:boot', 'has-slot:vendor_boot', 'has-slot:dtb', 'has-slot:dtbo',
    'slot-successful:a', 'slot-successful:b',
    'slot-unbootable:a', 'slot-unbootable:b',
    'slot-retry-count:a', 'slot-retry-count:b',
    'partition-size:boot_a', 'partition-size:boot_b',
    'partition-size:vendor_boot_a', 'partition-size:vendor_boot_b',
    'partition-size:dtb_a', 'partition-size:dtb_b',
    'partition-size:dtbo_a', 'partition-size:dtbo_b',
    'partition-type:boot_a', 'max-download-size',
)


def command_for(executable, serial, variable):
    if variable not in VARIABLES:
        raise ValueError('Not an allowed read-only fastboot variable')
    return [executable,'-s',serial,'getvar',variable]


def select_serial(output):
    entries = [line.split() for line in output.splitlines() if line.strip()]
    if len(entries) != 1 or len(entries[0]) < 2 or entries[0][1] != 'fastboot':
        raise ValueError('Exactly one fastboot transport required')
    return entries[0][0]


def extract_value(variable, output):
    for line in output.splitlines():
        line = line.strip().removeprefix('(bootloader)').strip()
        if line.startswith(variable+':'):
            return line[len(variable)+1:].strip()
    return None  # Preserve absent/unsupported instead of guessing a value.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    out = args.output.resolve()
    if out.exists() or not out.is_relative_to((root/'work').resolve()):
        parser.error('output must be a NEW directory under this repository work/')
    exe = shutil.which('fastboot')
    if not exe:
        raise SystemExit('fastboot unavailable')
    enumeration = subprocess.run([exe,'devices'],capture_output=True,text=True,timeout=12)
    if enumeration.returncode:
        raise SystemExit('fastboot enumeration failed')
    serial = select_serial(enumeration.stdout)
    public, private = out/'public', out/'private'
    public.mkdir(parents=True)
    private.mkdir()
    (private/'devices.txt').write_text(enumeration.stdout+enumeration.stderr,encoding='utf-8',newline='\n')
    records = {}
    for variable in VARIABLES:
        cmd = command_for(exe,serial,variable)
        try:
            result = subprocess.run(cmd,capture_output=True,text=True,timeout=8)
            raw, code = result.stdout+result.stderr, result.returncode
            status = 'OK' if code == 0 else 'COMMAND_ERROR'
        except subprocess.TimeoutExpired:
            raw, code, status = 'HOST_QUERY_TIMEOUT', None, 'TIMEOUT'
        filename = variable.replace(':','-')+'.txt'
        (private/filename).write_text(raw,encoding='utf-8',newline='\n')
        safe = raw.replace(serial,'<REDACTED_TRANSPORT_SERIAL>')
        value = extract_value(variable,safe) if status == 'OK' else None
        if status == 'OK' and not value:
            status = 'VALUE_NOT_CONFIRMED'
        records[variable] = {'command':['fastboot','-s','<PRIVATE_DEVICE>','getvar',variable],
                             'status':status,'exit_code':code,'value':value,'transcript':safe}
        print(variable+': '+(value if value is not None else status+'/VALUE_NOT_CONFIRMED'),flush=True)
        # Stop on a transport timeout instead of queuing more operations to a
        # potentially absent/rebooted device. No automatic recovery commands.
        if status == 'TIMEOUT':
            break
    report = {'schema_version':1,'label':'HOST_TESTED',
              'scope':'PHYSICAL_FASTBOOT_METADATA_ONLY_NO_ATLANTICOS_EXECUTION',
              'timestamp_utc':datetime.now(timezone.utc).isoformat(),
              'device_alias':'g20-'+hashlib.sha256(serial.encode()).hexdigest()[:12],
              'mode_entry_method':'HUMAN_PHYSICAL_ACTION_REQUIRES_USER_OBSERVATION',
              'battery_queried':False,'writes_or_flashing':False,'mode_changed_by_tool':False,
              'variables':records}
    userspace = records.get('is-userspace',{}).get('value')
    report['mode_reported'] = ('USERSPACE_FASTBOOTD' if userspace == 'yes' else
                               'BOOTLOADER' if userspace == 'no' else 'UNCONFIRMED')
    dest = public/'fastboot-intake.json'
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    manifest = {'schema_version':1,'label':'HOST_TESTED','scope':report['scope'],
                'artifacts':[{'path':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}]}
    (public/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('No mode change or storage write requested. Report:',dest)


if __name__ == '__main__':
    main()
