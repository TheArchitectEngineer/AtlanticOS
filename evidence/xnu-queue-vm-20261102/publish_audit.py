import hashlib,json,re,shutil,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'evidence/xnu-queue-vm-20261102';assert not out.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
lock=read(root/'xnu-port/patches.lock.json')
assert lock['port_id']=='560ed77e6b991310aa660d45319de4ef438447ada8a714c8fc88b0b27ed42c74' and len(lock['patches'])==31
source=root/'work/xnu-lab-sources'/lock['port_id'][:16]
for item in lock['canonical_lf_files']:assert sha(source/item['path'])==item['postimage_sha256']
for name,h in lock['patches'].items():assert sha(root/'xnu-port'/name)==h
selected={};folders=[];summary={}
def add(path,name):
    assert path.is_file() and name not in selected,name
    selected[name]=path
def inputs(r):
    for p,h in r.get('inputs',{}).items():assert sha(root/p)==h,p
def bindings(v):
    if isinstance(v,list):return [x for c in v for x in bindings(c)]
    if not isinstance(v,dict):return []
    return [h for k,h in v.items() if k in {'build_report_sha256','base_report_sha256','base_build_report_sha256'}]+[
        h for k,c in v.items() if k not in {'build_report_sha256','base_report_sha256','base_build_report_sha256'} for h in bindings(c)]
stems=['early-log','cpu','coalition','scheduler','policy','strings','startup','platform','brk','core',
       'pmap','pmap-scope','task','mig','kobject','rpc']
for lane,bid,rid,total in [('exp','0fdf9a959ed06335','b7e5f17188c28799',202),('std','b9930604df134152','9cde58a7be2e3f74',176)]:
    path=root/'work/xnu-lab-builds'/bid/'report.json';base=read(path);inputs(base)
    assert base['port_id']==lock['port_id'] and len(base['objects'])==(159 if lane=='exp' else 13)
    assert not base['failed_units'] and all(s['exit_code']==s['expected'] for s in base['steps'])
    for item in base['objects']:
        assert sha(source/item['source'])==item['source_sha256']
        assert sha(path.parent/item['object'])==item['object_sha256'],item['object']
    for item in base['config_headers']+base['generated_headers']:assert sha(path.parent/item['path'])==item['sha256']
    prior=root/'evidence/early-ram-log-20261102'/(lane+'-base-report.json');old=read(prior)
    before={i['source']:i['source_sha256'] for i in old['objects']};now={i['source']:i['source_sha256'] for i in base['objects']}
    changed={p for p,h in before.items() if now[p]!=h}
    assert changed==({'osfmk/vm/vm_object.c'} if lane=='exp' else set())
    added=set(now)-set(before)
    assert added==({'osfmk/arm/counter.c','libkern/c++/priority_queue.cpp'} if lane=='exp' else set())
    assert base['selected_defines']==old['selected_defines'] and base['generated_headers']==old['generated_headers']
    assert len(base['generated_headers'])==70 and len(base['assym']['definitions'])==137
    assert base['assym']['definitions']==old['assym']['definitions'] and base['assym']['header_sha256']==old['assym']['header_sha256']
    assert (path.parent/'genassym.s').read_text().replace(lock['port_id'][:16],'<PORT>') == (
        root/'evidence/early-ram-log-20261102'/(lane+'-genassym.s')).read_text().replace(old['port_id'][:16],'<PORT>')
    add(path,lane+'-base-report.json');add(path.parent/'include/assym.s',lane+'-assym.s');folders.append(path.parent)
    for record in base['objects']:
        if record['source'] in added:
            add(path.parent/record['object'],lane+'-'+record['object'])
            add(path.parent/(Path(record['object']).stem+'.log'),lane+'-'+Path(record['object']).stem+'-compile.log')
    rpcpath=root/'work/xnu-rpc-builds'/rid/'report.json';rpc=read(rpcpath);inputs(rpc)
    assert rpc['base_build_report_sha256']==sha(path) and len(rpc['objects'])==42
    assert not rpc['failed_units'] and not rpc['generation_failures']
    assert rpc['native_link_selection']['selected_object_count']==26
    for item in rpc['objects']:
        for field,digest in [('object','object_sha256'),('source','source_sha256'),('header','header_sha256')]:
            assert sha(rpcpath.parent/item[field])==item[digest]
    add(rpcpath,lane+'-rpc-report.json');folders.append(rpcpath.parent)
    count=0
    for stem in stems+(['memory','usage'] if lane=='exp' else []):
        directory=root/'work'/('queue-vm-regression-'+stem+'-'+lane);report=read(directory/'report.json');inputs(report)
        assert set(bindings(report))=={sha(path)},stem
        cases=report.get('outcomes',report.get('cases'));assert cases and all(c['passed'] for c in cases)
        count+=len(cases);add(directory/'report.json',lane+'-scope-'+stem+'-report.json');folders.append(directory)
    directory=root/'work'/('queue-vm-scope-'+lane+'-v2-20261102');report=read(directory/'report.json');inputs(report)
    assert report['build_report_sha256']==sha(path) and len(report['outcomes'])==(24 if lane=='exp' else 26)
    assert all(c['passed'] for c in report['outcomes']) and not report['xnu_executed']
    count+=len(report['outcomes']);assert count==total
    for p in directory.iterdir():
        # Keep native ABI bytes, diagnostics and object inspection; the 16
        # expanded conditional-region bodies remain hashed in local inventory.
        if p.is_file() and p.suffix in {'.json','.o','.log'} and not p.name.startswith('vm-region-'):
            add(p,'queue-'+lane+'/'+p.name)
    folders.append(directory)
    for stem in ['boot-tree','boot-prepare','macho']:
        directory=root/'work'/('queue-vm-regression-'+stem+'-'+lane);r=read(directory/'report.json');inputs(r)
        assert set(bindings(r))=={sha(path)} and r['sanitizers'] and not r['xnu_executed']
        if stem=='boot-prepare':assert r['host_contracts']['cases']==10038
        if stem=='macho':assert r['host_contracts']['cases']==45099 and len(r['lld_fixture_audits'])==15
        add(directory/'report.json',lane+'-'+stem+'-report.json');folders.append(directory)
    directory=root/'work'/('queue-vm-regression-link-'+lane);link=read(directory/'report.json')
    assert link['build_report_sha256']==sha(path) and link['rpc_build']['report_sha256']==sha(rpcpath)
    assert link['link_exit_code']==1 and not link['output_exists'] and not link['duplicate_symbol_error_count']
    assert not link['dead_stripping_requested'] and link['undefined_symbols_must_error']
    assert sha(directory/'link.log')==link['link_log_sha256']
    if lane=='exp':
        assert link['object_count']==185 and link['undefined_symbol_error_count']==436
        assert link['static_link_mode']=='ATLANTIC_BOUNDED_EXPERIMENTAL' and not link['unsupported_static_option_diagnostic_found']
        names=lambda s:set(re.findall(r'^ld64\.lld: error: undefined symbol: (.+)$',s,re.M))
        oldnames=names((root/'evidence/early-ram-log-20261102/exp-link.log').read_text())
        newnames=names((directory/'link.log').read_text());resolved=sorted(oldnames-newnames)
        assert len(resolved)==27 and not newnames-oldnames
    add(directory/'report.json',lane+'-link-report.json');add(directory/'link.log',lane+'-link.log');folders.append(directory)
    summary[lane]={'units':len(base['objects']),'checks':count,'unchanged_prior_source_hashes':len(before)-len(changed),
                   'modified_source_paths':sorted(changed),'added_native_sources':sorted(added),
                   'base_report_sha256':sha(path),'rpc_report_sha256':sha(rpcpath),'undefined':link['undefined_symbol_error_count']}

out.mkdir()
for name,p in selected.items():
    target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
additions={'host-quarantine-event.json':root/'work/scheduler-object-quarantine-20261102/event.json',
           'discarded-first-link.log':root/'work/vm-wait-scope-probe-20261102/link.log'}
for name,p in additions.items():shutil.copyfile(p,out/name)
write(out/'audit.json',{'schema_version':1,'scope':'NATIVE_QUEUES_COUNTERS_AND_VM_WAIT_BUILD_SCOPE_ABI_ONLY',
    'port_id':lock['port_id'],'lanes':summary,'resolved_old_names':resolved,'new_undefined_names':[],
    'native_code_executed':False,'kernel_linked':False,'phone_accessed':False,'physical_memory_measured':False,
    'discarded_earlier_link_comparison_used':False,'host_security_settings_changed':False})
inventory=[{'path':p.relative_to(root).as_posix(),'sha256':sha(p)} for folder in folders for p in sorted(folder.rglob('*')) if p.is_file()]
write(out/'local-inventory.json',inventory)
prior_ci=json.loads(subprocess.check_output(['gh','run','view','41402958398','--json','status,conclusion,headSha,url'],cwd=root,text=True))
assert prior_ci['status']=='completed' and prior_ci['conclusion']=='success' and prior_ci['headSha']=='5ce46c833278438bfd5e7f002c9fbb2743ea02a2'
write(out/'prior-ci157-status.json',prior_ci)
shutil.copyfile(Path(__file__),out/'publish_audit.py')
(out/'README.md').write_text('''# Colas nativas y VM wait — 2026-11-02

159 unidades experimentales / 13 estándar, 202/176 checks. Se incorporan counter.c
ARM y priority_queue.cpp íntegros. El patch 0031 separa alcance VM/IOSCHED sin
cambiar cuerpos. 156 fuentes anteriores conservadas, 137 constantes y 70 headers
MIG iguales; 42 probes RPC, 26 seleccionados. Enlace estático de 185 objetos:
436 nombres indefinidos, cero duplicados, exit 1 y ninguna imagen. Resuelve 27,
sin nombres pendientes nuevos. La lane estándar usa LLD upstream y registra
sus errores de opciones estáticas; no es el modo estático experimental local.

Se conservan informes completos, objetos nuevos, fixtures C/C++, rechazos ABI,
disassembly, fuentes ligadas por SHA-256 y logs reales del enlace. Las expansiones
completas de los bloques condicionales y otros archivos locales están inventariados
en local-inventory.json; no se presentan como archivos publicados. Las fuentes
nativas/objetos conservan su procedencia XNU y sus licencias, no MIT AtlanticOS.

Los casos de preprocessing son del bloque condicional aislado, no builds de todas
las configuraciones completas. Los bytes de child/key/deadline son sintéticos.
Las instrucciones atómicas de 64 bits se inspeccionan sin ejecutarse. No hay
ejecución de queues, contadores, VM o XNU, ni acceso al G20 o RAM física medida.

El primer ensayo falló al abrir un objeto de caché puesto en cuarentena por
Defender y se descartó: discarded-first-link.log no se usa para contar símbolos.
El enlace auditado usa una reconstrucción nueva con todas las entradas verificadas.
La cuarentena no se restauró y no se cambiaron protecciones/exclusiones.

La CI limpia success conservada corresponde a 157 unidades / 5ce46c8. No se
atribuye a esta ampliación de 159. publish_audit.py conserva las verificaciones
y rutas locales usadas al empaquetar. El contexto físico y handoff siguen pendientes.
''',encoding='utf-8',newline='\n')
files=sorted(p for p in out.rglob('*') if p.is_file())
write(out/'manifest.json',{'schema_version':1,'audit_date':'2026-11-02','label':'BUILT_ARM64',
    'scope':'NATIVE_C_CPP_QUEUES_COUNTER_VM_WAIT_ABI_AND_OBJECTS_ONLY_NO_EXECUTION',
    'port_id':lock['port_id'],'source_parent_commit':'5ce46c833278438bfd5e7f002c9fbb2743ea02a2',
    'source_inputs_bound_by_sha256':True,'kernel_linked':False,'xnu_executed':False,'phone_accessed':False,
    'artifacts':[{'path':p.relative_to(out).as_posix(),'sha256':sha(p)} for p in files]})
print(json.dumps({'artifacts':len(files),'lanes':summary,'resolved_count':len(resolved),'local_inventory_files':len(inventory)}))
