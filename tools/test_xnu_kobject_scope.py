"""Check native MIG table feature selection as preprocessing, not execution."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def table(text):
    matches = re.findall(r'static struct mig_kern_subsystem \*mig_e\[\] = \{(.*?)^\};', text, re.M|re.S)
    if len(matches) != 1:
        raise ValueError('Expected the actual native mig_e table')
    return 'static struct mig_kern_subsystem *mig_e[] = {'+matches[0]+'};\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    base = json.loads(args.build.read_text())
    lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if base['port_id'] != lock['port_id'] or base['failed_units']:
        ap.error('Use a successful current build')
    for name, expected in base['inputs'].items():
        if digest(ROOT/name) != expected:
            ap.error('Changed base input: '+name)
    rel = 'osfmk/kern/ipc_kobject.c'
    source = ROOT/'work/xnu-lab-sources'/lock['port_id'][:16]/rel
    original = ROOT/'xnu-upstream'/rel
    record = next(i for i in lock['canonical_lf_files'] if i['path']==rel)
    before_text, after_text = original.read_text(), source.read_text()
    if (hashlib.sha256(before_text.encode()).hexdigest() != record['preimage_sha256'] or
        digest(source) != record['postimage_sha256']):
        ap.error('Native source pre/postimage mismatch')
    before, after = table(before_text), table(after_text)
    compiler = next(c[0].replace('<ROOT>',str(ROOT)) for c in base['commands']
                    if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    out = args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():
        ap.error('Use a new output folder under work/')
    out.mkdir(parents=True)
    cases, commands = [], []
    for name, fw, bsd, iokit, count in [('outside-firmware',0,0,0,17),
        ('firmware-all-providers',1,1,1,17), ('firmware-minimal',1,0,0,14),
        ('firmware-bsd',1,1,0,16), ('firmware-iokit',1,0,1,15)]:
        prefix = ('#define VM32_SUPPORT 1\n#define CONFIG_USER_NOTIFICATION 0\n#define CONFIG_ARCADE 0\n'
                  '#define CONFIG_ATLANTIC_FIRMWARE '+str(fw)+'\n#define MACH_BSD '+str(bsd)+
                  '\n#define IOKIT '+str(iokit)+'\n')
        outputs = []
        for role, text in [('upstream',before), ('adapted',after)]:
            cmd = [compiler,'--target=arm64-apple-macos11','-E','-P','-x','c','-']
            result = subprocess.run(cmd,input=prefix+text,text=True,capture_output=True,timeout=30)
            (out/(name+'-'+role+'.log')).write_text(result.stderr)
            if result.returncode:
                raise RuntimeError('Native table preprocessing failed: '+result.stderr)
            outputs.append(result.stdout)
            commands.append(cmd)
        symbols = re.findall(r'&(\w+_subsystem)\b', outputs[1])
        assert len(symbols) == count and len(set(symbols)) == count
        assert ('catch_exc_subsystem' in symbols) == (not fw or bool(bsd))
        assert ('catch_mach_exc_subsystem' in symbols) == (not fw or bool(bsd))
        assert ('is_iokit_subsystem' in symbols) == (not fw or bool(iokit))
        unchanged = fw == 0 or (bsd == iokit == 1)
        if unchanged:
            assert outputs[0] == outputs[1], 'Unselected scope must remain byte-identical'
        cases.append({'name':name,'passed':True,'descriptor_count':count,'descriptors':symbols,
                      'upstream_byte_identical_required':unchanged,
                      'upstream_sha256':hashlib.sha256(outputs[0].encode()).hexdigest(),
                      'adapted_sha256':hashlib.sha256(outputs[1].encode()).hexdigest()})
    report = {'schema_version':1,'label':'HOST_TESTED',
        'scope':'NATIVE_KOBJECT_TABLE_PREPROCESSOR_SELECTION_ONLY_NOT_DISPATCH_OR_EXECUTION',
        'port_id':base['port_id'],'build_report_sha256':digest(args.build),
        'tool_sha256':digest(__file__),'upstream_source_sha256':record['preimage_sha256'],
        'adapted_source_sha256':record['postimage_sha256'],
        'cases':cases,'commands':commands,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'passed':len(cases),'scope':report['scope']}))


if __name__ == '__main__':
    main()
