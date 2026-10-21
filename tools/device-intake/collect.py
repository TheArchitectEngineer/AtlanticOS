"""Read-only Moto G20 intake. No reboot, root, writes, battery checks or boot images.

Only the enumerated commands below can reach ADB. Public reports redact the
transport serial; original stdout/stderr remain under the ignored work directory.
An intake record observes Android with an OEM build fingerprint. It does not
verify stock image integrity or DEVICE_VERIFIED AtlanticOS firmware.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

PROPERTIES = (
    'ro.product.manufacturer', 'ro.product.model', 'ro.product.device',
    'ro.product.board', 'ro.product.vendor.model', 'ro.hardware',
    'ro.soc.manufacturer', 'ro.soc.model', 'ro.build.fingerprint',
    'ro.build.id', 'ro.build.version.incremental', 'ro.build.version.release',
    'ro.build.version.sdk', 'ro.build.version.security_patch', 'ro.bootloader',
    'ro.boot.bootloader', 'ro.boot.hardware', 'ro.boot.hardware.sku',
    'ro.boot.flash.locked', 'ro.boot.vbmeta.device_state',
    'ro.boot.verifiedbootstate', 'ro.boot.veritymode', 'ro.boot.slot_suffix',
    'ro.boot.slot', 'ro.build.ab_update', 'ro.virtual_ab.enabled',
    'ro.boot.bootreason', 'ro.bootmode', 'sys.boot_completed',
    'ro.product.cpu.abilist', 'ro.product.cpu.abilist64',
)
SHELL_COMMANDS = {
    **{'prop-'+p: ('getprop', p) for p in PROPERTIES},
    'identity': ('id',),
    'kernel-release': ('cat', '/proc/sys/kernel/osrelease'),
    'kernel-version': ('cat', '/proc/version'),
    'memory-info': ('cat', '/proc/meminfo'),
    'cpu-present': ('cat', '/sys/devices/system/cpu/present'),
    'partition-names': ('ls', '-l', '/dev/block/by-name'),
    'dt-property-names': ('ls', '/sys/firmware/devicetree/base'),
    'dt-model': ('cat', '/sys/firmware/devicetree/base/model'),
    'dt-compatible': ('cat', '/sys/firmware/devicetree/base/compatible'),
}


def parse_devices(stdout):
    result = []
    for line in stdout.splitlines():
        fields = line.split()
        if not fields or line.startswith(('List of devices', '*')):
            continue
        if len(fields) < 2:
            raise ValueError('Unrecognized device enumeration')
        result.append((fields[0], fields[1]))
    return result


def select_device(devices, requested=None):
    if requested:
        matches = [(s, state) for s, state in devices if s == requested]
        if len(matches) != 1 or matches[0][1] != 'device':
            raise ValueError('Requested transport is not uniquely authorized')
        return matches[0][0]
    if len(devices) != 1 or devices[0][1] != 'device':
        raise ValueError('Exactly one authorized ADB device is required; no implicit multi-device selection')
    return devices[0][0]


def command_for(adb, serial, name):
    if name not in SHELL_COMMANDS:
        raise ValueError('Command is outside the read-only intake allowlist')
    return [adb, '-s', serial, 'shell', *SHELL_COMMANDS[name]]


def redact(value, serial):
    return value.replace(serial, '<REDACTED_TRANSPORT_SERIAL>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='new directory under ignored work/')
    parser.add_argument('--serial', help='optional explicit ADB transport; never written to public report')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    output = args.output.resolve()
    if not output.is_relative_to((root/'work').resolve()) or output.exists():
        parser.error('output must be a NEW directory under this repository work/')
    adb = shutil.which('adb')
    if not adb:
        raise SystemExit('ADB is unavailable')
    enum = subprocess.run([adb,'devices'], capture_output=True, text=True, timeout=12)
    if enum.returncode:
        raise SystemExit('ADB enumeration failed')
    serial = select_device(parse_devices(enum.stdout), args.serial)
    public, private = output/'public', output/'private'
    public.mkdir(parents=True)
    private.mkdir()
    (private/'adb-devices.txt').write_text(enum.stdout+enum.stderr, encoding='utf-8', newline='\n')
    records = {}
    for name in SHELL_COMMANDS:
        try:
            r = subprocess.run(command_for(adb,serial,name),capture_output=True,timeout=12)
            stdout, stderr = r.stdout, r.stderr
            status, code = ('OK' if r.returncode == 0 else 'COMMAND_ERROR'), r.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, stderr = exc.stdout or b'', exc.stderr or b''
            status, code = 'TIMEOUT', None
        (private/(name+'.stdout.bin')).write_bytes(stdout)
        (private/(name+'.stderr.bin')).write_bytes(stderr)
        value = redact(stdout.decode('utf-8',errors='replace').strip().replace('\x00',' | '),serial)
        error = redact(stderr.decode('utf-8',errors='replace').strip(),serial)
        if status == 'OK' and not value:
            status = 'EMPTY_NOT_CONFIRMED'
        records[name] = {'command':['adb','-s','<PRIVATE_DEVICE>','shell',*SHELL_COMMANDS[name]],
                         'status':status,'exit_code':code,'value':value,'stderr':error,
                         'raw_stdout_sha256':hashlib.sha256(stdout).hexdigest()}
    report = {
        'schema_version':1,'label':'HOST_TESTED',
        'scope':'READ_ONLY_ADB_OBSERVATIONS_OF_OEM_BUILD_ANDROID_NOT_IMAGE_INTEGRITY_OR_ATLANTICOS_EXECUTION',
        'observation_method':'AUTHORIZED_ADB_USB',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'device_alias':'g20-'+hashlib.sha256(serial.encode()).hexdigest()[:12],
        'battery_is_acceptance_gate':False,'battery_queried':False,
        'device_rebooted':False,'root_requested':False,'partition_data_read':False,
        'writes_or_flashing':False,'atlantic_firmware_executed':False,
        'queries':records,
    }
    target = public/'adb-intake.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    manifest = {'schema_version':1,'label':'HOST_TESTED','scope':report['scope'],
                'artifacts':[{'path':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}]}
    (public/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'public_report':str(target),'device_alias':report['device_alias'],
                      'queries':len(records),'non_ok':{k:v['status'] for k,v in records.items() if v['status']!='OK'}},indent=2))
    for key in ('ro.product.model','ro.build.fingerprint','ro.boot.flash.locked',
                'ro.boot.vbmeta.device_state','ro.boot.verifiedbootstate','ro.boot.slot_suffix',
                'ro.build.ab_update','sys.boot_completed'):
        print(key+': '+records['prop-'+key]['value'])


if __name__ == '__main__':
    main()
