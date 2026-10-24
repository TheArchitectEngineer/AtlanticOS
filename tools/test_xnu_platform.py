"""Compile the original PE/BSP contract and audit genuine target imports.

No PE, SecureDT, BSP callback, interrupt or XNU runtime execution occurs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from test_xnu_brk_scope import read_object, symbol_bytes

ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def strong_external_import(path,name):
    raw=path.read_bytes();cursor=32
    count,size=struct.unpack_from('<II',raw,16)
    symtab=None
    for _ in range(count):
        cmd,width=struct.unpack_from('<II',raw,cursor)
        assert width>=8 and cursor+width<=32+size
        if cmd==2:symtab=struct.unpack_from('<4I',raw,cursor+8)
        cursor+=width
    assert symtab and cursor==32+size
    symoff,nsyms,stroff,strsize=symtab
    assert symoff+16*nsyms<=len(raw) and stroff+strsize<=len(raw)
    strings=raw[stroff:stroff+strsize]
    matches=[]
    for i in range(nsyms):
        at,kind,section,desc,value=struct.unpack_from('<IBBHQ',raw,symoff+16*i)
        assert at<len(strings)
        current=strings[at:strings.index(0,at)].decode()
        if current==name:matches.append((kind,section,desc,value))
    assert len(matches)==1
    kind,section,desc,value=matches[0]
    return kind==1 and section==0 and value==0 and not desc&0x40

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    base=json.loads(args.build.read_text());lock=json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if base['port_id']!=lock['port_id'] or base['failed_units']:ap.error('Use a successful current build')
    for rel,expected in base['inputs'].items():
        if sha(ROOT/rel)!=expected:ap.error('Changed build input: '+rel)
    source=ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
    original={'xnu-port/platform/atlantic.h':'pexpert/pexpert/atlantic.h',
              'xnu-port/platform/pe_platform.c':'pexpert/atlantic/pe_platform.c'}
    for rel,dest in original.items():
        record=next(i for i in lock['canonical_lf_files'] if i['path']==dest)
        if sha(source/dest)!=sha(ROOT/rel) or sha(ROOT/rel)!=record['postimage_sha256'] or record['preimage_sha256'] is not None:
            ap.error('Original platform source differs from its added-file lock')
    command=next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    if command[-4]!='-c':ap.error('Unexpected target recipe')
    target=[s.replace('<ROOT>',str(ROOT)) for s in command[:-4]]
    if base['layout_provider'] and sha(target[0])!=base['layout_provider']['compiler_sha256']:
        ap.error('Changed experimental compiler')
    target+=['-UMACH_KERNEL_PRIVATE','-DPEXPERT_KERNEL_PRIVATE=1']
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():ap.error('Use a new output directory under work/')
    out.mkdir(parents=True)
    commands,outcomes=[],[]
    caller=source/'osfmk/arm64/arm_vm_init.c'
    if 'extern void PE_slide_devicetree(vm_offset_t);' not in caller.read_text():
        ap.error('Native VM caller no longer declares the expected slide ABI')
    outcomes.append({'name':'native-vm-slide-declaration-preserved','passed':True,'caller_sha256':sha(caller)})
    def run(name,cmd,expected=0,diagnostic=None):
        r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=60)
        (out/(name+'.log')).write_text((r.stdout+r.stderr).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        commands.append([s.replace(str(ROOT),'<ROOT>') for s in cmd])
        if r.returncode!=expected or (diagnostic and diagnostic not in r.stderr):raise RuntimeError(name+' failed: '+r.stderr[-2500:])
        outcomes.append({'name':name,'exit_code':r.returncode,'expected':expected,'passed':True,'diagnostic':diagnostic})
        return r.stdout
    fixture=ROOT/'tests/xnu_port/pe_platform_abi.c'
    for name,flags,expected in [('native-and-original-abi',[],0),('reject-irq-callback-abi',['-DATL_TEST_WRONG_IRQ_ABI=1'],1),
                              ('reject-mapping-callback-abi',['-DATL_TEST_WRONG_MAPPING_ABI=1'],1)]:
        run(name,[*target,*flags,'-Werror=incompatible-function-pointer-types','-fsyntax-only',str(fixture)],expected,
            'incompatible function pointer types' if expected else None)
    csource=source/'pexpert/atlantic/pe_platform.c'
    for name,flags,diagnostic in [
        ('reject-outside-firmware',['-UCONFIG_ATLANTIC_FIRMWARE'],'requires the explicit ARM64 firmware profile'),
        ('reject-bsd-backend',['-DMACH_BSD=1'],'has no BSD or IOKit platform backend'),
        ('reject-iokit-backend',['-DIOKIT=1'],'has no BSD or IOKit platform backend')]:
        run(name,[*target,*flags,'-E',str(csource)],1,diagnostic)
    native=next((i for i in base['objects'] if i['source']=='pexpert/atlantic/pe_platform.c'),None)
    if native:
        obj=args.build.parent/native['object']
        if sha(obj)!=native['object_sha256']:ap.error('Changed integrated PE object')
    else:
        obj=out/'pe-platform-probe.o'
        run('standard-pe-compile-probe',[*target,'-c',str(csource),'-o',str(obj)])
    parsed=read_object(obj)
    symbols=parsed[2]
    expected=['_PE_init_platform','_PE_slide_devicetree','_PE_call_timebase_callback',
              '_PE_register_timebase_callback','_PE_state','_gPEClockFrequencyInfo']
    assert set(expected)<=set(symbols)
    assert strong_external_import(obj,'_atlantic_pe_platform')
    outcomes.append({'name':'missing-bsp-remains-a-strong-import','passed':True})
    undefined=run('native-imports',['llvm-nm','--undefined-only',str(obj)])
    assert {'_SecureDTInit','_SecureDTLookupEntry','_SecureDTGetProperty','_panic','_atlantic_pe_platform'}<=set(undefined.split())
    assert not any(name in undefined for name in ['_pe_identify_machine','_pe_arm_init_interrupts','_iokit_'])
    code=symbol_bytes(parsed,'_PE_init_platform')
    assert len(code)%4==0
    words=struct.unpack('<'+'I'*(len(code)//4),code)
    assert any(w&~31==0xd53800a0 for w in words) # MPIDR_EL1
    assert any(w&~31==0xd53be000 for w in words) # CNTFRQ_EL0
    outcomes.append({'name':'actual-target-register-read-encodings','passed':True,'executed':False})
    run('disassembly',['llvm-objdump','--macho','--disassemble',str(obj)])
    report={'schema_version':1,'label':'HOST_TESTED',
        'scope':'ORIGINAL_PE_NATIVE_ABI_SOURCE_SELECTION_AND_OBJECT_IMPORTS_ONLY_NO_PE_OR_XNU_EXECUTION',
        'port_id':base['port_id'],'build_report_sha256':sha(args.build),
        'inputs':{rel:sha(ROOT/rel) for rel in [*original,'tools/test_xnu_platform.py','tools/test_xnu_brk_scope.py',
                                             'tests/xnu_port/pe_platform_abi.c']},
        'object_sha256':sha(obj),'object_selected_in_base':native is not None,
        'native_vm_caller_sha256':sha(caller),
        'bsp_strong_import':'_atlantic_pe_platform','bsp_provider_linked':False,
        'required_native_definitions':expected,'outcomes':outcomes,'commands':commands,
        'pe_executed':False,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':len(outcomes),'pe_object_in_base':native is not None,'bsp_implementation_provided':False}))

if __name__=='__main__':main()
