"""Bind the local two-lane build, native audits and strict rejection to evidence."""
import hashlib, json, re, shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root/'evidence/early-ram-log-20261102'
assert not out.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
lock = read(root/'xnu-port/patches.lock.json')
assert lock['port_id'] == '5647a1f4c6efdb54864c33f22420ccd5669e260f7911b2ef61e33d18e16de646'
assert len(lock['patches']) == 30
source = root/'work/xnu-lab-sources'/lock['port_id'][:16]
for item in lock['canonical_lf_files']:
    assert sha(source/item['path']) == item['postimage_sha256']
for name, digest in lock['patches'].items():
    assert sha(root/'xnu-port'/name) == digest

selected, local_roots, results = {}, [], {}
def add(path, name):
    assert path.is_file() and name not in selected
    selected[name] = path

def inputs(report):
    for rel, digest in report.get('inputs', {}).items():
        assert sha(root/rel) == digest, rel

def bindings(value):
    if isinstance(value, dict):
        return [v for k,v in value.items() if k in {'build_report_sha256','base_report_sha256','base_build_report_sha256'}] + [
            h for k,v in value.items() if k not in {'build_report_sha256','base_report_sha256','base_build_report_sha256'} for h in bindings(v)]
    if isinstance(value, list): return [h for v in value for h in bindings(v)]
    return []

stems = ['cpu','coalition','scheduler','policy','strings','startup','platform','brk','core',
         'pmap','pmap-scope','task','mig','kobject','rpc']
for lane, build_id, rpc_id, logger_id, count, total in [
    ('exp','71c767f7ac383d0d','4ce1dafa6cb596de','early-log-native-exp-20261102',157,178),
    ('std','93c8768bdde5ff9e','ad476699d62626fe','early-log-native-std-v2-20261102',13,150)]:
    path = root/'work/xnu-lab-builds'/build_id/'report.json'
    base = read(path); inputs(base)
    assert base['port_id'] == lock['port_id'] and not base['failed_units'] and len(base['objects']) == count
    assert all(step['exit_code'] == step['expected'] for step in base['steps'])
    assert len(base['generated_headers']) == 70 and len(base['assym']['definitions']) == 137
    assert not base['kernel_linked'] and not base['xnu_executed'] and not base['phone_accessed']
    for item in base['config_headers']+base['generated_headers']:
        assert sha(path.parent/item['path']) == item['sha256']
    for item in base['objects']:
        assert sha(source/item['source']) == item['source_sha256']
        assert sha(path.parent/item['object']) == item['object_sha256']
    prior_id = '24560146b549e6c0' if lane == 'exp' else 'd3ccaaae1968be15'
    prior_path = root/'work/xnu-lab-builds'/prior_id/'report.json'
    prior = read(prior_path)
    current_sources = {o['source']:o['source_sha256'] for o in base['objects']}
    assert all(current_sources[o['source']] == o['source_sha256'] for o in prior['objects'])
    assert base['selected_defines'] == prior['selected_defines']
    assert base['assym']['definitions'] == prior['assym']['definitions']
    assert base['assym']['header_sha256'] == prior['assym']['header_sha256']
    assert base['generated_headers'] == prior['generated_headers']
    old_assembly = (prior_path.parent/'genassym.s').read_text()
    new_assembly = (path.parent/'genassym.s').read_text()
    assert old_assembly.replace(prior['port_id'][:16], '<PORT>') == new_assembly.replace(base['port_id'][:16], '<PORT>')
    add(path, lane+'-base-report.json'); local_roots.append(path.parent)
    add(path.parent/'include/assym.s', lane+'-assym.s')
    add(path.parent/'genassym.s', lane+'-genassym.s')
    add(path.parent/'config/Makefile', lane+'-Makefile')
    if lane == 'exp':
        new_sources = set(current_sources) - {o['source'] for o in prior['objects']}
        assert new_sources == {'osfmk/atlantic/early_log.c','osfmk/kern/atlantic_early_log.c'}
        for item in base['objects']:
            if item['source'] in new_sources:
                add(path.parent/item['object'], lane+'-'+item['object'])
                add(path.parent/(Path(item['object']).stem+'.log'), lane+'-'+Path(item['object']).stem+'-compile.log')
    rpcpath = root/'work/xnu-rpc-builds'/rpc_id/'report.json'
    rpc = read(rpcpath); inputs(rpc)
    assert rpc['base_build_report_sha256'] == sha(path)
    assert len(rpc['objects']) == 42 and not rpc['failed_units'] and not rpc['generation_failures']
    assert rpc['native_link_selection']['selected_object_count'] == 26
    for item in rpc['objects']:
        for field, digest in [('source','source_sha256'),('object','object_sha256'),('header','header_sha256')]:
            assert sha(rpcpath.parent/item[field]) == item[digest]
    add(rpcpath, lane+'-rpc-report.json'); local_roots.append(rpcpath.parent)
    checks = 0
    for stem in stems + (['memory','usage'] if lane == 'exp' else []):
        directory = root/'work'/('early-log-regression-'+stem+'-'+lane)
        report = read(directory/'report.json'); inputs(report)
        assert set(bindings(report)) == {sha(path)}, stem
        cases = report.get('outcomes', report.get('cases'))
        assert cases and all(c['passed'] for c in cases)
        checks += len(cases)
        add(directory/'report.json', lane+'-scope-'+stem+'-report.json'); local_roots.append(directory)
    logger_dir = root/'work'/logger_id
    logger = read(logger_dir/'report.json'); inputs(logger)
    assert set(bindings(logger)) == {sha(path)}
    assert logger['sanitizers'] and logger['host_model_records'] == 6000 and logger['host_concurrent_attempts'] == 16000
    assert len(logger['outcomes']) == (14 if lane == 'exp' else 16) and all(c['passed'] for c in logger['outcomes'])
    assert not logger['native_formatter_executed'] and not logger['xnu_executed'] and not logger['phone_accessed']
    if lane == 'exp': assert logger['thread_sanitizer'] and not logger['thread_sanitizer']['race_reported']
    checks += len(logger['outcomes']); assert checks == total
    local_roots.append(logger_dir)
    for p in logger_dir.iterdir():
        if p.is_file() and p.suffix in {'.json','.log','.ll','.o'}:
            add(p, 'logger-'+lane+'/'+p.name)
    for stem in ['boot-tree','boot-prepare','macho']:
        directory = root/'work'/('early-log-regression-'+stem+'-'+lane)
        report = read(directory/'report.json'); inputs(report)
        assert set(bindings(report)) == {sha(path)} and report['sanitizers']
        assert not report['xnu_executed'] and not report['phone_accessed']
        if stem == 'boot-prepare': assert report['host_contracts']['cases'] == 10038
        if stem == 'macho': assert report['host_contracts']['cases'] == 45099 and len(report['lld_fixture_audits']) == 15
        add(directory/'report.json', lane+'-'+stem+'-report.json'); local_roots.append(directory)
    linkdir = root/'work'/('early-log-regression-link-'+lane)
    link = read(linkdir/'report.json')
    assert link['build_report_sha256'] == sha(path) and link['rpc_build']['report_sha256'] == sha(rpcpath)
    assert link['link_exit_code'] == 1 and not link['output_exists'] and not link['duplicate_symbol_error_count']
    assert link['undefined_symbols_must_error'] and not link['dead_stripping_requested']
    assert sha(linkdir/'link.log') == link['link_log_sha256']
    if lane == 'exp':
        assert link['object_count'] == 183 and link['undefined_symbol_error_count'] == 463
        assert link['static_link_mode'] == 'ATLANTIC_BOUNDED_EXPERIMENTAL'
        names = lambda text: set(re.findall(r'^ld64\.lld: error: undefined symbol: (.+)$', text, re.M))
        before = names((root/'work/cpu-cache-component-link-exp/link.log').read_text())
        after = names((linkdir/'link.log').read_text())
        assert before-after == {'_kprintf','_PE_kputc'} and not after-before
    add(linkdir/'report.json', lane+'-link-report.json')
    add(linkdir/'link.log', lane+'-link.log'); local_roots.append(linkdir)
    results[lane] = {'units':count,'checks':checks,'base_report_sha256':sha(path),
                     'rpc_report_sha256':sha(rpcpath),'old_source_hashes_preserved':len(prior['objects']),
                     'genassym_equal_except_source_path':True,'undefined':link['undefined_symbol_error_count']}

out.mkdir()
for name, path in selected.items():
    dest = out/name; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, dest)
for name, rel in [('header-conflict-before-context-fix.log','work/early-log-native-preflight-20261102/exp-pe.log')]:
    shutil.copyfile(root/rel, out/name)
inventory = [{'path':p.relative_to(root).as_posix(),'sha256':sha(p)}
             for directory in local_roots for p in sorted(directory.rglob('*')) if p.is_file()]
write = lambda p, obj: p.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8',newline='\n')
write(out/'local-inventory.json', inventory)
write(out/'audit.json', {'schema_version':1,'scope':'LOCAL_NATIVE_BUILD_AND_HOST_DIAGNOSTICS_NO_XNU_EXECUTION',
    'lanes':results,'port_id':lock['port_id'],'patch_count':30,'resolved_old_names':['_PE_kputc','_kprintf'],
    'new_undefined_names':[],'native_formatter_unchanged':True,'kernel_linked':False,
    'native_formatter_executed':False,'xnu_executed':False,'phone_accessed':False,'physical_memory_measured':False})
shutil.copyfile(Path(__file__),out/'publish_audit.py')
(out/'README.md').write_text('''# Logging RAM original — 2026-11-02

Dos componentes originales integrados: 157 unidades experimentales / 13 estándar.
Pasan 178/150 checks de alcance/ABI/objetos. Se conservan 155 fuentes anteriores,
137 constantes de layout y 70 headers MIG; 42 probes RPC, 26 seleccionados.
Enlace estático experimental: 183 objetos, 463 nombres indefinidos, cero
duplicados, exit 1 y ninguna imagen. Resuelve kprintf/PE_kputc sin imports nuevos.
La lane estándar no incluye estos componentes en su base y usa LLD upstream.

6 000 registros modelados y 16 000 intentos concurrentes por ejecución host,
ASan/UBSan en ambas lanes; una ejecución aparte con ThreadSanitizer en exp.
Los counts de assertions y contención son variables, no tests independientes.
Se publican los dos objetos integrados, probes estándar, IR/disassembly,
rechazos ABI y configuración, informes completos y logs del enlace. El log
del conflicto de headers previo a seleccionar el contexto core es histórico.
local-inventory.json liga los archivos completos que permanecen bajo work/;
los archivos no incluidos en este manifiesto no se presentan como publicados.

publish_audit.py conserva las verificaciones/rutas locales del empaquetado.
La asamblea genassym cambia rutas de depuración por el nuevo port_id; coincide
al sustituir solo esa ruta, y las 137 constantes/header permanecen idénticos.
No se afirma reproducción binaria completa. La CI limpia anterior era de 155
unidades; sus resultados no se atribuyen a estas 157.

El host ejecuta solo transporte/capturador originales. No hay ejecución del
formatter nativo, adaptador ARM64, XNU, G20 o EDK2. No hay exportación física
de logs ni medición de RAM. 16 432 bytes de BSS es tamaño de objeto; no consumo
total. Se exige RAM normal/shareable mapeada: fuera del preflight MMU-off.
''',encoding='utf-8',newline='\n')
files = sorted(p for p in out.rglob('*') if p.is_file())
write(out/'manifest.json', {'schema_version':1,'audit_date':'2026-11-02','label':'BUILT_ARM64',
    'scope':'ORIGINAL_RAM_DIAGNOSTICS_HOST_TESTS_AND_NATIVE_ABI_OBJECTS_ONLY_NO_XNU_OR_PHONE_EXECUTION',
    'port_id':lock['port_id'],'source_parent_commit':'01af7b267af07b576ccbc6cc869be7dbabbf3da6',
    'source_inputs_bound_by_sha256':True,'kernel_linked':False,'xnu_executed':False,'phone_accessed':False,
    'artifacts':[{'path':p.relative_to(out).as_posix(),'sha256':sha(p)} for p in files]})
print(json.dumps({'artifacts':len(files),'lanes':results,'local_inventory_files':len(inventory)}))
