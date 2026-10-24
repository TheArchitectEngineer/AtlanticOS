"""Audit selected genuine memory providers and the original cache adapter.

Native source provenance, target ABI, relocations and ARM64 instruction bytes
only. No cache operation, physical access, pmap, pager or XNU is executed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from test_xnu_brk_scope import function, read_object, symbol_bytes

ROOT=Path(__file__).resolve().parents[1]
NATIVE={
    'osfmk/arm/caches.c':'_cache_sync_page',
    'osfmk/arm64/caches_asm.s':'_CleanPoC_DcacheRegion_Force',
    'osfmk/arm64/loose_ends.c':'_bcopy_phys',
    'osfmk/arm/pmap/pmap_ppl_interface.c':'_mapping_free_prime',
    'osfmk/arm64/machine_task.c':'_machine_task_get_state',
    'libkern/gen/OSAtomicOperations.c':'_OSCompareAndSwap64',
    'osfmk/vm/memory_object.c':'_memory_object_lock_request'}
ADAPTER='osfmk/arm64/atlantic_cache_asm.s'
ALIAS='_CleanPoC_DcacheRegion_Force_nopreempt_nohid'
FORCE='_CleanPoC_DcacheRegion_Force'
GUARDED='osfmk/arm64/loose_ends.c'
CALLOUT_GUARD='#if !MACH_KDP\nvoid\nkdp_register_callout'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def words(obj,name):
    code=symbol_bytes(obj,name)
    assert code and len(code)%4==0
    return struct.unpack('<'+'I'*(len(code)//4),code)

def imported_name(raw,index):
    count,size=struct.unpack_from('<II',raw,16)
    cursor=32
    for _ in range(count):
        cmd,width=struct.unpack_from('<II',raw,cursor)
        assert width>=8 and cursor+width<=32+size
        if cmd==2:
            symoff,nsyms,stroff,strsize=struct.unpack_from('<4I',raw,cursor+8)
            assert index<nsyms and symoff+16*nsyms<=len(raw) and stroff+strsize<=len(raw)
            start,kind,section,desc,value=struct.unpack_from('<IBBHQ',raw,symoff+16*index)
            assert kind==1 and section==0 and value==0 and not desc&0x40
            strings=raw[stroff:stroff+strsize]
            assert start<len(strings)
            return strings[start:strings.index(0,start)].decode()
        cursor+=width
    raise AssertionError('Missing symbol table')

def audit_adapter(obj):
    raw,sections,symbols=obj
    second='_CleanPoC_DcacheRegion_Force_nopreempt'
    assert symbols[ALIAS]['value']==symbols[second]['value']
    assert symbols[ALIAS]['type']==symbols[second]['type']==0x0f
    assert words(obj,ALIAS)==(0x14000000,), 'Need a tail branch, never RET/NOP/BL'
    section=sections[symbols[ALIAS]['section']-1]
    assert section['relocation_count']==1
    at=section['relocation_offset']
    assert 0<=at<=len(raw)-8
    address,info=struct.unpack_from('<iI',raw,at)
    assert address==symbols[ALIAS]['value']-section['address']
    assert (info>>24)&1==1 and (info>>25)&3==2 and (info>>27)&1==1 and info>>28==2
    assert imported_name(raw,info&0xffffff)==FORCE
    return {'relocation':'ARM64_RELOC_BRANCH26','target':FORCE,'tail_branch':True}

def audit_cache(obj):
    force=words(obj,FORCE)
    assert len(force)==1 and force[0]&0xfc000000==0x14000000
    delta=force[0]&0x3ffffff
    if delta&0x2000000:delta-=0x4000000
    target=obj[2][FORCE]['value']+4*delta
    assert target==obj[2]['_CleanPoC_DcacheRegion_internal']['value']
    clean=words(obj,'_CleanPoC_DcacheRegion_internal')
    assert clean[0]==0xd5033f9f and clean[-2:]==(0xd5033f9f,0xd65f03c0)
    assert 0xd50b7a20 in clean, 'Missing native DC CVAC'
    pou=words(obj,'_CleanPoU_DcacheRegion')
    assert any(w&~31==0xd50b7b20 for w in pou), 'Missing native DC CVAU'
    instruction=words(obj,'_InvalidatePoU_IcacheRegion')
    assert any(w&~31==0xd50b7520 for w in instruction), 'Missing native IC IVAU'
    assert 0xd5033f9f in instruction and 0xd5033fdf in instruction
    return {'native_force_branch_target':hex(target),'dc_cvac':True,'dc_cvau':True,
            'ic_ivau':True,'dsb_sy':True,'isb_sy':True,'executed':False}

def changed_word(obj,name,offset,value):
    raw,sections,symbols=obj
    symbol=symbols[name];section=sections[symbol['section']-1]
    at=section['offset']+symbol['value']-section['address']+offset
    assert 0<=at<=len(raw)-4
    copy=bytearray(raw);struct.pack_into('<I',copy,at,value)
    return bytes(copy),sections,symbols

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    base=json.loads(args.build.read_text());lock=json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if base['port_id']!=lock['port_id'] or base['failed_units'] or not base['layout_provider']:
        ap.error('Use a successful current experimental build')
    for rel,expected in base['inputs'].items():
        if sha(ROOT/rel)!=expected:ap.error('Changed build input: '+rel)
    source=ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():ap.error('Use a new output directory under work/')
    out.mkdir(parents=True)
    outcomes,commands,objects=[],[],{}
    for rel,symbol in {**NATIVE,ADAPTER:ALIAS}.items():
        record=next(o for o in base['objects'] if o['source']==rel)
        path=(args.build.parent/record['object']).resolve()
        assert path.is_relative_to(args.build.parent.resolve()) and sha(path)==record['object_sha256']
        assert sha(source/rel)==record['source_sha256']
        if rel in NATIVE:
            # Git checks out upstream as CRLF on this Windows workspace. The
            # builder already requires its pinned HEAD and pristine status.
            before=(ROOT/'xnu-upstream'/rel).read_text()
            upstream=hashlib.sha256(before.encode()).hexdigest()
            if rel==GUARDED:
                item=next(r for r in lock['canonical_lf_files'] if r['path']==rel)
                assert item['preimage_sha256']==upstream and item['postimage_sha256']==record['source_sha256']
                assert before.count(CALLOUT_GUARD)==1
                assert before.replace(CALLOUT_GUARD,CALLOUT_GUARD.replace('!MACH_KDP','!MACH_KDP && !CONFIG_ATLANTIC_FIRMWARE'))==(source/rel).read_text()
            else:assert upstream==record['source_sha256'], 'Native provider source changed: '+rel
            outcomes.append({'name':('guarded-' if rel==GUARDED else '')+'native-source-and-object-'+Path(rel).stem,'passed':True,
                             'source':rel,'source_sha256':record['source_sha256'],
                             'upstream_source_sha256':upstream,'guarded_empty_fallback':rel==GUARDED,'object_sha256':sha(path)})
        else:
            item=next(r for r in lock['canonical_lf_files'] if r['path']==rel)
            assert item['preimage_sha256'] is None
            assert sha(source/rel)==sha(ROOT/'xnu-port/platform/cache_asm.s')==item['postimage_sha256']
            outcomes.append({'name':'original-adapter-locked-mirror','passed':True,'object_sha256':sha(path)})
        objects[rel]=read_object(path)
        assert symbol in objects[rel][2]
    def run(name,cmd,expected=0,diagnostic=None,data=None,record=True):
        result=subprocess.run(cmd,input=data,cwd=ROOT,text=True,capture_output=True,timeout=60)
        commands.append([s.replace(str(ROOT),'<ROOT>') for s in cmd])
        (out/(name+'.log')).write_text((result.stdout+result.stderr).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        assert result.returncode==expected and (not diagnostic or diagnostic in result.stderr), name+': '+result.stderr[-2000:]
        if record:outcomes.append({'name':name,'passed':True,'exit_code':result.returncode,'expected':expected,'diagnostic':diagnostic})
        return result.stdout
    command=next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    assert command[-4]=='-c'
    target=[s.replace('<ROOT>',str(ROOT)) for s in command[:-4]]
    assert sha(target[0])==base['layout_provider']['compiler_sha256']
    import re
    versions=[(ROOT/'xnu-upstream'/GUARDED).read_text(),(source/GUARDED).read_text()]
    fragments=[re.search(r'^#if !MACH_KDP[^\n]*\nvoid\nkdp_register_callout\(.*?^#endif',v,re.M|re.S)[0]+'\n' for v in versions]
    for name,fw,kdp in [('outside-firmware-no-kdp',0,0),('firmware-no-kdp',1,0),
                        ('outside-firmware-kdp',0,1),('firmware-kdp',1,1)]:
        prefix=f'#define CONFIG_ATLANTIC_FIRMWARE {fw}\n#define MACH_KDP {kdp}\n'
        outputs=[run(name+'-'+role,[target[0],'-E','-P','-x','c','-'],data=prefix+text,record=False)
                 for role,text in zip(['upstream','adapted'],fragments)]
        present='kdp_register_callout(' in outputs[1]
        assert present==(not fw and not kdp)
        if not fw or kdp:assert outputs[0]==outputs[1]
        outcomes.append({'name':name,'passed':True,'empty_fallback_present':present,
                         'upstream_byte_identical_required':not fw or bool(kdp)})
    debug='osfmk/kern/debug.c'
    assert function((ROOT/'xnu-upstream'/debug).read_text(),'kdp_register_callout')==function((source/debug).read_text(),'kdp_register_callout')
    registry=next(o for o in base['objects'] if o['source']==debug)
    registry_path=args.build.parent/registry['object']
    assert sha(registry_path)==registry['object_sha256']
    assert len(symbol_bytes(read_object(registry_path),'_kdp_register_callout'))>32
    assert '_kdp_register_callout' not in objects[GUARDED][2]
    outcomes.append({'name':'actual-native-debug-registry-retained-without-empty-duplicate','passed':True,
                     'registry_object_sha256':sha(registry_path),'executed':False})
    fixture=ROOT/'tests/xnu_port/memory_provider_abi.c'
    run('native-call-abi',[*target,'-fsyntax-only',str(fixture)])
    run('reject-truncated-native-range',[*target,'-DATL_TEST_TRUNCATED_RANGE=1',
        '-Werror=incompatible-function-pointer-types','-fsyntax-only',str(fixture)],1,'incompatible function pointer types')
    for name,flags,diagnostic in [
        ('reject-outside-firmware',['-UCONFIG_ATLANTIC_FIRMWARE'],'requires the explicit ARM64 firmware profile'),
        ('reject-apple-provider',['-DAPPLE_ARM64_ARCH_FAMILY=1'],'requires the generic non-Apple cache provider'),
        ('reject-vmapple-provider',['-DVMAPPLE=1'],'requires the generic non-Apple cache provider')]:
        run(name,[*target,*flags,'-DASSEMBLER','-D__ASSEMBLER__','-x','assembler-with-cpp','-E',str(source/ADAPTER)],1,diagnostic)
    adapter=audit_adapter(objects[ADAPTER])
    cache=audit_cache(objects['osfmk/arm64/caches_asm.s'])
    outcomes.extend([{'name':'actual-adapter-branch-relocation','passed':True,**adapter},
                     {'name':'actual-native-cache-instructions','passed':True,**cache}])
    for name,obj,symbol,value,audit in [
        ('reject-return-only-adapter',objects[ADAPTER],ALIAS,0xd65f03c0,audit_adapter),
        ('reject-missing-first-cache-barrier',objects['osfmk/arm64/caches_asm.s'],
         '_CleanPoC_DcacheRegion_internal',0xd503201f,audit_cache)]:
        try:audit(changed_word(obj,symbol,0,value))
        except AssertionError:pass
        else:raise AssertionError('Failed to reject mutated target instruction: '+name)
        outcomes.append({'name':name,'passed':True,'modified_only_in_memory':True})
    atomics=words(objects['libkern/gen/OSAtomicOperations.c'],'_OSCompareAndSwap64')
    assert any(w&0xfffffc00==0xc85ffc00 for w in atomics)
    assert any(w&0xffe0fc00==0xc800fc00 for w in atomics) and 0xd5033f5f in atomics
    outcomes.append({'name':'actual-native-cas-acquire-release-exclusive-loop','passed':True,'executed':False})
    pager=words(objects['osfmk/vm/memory_object.c'],'_memory_object_data_request')
    assert any(w&0xfffffc1f==0xd61f0000 for w in pager)
    outcomes.append({'name':'native-pager-ops-indirect-dispatch-retained','passed':True,'executed':False})
    for rel,symbol in [('osfmk/arm64/caches_asm.s','_CleanPoC_DcacheRegion_internal'),
                       ('libkern/gen/OSAtomicOperations.c','_OSCompareAndSwap64'),
                       ('osfmk/vm/memory_object.c','_memory_object_data_request')]:
        record=next(o for o in base['objects'] if o['source']==rel)
        run('disassembly-'+Path(rel).stem,['llvm-objdump','--macho','--disassemble','--dis-symname',symbol,str(args.build.parent/record['object'])])
    report={'schema_version':1,'label':'HOST_TESTED',
        'scope':'NATIVE_MEMORY_SOURCE_ABI_AND_TARGET_INSTRUCTIONS_ONLY_NO_CACHE_PMAP_PAGER_OR_XNU_EXECUTION',
        'port_id':base['port_id'],'build_report_sha256':sha(args.build),
        'inputs':{rel:sha(ROOT/rel) for rel in ['tools/test_xnu_memory_providers.py','tools/test_xnu_brk_scope.py',
            'tests/xnu_port/memory_provider_abi.c','xnu-port/platform/cache_asm.s']},
        'native_units_unchanged':len(NATIVE)-1,'native_units_guarded':1,'original_cache_adapter_units':1,
        'outcomes':outcomes,'commands':commands,'cache_executed':False,'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':len(outcomes),'native_units_unchanged':len(NATIVE)-1,'native_units_guarded':1,'cache_executed':False}))

if __name__=='__main__':main()
