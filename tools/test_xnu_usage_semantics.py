"""Compare native usage metadata against a control with identical target ABI.

Only preprocessing and ARM64 IR constants. Does not execute the allocator, UPL,
pageout, pointer authentication, Mach or any firmware.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
METADATA = {'ppnum_summary', 'page_info_summary', 'offset_summary', 'slide_summary', 'lock_ptr_summary'}
ABI = {'ppnum_bytes','ppnum_align','page_info_bytes','page_info_align','page_info_address_offset',
       'upl_bytes','upl_align','upl_page_list_offset','upl_object_offset','slide_bytes',
       'slide_address_offset','slide_offset_offset','lock_ptr_bytes'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    build = json.loads(args.build.read_text())
    lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if build['port_id'] != lock['port_id'] or build['failed_units'] or not build['layout_provider']:
        ap.error('Use a successful current experimental build')
    for rel, sha in build['inputs'].items():
        if digest(ROOT/rel) != sha:
            ap.error('Changed base input: '+rel)
    source = ROOT/'work/xnu-lab-sources'/build['port_id'][:16]
    for item in lock['canonical_lf_files']:
        if digest(source/item['path']) != item['postimage_sha256']:
            ap.error('Changed prepared source: '+item['path'])
    command = next(c for c in build['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    if command[-4] != '-c':
        ap.error('Unexpected native target recipe')
    target = [s.replace('<ROOT>',str(ROOT)) for s in command[:-4]]
    if digest(target[0]) != build['layout_provider']['compiler_sha256']:
        ap.error('Changed experimental compiler')
    out = args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():
        ap.error('Use a new output directory under work/')
    out.mkdir(parents=True)
    fixture = ROOT/'tests/xnu_port/usage_semantics.c'
    outcomes, layouts, commands = [], {}, []

    def run(name, cmd, data=None):
        result = subprocess.run(cmd,input=data,text=True,capture_output=True,timeout=60)
        commands.append([s.replace(str(ROOT),'<ROOT>') for s in cmd])
        (out/(name+'.log')).write_text((result.stdout+result.stderr).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        if result.returncode:
            raise RuntimeError(name+' failed: '+result.stderr[-2000:])
        return result.stdout

    for name, flags, expected in [('native-usage',[],
         {'ppnum_summary':2,'page_info_summary':8,'offset_summary':2,'slide_summary':4,'lock_ptr_summary':8}),
        ('no-usage-control',['-UCONFIG_ATLANTIC_C_LAYOUT','-DCONFIG_ATLANTIC_C_LAYOUT=0'],
         {'ppnum_summary':4,'page_info_summary':4,'offset_summary':4,'slide_summary':4,'lock_ptr_summary':4})]:
        ir = out/(name+'.ll')
        run(name,[*target,*flags,'-S','-emit-llvm',str(fixture),'-o',str(ir)])
        values = {}
        for line in ir.read_text().splitlines():
            if not line.startswith('@atl_usage_'):
                continue
            match = re.fullmatch(r'@atl_usage_(\w+) = .*constant i64 (\d+),.*',line)
            if match is None or match[1] in values:
                raise ValueError('Unexpected native constant: '+line)
            values[match[1]] = int(match[2])
        assert set(values)==ABI|METADATA
        assert {k:values[k] for k in METADATA}==expected, (name,values)
        assert values['ppnum_bytes']==4 and values['page_info_bytes']==8
        layouts[name]=values
        outcomes.append({'name':name,'passed':True,'ir_sha256':digest(ir),'metadata':expected})
    assert {k:layouts['native-usage'][k] for k in ABI}=={k:layouts['no-usage-control'][k] for k in ABI}
    outcomes.append({'name':'native-target-abi-unchanged','passed':True,'constants_compared':len(ABI)})

    rel='bsd/sys/cdefs.h'
    before=(ROOT/'xnu-upstream'/rel).read_text()
    after=(source/rel).read_text()
    def block(text):
        start=text.index('#if defined(KERNEL) && ')
        end=text.index('#endif /* defined(KERNEL) && __has_attribute(xnu_usage_semantics) */',start)
        return text[start:end]+'#endif\n'
    # Source file has multiple KERNEL guards: anchor the exact usage section.
    old_start=before.index('#if defined(KERNEL) && __has_attribute(xnu_usage_semantics)')
    new_start=after.index('#if defined(KERNEL) && CONFIG_ATLANTIC_C_LAYOUT')
    old_block=block(before[old_start:]);new_block=block(after[new_start:])
    for name,kernel,selected in [('kernel-outside-provider',1,0),('outside-kernel',0,0),('outside-kernel-provider-set',0,1)]:
        prefix=('#define KERNEL 1\n' if kernel else '')+'#define CONFIG_ATLANTIC_C_LAYOUT '+str(selected)+'\n'
        outputs=[]
        for role,text in [('upstream',old_block),('adapted',new_block)]:
            outputs.append(run(name+'-'+role,[target[0],'--target=arm64-apple-macos11.0','-E','-dM','-x','c','-'],prefix+text))
        assert outputs[0]==outputs[1], 'Native macros outside provider changed'
        outcomes.append({'name':name,'passed':True,'upstream_byte_identical':True})
    unchanged={}
    for rel in ['osfmk/vm/vm_pageout.c','osfmk/vm/vm_pageout_xnu.h','osfmk/mach/memory_object_types.h']:
        canonical=(ROOT/'xnu-upstream'/rel).read_text().encode()
        assert hashlib.sha256(canonical).hexdigest()==digest(source/rel), 'UPL code or representation changed'
        unchanged[rel]=digest(source/rel)
    report={'schema_version':1,'label':'HOST_TESTED',
        'scope':'REAL_XNU_USAGE_METADATA_AND_UNCHANGED_TARGET_ABI_ONLY_NO_ALLOCATOR_OR_XNU_EXECUTION',
        'port_id':build['port_id'],'build_report_sha256':digest(args.build),'tool_sha256':digest(__file__),
        'fixture_sha256':digest(fixture),'layouts':layouts,'unchanged_native_upl_sources':unchanged,
        'outcomes':outcomes,'commands':commands,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':len(outcomes),'abi_constants_unchanged':len(ABI)}))


if __name__ == '__main__':
    main()
