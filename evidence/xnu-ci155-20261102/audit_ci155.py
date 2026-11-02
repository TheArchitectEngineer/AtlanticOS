"""Publish a bounded, source/ABI-level audit of the completed exact CI run."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOWNLOAD = ROOT / 'work/ci155-41374630610'
OUT = ROOT / 'evidence/xnu-ci155-20261102'
HEAD = '1f2fa529cb1c567f3f405f532017d77ad24f8bfa'
RUN = '41374630610'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def gh(*args):
    return json.loads(subprocess.check_output(['gh', *args], cwd=ROOT, text=True))

def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')

assert not OUT.exists()
assert subprocess.check_output(['git.exe', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == HEAD
run = gh('run', 'view', RUN, '--json', 'status,conclusion,headSha,createdAt,updatedAt,url,jobs')
assert run['headSha'] == HEAD and run['status'] == 'completed' and run['conclusion'] == 'success'
assert len(run['jobs']) == 1 and run['jobs'][0]['conclusion'] == 'success'
artifacts = gh('api', f'repos/h0nda1337/AtlanticOS/actions/runs/{RUN}/artifacts')
assert len(artifacts['artifacts']) == 1 and not artifacts['artifacts'][0]['expired']
local_path = ROOT / 'work/xnu-lab-builds/24560146b549e6c0/report.json'
base_path = next((DOWNLOAD/'xnu-lab-builds').glob('*/report.json'))
rpc_path = next((DOWNLOAD/'xnu-rpc-builds').glob('*/report.json'))
local, base, rpc = read(local_path), read(base_path), read(rpc_path)
compiler = read(DOWNLOAD/'clang-layout-ci/report.json')
api = read(DOWNLOAD/'clang-layout-ci/tests/report.json')
assert compiler['source_files_verified'] == 11996 and len(api['outcomes']) == 26
assert all(item['passed'] for item in api['outcomes'])
assert compiler['compiler_sha256'] == api['compiler_sha256'] == base['layout_provider']['compiler_sha256']
assert base['layout_provider']['proof_sha256'] == sha(DOWNLOAD/'clang-layout-ci/tests/report.json')
assert compiler['upstream_commit'] == 'cd708029e0b2869e80abe31ddb175f7c35361f90'
assert base['port_id'] == read(ROOT/'xnu-port/patches.lock.json')['port_id']
for key in ['port_id', 'upstream_commit', 'patches', 'inputs', 'selected_defines', 'assym', 'config_headers', 'generated_headers']:
    assert base[key] == local[key], key
assert len(base['objects']) == 155 and not base['failed_units']
assert all(step['exit_code'] == step['expected'] for step in base['steps'])
assert len(base['assym']['definitions']) == 137 and len(base['generated_headers']) == 70
local_objects = {item['source']: item for item in local['objects']}
assert {item['source']: item['source_sha256'] for item in base['objects']} == {
    item['source']: item['source_sha256'] for item in local['objects']}
assert len(rpc['objects']) == 42 and not rpc['failed_units'] and not rpc['generation_failures']
assert rpc['base_build_report_sha256'] == sha(base_path)
local_rpc = read(ROOT/'work/xnu-rpc-builds/e5e21bf61513987d/report.json')
for key in ['scope', 'sources', 'selected_object_count', 'excluded_probe_object_count']:
    assert rpc['native_link_selection'][key] == local_rpc['native_link_selection'][key], key
ci_makefile = base_path.parent/'config/Makefile'
local_makefile = local_path.parent/'config/Makefile'
assert sha(ci_makefile) == base['config_makefile_sha256'] == rpc['native_link_selection']['config_makefile_sha256']
assert sha(local_makefile) == local['config_makefile_sha256']
assert re.sub(r'^SOURCE_DIR=.*$', 'SOURCE_DIR=<SOURCE>', ci_makefile.read_text(), flags=re.M) == re.sub(
    r'^SOURCE_DIR=.*$', 'SOURCE_DIR=<SOURCE>', local_makefile.read_text(), flags=re.M)
assert rpc['native_link_selection']['selected_object_count'] == 26
assert {(i['source'], i['source_sha256'], i['header_sha256'], i['definition_sha256'], i['kernel_link_selected']) for i in rpc['objects']} == {
    (i['source'], i['source_sha256'], i['header_sha256'], i['definition_sha256'], i['kernel_link_selected']) for i in local_rpc['objects']}
scopes = ['coalition-bank', 'scheduler-provider', 'ipc-policy-scope', 'string-support',
          'startup-scope', 'pe-platform', 'brk-scope', 'core-scope', 'pmap-firmware',
          'pmap-cs-scope', 'task-metadata', 'ipc-mig-abi', 'kobject-scope',
          'memory-provider', 'usage-semantics', 'xnu-rpc', 'cpu-cache']
check_count = 0
reports = sorted(DOWNLOAD.rglob('report.json'))
inputs_verified = set()
for path in reports:
    report = read(path)
    for rel, expected in report.get('inputs', {}).items():
        assert sha(ROOT/rel) == expected, (path, rel)
        inputs_verified.add(rel)
    assert not report.get('xnu_executed', False) and not report.get('phone_accessed', False)
for stem in scopes:
    report = read(DOWNLOAD/(stem+'-tests')/'report.json')
    cases = report.get('outcomes', report.get('cases'))
    assert cases and all(item['passed'] for item in cases)
    check_count += len(cases)
assert check_count == 164
link_path = DOWNLOAD/'xnu-link-diagnostics/report.json'
link = read(link_path)
local_link = read(ROOT/'work/cpu-cache-component-link-exp/report.json')
assert link['build_report_sha256'] == sha(base_path) and link['rpc_build']['report_sha256'] == sha(rpc_path)
assert link['object_count'] == 181 and link['link_exit_code'] == 1
assert link['undefined_symbol_error_count'] == 465 and link['duplicate_symbol_error_count'] == 0
assert link['static_link_mode'] == 'UPSTREAM_LD64_STATIC_OPTIONS' and link['unsupported_static_option_diagnostic_found']
assert local_link['static_link_mode'] == 'ATLANTIC_BOUNDED_EXPERIMENTAL'
assert link['undefined_symbols_must_error'] and not link['dead_stripping_requested']
assert not link['output_exists'] and not link['kernel_linked']
assert sha(link_path.parent/'link.log') == link['link_log_sha256']
def unresolved(log):
    return set(re.findall(r'^ld64\.lld: error: undefined symbol: (.+)$', log, re.M))
ci_missing = unresolved((link_path.parent/'link.log').read_text())
assert ci_missing == unresolved((ROOT/'work/cpu-cache-component-link-exp/link.log').read_text())
assert len(ci_missing) == 465
macho = read(DOWNLOAD/'macho-plan-tests/report.json')
boot = read(DOWNLOAD/'boot-prepare-tests/report.json')
assert macho['host_contracts']['cases'] == 45084 and not macho['lld_fixture_audits']
assert boot['host_contracts']['cases'] == 10038 and boot['native_abi']['all_1152_bytes_match_native_initializer']
assert boot['record_sha256'] == sha(DOWNLOAD/'boot-prepare-tests/candidate-boot-args.bin')
assert boot['record_sha256'] == '8971c60b7399ceaf65a735ffa4b59af9c0e921b3fd632690da538b5f2e2dcbcd'

OUT.mkdir()
for path in reports + [base_path.parent/'config/Makefile', link_path.parent/'link.log',
                       DOWNLOAD/'boot-prepare-tests/candidate-boot-args.bin']:
    target = OUT/'remote'/path.relative_to(DOWNLOAD)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, target)
write(OUT/'github-run.json', run)
write(OUT/'github-artifacts.json', artifacts)
write(OUT/'download-inventory.json', [{'path': p.relative_to(DOWNLOAD).as_posix(), 'sha256': sha(p)}
                                     for p in sorted(DOWNLOAD.rglob('*')) if p.is_file()])
audit = {
    'schema_version': 1, 'scope': 'CI_SOURCE_SELECTION_AND_ABI_REPRODUCTION_NOT_BINARY_REPRODUCIBILITY_OR_EXECUTION',
    'repository_commit': HEAD, 'run_id': int(RUN), 'conclusion': run['conclusion'],
    'local_base_report_sha256': sha(local_path), 'ci_base_report_sha256': sha(base_path),
    'compiler_source_files_verified': 11996, 'compiler_api_checks': 26,
    'base_units': 155, 'rpc_compiled_probes': 42, 'rpc_selected_units': 26,
    'scope_and_abi_checks': check_count, 'matching_layout_constants': 137,
    'matching_mig_headers_and_roles': 70, 'matching_selected_defines': True,
    'matching_base_source_hashes': 155, 'matching_rpc_source_and_header_hashes': 42,
    'matching_config_headers': 50, 'makefiles_equal_except_source_dir': True,
    'verified_current_repository_inputs': sorted(inputs_verified),
    'matching_object_file_hashes': sum(item['object_sha256'] == local_objects[item['source']]['object_sha256'] for item in base['objects']),
    'bit_identical_build_claimed': False, 'ci_uses_custom_static_lld': False,
    'local_uses_custom_static_lld': True, 'matching_undefined_names': sorted(ci_missing),
    'ci_static_options_unsupported': True, 'kernel_linked': False,
    'macho_ci_host_cases': 45084, 'macho_ci_real_lld_fixture_cases': 0,
    'boot_args_ci_host_cases': 10038, 'candidate_boot_args_wire_sha256': boot['record_sha256'],
    'xnu_executed': False, 'phone_accessed': False, 'edk2_handoff_executed': False,
    'physical_memory_measured': False}
write(OUT/'audit.json', audit)
shutil.copyfile(Path(__file__), OUT/'audit_ci155.py')
(OUT/'README.md').write_text('''# Reconstrucción limpia de 155 unidades — 2026-11-02

Run 41374630610, commit 1f2fa529cb1c567f3f405f532017d77ad24f8bfa, success.
Se conserva el metadata remoto, los 27 informes originales, Makefile, link.log,
boot_args candidato y un inventario SHA-256 de toda la descarga. La descarga
completa permanece en work/ci155-41374630610; no se vuelven a publicar todos sus logs.
audit_ci155.py registra las verificaciones realizadas y sus rutas locales.

Coinciden las fuentes de las 155 unidades, los 42 RPC generados y sus headers,
70 headers MIG instalados/roles, 50 headers config, defines y 137 constantes.
Pasan 26 checks de API del compilador y 164 de alcance/ABI/objetos.
Solo 77/155 hashes de objeto son iguales: no se afirma reproducción binaria.
Los binarios de compilador y rutas de trabajo difieren entre WSL y GitHub.

La CI usa LLD upstream, que también rechaza tres opciones estáticas. No reproduce
el LLD estático original local. Sí reproduce los mismos 465 nombres indefinidos,
cero duplicados y ausencia de imagen. El parser Mach-O tiene 45 084 casos en esta
CI; los otros 15 fixtures LLD de la prueba local no se ejecutan en este run.
boot_args conserva 10 038 casos y los 1 152 bytes coincidentes con el ABI nativo.

BUILT_ARM64 aquí solo prueba compilación. No hay ejecución XNU, acceso al G20,
handoff EDK2 ni medición de RAM física. El estado success acredita el alcance
del workflow; no un kernel enlazado ni un arranque.
''', encoding='utf-8', newline='\n')
files = sorted(p for p in OUT.rglob('*') if p.is_file())
write(OUT/'manifest.json', {
    'schema_version': 1, 'audit_date': '2026-11-02', 'label': 'BUILT_ARM64',
    'scope': 'CLEAN_CI155_SOURCE_ABI_REPRODUCTION_ONLY_NO_KERNEL_OR_HARDWARE_EXECUTION',
    'repository_commit': HEAD, 'github_run_id': int(RUN),
    'port_id': base['port_id'], 'kernel_linked': False, 'xnu_executed': False,
    'phone_accessed': False, 'artifacts': [{'path': p.relative_to(OUT).as_posix(), 'sha256': sha(p)} for p in files]})
print(json.dumps({'published_artifacts': len(files), 'base_units': 155, 'checks': check_count,
                  'matching_object_files': audit['matching_object_file_hashes'], 'undefined': len(ci_missing)}))
