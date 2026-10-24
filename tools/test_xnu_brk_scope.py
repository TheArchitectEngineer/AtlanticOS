"""Audit native exception selection and emitted ARM64 BRK fixture instructions.

Preprocessing, target objects and IR only. No exception, assert, interrupt,
telemetry collection, kernel or phone execution is performed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'_atl_builtin_trap':1,'_atl_debug_trap':0xf000,'_atl_reserved_trap_25':0x5519,
          '_atl_native_assert':0xbffc,'_atl_native_assert_values':0xbffc}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_object(path):
    """Read only the bounded native Mach-O object sections/symbols we audit."""
    raw=path.read_bytes()
    magic,cpu,sub,kind,count,size,flags,reserved=struct.unpack_from('<8I',raw)
    assert (magic,cpu,sub,kind,reserved)==(0xfeedfacf,0x100000c,0,1,0)
    assert 0<count<64 and 32+size<=len(raw)
    sections,symbols,symtab=[],{},None
    cursor=32
    for _ in range(count):
        cmd,width=struct.unpack_from('<II',raw,cursor)
        assert width>=8 and width%8==0 and cursor+width<=32+size
        if cmd==0x19:
            nsects=struct.unpack_from('<I',raw,cursor+64)[0]
            assert width==72+80*nsects
            for i in range(nsects):
                name,seg,addr,length,off,align,reloff,nreloc,sflags,r1,r2,r3=struct.unpack_from('<16s16s2Q8I',raw,cursor+72+80*i)
                sections.append({'name':name.rstrip(b'\0').decode(),'segment':seg.rstrip(b'\0').decode(),
                    'address':addr,'size':length,'offset':off,'flags':sflags,
                    'relocation_offset':reloff,'relocation_count':nreloc})
        elif cmd==2:
            assert symtab is None
            symtab=struct.unpack_from('<4I',raw,cursor+8)
        cursor+=width
    assert cursor==32+size and symtab is not None
    symoff,nsyms,stroff,strsize=symtab
    assert symoff+16*nsyms<=len(raw) and stroff+strsize<=len(raw)
    strings=raw[stroff:stroff+strsize]
    for i in range(nsyms):
        nameoff,stype,section,desc,value=struct.unpack_from('<IBBHQ',raw,symoff+16*i)
        assert nameoff<len(strings)
        if stype&0xe0 or stype&0xe!=0xe:
            continue
        assert 0<section<=len(sections)
        name=strings[nameoff:strings.index(0,nameoff)].decode()
        assert name not in symbols
        symbols[name]={'section':section,'value':value,'type':stype,'index':i}
    return raw,sections,symbols


def symbol_bytes(obj,name,width=None):
    raw,sections,symbols=obj
    symbol=symbols[name];section=sections[symbol['section']-1]
    assert section['flags']&0xff not in {1,12,18}, 'Need file-backed object bytes'
    start=symbol['value'];delta=start-section['address']
    if width is None:
        end=min([s['value'] for s in symbols.values() if s['section']==symbol['section'] and s['value']>start]
                +[section['address']+section['size']])
        width=end-start
    assert 0<=delta<=section['size'] and width<=section['size']-delta
    offset=section['offset']+delta
    assert 0<=offset<=len(raw) and width<=len(raw)-offset
    return raw[offset:offset+width]


def audit_brks(obj,names):
    result={}
    for name in names:
        expected=EXPECTED[name]
        code=symbol_bytes(obj,name)
        assert code and len(code)%4==0
        words=struct.unpack('<'+'I'*(len(code)//4),code)
        comments=[(w>>5)&0xffff for w in words if w&0xffe0001f==0xd4200000]
        if comments!=[expected]:
            raise ValueError('BRK comment mismatch for '+name+': '+repr(comments))
        result[name]={'comment':hex(expected),'instruction_word':hex(0xd4200000|(expected<<5))}
    return result


def function(text,name):
    match=re.search(r'^'+re.escape(name)+r'\(.*?^\}',text,re.M|re.S)
    if not match:
        raise ValueError('Expected native function '+name)
    return match[0]+'\n'


def scope_fragments(text):
    guard=re.search(r'^#if [^\n]+\n#define HAS_TELEMETRY_KERNEL_BRK 1\n#endif',text,re.M)
    assert guard is not None
    start=text.index('#if __has_feature(ptrauth_calls)\nKERNEL_BRK_DESCRIPTOR_DEFINE(ptrauth_desc,')
    end=text.index('static void\n#if !HAS_TELEMETRY_KERNEL_BRK',start)
    test=re.search(r'^#if MACH_ASSERT[^\n]*\nstatic int trap_handled;.*?^#endif',text,re.M|re.S)
    assert test is not None
    return guard[0]+'\n'+text[start:end]+function(text,'handle_kernel_breakpoint')+test[0]+'\n'


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    build=json.loads(args.build.read_text())
    lock=json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if build['port_id']!=lock['port_id'] or build['failed_units']:
        ap.error('Use a successful current build')
    for rel,sha in build['inputs'].items():
        if digest(ROOT/rel)!=sha:
            ap.error('Changed base input: '+rel)
    source=ROOT/'work/xnu-lab-sources'/build['port_id'][:16]
    rel='osfmk/arm64/sleh.c'
    entry=next(i for i in lock['canonical_lf_files'] if i['path']==rel)
    before=(ROOT/'xnu-upstream'/rel).read_text();after=(source/rel).read_text()
    if hashlib.sha256(before.encode()).hexdigest()!=entry['preimage_sha256'] or digest(source/rel)!=entry['postimage_sha256']:
        ap.error('Native SLEH pre/postimage mismatch')
    native_headers={}
    for header in ['osfmk/kern/trap_telemetry.h','osfmk/kern/assert.h','osfmk/machine/trap.h','osfmk/arm/trap.h']:
        if hashlib.sha256((ROOT/'xnu-upstream'/header).read_text().encode()).hexdigest()!=digest(source/header):
            ap.error('Native trap definitions changed: '+header)
        native_headers[header]=digest(source/header)
    command=next(c for c in build['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c))
    if command[-4]!='-c':
        ap.error('Unexpected target recipe')
    target=[s.replace('<ROOT>',str(ROOT)) for s in command[:-4]]
    if build['layout_provider'] and digest(target[0])!=build['layout_provider']['compiler_sha256']:
        ap.error('Changed experimental compiler')
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'work').resolve()) or out.exists():
        ap.error('Use a new output directory under work/')
    out.mkdir(parents=True)
    outcomes,commands=[],[]
    def run(name,cmd,data=None):
        result=subprocess.run(cmd,input=data,text=True,capture_output=True,timeout=60)
        commands.append([s.replace(str(ROOT),'<ROOT>') for s in cmd])
        (out/(name+'.log')).write_text((result.stdout+result.stderr).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        if result.returncode:
            raise RuntimeError(name+' failed: '+result.stderr[-2000:])
        return result.stdout
    assert function(before,'xnu_hard_trap_handle_breakpoint')==function(after,'xnu_hard_trap_handle_breakpoint')
    outcomes.append({'name':'native-hard-handler-body-unchanged','passed':True})
    deps=run('sleH-dependencies', [*target,'-M',str(source/rel)])
    assert 'apple_arm64_cpu.h' not in deps and 'kern/trap_telemetry.h' in deps
    outcomes.append({'name':'native-trap-header-without-apple-cpu-helpers','passed':True})
    cases=[('outside-firmware-development',0,1,0,1,1,5),('outside-firmware-release',0,0,0,1,0,4),
           ('firmware-telemetry',1,1,1,1,1,5),('firmware-minimal',1,1,0,1,0,3),
           ('firmware-release',1,0,0,1,0,3),('firmware-telemetry-no-assert',1,1,1,0,1,4)]
    for name,fw,dev,telemetry,assertions,recovery,count in cases:
        prefix=('#define CONFIG_ATLANTIC_FIRMWARE '+str(fw)+'\n#define DEBUG 0\n#define DEVELOPMENT '+str(dev)+
                '\n#define CONFIG_TELEMETRY '+str(telemetry)+'\n#define MACH_ASSERT '+str(assertions)+'\n')
        outputs=[]
        for role,text in [('upstream',before),('adapted',after)]:
            outputs.append(run(name+'-'+role,[target[0],'--target=arm64-apple-macos11.0','-mcpu=cortex-a57','-E','-P','-x','c','-'],prefix+scope_fragments(text)))
        descriptors=re.findall(r'KERNEL_BRK_DESCRIPTOR_DEFINE\((\w+)',outputs[1])
        assert len(descriptors)==count and len(set(descriptors))==count
        assert 'panic_with_thread_kernel_state(msg, state);' in outputs[1]
        assert ('add_saved_state_pc(state, 4);' in outputs[1])==bool(recovery)
        assert ('trap_telemetry_report_exception(' in outputs[1])==bool(recovery)
        assert ('test_desc' in descriptors)==bool(assertions and (not fw or recovery))
        unchanged=not fw or bool(telemetry and dev)
        if unchanged:
            assert outputs[0]==outputs[1], 'Native enabled/outside context changed'
        outcomes.append({'name':name,'passed':True,'recoverable_path_present':bool(recovery),
                         'descriptors':descriptors,'upstream_byte_identical_required':unchanged})
    fixture=ROOT/'tests/xnu_port/brk_encoding.c'
    obj=out/'brk.o'
    run('brk-compile',[*target,'-c',str(fixture),'-o',str(obj)])
    parsed=read_object(obj)
    c_names=[n for n in EXPECTED if n!='_atl_reserved_trap_25']
    brks=audit_brks(parsed,c_names)
    reserved_fixture=ROOT/'tests/xnu_port/brk_reserved.ll'
    reserved_obj=out/'reserved-trap.o'
    backend=[target[0],'--target=arm64-apple-macos11.0','-mcpu=cortex-a57','-O1']
    run('reserved-trap-compile',[*backend,'-c',str(reserved_fixture),'-o',str(reserved_obj)])
    brks.update(audit_brks(read_object(reserved_obj),['_atl_reserved_trap_25']))
    for name,audit in brks.items():
        outcomes.append({'name':name,'passed':True,**audit})
    run('brk-disassembly',['llvm-objdump','--macho','--disassemble',str(obj)])
    ir=out/'brk.ll'
    run('brk-ir',[*target,'-S','-emit-llvm',str(fixture),'-o',str(ir)])
    body=re.search(r'^define [^\n]*@atl_native_assert_values\(.*?^\}',ir.read_text(),re.M|re.S)
    assert body and all('{'+reg+'}' in body[0] for reg in ['x8','x16','x17'])
    words=struct.unpack('<'+'I'*(len(symbol_bytes(parsed,'_atl_native_assert_values'))//4),symbol_bytes(parsed,'_atl_native_assert_values'))
    assert 0xaa0003f0 in words and 0xaa0103f1 in words, 'Native assertion values must reach x16/x17'
    outcomes.append({'name':'native-assert-register-contract','passed':True,'registers':['x8','x16','x17']})
    wrong_ir=out/'wrong-reserved-trap.ll'
    text=reserved_fixture.read_text()
    assert text.count('i8 25')==1
    wrong_ir.write_text(text.replace('i8 25','i8 26'),encoding='utf-8',newline='\n')
    wrong=out/'wrong-reserved-trap.o'
    run('wrong-reserved-trap-compile',[*backend,'-c',str(wrong_ir),'-o',str(wrong)])
    try:
        audit_brks(read_object(wrong),['_atl_reserved_trap_25'])
    except ValueError as error:
        assert '_atl_reserved_trap_25' in str(error)
        (out/'wrong-reserved-trap-rejected.log').write_text(str(error)+'\n',encoding='utf-8',newline='\n')
    else:
        raise AssertionError('Wrong reserved trap comment was accepted')
    outcomes.append({'name':'wrong-reserved-trap-comment-rejected','passed':True})
    native=next((o for o in build['objects'] if o['source']==rel),None)
    object_check=None
    if native:
        path=(args.build.parent/native['object']).resolve()
        assert path.is_relative_to(args.build.parent.resolve()) and digest(path)==native['object_sha256']
        actual=read_object(path)
        _,sections,symbols=actual
        names=['_clang_desc','_libcxx_desc','_xnu_hard_traps_desc']
        descriptor_section=next(s for s in sections if s['name']=='__kern_brk_desc')
        assert descriptor_section['size']==72  # native target descriptor is 24 bytes
        assert not any(name in symbols for name in ['_test_desc','_xnu_soft_traps_desc','_recoverable_kernel_trap_test'])
        ranges={names[0]:(2,0x5500,0x55ff),names[1]:(3,0x800,0x800),names[2]:(5,0xb000,0xbfff)}
        for name,expected in ranges.items():
            data=symbol_bytes(actual,name,24)
            assert struct.unpack_from('<IHH',data)==expected and data[8]&3==0
        # Native Mach-O UNSIGNED relocation binds the hard descriptor to the
        # real local handler. The zero slot is an unlinked addend, not a stub.
        assert descriptor_section['relocation_count']==1
        reloc=descriptor_section['relocation_offset']
        assert 0<=reloc<=len(actual[0])-8
        address,info=struct.unpack_from('<iI',actual[0],reloc)
        expected_slot=symbols['_xnu_hard_traps_desc']['value']-descriptor_section['address']+16
        assert address==expected_slot
        assert (info>>24)&1==0 and (info>>25)&3==3 and (info>>27)&1==1 and info>>28==0
        assert info&0xffffff==symbols['_xnu_hard_trap_handle_breakpoint']['index']
        assert struct.unpack_from('<Q',symbol_bytes(actual,'_xnu_hard_traps_desc',24),16)[0]==0
        undefined=run('sleH-undefined',['llvm-nm','--undefined-only',str(path)])
        assert 'trap_telemetry' not in undefined and '_panic' in undefined
        object_check={'object_sha256':digest(path),'fatal_descriptor_count':3,'descriptor_bytes':24,
                      'recoverable_test_registered':False,'telemetry_backend_referenced':False,
                      'hard_callback_relocation':'ARM64_RELOC_UNSIGNED',
                      'hard_callback_symbol':'_xnu_hard_trap_handle_breakpoint',
                      'hard_callback_slot_offset':address,'hard_callback_relocation_info':hex(info)}
    report={'schema_version':1,'label':'HOST_TESTED',
        'scope':'NATIVE_HANDLER_SELECTION_AND_TARGET_BRK_ENCODING_ONLY_NOT_EXCEPTION_OR_XNU_EXECUTION',
        'port_id':build['port_id'],'build_report_sha256':digest(args.build),'tool_sha256':digest(__file__),
        'fixture_sha256':digest(fixture),'source_preimage_sha256':entry['preimage_sha256'],
        'reserved_ir_fixture_sha256':digest(reserved_fixture),'reserved_object_sha256':digest(reserved_obj),
        'unchanged_native_headers':native_headers,
        'source_postimage_sha256':entry['postimage_sha256'],'outcomes':outcomes,'commands':commands,
        'brk_object_sha256':digest(obj),'llvm_ir_sha256':digest(ir),'native_object_audit':object_check,
        'xnu_executed':False,'phone_accessed':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':len(outcomes),'native_sleh_audited':object_check is not None}))


if __name__=='__main__':
    main()
