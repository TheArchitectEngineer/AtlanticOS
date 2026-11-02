"""Audit native CPU/cache providers and upstream empty Apple hooks; no execution."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

from test_xnu_brk_scope import read_object,symbol_bytes,function
from test_xnu_memory_providers import imported_name,words

ROOT=Path(__file__).resolve().parents[1]
SOURCES=['osfmk/arm/cpuid.c','osfmk/arm/machine_routines_apple.c','osfmk/arm/machine_cpuid.c']
HOOKS=['_configure_misc_apple_boot_args','_configure_misc_apple_regs','_configure_timer_apple_regs']
CHAINS={'_do_cpuid':{'_machine_read_midr'},'_do_debugid':{'_machine_do_debugid'},
        '_arm_debug_info':{'_machine_arm_debug_info'},'_do_mvfpid':{'_machine_do_mvfpid'},
        '_arm_mvfp_info':{'_machine_arm_mvfp_info'},
        '_do_cacheid':{'_machine_read_clidr','_machine_write_csselr','_machine_read_ccsidr'},
        '_cache_info_type':{'_assert_wait','_clear_wait','_thread_block'}}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def branches(obj,name):
    raw,sections,symbols=obj
    sym=symbols[name];section=sections[sym['section']-1]
    first=sym['value']-section['address'];end=first+len(symbol_bytes(obj,name))
    defined={s['index']:n for n,s in symbols.items()};edges=set()
    for i in range(section['relocation_count']):
        at=section['relocation_offset']+8*i
        address,info=struct.unpack_from('<iI',raw,at)
        if not first<=address<end or info>>28!=2:continue
        assert (info>>24)&1 and (info>>25)&3==2 and (info>>27)&1
        inst=struct.unpack_from('<I',raw,section['offset']+address)[0]
        assert inst&0x7c000000==0x14000000
        index=info&0xffffff
        edges.add(defined[index] if index in defined else imported_name(raw,index))
    return edges

def audit_backend(obj):
    reads={'_machine_read_midr':0xd5380000,'_machine_read_clidr':0xd5390020,'_machine_read_ccsidr':0xd5390000}
    for name,opcode in reads.items():
        code=words(obj,name)
        assert code[:2]==(opcode,0xd65f03c0) and all(w==0xd503201f for w in code[2:])
    code=words(obj,'_machine_write_csselr')
    matches=[i for i,w in enumerate(code) if w&~31==0xd51a0000]
    assert len(matches)==1 and code[matches[0]+1]==0xd5033fdf
    return {'mrs_registers':['MIDR_EL1','CLIDR_EL1','CCSIDR_EL1'],'csselr_followed_by_isb':True}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();base=json.loads(a.build.read_text());lock=json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    assert not base['failed_units'] and base['port_id']==lock['port_id']
    for rel,h in base['inputs'].items():assert sha(ROOT/rel)==h,'Changed build input: '+rel
    for item in base['config_headers']+base['generated_headers']:
        assert sha(a.build.parent/item['path'])==item['sha256']
    source=ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
    out=a.output.resolve();assert not out.exists() and out.is_relative_to((ROOT/'work').resolve())
    out.mkdir(parents=True);outcomes=[];commands=[];objects={};provenance={}
    def run(name,cmd,expected=0,diagnostic=None,check=True):
        r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=120)
        commands.append([str(s).replace(str(ROOT),'<ROOT>') for s in cmd])
        (out/(name+'.log')).write_text((r.stdout+r.stderr).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        assert r.returncode==expected and (not diagnostic or diagnostic in r.stderr),name+': '+r.stderr[-2500:]
        if check:outcomes.append({'name':name,'passed':True,'exit_code':r.returncode})
        return r.stdout
    for rel in SOURCES:
        h=hashlib.sha256((ROOT/'xnu-upstream'/rel).read_text().encode()).hexdigest()
        assert sha(source/rel)==h
        provenance[rel]=h
    outcomes.append({'name':'three-complete-native-sources-unchanged','passed':True,'hashes':provenance})
    makefile=(a.build.parent/'config/Makefile').read_text().replace('\\\n',' ')
    cfiles=re.findall(r'^CFILES\s*=\s*([^\n]+)',makefile,re.M)
    assert len(cfiles)==1 and all('$(SOURCE_DIR)/'+rel in cfiles[0].split() for rel in SOURCES)
    outcomes.append({'name':'official-generated-cfiles-contains-cpu-and-non-apple-compatibility-units','passed':True})
    recipe=next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c));assert recipe[-4]=='-c'
    target=[s.replace('<ROOT>',str(ROOT)) for s in recipe[:-4]]
    if base['layout_provider']:assert sha(target[0])==base['layout_provider']['compiler_sha256']
    fixture=ROOT/'tests/xnu_port/cpu_cache_abi.c';abi=out/'native-cpu-cache-abi.o'
    run('native-abi',[*target,'-c',str(fixture),'-o',str(abi)])
    parsed=read_object(abi)
    assert struct.unpack('<I',symbol_bytes(parsed,'_atl_native_cpuid_layout',4))[0]==0x412cabc3
    outcomes.append({'name':'synthetic-native-bitfield-layout-not-hardware-identity','passed':True})
    for name,define in [('reject-midr-width','ATL_TEST_WRONG_MIDR_WIDTH'),('reject-cache-pointer','ATL_TEST_WRONG_CACHE_POINTER')]:
        run(name,[*target,'-D'+define+'=1','-Werror=incompatible-function-pointer-types','-fsyntax-only',str(fixture)],
            expected=1,diagnostic='incompatible function pointer types')
    for rel in SOURCES:
        record=next((r for r in base['objects'] if r['source']==rel),None)
        assert (record is not None)==bool(base['layout_provider'])
        if record:
            path=(a.build.parent/record['object']).resolve()
            assert path.is_relative_to(a.build.parent.resolve()) and sha(path)==record['object_sha256']
            assert record['source_sha256']==provenance[rel]
        else:
            path=out/(Path(rel).stem+'-probe.o')
            run('standard-'+Path(rel).stem+'-probe',[*target,'-c',str(source/rel),'-o',str(path)])
        objects[rel]=read_object(path)
        outcomes.append({'name':'native-object-'+Path(rel).stem,'passed':True,'selected':record is not None,'sha256':sha(path)})
    cpu=objects[SOURCES[0]]
    for caller,required in CHAINS.items():
        actual=branches(cpu,caller);assert required<=actual,(caller,actual)
        outcomes.append({'name':'actual-strong-native-chain-'+caller,'passed':True,'required':sorted(required)})
    backend=objects[SOURCES[2]]
    outcomes.append({'name':'actual-native-register-reads-and-selector-barrier','passed':True,**audit_backend(backend)})
    raw,sects,syms=backend
    for name,word in [('_machine_read_midr',0xd65f03c0),('_machine_write_csselr',0xd503201f)]:
        data=bytearray(raw);s=syms[name];section=sects[s['section']-1]
        delta=0 if name=='_machine_read_midr' else 4*(next(i for i,w in enumerate(words(backend,name)) if w&~31==0xd51a0000)+1)
        offset=section['offset']+s['value']-section['address']+delta
        struct.pack_into('<I',data,offset,word)
        changed=(bytes(data),sects,syms)
        try:audit_backend(changed)
        except AssertionError:pass
        else:raise AssertionError('Corrupted native register/barrier accepted')
        outcomes.append({'name':'reject-corrupted-'+name,'passed':True})
    compat=objects[SOURCES[1]]
    for name in HOOKS:
        code=words(compat,name)
        assert code[0]==0xd65f03c0 and all(w==0xd503201f for w in code[1:])
        assert function((source/SOURCES[1]).read_text(),name[1:]).split('{',1)[1].rsplit('}',1)[0].strip() in {'','#pragma unused(is_boot_cpu)'}
    outcomes.append({'name':'three-genuine-empty-upstream-hooks-not-timer-or-platform-drivers','passed':True})
    text=(source/SOURCES[0]).read_text();mvfp=(source/SOURCES[2]).read_text()
    assert 'CPUFAMILY_UNKNOWN' in function(text,'cpuid_get_cpufamily')
    assert 'CPU_ARCH_ARMv8' in function(text,'do_cpuid')
    assert 'os_atomic_load(&ret->c_valid, acquire)' in function(text,'cache_info_type')
    assert 'cpuid_mvfp_info.neon = 1;' in function(mvfp,'machine_do_mvfpid')
    outcomes.append({'name':'native-unknown-family-arch-normalization-validity-wait-and-compiled-neon-assumption-preserved','passed':True})
    inputs=['tools/test_xnu_cpu_cache.py','tests/xnu_port/cpu_cache_abi.c',
            'tools/test_xnu_brk_scope.py','tools/test_xnu_memory_providers.py']
    report={'schema_version':1,'label':'HOST_TESTED',
        'scope':'NATIVE_CPU_CACHE_ABI_AND_OBJECTS_ONLY_NO_REGISTER_IO_OR_XNU_EXECUTION',
        'base_build_report_sha256':sha(a.build),'native_sources':provenance,
        'inputs':{p:sha(ROOT/p) for p in inputs},'commands':commands,'outcomes':outcomes,
        'checks_passed':len(outcomes),'selected_new_units':bool(base['layout_provider']),
        'xnu_executed':False,'cpu_registers_read':False,'cache_geometry_measured':False,
        'phone_accessed':False,'platform_drivers_implemented':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'checks_passed':len(outcomes),'selected':bool(base['layout_provider'])}))
if __name__=='__main__':main()
