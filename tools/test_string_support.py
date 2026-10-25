"""Execute original string contracts on host; audit genuine target ABI separately.

No XNU, native Mach-O parser, BSP or phone is executed. The portable functions
have distinct names, so tests do not interpose host libc or ASan interceptors.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
from test_xnu_brk_scope import read_object, symbol_bytes
from test_xnu_memory_providers import imported_name

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL={'atlantic-core/string.c':'osfmk/atlantic/string.c',
          'include/atlantic/string.h':'osfmk/atlantic/string.h',
          'xnu-port/platform/string.c':'osfmk/kern/atlantic_string.c'}
NATIVE={'libkern/kernel_mach_header.c':['getlastkerneladdr','getsegdatafromheader','getsectdatafromheader','getuuidfromheader'],
        'bsd/libkern/strsep.c':['strsep']}
BRANCHES={'_strcmp':'_atl_string_compare','_memcmp':'_atl_memory_compare',
          '_strlcpy':'_atl_string_copy','_strlcat':'_atl_string_append'}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def audit_chain(portable,adapter):
    first=read_object(portable);second=read_object(adapter)
    assert set(BRANCHES.values())<=set(first[2]) and set(BRANCHES)<=set(second[2])
    raw,sections,symbols=second
    text=sections[symbols['_strcmp']['section']-1]
    assert text['relocation_count']==4
    seen={}
    for i in range(text['relocation_count']):
        at=text['relocation_offset']+8*i;assert 0<=at<=len(raw)-8
        address,info=struct.unpack_from('<iI',raw,at)
        assert (info>>24)&1==1 and (info>>25)&3==2 and (info>>27)&1==1 and info>>28==2
        callers=[name for name in BRANCHES if symbols[name]['value']-text['address']==address]
        assert len(callers)==1
        name=callers[0];code=symbol_bytes(second,name)
        assert struct.unpack_from('<I',code)[0]==0x14000000
        assert imported_name(raw,info&0xffffff)==BRANCHES[name] and name not in seen
        seen[name]=BRANCHES[name]
    assert seen==BRANCHES
    return seen

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sanitize',action='store_true')
    ap.add_argument('--xnu-build',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():ap.error('Use a new output directory under work/')
    out.mkdir(parents=True)
    commands,outcomes=[],[]
    def run(name,cmd,expected=0,diagnostic=None,native_check=False):
        result=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=60)
        commands.append([str(s).replace(str(ROOT),'<ROOT>') for s in cmd])
        (out/(name+'.log')).write_text((result.stdout+result.stderr).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        assert result.returncode==expected and (not diagnostic or diagnostic in result.stderr),name+': '+result.stderr[-2500:]
        if native_check:outcomes.append({'name':name,'passed':True,'exit_code':result.returncode,'expected':expected,'diagnostic':diagnostic})
        return result.stdout
    compiler=shutil.which('clang')
    if not compiler:ap.error('clang is required')
    flags=['-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fno-builtin','-I'+str(ROOT/'include')]
    if args.sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
    host=out/'test-string'
    run('host-build',[compiler,*flags,str(ROOT/'atlantic-core/string.c'),str(ROOT/'tests/c/test_string.c'),'-o',str(host)])
    result=run('host-contracts',[str(host)])
    match=re.fullmatch(r'PASS: (\d+) original string contract cases; no kernel or hardware execution\n',result)
    assert match and int(match[1])==79344
    elf=out/'string-arm64.o'
    run('portable-arm64-compile',[compiler,'--target=aarch64-none-elf','-std=c11','-ffreestanding',
        '-fno-builtin','-fno-stack-protector','-O1','-I'+str(ROOT/'include'),'-c',str(ROOT/'atlantic-core/string.c'),'-o',str(elf)])
    raw=elf.read_bytes();assert raw[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',raw,18)[0]==183
    native_audit=None
    inputs=[*ORIGINAL,'tools/test_string_support.py','tests/c/test_string.c',
            'tests/xnu_port/string_support_abi.c','tools/test_xnu_brk_scope.py','tools/test_xnu_memory_providers.py']
    if args.xnu_build:
        base=json.loads(args.xnu_build.read_text());lock=json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
        if base['port_id']!=lock['port_id'] or base['failed_units']:ap.error('Use a successful current XNU build')
        for rel,expected in base['inputs'].items():
            if sha(ROOT/rel)!=expected:ap.error('Changed XNU input: '+rel)
        source=ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
        for rel,destination in ORIGINAL.items():
            item=next(i for i in lock['canonical_lf_files'] if i['path']==destination)
            assert item['preimage_sha256'] is None
            assert sha(ROOT/rel)==sha(source/destination)==item['postimage_sha256']
        recipe=next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
        assert recipe[-4]=='-c';target=[s.replace('<ROOT>',str(ROOT)) for s in recipe[:-4]]
        if base['layout_provider']:assert sha(target[0])==base['layout_provider']['compiler_sha256']
        fixture=ROOT/'tests/xnu_port/string_support_abi.c'
        run('native-abi',[*target,'-fsyntax-only',str(fixture)],native_check=True)
        for name,define in [('reject-copy-capacity','ATL_TEST_WRONG_COPY_ABI'),('reject-macho-size-output','ATL_TEST_WRONG_MACHO_ABI')]:
            run(name,[*target,'-D'+define+'=1','-Werror=incompatible-function-pointer-types','-fsyntax-only',str(fixture)],
                expected=1,diagnostic='incompatible function pointer types',native_check=True)
        objects=[]
        selected=base['layout_provider'] is not None
        for rel in ['osfmk/atlantic/string.c','osfmk/kern/atlantic_string.c']:
            record=next((i for i in base['objects'] if i['source']==rel),None)
            assert (record is not None)==selected
            if record:
                obj=(args.xnu_build.parent/record['object']).resolve()
                assert obj.is_relative_to(args.xnu_build.parent.resolve()) and sha(obj)==record['object_sha256']
            else:
                obj=out/(Path(rel).stem+'-probe.o')
                run('standard-'+Path(rel).stem+'-probe',[*target,'-c',str(source/rel),'-o',str(obj)],native_check=True)
            objects.append(obj)
        chain=audit_chain(*objects)
        portable_imports=run('portable-native-imports',['llvm-nm','--undefined-only',str(objects[0])])
        adapter_imports=run('adapter-native-imports',['llvm-nm','--undefined-only',str(objects[1])])
        assert not portable_imports.strip() and set(adapter_imports.split())==set(BRANCHES.values())
        outcomes.append({'name':'actual-strong-native-entry-chain-to-original-functions','passed':True,'branches':chain})
        native_objects=[]
        for rel,required in NATIVE.items():
            original=hashlib.sha256((ROOT/'xnu-upstream'/rel).read_text().encode()).hexdigest()
            assert sha(source/rel)==original
            outcomes.append({'name':'native-source-unchanged-'+Path(rel).stem,'passed':True,'source_sha256':original})
            record=next((i for i in base['objects'] if i['source']==rel),None)
            assert (record is not None)==selected
            if record:
                obj=(args.xnu_build.parent/record['object']).resolve()
                assert obj.is_relative_to(args.xnu_build.parent.resolve()) and sha(obj)==record['object_sha256']
                parsed=read_object(obj)
                assert all(('_'+symbol) in parsed[2] for symbol in required)
                native_objects.append({'source':rel,'source_sha256':original,'object_sha256':sha(obj)})
        if selected:outcomes.append({'name':'genuine-native-macho-and-tokenizer-selected','passed':True,'objects':native_objects})
        run('reject-provider-outside-firmware',[*target,'-UCONFIG_ATLANTIC_FIRMWARE','-E',
            str(source/'osfmk/kern/atlantic_string.c')],1,'require the explicit ARM64 firmware profile',native_check=True)
        run('native-entry-disassembly',['llvm-objdump','--macho','--disassemble',str(objects[1])])
        native_audit={'build_report_sha256':sha(args.xnu_build),'port_id':base['port_id'],
            'objects_selected_in_base':selected,'object_sha256':[sha(p) for p in objects],
            'native_source_objects':native_objects,'native_macho_parser_executed':False}
    report={'schema_version':1,'label':'HOST_TESTED',
        'scope':'ORIGINAL_STRING_HOST_CONTRACTS_AND_TARGET_ABI_ONLY_NO_XNU_NATIVE_PARSER_OR_PHONE_EXECUTION',
        'inputs':{rel:sha(ROOT/rel) for rel in inputs},'sanitizers':args.sanitize,
        'host_exit_code':0,'host_contract_cases':int(match[1]),'host_original_functions_executed':True,
        'host_executable_sha256':sha(host),'portable_arm64_elf_sha256':sha(elf),
        'native_xnu_abi':native_audit,'outcomes':outcomes,'commands':commands,
        'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'host_cases':int(match[1]),'sanitizers':args.sanitize,'native_checks':len(outcomes),
                      'objects_selected_in_base':None if native_audit is None else native_audit['objects_selected_in_base']}))

if __name__=='__main__':main()
