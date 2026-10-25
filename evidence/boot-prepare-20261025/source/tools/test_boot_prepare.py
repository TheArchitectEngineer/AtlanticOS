"""Verify original candidate boot_args and native block reach; never load XNU."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import struct
import subprocess

from test_xnu_brk_scope import read_object, symbol_bytes

ROOT=Path(__file__).resolve().parents[1]
INPUTS=['include/atlantic/boot_prepare.h','atlantic-core/boot_prepare.c',
        'include/atlantic/boot_tree.h','include/atlantic/macho.h','atlantic-core/macho.c',
        'tests/c/test_boot_prepare.c','tests/xnu_port/boot_prepare_abi.c',
        'tools/test_boot_prepare.py','tools/test_xnu_brk_scope.py']
FIXTURES=ROOT/'evidence/static-image-plan-20261025/lld-fixtures'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--sanitize',action='store_true')
    ap.add_argument('--xnu-build',type=Path)
    a=ap.parse_args();out=a.output.resolve();cc=shutil.which('clang')
    if platform.system()!='Linux' or not cc:ap.error('Use Linux/WSL with Clang')
    if out.exists() or not out.is_relative_to((ROOT/'work').resolve()):ap.error('Use a new work/ output')
    locked=json.loads((FIXTURES/'report.json').read_text())
    for name in ['high.macho','low.macho']:
        assert sha(FIXTURES/name) in {r['file_sha256'] for r in locked['images']}
    out.mkdir(parents=True);commands=[]
    def run(name,cmd):
        r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=60)
        commands.append([str(s).replace(str(ROOT),'<ROOT>') for s in cmd])
        (out/(name+'.log')).write_text((r.stdout+r.stderr).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        if r.returncode:raise RuntimeError(name+' failed: '+r.stderr[-2500:])
        return r.stdout
    flags=['-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-I'+str(ROOT/'include')]
    if a.sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
    exe=out/'host-tests';record=out/'candidate-boot-args.bin'
    run('host-build',[cc,*flags,str(ROOT/'atlantic-core/macho.c'),str(ROOT/'atlantic-core/boot_prepare.c'),
                      str(ROOT/'tests/c/test_boot_prepare.c'),'-o',str(exe)])
    result=run('host-tests',[str(exe),str(FIXTURES/'high.macho'),str(record),str(FIXTURES/'low.macho')])
    stats=json.loads(next(s[5:] for s in result.splitlines() if s.startswith('PASS ')))
    assert stats['mutations']==10000 and stats['directed_rejections']>=28
    blob=record.read_bytes();assert len(blob)==1152
    assert struct.unpack_from('<HH',blob)==(2,2) and not any(blob[40:88])
    assert struct.unpack_from('<Q',blob,96)[0]==0xfffffff00701c000
    obj=out/'boot-prepare-arm64.o'
    run('arm64-build',[cc,'--target=aarch64-none-elf','-mstrict-align','-std=c11','-O2','-ffreestanding','-fno-builtin',
                       '-fno-stack-protector','-Wall','-Wextra','-Werror','-I'+str(ROOT/'include'),
                       '-c',str(ROOT/'atlantic-core/boot_prepare.c'),'-o',str(obj)])
    imports=run('arm64-imports',['llvm-nm','--undefined-only',str(obj)])
    assert imports.split()==['U','atl_macho_plan']
    native=None
    if a.xnu_build:
        base=json.loads(a.xnu_build.read_text());lock=json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
        assert base['port_id']==lock['port_id'] and not base['failed_units']
        for rel,h in base['inputs'].items():assert sha(ROOT/rel)==h,'Changed native input: '+rel
        for item in base['config_headers']+base['generated_headers']:
            assert sha(a.xnu_build.parent/item['path'])==item['sha256']
        recipe=next(c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
        assert recipe[-4]=='-c';target=[s.replace('<ROOT>',str(ROOT)) for s in recipe[:-4]]
        if base['layout_provider']:assert sha(target[0])==base['layout_provider']['compiler_sha256']
        source=ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
        headers=['pexpert/pexpert/arm64/boot.h','osfmk/arm64/proc_reg.h','osfmk/arm/pmap/pmap.h']
        header_audits={}
        for rel in headers:
            original=hashlib.sha256((ROOT/'xnu-upstream'/rel).read_text().encode()).hexdigest()
            prepared=sha(source/rel)
            patch=next((i for i in lock['canonical_lf_files'] if i['path']==rel),None)
            if patch:assert (original,prepared)==(patch['preimage_sha256'],patch['postimage_sha256'])
            else:assert prepared==original
            header_audits[rel]={'upstream_sha256':original,'prepared_sha256':prepared,'patched':patch is not None}
        native_obj=out/'native-boot-abi.o'
        run('native-boot-abi',[*target,'-c',str(ROOT/'tests/xnu_port/boot_prepare_abi.c'),'-o',str(native_obj)])
        parsed=read_object(native_obj)
        actual=symbol_bytes(parsed,'_atl_native_boot_reference',1152)
        assert actual==blob,'Portable wire record differs from real native initializer bytes'
        geometry=list(struct.unpack('<7Q',symbol_bytes(parsed,'_atl_native_boot_geometry',56)))
        assert geometry==[12,4096,21,2097152,32768,0xfffffff007004000,0x22a5192519]
        upstream_start=(ROOT/'xnu-upstream/osfmk/arm64/start.s').read_text()
        prepared_start=(source/'osfmk/arm64/start.s').read_text()
        contracts={}
        for name in ['create_l1_table_entry','create_l2_block_entries','create_bootstrap_mapping']:
            pattern=r'^\.macro[ \t]+'+name+r'\b.*?^\.endmacro'
            original=re.search(pattern,upstream_start,re.M|re.S).group()
            current=re.search(pattern,prepared_start,re.M|re.S).group()
            assert original==current
            contracts[name]=hashlib.sha256(current.encode()).hexdigest()
        for name,pattern in [
            ('cold_mapping_extent',r'^Lkernelcache_base_found:.*?\n[ \t]+b[ \t]+common_start'),
            ('boot_args_kva',r'// Set KVA of boot args as first arg\n[^\n]+\n[^\n]+'),
        ]:
            original=re.search(pattern,upstream_start,re.M|re.S).group()
            current=re.search(pattern,prepared_start,re.M|re.S).group()
            assert original==current
            contracts[name]=hashlib.sha256(current.encode()).hexdigest()
        for name,rel,fragment in [
            ('native_args_copy','osfmk/arm/arm_init.c','const_boot_args = *args;\n\tBootArgs = args = &const_boot_args;'),
            ('native_prefix_reclaim','osfmk/arm64/arm_vm_init.c','ml_static_mfree(phystokv(gPhysBase), segLOWEST - gVirtBase);'),
        ]:
            assert fragment in (ROOT/'xnu-upstream'/rel).read_text() and fragment in (source/rel).read_text()
            contracts[name]=hashlib.sha256(fragment.encode()).hexdigest()
        native={'build_report_sha256':sha(a.xnu_build),'object_sha256':sha(native_obj),
                'headers':header_audits,'geometry':geometry,
                'native_algorithm_fragments_unchanged':contracts,
                'all_1152_bytes_match_native_initializer':True,'xnu_executed':False}
    report={'schema_version':1,'label':'HOST_TESTED',
        'scope':'ORIGINAL_CANDIDATE_BOOT_ARGS_AND_BLOCK_REACH_ONLY_NO_OWNERSHIP_OR_LOADING_OR_XNU_EXECUTION',
        'inputs':{p:sha(ROOT/p) for p in INPUTS},'fixture_sha256':{p:sha(FIXTURES/p) for p in ['high.macho','low.macho']},
        'commands':commands,'sanitizers':a.sanitize,'host_contracts':stats,'native_abi':native,
        'record_sha256':sha(record),'arm64_object_sha256':sha(obj),
        'record_is_candidate':True,'retained_context_constructed':False,'image_loaded':False,
        'memory_owned':False,'mmu_enabled':False,'xnu_executed':False,'phone_accessed':False,
        'physical_memory_measured':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'host_passed':True,**stats,'native_abi':native is not None}))
if __name__=='__main__':main()
