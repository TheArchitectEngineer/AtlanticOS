"""Generate and compile the pinned native MIG kernel RPC source recipes.

Uses a successful XNU laboratory build and its real target configuration.
No handwritten RPC implementation, fake SDK, kernel link, execution or phone IO.
Empty selected interfaces are recorded explicitly and provide no RPC services.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import struct
import subprocess

from build_xnu_lab import make_list

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--windows-git', action='store_true')
    ap.add_argument('--jobs', type=int, default=2, choices=range(1,5))
    args = ap.parse_args()
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        ap.error('Use Linux x86_64 or Debian/WSL')
    build_path = args.build.resolve()
    base = json.loads(build_path.read_text())
    lock = json.loads((ROOT/'dependencies.lock.json').read_text())
    patches = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if base['port_id'] != patches['port_id'] or base['failed_units'] or base['upstream_commit'] != lock['xnu']['commit']:
        ap.error('Use a successful build of the current pinned port')
    for rel, expected in base['inputs'].items():
        if digest(ROOT/rel) != expected:
            ap.error('Changed base build input: '+rel)
    for rel, expected in patches['patches'].items():
        if digest(ROOT/'xnu-port'/rel) != expected:
            ap.error('Changed source patch: '+rel)
    source = ROOT/'work/xnu-lab-sources'/base['port_id'][:16]
    git = 'git.exe' if args.windows_git else 'git'
    def scm(*argv):
        folder = subprocess.check_output(['wslpath','-w',str(source)],text=True).strip() if args.windows_git else str(source)
        return subprocess.check_output([git,'-c','core.autocrlf=true','-C',folder,*argv],timeout=60)
    stamp = json.loads(source.with_suffix('.json').read_text())
    if (stamp['port_id'] != base['port_id'] or
        scm('rev-parse','HEAD').decode().strip() != lock['xnu']['commit'] or
        hashlib.sha256(scm('diff','--cached','--binary','HEAD')).hexdigest() != stamp['diff_sha256'] or
        scm('diff','--name-only') or b'?? ' in scm('status','--porcelain')):
        ap.error('Prepared XNU source changed; preserve it for inspection')
    for item in patches['canonical_lf_files']:
        if digest(source/item['path']) != item['postimage_sha256']:
            ap.error('Changed prepared source: '+item['path'])
    for item in base['config_headers']+base['generated_headers']:
        path = (build_path.parent/item['path']).resolve()
        if not path.is_relative_to(build_path.parent) or digest(path) != item['sha256']:
            ap.error('Changed or escaping base header: '+item['path'])
    if digest(build_path.parent/'include/libkern/version.h') != base['version_header_sha256']:
        ap.error('Changed generated version header')
    mig_dir = ROOT/'work/mig-host'
    mig = mig_dir/'migcom'
    mig_report = json.loads((mig_dir/'report.json').read_text())
    if (mig_report['bootstrap_commit'] != lock['mig_host_tool']['commit'] or
        digest(mig) != mig_report['migcom_sha256']):
        ap.error('Use the pinned official MIG host tool')
    for rel, expected in mig_report['source_sha256'].items():
        if digest(ROOT/rel) != expected:
            ap.error('Changed MIG host source: '+rel)
    target_commands = [c for c in base['commands'] if any(s.endswith('/tests/xnu_port/boot_abi.c') for s in c)]
    if len(target_commands) != 1 or target_commands[0][-4] != '-c':
        ap.error('Unexpected base target command')
    target = [s.replace('<ROOT>',str(ROOT)) for s in target_commands[0][:-4]]
    compiler = Path(shutil.which(target[0]) or target[0])
    compiler_hash = digest(compiler)
    if base['layout_provider'] and compiler_hash != base['layout_provider']['compiler_sha256']:
        ap.error('Changed experimental compiler')
    cpp_commands = [c for c in base['commands'] if '-DKERNEL_USER=1' in c and
                    any(s.endswith('/osfmk/mach/mach_notify.defs') for s in c)]
    if len(cpp_commands) != 1:
        ap.error('Native kernel-sender preprocessor recipe missing')
    cpp_base = [s.replace('<ROOT>',str(ROOT)) for s in cpp_commands[0][:-2]]
    if cpp_commands[0][-2] != '-DKERNEL_USER=1':
        ap.error('Unexpected native preprocessor role position')
    mk_path = source/'osfmk/mach/Makefile'
    mk = mk_path.read_text()
    users = make_list(mk,'MIG_KUSRC')
    servers = make_list(mk,'MIG_KSSRC')
    if any(not n.endswith('_user.c') for n in users) or any(not n.endswith('_server.c') for n in servers):
        ap.error('Native RPC file naming changed')
    if make_list((source/'osfmk/device/Makefile').read_text(),'DEVICE_FILES') != ['device_server.h','device_server.c']:
        ap.error('Native device recipe changed')
    units = [('mach',n.removesuffix('_user.c'),'kernel-sender') for n in users]
    units += [('mach',n.removesuffix('_server.c'),'kernel-server') for n in servers]
    units += [('device','device','kernel-server')]
    inputs = {'tools/build_xnu_rpc.py':digest(__file__),
              'tools/build_xnu_lab.py':digest(ROOT/'tools/build_xnu_lab.py'),
              'tests/xnu_port/mig_rpc_config.c':digest(ROOT/'tests/xnu_port/mig_rpc_config.c')}
    build_id = hashlib.sha256(json.dumps({'base':digest(build_path),'inputs':inputs,
        'compiler_sha256':compiler_hash,'mig_sha256':digest(mig)},sort_keys=True).encode()).hexdigest()
    out = ROOT/'work/xnu-rpc-builds'/build_id[:16]
    if out.exists():
        ap.error('Preserve existing RPC attempt: '+str(out))
    out.mkdir(parents=True)
    commands, config_cases, idl_scope_cases, generation_failures, generated = [], [], [], [], []
    def clean(command):
        return [str(s).replace(str(ROOT),'<ROOT>') for s in command]
    def run(command, *, name, data=None, cpp=False):
        r = subprocess.run(command,input=data,text=True,capture_output=True,cwd=out,timeout=120)
        commands.append(clean(command))
        (out/(name+'.log')).write_text(((r.stderr if cpp else r.stdout+r.stderr)).replace(str(ROOT),'<ROOT>'),encoding='utf-8',newline='\n')
        return r
    fixture = ROOT/'tests/xnu_port/mig_rpc_config.c'
    for name,flags,expected,diagnostic in [('runtime-config',[],0,None),
        ('reject-disabled-typecheck',['-D__MigTypeCheck=0'],1,'MIG runtime type checks must remain enabled')]:
        cmd = [*target,*flags,'-fsyntax-only',str(fixture)]
        r = run(cmd,name=name)
        config_cases.append({'name':name,'exit_code':r.returncode,'expected':expected,
            'passed':r.returncode==expected and (diagnostic is None or diagnostic in r.stderr),
            'command':clean(cmd)})
    if not all(c['passed'] for c in config_cases):
        ap.error('Native MIG configuration check failed; diagnostics preserved at '+str(out))
    # Check the scope of the three IDL adaptations against actual upstream
    # generation. This compares both outputs byte-for-byte, without executing RPC.
    for module,role in [('vm_map','kernel-sender'),('arcade_register','kernel-server'),
                        ('arcade_upcall','kernel-sender')]:
        rel = 'osfmk/mach/'+module+'.defs'
        original = scm('show','HEAD:'+rel).decode()
        modified = (source/rel).read_text()
        cases = [('outside-firmware',[s for s in cpp_base if s!='-DCONFIG_ATLANTIC_FIRMWARE'])]
        if module!='vm_map':
            cases.append(('enabled-arcade', [*cpp_base,'-DCONFIG_ARCADE=1']))
        for case,flags in cases:
            outputs = []
            for variant,text in [('upstream',original),('adapted',modified)]:
                folder = out/'idl-scope'/module/case/variant
                folder.mkdir(parents=True)
                definition = folder/(module+'.defs')
                definition.write_text(text,encoding='utf-8',newline='\n')
                marker = '-DKERNEL_SERVER=1' if role=='kernel-server' else '-DKERNEL_USER=1'
                cpp = run([*flags,marker,str(definition)],name='scope-cpp-'+module+'-'+case+'-'+variant,cpp=True)
                if cpp.returncode:
                    raise RuntimeError('IDL scope preprocessing failed: '+module+'/'+case)
                header = folder/(module+('_server.h' if role=='kernel-server' else '.h'))
                cfile = folder/(module+('_server.c' if role=='kernel-server' else '_user.c'))
                cmd = [str(mig),'-novouchers',*(['-mach_msg2'] if role=='kernel-server' else ['-maxonstack','1024']),
                    '-header',str(header) if role=='kernel-sender' else '/dev/null',
                    '-sheader',str(header) if role=='kernel-server' else '/dev/null',
                    '-server',str(cfile) if role=='kernel-server' else '/dev/null',
                    '-user',str(cfile) if role=='kernel-sender' else '/dev/null']
                r = run(cmd,name='scope-mig-'+module+'-'+case+'-'+variant,data=cpp.stdout)
                if r.returncode:
                    raise RuntimeError('IDL scope generation failed: '+module+'/'+case)
                outputs.append({'header_sha256':digest(header),'source_sha256':digest(cfile)})
            idl_scope_cases.append({'module':module,'name':case,'upstream':outputs[0],
                'adapted':outputs[1],'passed':outputs[0]==outputs[1]})
    if not all(c['passed'] for c in idl_scope_cases):
        ap.error('IDL adaptation changed an unselected scope; preserve '+str(out))
    base_headers = {h['path']:h for h in base['generated_headers']}
    for domain,module,role in units:
        stem = domain+'-'+module+('-server' if role=='kernel-server' else '-user')
        definition = source/'osfmk'/domain/(module+'.defs')
        marker = '-DKERNEL_SERVER=1' if role=='kernel-server' else '-DKERNEL_USER=1'
        cpp = run([*cpp_base,marker,str(definition)],name='cpp-'+stem,cpp=True)
        if cpp.returncode:
            generation_failures.append({'module':module,'role':role,'step':'cpp','exit_code':cpp.returncode})
            continue
        header = out/'include'/domain/(module+('_server.h' if role=='kernel-server' else '.h'))
        cfile = out/'generated'/domain/(module+('_server.c' if role=='kernel-server' else '_user.c'))
        header.parent.mkdir(parents=True,exist_ok=True)
        cfile.parent.mkdir(parents=True,exist_ok=True)
        cmd = [str(mig),'-novouchers',*(['-mach_msg2'] if role=='kernel-server' else ['-maxonstack','1024']),
            '-header',str(header) if role=='kernel-sender' else '/dev/null',
            '-sheader',str(header) if role=='kernel-server' else '/dev/null',
            '-server',str(cfile) if role=='kernel-server' else '/dev/null',
            '-user',str(cfile) if role=='kernel-sender' else '/dev/null']
        r = run(cmd,name='mig-'+stem,data=cpp.stdout)
        if r.returncode:
            generation_failures.append({'module':module,'role':role,'step':'mig','exit_code':r.returncode})
            continue
        relative_header = header.relative_to(out).as_posix()
        existing = base_headers.get(relative_header)
        if existing is None or existing.get('role') != role or digest(header) != existing['sha256']:
            raise RuntimeError('Generated header differs from selected base ABI: '+relative_header)
        text = header.read_text()
        counts = re.findall(r'^#define\s+\w+_MSG_COUNT\s+(\d+)\s*$',text,re.M)
        if len(counts) != 1:
            raise RuntimeError('Unexpected native MIG message count: '+relative_header)
        message_count = int(counts[0])
        if role=='kernel-server':
            descriptors = re.findall(r'^}\s+(\w+_subsystem);',text,re.M)
            entries = re.findall(r'^boolean_t\s+(\w+)\s*\(',text,re.M)
            if len(descriptors)!=1 or len(entries)!=1:
                raise RuntimeError('Unexpected native MIG server descriptor/entry: '+relative_header)
            required = ['_'+entries[0]]
            descriptor = '_'+descriptors[0]
        else:
            required = ['_'+s for s in re.findall(r'^kern_return_t\s+(\w+)\s*\(',text,re.M)]
            descriptor = None
            if message_count and not required:
                raise RuntimeError('Nonempty sender has no declarations: '+relative_header)
        generated.append({'module':module,'role':role,'domain':domain,
            'definition':definition.relative_to(source).as_posix(),'definition_sha256':digest(definition),
            'preprocessed_sha256':hashlib.sha256(cpp.stdout.encode()).hexdigest(),
            'source':cfile.relative_to(out).as_posix(),'source_sha256':digest(cfile),
            'header':relative_header,'header_sha256':digest(header),'message_count':message_count,
            'required_external_text':required,'required_descriptor':descriptor})
    def compile_unit(item):
        name = item['domain']+'-'+Path(item['source']).stem
        obj = out/(name+'.o')
        cmd = [target[0],'-I'+str(out/'include'/item['domain']),'-I'+str(out/'include'),
               *target[1:],'-c',str(out/item['source']),'-o',str(obj)]
        r = run(cmd,name='compile-'+name)
        result = {**item,'exit_code':r.returncode,'command':clean(cmd),
            'errors':[s.replace(str(ROOT),'<ROOT>') for s in r.stderr.splitlines() if 'error:' in s]}
        if r.returncode:
            print(json.dumps({'module':item['module'],'role':item['role'],'exit_code':r.returncode,
                              'errors':result['errors'][:2]}),flush=True)
            return result
        raw = obj.read_bytes()
        if len(raw)<32 or struct.unpack_from('<4I',raw)!=(0xfeedfacf,0x100000c,0,1):
            raise RuntimeError('Expected genuine ARM64 Mach-O RPC object: '+name)
        defined = run(['llvm-nm','--defined-only',str(obj)],name=name+'-defined').stdout
        if not all(any(line.split()[-2:]==['T',symbol] for line in defined.splitlines())
                   for symbol in item['required_external_text']):
            raise RuntimeError('Missing substantive RPC text export: '+name)
        if item['required_descriptor'] and not any(
            line.split()[-1:]==[item['required_descriptor']] and line.split()[-2] in {'S','D'}
            for line in defined.splitlines()):
            raise RuntimeError('Missing native server descriptor: '+name)
        undefined = run(['llvm-nm','--undefined-only',str(obj)],name=name+'-undefined').stdout.splitlines()
        if item['role']=='kernel-sender' and item['message_count']:
            if {'_mach_msg','_mach_msg_overwrite'}.intersection(s.strip() for s in undefined):
                raise RuntimeError('Kernel sender retained a userland transport: '+name)
            transports = [s.strip() for s in undefined if s.strip().startswith(
                ('_mach_msg_rpc_from_kernel','_mach_msg_send_from_kernel'))]
            if not transports:
                raise RuntimeError('No genuine native kernel transport found: '+name)
            result['native_kernel_transports'] = transports
        exports = run(['llvm-nm','--extern-only','--defined-only','--format=posix',str(obj)],name=name+'-exports').stdout.splitlines()
        result.update({'source_origin':'mig_generated','object':obj.name,'object_sha256':digest(obj),
            'object_file_bytes':len(raw),'defined_external_symbols':[s.split()[0] for s in exports if s.split()],
            'undefined_symbols':undefined})
        return result
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(compile_unit,generated))
    objects = [c for c in results if c['exit_code']==0]
    failures = [c for c in results if c['exit_code']!=0]
    definitions = {s for item in objects for s in item['defined_external_symbols']}
    base_definitions = {s for item in base['objects'] for s in item['defined_external_symbols']}
    all_definitions = base_definitions | definitions
    missing = sorted({s for item in [*base['objects'],*objects] for s in item['undefined_symbols']} - all_definitions)
    report = {'schema_version':1,'label':'BUILT_ARM64',
        'scope':'GENUINE_GENERATED_XNU_KERNEL_RPC_OBJECTS_ONLY_NOT_LINKED_OR_EXECUTED',
        'upstream_commit':lock['xnu']['commit'],'port_id':base['port_id'],'build_id':build_id,
        'base_build_report_sha256':digest(build_path),'base_build_id':base['build_id'],
        'base_build_report':str(build_path).replace(str(ROOT),'<ROOT>'),'inputs':inputs,
        'compiler_sha256':compiler_hash,'mig_sha256':digest(mig),
        'mig_report_sha256':digest(mig_dir/'report.json'),'bootstrap_commit':mig_report['bootstrap_commit'],
        'recipe_sha256':{p: digest(source/p) for p in ['osfmk/mach/Makefile','osfmk/device/Makefile']},
        'config_cases':config_cases,'idl_scope_cases':idl_scope_cases,'commands':commands,'generated':generated,
        'objects':objects,'failed_units':failures,'generation_failures':generation_failures,
        'combined_symbol_inventory':{'scope':'NAME_INVENTORY_ONLY_NOT_A_LINK_OR_RELOCATION_CHECK',
            'defined_external_count':len(all_definitions),'unprovided_symbols':missing},
        'empty_interfaces':[{'module':c['module'],'role':c['role']} for c in generated if not c['message_count']],
        'kernel_linked':False,'xnu_executed':False,'phone_accessed':False,
        'object_sizes_are_not_runtime_ram':True}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'compiled_rpc_units':len(objects),'failed_rpc_units':len(failures),
        'generation_failures':len(generation_failures),'empty_interfaces':len(report['empty_interfaces']),
        'kernel_linked':False,'report':str(out/'report.json')}))
    return 1 if failures or generation_failures else 0


if __name__=='__main__':
    raise SystemExit(main())
