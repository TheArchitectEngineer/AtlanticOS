"""Compile real XNU core objects using original AtlanticOS laboratory patches.

This is an incremental port build, not a linked kernel, boot image, or execution.
No fake SDK, simulator macros, host MIG bridge in target flags, or phone IO.
Requires pinned sources and the genuine MIG build from tools/build_mig.py.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import struct
import subprocess
from xnu_assym import parse_assym, render_assym

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT/'xnu-port/config/MASTER.arm64.atlanticlab.AtlanticOS'
UNITS = {'osfmk/kern/startup.c': '_kernel_bootstrap',
         'osfmk/kern/sched_prim.c': '_sched_init',
         'osfmk/kern/clock.c': '_clock_init',
         'osfmk/vm/vm_init.c': '_vm_mem_bootstrap',
         'osfmk/vm/vm_kern.c': '_kmem_alloc_guard',
         'osfmk/arm64/cswitch.s': '_Switch_context',
         'osfmk/arm64/start.s': '_start_first_cpu',
         'osfmk/arm64/locore.s': '_ExceptionVectorsBase',
         'osfmk/arm64/machine_routines_asm.s': '_set_mmu_ttb',
         'osfmk/arm/arm_init.c': '_arm_init',
         'osfmk/arm64/arm_vm_init.c': '_arm_vm_init',
         'osfmk/arm64/machine_routines.c': '_machine_startup',
         'osfmk/ipc/ipc_init.c': '_ipc_init'}
# IPC registers a genuine static initializer in STARTUP(MACH_IPC, ...).
SYMBOL_TYPES = {'osfmk/ipc/ipc_init.c': 't', 'osfmk/kern/sched_dualq.c': 't',
                'osfmk/ipc/ipc_importance.c': 't', 'osfmk/ipc/ipc_voucher.c': 't',
                'osfmk/vm/vm_sanitize_error_compat.c': 'S', 'osfmk/arm/data.s': 'D'}
STARTUP_SYMBOL_PREFIXES = {
    'osfmk/ipc/ipc_init.c': '___startup_MACH_IPC_entry_ipc_init_',
    'osfmk/ipc/ipc_importance.c': '___startup_MACH_IPC_entry_ipc_importance_init_',
    'osfmk/kern/ipc_kobject.c': '___startup_MACH_IPC_entry_mig_init_',
    'osfmk/ipc/ipc_voucher.c': '___startup_MACH_IPC_entry_ipc_voucher_init_'}
EXTRA_SYMBOLS = {'osfmk/arm64/cswitch.s': ['_machine_load_context', '_Call_continuation'],
                 'osfmk/arm64/start.s': ['__start', '_LowResetVectorBase'],
                 'osfmk/arm64/locore.s': ['_fleh_synchronous', '_fleh_irq'],
                 'osfmk/arm64/machine_routines_asm.s': ['_set_mmu_ttb_alternate'],
                 'osfmk/arm/arm_init.c': ['_arm_init_cpu', '_arm_init_idle_cpu', '_const_boot_args'],
                 'osfmk/arm64/arm_vm_init.c': ['_bootstrap_pagetables'],
                 'osfmk/kern/thread.c': ['_kernel_thread_start', '_thread_terminate_self'],
                 'osfmk/kern/kalloc.c': ['_kalloc_type_impl_external', '_kfree_type_impl_external'],
                 'osfmk/kern/zalloc.c': ['_zone_create_ext', '_zalloc_ext', '_zfree_ext'],
                 'osfmk/arm/pmap/pmap.c': ['_pmap_enter_options', '_pmap_page_protect', '_pmap_ro_zone_memcpy', '_cpu_ttep']}
EXTRA_SYMBOLS.update({
    'osfmk/kern/task.c': ['_task_create_internal', '_task_get_ro', '_task_info'],
    'osfmk/kern/task_ref.c': ['_task_ref_count_init', '_task_ref_count_fini'],
    'osfmk/kern/atlantic_task_metadata.c': ['_proc_ro_ref_task', '_proc_ro_erase_task',
        '_task_ref_hold_proc_task_struct', '_task_release_proc_task_struct', '_proc_require', '_kernproc']})
EXTRA_SYMBOLS.update({
    'osfmk/vm/vm_object.c': ['_vm_object_allocate', '_vm_object_deallocate'],
    'osfmk/vm/vm_fault.c': ['_vm_fault_page', '_vm_fault_enter', '_vm_fault_wire'],
    'osfmk/vm/vm_resident.c': ['_vm_page_grab_options', '_vm_page_release', '_pmap_steal_memory'],
    'osfmk/kern/sched_dualq.c': ['_sched_dualq_dispatch', '_sched_dualq_choose_thread'],
    'osfmk/kern/processor.c': ['_processor_init', '_processor_boot'],
    'libkern/os/refcnt.c': ['_os_ref_retain_internal', '_os_ref_release_barrier_internal']})
EXTRA_SYMBOLS.update({
    'osfmk/ipc/ipc_importance.c': ['_ipc_importance_send', '_ipc_importance_receive'],
    'osfmk/ipc/ipc_object.c': ['_ipc_object_copyout'],
    'osfmk/ipc/ipc_port.c': ['_ipc_port_destroy', '_ipc_port_adjust_special_reply_port'],
    'osfmk/ipc/ipc_kmsg.c': ['_ipc_kmsg_copyin_from_kernel', '_ipc_kmsg_destroy'],
    'osfmk/ipc/ipc_mqueue.c': ['_ipc_mqueue_receive', '_ipc_mqueue_send_locked'],
    'osfmk/ipc/ipc_right.c': ['_ipc_right_copyout_any_send'],
    'osfmk/kern/ipc_kobject.c': ['_ipc_kobject_alloc_port', '_mig_init'],
    'osfmk/kern/atlantic_thread_metadata.c': ['_current_thread_ro', '_get_threadtask', '_get_threadtask_early']})
EXPERIMENTAL_UNITS = {'osfmk/kern/thread.c': '_thread_init',
                      'osfmk/kern/kalloc.c': '_kalloc_type_impl_internal',
                      'osfmk/kern/zalloc.c': '_zinit',
                      'osfmk/vm/vm_map.c': '_vm_map_enter',
                      'osfmk/arm/pmap/pmap.c': '_pmap_bootstrap',
                      'osfmk/kern/task.c': '_task_init',
                      'osfmk/kern/task_ref.c': '_task_ref_init',
                      'osfmk/kern/atlantic_task_metadata.c': '_proc_ro_alloc',
                      'osfmk/kern/atlantic_task_process.c': '_get_bsdtask_info',
                      'osfmk/vm/vm_object.c': '_vm_object_bootstrap',
                      'osfmk/vm/vm_fault.c': '_vm_fault_init',
                      'osfmk/vm/vm_resident.c': '_vm_page_bootstrap',
                      'osfmk/kern/locks.c': '_hw_lock_bit',
                      'osfmk/kern/ledger.c': '_ledger_instantiate',
                      'osfmk/kern/stack.c': '_stack_alloc',
                      'osfmk/kern/smr.c': '_smr_synchronize',
                      'osfmk/kern/waitq.c': '_waitq_assert_wait64',
                      'osfmk/kern/turnstile.c': '_turnstiles_init',
                      'osfmk/kern/thread_call.c': '_thread_call_enter',
                      'osfmk/kern/timer.c': '_timer_init',
                      'osfmk/kern/sched_dualq.c': '_sched_dualq_init',
                      'osfmk/kern/thread_act.c': '_thread_abort',
                      'osfmk/kern/processor.c': '_processor_bootstrap',
                      'libkern/os/refcnt.c': '_os_ref_init_count_internal',
                      'osfmk/ipc/ipc_space.c': '_ipc_space_create',
                      'osfmk/ipc/ipc_entry.c': '_ipc_entry_alloc',
                      'osfmk/ipc/ipc_importance.c': '_ipc_importance_init',
                      'osfmk/ipc/ipc_object.c': '_ipc_object_copyin',
                      'osfmk/ipc/ipc_port.c': '_ipc_port_alloc',
                      'osfmk/ipc/ipc_kmsg.c': '_ipc_kmsg_alloc',
                      'osfmk/ipc/ipc_mqueue.c': '_ipc_mqueue_init',
                      'osfmk/ipc/ipc_right.c': '_ipc_right_copyin',
                      'osfmk/kern/ipc_kobject.c': '_ipc_kobject_server',
                      'osfmk/kern/atlantic_thread_metadata.c': '_get_thread_ro',
                      'osfmk/ipc/mach_msg.c': '_mach_msg2_trap',
                      'osfmk/ipc/ipc_notify.c': '_ipc_notify_dead_name',
                      'osfmk/ipc/ipc_pset.c': '_ipc_pset_alloc',
                      'osfmk/ipc/ipc_eventlink.c': '_mach_eventlink_create',
                      'osfmk/ipc/ipc_voucher.c': '_ipc_voucher_init',
                      'osfmk/kern/ipc_mig.c': '_kernel_mach_msg_rpc',
                      'osfmk/kern/ipc_tt.c': '_ipc_task_init',
                      'osfmk/kern/ipc_host.c': '_ipc_host_init',
                      'osfmk/kern/ipc_clock.c': '_ipc_clock_init',
                      'osfmk/kern/host.c': '_host_info',
                      'osfmk/kern/host_notify.c': '_host_notify_calendar_change',
                      'osfmk/kern/sync_sema.c': '_semaphore_create',
                      'osfmk/vm/vm_memory_entry.c': '_mach_make_memory_entry_64',
                      'osfmk/vm/vm_upl.c': '_upl_commit_range',
                      'osfmk/vm/vm_user.c': '_mach_vm_allocate_external'}
EXPERIMENTAL_UNITS.update({
    'osfmk/ipc/mach_kernelrpc.c': '__kernelrpc_mach_vm_allocate_trap',
    'osfmk/ipc/ipc_hash.c': '_ipc_hash_lookup',
    'osfmk/ipc/ipc_service_port.c': '_ipc_service_port_label_alloc',
    'osfmk/ipc/mach_port.c': '_mach_port_allocate',
    'osfmk/kern/priority.c': '_sched_compute_timeshare_priority',
    'osfmk/kern/sched_average.c': '_compute_averages',
    'osfmk/kern/timer_call.c': '_timer_call_enter',
    'osfmk/kern/exception.c': '_exception_triage',
    'osfmk/kern/static_if_common.c': '_static_if_init',
    'osfmk/arm/locks_arm.c': '_arm_usimple_lock_init',
    'osfmk/arm64/copyio.c': '_copyin',
    'osfmk/arm/pmap/pmap_data.c': '_mapping_adjust',
    'osfmk/arm64/static_if.c': '_ml_static_if_entry_patch',
    'osfmk/vm/vm32_user.c': '_vm32_vm_allocate',
    'osfmk/vm/vm_sanitize.c': '_vm_sanitize_addr',
    'osfmk/vm/vm_sanitize_error_compat.c': '_VM_SANITIZE_CALLER_MACH_MAKE_MEMORY_ENTRY',
    'osfmk/vm/vm_map_store.c': '_vm_map_store_entry_link',
    'osfmk/vm/vm_map_store_rb.c': '_rb_head_RB_FIND',
    'osfmk/vm/vm_purgeable.c': '_vm_purgeable_object_purge_one',
    'osfmk/arm64/bcopy.s': '_memcpy',
    'osfmk/arm64/bzero.s': '_bzero',
    'osfmk/arm64/strnlen.s': '_strnlen',
    'osfmk/arm64/strncmp.s': '_strncmp',
    'osfmk/arm64/memcmp_zero.s': '_memcmp_zero_ptr_aligned',
    'osfmk/arm64/pcb.c': '_machine_thread_create',
    'osfmk/arm/machine_routines_common.c': '_machine_init',
    'osfmk/kern/ast.c': '_ast_taken_kernel',
    'osfmk/arm64/cpu.c': '_cpu_bootstrap',
    'osfmk/arm/cpu_common.c': '_cpu_broadcast_xcall',
    'osfmk/kern/lock_rw.c': '_lck_rw_lock_shared',
    'osfmk/kern/lock_mtx.c': '_lck_mtx_lock',
    'osfmk/kern/lock_ticket.c': '_hw_lck_ticket_init',
    'osfmk/kern/lock_ptr.c': '_hw_lck_ptr_init',
    'osfmk/kern/lock_group.c': '_lck_attr_alloc_init',
    'osfmk/kern/printf.c': '___doprnt',
    'osfmk/kern/debug.c': '_panic',
    'osfmk/kern/atlantic_printf.c': '_vsnprintf',
    'osfmk/vm/vm_pageout.c': '_vm_pageout',
    'osfmk/arm64/sleh.c': '_sleh_synchronous',
    'osfmk/arm/rtclock.c': '_rtclock_intr',
    'osfmk/kern/recount.c': '_recount_enter_interrupt',
    'osfmk/kern/clock_oldops.c': '_clock_get_time',
    'osfmk/arm/arm_timer.c': '_timer_intr',
    'osfmk/arm/data.s': '_RTClockData',
    'osfmk/arm/commpage/commpage.c': '_commpage_set_timestamp'})
EXPERIMENTAL_UNITS.update({
    'pexpert/gen/bootargs.c': '_PE_parse_boot_argn',
    'pexpert/arm/pe_bootargs.c': '_PE_boot_args',
    'pexpert/gen/device_tree.c': '_SecureDTInit',
    'osfmk/kern/sched_rt.c': '_sched_realtime_timebase_init',
    'osfmk/arm/preemption_disable.c': '__disable_preemption',
    'osfmk/kern/compact_id.c': '_compact_id_table_init',
    'osfmk/kern/mpsc_queue.c': '_thread_deallocate_daemon_init',
    'osfmk/kern/thread_group.c': '_thread_group_init',
    'osfmk/kern/restartable.c': '_restartable_init',
    'osfmk/kern/machine.c': '_processor_up',
    'osfmk/arm/cpu_common.c': '_cpu_machine_init',
    'osfmk/arm64/cpu.c': '_cpu_bootstrap',
    'osfmk/arm64/status.c': '_machine_thread_set_state',
    'osfmk/arm64/lowmem_vectors.c': '_patch_low_glo',
    'osfmk/kern/backtrace.c': '_backtrace',
    'osfmk/kern/btlog.c': '_btlog_create',
    'osfmk/kern/lock_mtx.c': '_lck_mtx_lock',
    'osfmk/arm/machine_cpuid.c': '_machine_read_midr',
    'bsd/kern/qsort.c': '_qsort'})
EXTRA_SYMBOLS.update({
    'pexpert/gen/bootargs.c': ['_PE_parse_boot_arg_str', '_PE_get_default'],
    'pexpert/gen/device_tree.c': ['_SecureDTLookupEntry', '_SecureDTGetProperty',
                                '_SecureDTInitEntryIterator', '_SecureDTIterateEntries'],
    'osfmk/kern/sched_rt.c': ['_sched_rt_choose_thread', '_rt_runq_insert', '_rt_runq_remove'],
    'osfmk/arm/preemption_disable.c': ['__enable_preemption', '_get_preemption_level'],
    'osfmk/kern/compact_id.c': ['_compact_id_get', '_compact_id_put', '_compact_id_resolve'],
    'osfmk/kern/mpsc_queue.c': ['_mpsc_daemon_enqueue', '_mpsc_daemon_queue_init_with_thread',
                             '_thread_deallocate_daemon_register_queue'],
    'osfmk/kern/thread_group.c': ['_thread_group_init_thread', '_thread_group_get'],
    'osfmk/kern/machine.c': ['_machine_info', '_processor_cpu_reinit'],
    'osfmk/arm/cpu_common.c': ['_CpuDataEntries', '_cpu_data_alloc', '_cpu_signal_handler'],
    'osfmk/arm64/cpu.c': ['_cpu_data_init', '_cpu_stack_alloc', '_cpu_timebase_init'],
    'osfmk/arm64/status.c': ['_machine_thread_get_state', '_machine_thread_reset_pc'],
    'osfmk/arm64/lowmem_vectors.c': ['_patch_low_glo_static_region'],
    'osfmk/kern/backtrace.c': ['_backtrace_packed', '_backtrace_unpack'],
    'osfmk/kern/btlog.c': ['_btref_get', '_btref_put', '_btlog_record'],
    'osfmk/kern/lock_mtx.c': ['_lck_mtx_init', '_lck_mtx_unlock'],
    'osfmk/arm/machine_cpuid.c': ['_machine_read_clidr', '_machine_read_ccsidr'],
    'bsd/kern/qsort.c': ['_kx_qsort']})
EXTRA_SYMBOLS.update({
    'osfmk/kern/debug.c': ['_panic_get_thread_proc_task', '_mach_assert_jump_key'],
    'osfmk/kern/atlantic_printf.c': ['_snprintf'],
    'osfmk/kern/lock_rw.c': ['_lck_rw_lock_exclusive', '_lck_rw_done', '_lck_rw_assert_jump_key'],
    'osfmk/arm/pmap/pmap_data.c': ['_pv_head_table', '_pp_attr_table'],
    'osfmk/arm/machine_routines_common.c': ['_ml_set_interrupts_enabled'],
    'osfmk/arm64/bcopy.s': ['_bcopy', '_memmove'],
    'osfmk/arm64/bzero.s': ['_memset'],
    'osfmk/arm64/strnlen.s': ['_strlen'],
    'osfmk/vm/vm32_user.c': ['_vm32_vm_read', '_vm32_vm_write'],
    'osfmk/arm64/static_if.c': ['_ml_static_if_flush_icache'],
    'osfmk/vm/vm_pageout.c': ['_upl_deallocate', '_upl_get_internal_page_list',
                            '_vm_object_upl_request', '_vm_object_iopl_request'],
    'osfmk/arm64/sleh.c': ['_sleh_synchronous_sp1', '_sleh_irq', '_sleh_fiq', '_sleh_serror',
                         '_panic_with_thread_kernel_state', '_thread_exception_return'],
    'osfmk/arm/rtclock.c': ['_mach_absolute_time', '_rtclock_init', '_rtclock_early_init', '_clock_timebase_info'],
    'osfmk/kern/recount.c': ['_recount_leave_interrupt', '_recount_thread_init', '_recount_task_init', '_recount_processor_init'],
    'osfmk/kern/clock_oldops.c': ['_clock_oldconfig', '_clock_oldinit', '_clock_alarm', '_clock_sleep_trap'],
    'osfmk/arm/arm_timer.c': ['_timer_resync_deadlines', '_timer_set_deadline'],
    'osfmk/arm/data.s': ['_intstack', '_excepstack', '_kd_early_buffer'],
    'osfmk/arm/commpage/commpage.c': ['_commpage_populate', '_commpage_update_active_cpus']})
EXTRA_SYMBOLS.update({
    'osfmk/kern/ipc_mig.c': ['_kernel_mach_msg_send'],
    'osfmk/kern/ipc_tt.c': ['_ipc_task_enable', '_ipc_task_terminate', '_convert_port_to_map'],
    'osfmk/kern/sync_sema.c': ['_semaphore_wait', '_semaphore_signal'],
    'osfmk/vm/vm_memory_entry.c': ['_mach_memory_entry_purgable_control'],
    'osfmk/vm/vm_upl.c': ['_upl_abort_range'],
    'osfmk/vm/vm_user.c': ['_mach_vm_deallocate', '_mach_vm_read', '_mach_vm_write']})
PROBES = ['osfmk/vm/vm_pageout.c']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_list(text, name):
    flat = text.replace('\\\n', ' ')
    match = re.search(r'^'+re.escape(name)+r'\s*=\s*([^\n]+)', flat, re.M)
    if not match:
        raise ValueError('Missing upstream literal list: '+name)
    values = match.group(1).split()
    if not values or any(not re.fullmatch(r'[A-Za-z0-9_.-]+', v) for v in values):
        raise ValueError('Nonliteral upstream list requires review: '+name)
    return values


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--windows-git', action='store_true')
    ap.add_argument('--probe-remaining', action='store_true',
                    help='Try the remaining pageout unit; failures return nonzero')
    ap.add_argument('--layout-compiler', type=Path,
                    help='Explicit experimental compiler; also builds selected Mach, VM and IPC core units')
    ap.add_argument('--layout-proof', type=Path,
                    help='Successful tools/test_atlantic_clang.py report for this compiler')
    args = ap.parse_args()
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        ap.error('Use Linux x86_64 or Debian/WSL')
    if bool(args.layout_compiler) != bool(args.layout_proof):
        ap.error('--layout-compiler and --layout-proof must be selected together')
    target_compiler = 'clang'
    provider = None
    if args.layout_compiler:
        target_compiler = str(args.layout_compiler.resolve(strict=True))
        proof = json.loads(args.layout_proof.read_text())
        required_inputs = ['compiler-port/SemaAtlanticLayout.cpp', 'compiler-port/ParseAtlanticLayout.inc',
            'compiler-port/patches.lock.json', 'tests/clang_layout/positive.c',
            'tests/clang_layout/negative.json', 'tools/test_atlantic_clang.py']
        inputs = {p: digest(ROOT/p) for p in required_inputs}
        cases = json.loads((ROOT/'tests/clang_layout/negative.json').read_text())
        expected = [('positive', 0, None), ('llvm-ir', 0, None)] + [
            (c['name'], 1, c['diagnostic']) for c in cases]
        outcomes = proof.get('outcomes', [])
        actual = [(c.get('name'), c.get('expected'), c.get('required_diagnostic')) for c in outcomes]
        if (proof.get('scope') != 'EXPERIMENTAL_C_LAYOUT_COMPILER_API_ONLY_NOT_XNU_OR_PHONE_EXECUTION' or
            proof.get('label') != 'HOST_TESTED' or proof.get('inputs') != inputs or
            proof.get('compiler_sha256') != digest(target_compiler) or actual != expected or
            any(c.get('passed') is not True or c.get('exit_code') != c.get('expected') for c in outcomes)):
            ap.error('Experimental compiler proof is stale, incomplete, or for another binary')
        compiler_lock = json.loads((ROOT/'compiler-port/patches.lock.json').read_text())
        compiler_patch = ROOT/'compiler-port/0001-add-atlantic-c-layout-primitives.patch'
        if digest(compiler_patch) != compiler_lock['patch_sha256']:
            ap.error('Compiler patch differs from the tested provenance lock')
        provider = {'api': 'ATLANTIC_C_LAYOUT_USAGE_V2_EXPERIMENTAL', 'compiler_sha256': digest(target_compiler),
                    'proof_sha256': digest(args.layout_proof), 'proof_inputs': inputs,
                    'compiler_patch_sha256': digest(compiler_patch), 'api_checks_passed': len(outcomes)}
    git = 'git.exe' if args.windows_git else 'git'
    for tool in [git, 'clang', 'bison', 'flex', 'csh', 'unifdef', 'perl', 'llvm-nm', 'llvm-size']:
        if not shutil.which(tool):
            ap.error('Missing build tool: '+tool)
    capability = subprocess.run([target_compiler, '--target=arm64-apple-macos11.0', '-nostdinc', '-fsyntax-only', '-x', 'c', '-'],
        input='#if !__has_builtin(__builtin_clzg) || !__has_builtin(__builtin_ctzg)\n'
              '#error This XNU revision requires generic count-leading/trailing-zero builtins (Clang 19+)\n#endif\n',
        text=True, capture_output=True, timeout=10)
    if capability.returncode:
        ap.error('Selected clang lacks required target builtins. Use Clang 19 or newer: '+capability.stderr)
    def path_arg(p):
        return subprocess.check_output(['wslpath', '-w', str(p)], text=True).strip() if args.windows_git else str(p)
    def scm(folder, *argv):
        return subprocess.check_output([git, '-c', 'core.autocrlf=true', '-C', path_arg(folder), *argv], timeout=60)
    lock = json.loads((ROOT/'dependencies.lock.json').read_text())
    pristine = ROOT/'xnu-upstream'
    if scm(pristine, 'rev-parse', 'HEAD').decode().strip() != lock['xnu']['commit'] or scm(pristine, 'status', '--porcelain'):
        ap.error('Preserve upstream: source must match its lock and be pristine')
    series = [s.strip() for s in (ROOT/'xnu-port/series').read_text().splitlines() if s.strip() and not s.startswith('#')]
    if not series or any(not re.fullmatch(r'[a-z0-9-]+\.patch', s) for s in series):
        ap.error('Invalid patch series')
    patches = {s: digest(ROOT/'xnu-port'/s) for s in series}
    port_id = hashlib.sha256(json.dumps({'upstream': lock['xnu']['commit'], 'series': list(patches.items())}, sort_keys=True).encode()).hexdigest()
    source = ROOT/'work/xnu-lab-sources'/port_id[:16]
    stamp = source.parent/(source.name+'.json')
    source.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        subprocess.run([git, 'clone', '--shared', '--no-checkout', path_arg(pristine), path_arg(source)], check=True, timeout=60)
        subprocess.run([git, '-C', path_arg(source), 'config', 'core.autocrlf', 'false'], check=True, timeout=10)
        subprocess.run([git, '-C', path_arg(source), 'checkout', '--detach', lock['xnu']['commit']], check=True, timeout=60)
        for name in series:
            subprocess.run([git, '-C', path_arg(source), 'apply', '--index', '--whitespace=nowarn', path_arg(ROOT/'xnu-port'/name)], check=True, timeout=15)
        diff_hash = hashlib.sha256(scm(source, 'diff', '--cached', '--binary', 'HEAD')).hexdigest()
        stamp.write_text(json.dumps({'port_id': port_id, 'diff_sha256': diff_hash})+'\n', encoding='utf-8', newline='\n')
    if not stamp.is_file():
        ap.error('Preserve incomplete source preparation; inspect it manually')
    prepared = json.loads(stamp.read_text())
    if (prepared['port_id'] != port_id or
        scm(source, 'rev-parse', 'HEAD').decode().strip() != lock['xnu']['commit'] or
        hashlib.sha256(scm(source, 'diff', '--cached', '--binary', 'HEAD')).hexdigest() != prepared['diff_sha256'] or
        scm(source, 'diff', '--name-only') or b'?? ' in scm(source, 'status', '--porcelain')):
        ap.error('Preserve prepared source: unexpected local changes')
    patch_lock = json.loads((ROOT/'xnu-port/patches.lock.json').read_text())
    if patch_lock['port_id'] != port_id or patch_lock['patches'] != patches or patch_lock['upstream_commit'] != lock['xnu']['commit']:
        ap.error('Patch provenance lock does not match this series')
    for item in patch_lock['canonical_lf_files']:
        if digest(source/item['path']) != item['postimage_sha256']:
            ap.error('Patched file differs from recorded postimage: '+item['path'])
        if item['preimage_sha256'] is not None and hashlib.sha256(scm(source, 'show', 'HEAD:'+item['path'])).hexdigest() != item['preimage_sha256']:
            ap.error('Upstream preimage mismatch: '+item['path'])
    native_lock_path = ROOT/'xnu-port/task-metadata-native.lock.json'
    native_lock = json.loads(native_lock_path.read_text())
    if native_lock['upstream_commit'] != lock['xnu']['commit'] or not native_lock['functions']:
        ap.error('Native metadata provenance must match pinned XNU')
    for item in native_lock['functions']:
        lines = scm(source, 'show', 'HEAD:'+item['source']).decode().splitlines(True)
        body = ''.join(lines[item['first_line']-1:item['last_line']]).rstrip('\n')+'\n\n'
        if (hashlib.sha256(body.encode()).hexdigest() != item['sha256'] or
            (source/item['destination']).read_text().count(body) != 1):
            ap.error('Native metadata body changed: '+item['destination'])
    printf_lock_path = ROOT/'xnu-port/printf-native.lock.json'
    printf_lock = json.loads(printf_lock_path.read_text())
    if printf_lock['upstream_commit'] != lock['xnu']['commit'] or len(printf_lock['fragments']) != 4:
        ap.error('Native formatting provenance must match pinned XNU')
    for item in printf_lock['fragments']:
        lines = scm(source, 'show', 'HEAD:'+item['source']).decode().splitlines(True)
        body = ''.join(lines[item['first_line']-1:item['last_line']]).rstrip('\n')+'\n\n'
        if (hashlib.sha256(body.encode()).hexdigest() != item['sha256'] or
            (source/item['destination']).read_text().count(body) != 1):
            ap.error('Native formatting fragment changed: '+item['name'])
    mig_dir = ROOT/'work/mig-host'
    mig_report = json.loads((mig_dir/'report.json').read_text())
    if mig_report['bootstrap_commit'] != lock['mig_host_tool']['commit'] or digest(mig_dir/'migcom') != mig_report['migcom_sha256']:
        ap.error('Rebuild the pinned official MIG host tool')
    for name, sha in mig_report['source_sha256'].items():
        if digest(ROOT/name) != sha:
            ap.error('MIG host adaptation changed; rebuild it first')
    build_inputs = {'tools/build_xnu_lab.py': digest(__file__),
                    'tools/xnu_assym.py': digest(ROOT/'tools/xnu_assym.py'),
                    'xnu-port/patches.lock.json': digest(ROOT/'xnu-port/patches.lock.json'),
                    'xnu-port/task-metadata-native.lock.json': digest(native_lock_path),
                    'xnu-port/printf-native.lock.json': digest(printf_lock_path),
                    'xnu-port/config/'+PROFILE.name: digest(PROFILE),
                    'tests/xnu_port/boot_abi.c': digest(ROOT/'tests/xnu_port/boot_abi.c'),
                    'tests/xnu_port/assym_abi.c': digest(ROOT/'tests/xnu_port/assym_abi.c')}
    if provider:
        build_inputs['tests/xnu_port/kalloc_layout.c'] = digest(ROOT/'tests/xnu_port/kalloc_layout.c')
    build_id = hashlib.sha256(json.dumps({'port_id': port_id, 'inputs': build_inputs,
        'layout_provider': provider, 'probe_remaining': args.probe_remaining}, sort_keys=True).encode()).hexdigest()
    out = ROOT/'work/xnu-lab-builds'/build_id[:16]
    out.mkdir(parents=True, exist_ok=True)
    commands, steps = [], []
    def run(command, *, cwd=ROOT, env=None, data=None, expected=0, name='step'):
        r = subprocess.run(command, cwd=cwd, env=env, input=data, text=True, capture_output=True, timeout=60)
        commands.append([str(s).replace(str(ROOT), '<ROOT>') for s in command])
        log = out/(name+'.log')
        log.write_text(r.stdout+r.stderr, encoding='utf-8', newline='\n')
        steps.append({'name': name, 'exit_code': r.returncode, 'expected': expected, 'log': log.name})
        if r.returncode != expected:
            raise RuntimeError(name+' failed: '+r.stderr[-2000:])
        return r
    # Build the official config program, retaining its source and license notices.
    host = out/'config-host';host.mkdir(exist_ok=True)
    conf_src = source/'SETUP/config'
    run(['bison', '-y', '-d', '-o', str(host/'parser.c'), str(conf_src/'parser.y')], name='config-bison')
    run(['flex', '--header-file='+str(host/'lexer.yy.h'), '-o', str(host/'lexer.yy.c'), str(conf_src/'lexer.l')], name='config-flex')
    csrc = [str(conf_src/n) for n in ['externs.c','main.c','mkheaders.c','mkioconf.c','mkmakefile.c','openp.c','searchp.c']]
    csrc += [str(host/'parser.c'), str(host/'lexer.yy.c')]
    program = out/'obj/SETUP/config/config';program.parent.mkdir(parents=True, exist_ok=True)
    run(['clang', '-std=gnu11', '-DYY_NO_INPUT', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
         '-I'+str(conf_src), '-I'+str(host), *csrc, '-o', str(program)], name='config-build')
    masters = out/'masters';masters.mkdir(exist_ok=True)
    shutil.copyfile(source/'config/MASTER', masters/'MASTER')
    shutil.copyfile(PROFILE, masters/PROFILE.name)
    config = out/'config';config.mkdir(exist_ok=True)
    # doconf can mask config failures; do not accept these outputs from an old run.
    for name in ['meta_features.h', 'Makefile']:
        (config/name).unlink(missing_ok=True)
    env = dict(os.environ, OBJROOT=str(out/'obj'), SRCROOT=str(source), SOURCE=str(source/'osfmk/conf')+'/', ASAN_OPTIONS='detect_leaks=0')
    run(['csh', '-f', str(conf_src/'doconf'), '-c', '-cpu', 'arm64', '-soc', 'atlanticlab', '-platform', 'AtlanticOS',
         '-d', str(config), '-s', str(source/'osfmk/conf'), '-m', str(masters), 'ATLANTIC'], env=env, name='config-generate')
    if not (config/'meta_features.h').is_file() or not (config/'Makefile').is_file():
        raise RuntimeError('doconf can mask config failures; required outputs are missing')
    line = next(s for s in (config/'Makefile').read_text().splitlines() if s.startswith('export CONFIG_DEFINES ='))
    defines = shlex.split(line.split('=',1)[1])
    if '-DCONFIG_ATLANTIC_FIRMWARE' not in defines or any(v in defines for v in ['-DMACH_BSD','-DIOKIT','-DLIBKERNCPP']):
        raise RuntimeError('Unexpected firmware feature selection')
    inc = out/'include';(inc/'mach').mkdir(parents=True, exist_ok=True)
    for sub in ['memory', 'coverage']:
        (inc/'san').mkdir(exist_ok=True)
        for h in (source/'san'/sub).glob('*.h'):
            shutil.copyfile(h, inc/'san'/h.name)
    # Match actual upstream MIG sender and kernel-server header roles.
    base = ['clang', '--target=arm64-apple-macos11.0', '-E', '-x', 'c', '-D__MIG__', '-DAPPLE', '-DKERNEL',
            '-DPRIVATE', '-DKERNEL_PRIVATE', '-DXNU_KERNEL_PRIVATE', '-DMACH_KERNEL_PRIVATE', *defines]
    base += ['-I'+str(source/p) for p in ['osfmk','bsd','EXTERNAL_HEADERS']]
    mk = (source/'osfmk/mach/Makefile').read_text()
    generated = []
    generated_roles = {}
    declared_kernel_senders = make_list(mk, 'MIG_KUHDRS')
    # Internal sender headers are also emitted as side effects of MIG_KUSRC.
    # Generate every native variant before compiling callers against them.
    kernel_senders = [name.removesuffix('_user.c')+'.h' for name in make_list(mk, 'MIG_KUSRC')]
    if not set(declared_kernel_senders).issubset(kernel_senders):
        raise RuntimeError('Native kernel sender header/source lists disagree')
    groups = [('MIG_UUHDRS', 'sender'), ('MIG_KSHDRS', 'kernel-server')]
    for variable, role in groups:
        for header in make_list(mk, variable):
            # Native kernel-user output takes precedence over public sender
            # headers with the same name, as explained in mach/Makefile.
            if role == 'sender' and header in kernel_senders:
                continue
            module = header.removesuffix('_server.h') if role == 'kernel-server' else header.removesuffix('.h')
            flags = ['-DKERNEL_SERVER=1'] if role == 'kernel-server' else []
            cpp = run([*base, *flags, str(source/('osfmk/mach/'+module+'.defs'))], name='cpp-'+header)
            destination = inc/'mach'/header
            opts = ['-mach_msg2'] if role == 'kernel-server' else []
            run([str(mig_dir/'migcom'), '-novouchers', *opts, '-header', str(destination) if role=='sender' else '/dev/null',
                 '-sheader', str(destination) if role=='kernel-server' else '/dev/null', '-server', '/dev/null', '-user', '/dev/null'],
                cwd=out, data=cpp.stdout, name='mig-'+header)
            generated.append(destination)
            generated_roles[destination] = role
    # Kernel sender roles follow the complete literal upstream list.
    for header in kernel_senders:
        module = header.removesuffix('.h')
        cpp = run([*base, '-DKERNEL_USER=1', str(source/('osfmk/mach/'+module+'.defs'))], name='cpp-'+module)
        resource = inc/'mach'/header
        run([str(mig_dir/'migcom'), '-novouchers', '-maxonstack', '1024', '-header', str(resource), '-server', '/dev/null', '-user', '/dev/null'],
            cwd=out, data=cpp.stdout, name='mig-'+module)
        generated.append(resource)
        generated_roles[resource] = 'kernel-sender'
    # IPC references the native device kernel-server declarations even when
    # IOKIT is absent. Generate the actual selected interface, never a stub.
    device_mk = (source/'osfmk/device/Makefile').read_text()
    if make_list(device_mk, 'DEVICE_FILES') != ['device_server.h', 'device_server.c']:
        raise RuntimeError('Native device server recipe changed')
    (inc/'device').mkdir(exist_ok=True)
    device_header = inc/'device/device_server.h'
    cpp = run([*base, '-DKERNEL_SERVER=1', str(source/'osfmk/device/device.defs')], name='cpp-device-server')
    run([str(mig_dir/'migcom'), '-novouchers', '-mach_msg2', '-header', '/dev/null',
         '-sheader', str(device_header), '-server', '/dev/null', '-user', '/dev/null'],
        cwd=out, data=cpp.stdout, name='mig-device-server')
    generated.append(device_header)
    generated_roles[device_header] = 'kernel-server'
    if len(generated) != len(set(generated)):
        raise RuntimeError('Duplicate generated header destinations')
    # Use upstream's real version template/generator with explicit build metadata.
    version = inc/'libkern/version.h';version.parent.mkdir(exist_ok=True)
    shutil.copyfile(source/'libkern/libkern/version.h.template', version)
    (out/'xnuVersion').write_text('25.0.0\n', encoding='utf-8', newline='\n')
    venv = dict(os.environ, SRCROOT=str(source), OBJROOT=str(out), TARGET=str(out), CURRENT_KERNEL_CONFIG_LC='atlantic-lab',
                KERNEL_BUILD_DATE='SOURCE_DATE_EPOCH=0', KERNEL_BUILD_OBJROOT='AtlanticOS-laboratory')
    run(['perl', str(source/'config/newvers.pl'), str(version)], cwd=out, env=venv, name='version-generate')
    clang_resource = subprocess.check_output([target_compiler,'-print-resource-dir'], text=True).strip()
    target = [target_compiler, '--target=arm64-apple-macos11.0', '-mcpu=cortex-a57', '-std=gnu11', '-ffreestanding', '-nostdinc',
              '-fno-builtin', '-fno-stack-protector', '-mkernel', '-fblocks', '-O1', '-g', '-Darm64', '-DARM64', '-D__ARM64__',
              '-DLP64', '-DPAGE_SIZE_FIXED', '-DVM_KERNEL_LINK_ADDRESS=0xfffffff007004000',
              '-DPRIVATE', '-DAPPLE', '-D__MACHO__=1', '-DXNU_KERN_EVENT_DATA_IS_VLA',
              '-DKERNEL', '-DKERNEL_PRIVATE', '-DXNU_KERNEL_PRIVATE', '-DMACH_KERNEL_PRIVATE', '-DMACH_KERNEL',
              '-DARM64_BOARD_CONFIG_ATLANTIC_LAB', '-include', str(config/'meta_features.h'),
              '-ffile-prefix-map='+str(ROOT)+'=.', '-fdebug-compilation-dir=.', '-I'+str(config), '-I'+str(inc)]
    target += ['-I'+str(source/p) for p in ['osfmk','bsd','pexpert','libkern','iokit','osfmk/libsa','libsa','EXTERNAL_HEADERS','.']]
    target += ['-isystem', clang_resource+'/include', *defines]
    if provider:
        target += ['-DCONFIG_ATLANTIC_C_LAYOUT=1']
        layout_fixture = str(ROOT/'tests/xnu_port/kalloc_layout.c')
        run([*target, '-c', layout_fixture, '-o', str(out/'kalloc-layout.o')], name='kalloc-layout')
        rejection = run([*target, '-DATL_TEST_BAD_POINTER=1', '-fsyntax-only', layout_fixture],
                        expected=1, name='reject-kalloc-layout-pointer')
        if 'Pointer type is not compatible with specified type' not in rejection.stderr:
            raise RuntimeError('Wrong incompatible-pointer rejection reason')
        rejection = run([*target, '-DATL_TEST_BAD_TRAILING_DATA=1', '-fsyntax-only', layout_fixture],
                        expected=1, name='reject-kalloc-data-trailer')
        if 'cannot allocate data-only array' not in rejection.stderr:
            raise RuntimeError('Wrong data-only trailer rejection reason')
        rejection = run([*target, '-DATL_TEST_BAD_ADDRESS_USAGE=1', '-fsyntax-only', layout_fixture],
                        expected=1, name='reject-kalloc-address-usage')
        if 'Pointer type is not compatible with specified type' not in rejection.stderr:
            raise RuntimeError('Wrong address-usage rejection reason')
    # A stock compiler must not silently accept the opt-in metadata provider.
    rejection = run(['clang', *target[1:], '-DCONFIG_ATLANTIC_C_LAYOUT=1', '-E', '-x', 'c', '-'],
                    data='#include <kern/kalloc.h>\n', expected=1, name='reject-untested-layout-provider')
    if 'requires the tested AtlanticOS compiler API v2' not in rejection.stderr:
        raise RuntimeError('Wrong compiler-provider rejection reason')
    abi = run([*target, '-c', str(ROOT/'tests/xnu_port/boot_abi.c'), '-o', str(out/'boot-abi.o')], name='boot-abi')
    # Generate assembler offsets with the target compiler, never a host ABI.
    genassym = out/'genassym.s'
    run([*target, '-fno-integrated-as', '-S', str(source/'osfmk/arm64/genassym.c'), '-o', str(genassym)], name='genassym')
    assym_values = parse_assym(genassym.read_text(), required=['TH_KSTACKPTR','ACT_CPUDATAP','CPU_ACTIVE_THREAD',
        'SS64_KERNEL_SP','NS64_KERNEL_D8','BA_VIRT_BASE','BA_PHYS_BASE','BA_BOOT_FLAGS'])
    assym = inc/'assym.s'
    assym.write_text(render_assym(assym_values), encoding='utf-8', newline='\n')
    (inc/'assym-check.h').write_text(render_assym(assym_values, prefix='ATL_ASSYM_'), encoding='utf-8', newline='\n')
    run([*target, '-c', str(ROOT/'tests/xnu_port/assym_abi.c'), '-o', str(out/'assym-abi.o')], name='assym-abi')
    bad_assym = out/'invalid-assym';bad_assym.mkdir(exist_ok=True)
    wrong = dict(assym_values);wrong['TH_KSTACKPTR'] += 1
    (bad_assym/'assym-check.h').write_text(render_assym(wrong, prefix='ATL_ASSYM_'), encoding='utf-8', newline='\n')
    rejection = run([target[0], '-I'+str(bad_assym), *target[1:], '-c', str(ROOT/'tests/xnu_port/assym_abi.c'),
                     '-o', str(out/'invalid-assym.o')], expected=1, name='reject-assym-offset')
    if 'TH_KSTACKPTR target layout' not in rejection.stderr:
        raise RuntimeError('Wrong generated-offset rejection reason')
    # Reject accidental PMU enablement and forbidden BSD/IOKit composition.
    bad = '#undef CONFIG_CPU_COUNTERS\n#define CONFIG_CPU_COUNTERS 1\n#include <pexpert/arm64/board_config.h>\n'
    rejection = run([*target, '-E', '-x', 'c', '-'], data=bad, expected=1, name='reject-pmu')
    if 'laboratory PMU backend is not implemented' not in rejection.stderr:
        raise RuntimeError('Wrong PMU rejection reason')
    for feature in ['MACH_BSD','IOKIT']:
        rejection = run([*target, '-E', '-x', 'c', '-'], data='#define '+feature+' 1\n#include <kern/startup.c>\n',
                        expected=1, name='reject-'+feature.lower())
        if 'firmware profile excludes BSD userland and IOKit' not in rejection.stderr:
            raise RuntimeError('Wrong forbidden composition rejection reason')
    objects, failures = [], []
    selected_units = dict(UNITS)
    if provider:
        selected_units.update(EXPERIMENTAL_UNITS)
    units = list(selected_units) + ([p for p in PROBES if p not in selected_units] if args.probe_remaining else [])
    for rel in units:
        obj = out/(Path(rel).stem+'.o')
        # This flag is mandated for VM sources by upstream Makefile.template.
        per_file = ['-DVM_UNSAFE_TYPES'] if rel.startswith('osfmk/vm/') else []
        if rel in {'osfmk/kern/atlantic_task_metadata.c', 'libkern/os/refcnt.c'}:
            # Match the real BSD-private header context, without BSD userland.
            per_file += ['-UMACH_KERNEL_PRIVATE', '-DBSD_KERNEL_PRIVATE=1']
        if rel.startswith('pexpert/'):
            # pexpert/conf/Makefile.template selects this component's private
            # context. Mach-private clock_t/libsa types conflict with BSD types.
            per_file += ['-UMACH_KERNEL_PRIVATE', '-DPEXPERT_KERNEL_PRIVATE=1']
        if rel.startswith('bsd/'):
            # A native BSD library helper does not enable MACH_BSD userland.
            per_file += ['-UMACH_KERNEL_PRIVATE', '-DBSD_KERNEL_PRIVATE=1']
        if rel.endswith('.s'):
            # Match upstream SFLAGS_GEN, including the non-Clang ASSEMBLER guard.
            per_file += ['-DASSEMBLER', '-D__ASSEMBLER__', '-x', 'assembler-with-cpp']
        cmd = [*target, *per_file, '-c', str(source/rel), '-o', str(obj)]
        r = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=60)
        commands.append([str(s).replace(str(ROOT),'<ROOT>') for s in cmd])
        log = out/(obj.stem+'.log');log.write_text(r.stdout+r.stderr, encoding='utf-8', newline='\n')
        if r.returncode:
            failures.append({'source':rel,'exit_code':r.returncode,'log':log.name,
                             'diagnostics':[s.replace(str(ROOT),'<ROOT>') for s in r.stderr.splitlines() if 'error:' in s]})
            print(json.dumps(failures[-1]), flush=True)
            continue
        raw = obj.read_bytes()
        if len(raw)<32 or struct.unpack_from('<4I',raw) != (0xfeedfacf,0x100000c,0,1):
            raise RuntimeError('Expected AArch64 Mach-O object, not a kernel image')
        nm = run(['llvm-nm','--defined-only',str(obj)],name=obj.stem+'-defined').stdout
        required_symbols = ([selected_units[rel]]+EXTRA_SYMBOLS.get(rel, [])) if rel in selected_units else []
        binding = SYMBOL_TYPES.get(rel, 'T')
        if rel in selected_units and not any(line.split()[-2:]==[binding, selected_units[rel]] for line in nm.splitlines()):
            raise RuntimeError('Expected native symbol and binding: '+selected_units[rel])
        for symbol in required_symbols:
            if not any(line.split()[-1:]==[symbol] for line in nm.splitlines()):
                raise RuntimeError('Missing native XNU definition: '+symbol)
        if rel in STARTUP_SYMBOL_PREFIXES and not any(
            line.split()[-1].startswith(STARTUP_SYMBOL_PREFIXES[rel]) for line in nm.splitlines() if line.split()):
            raise RuntimeError('Genuine static IPC initializer lost its startup registration: '+rel)
        if rel == 'osfmk/arm/pmap/pmap.c' and any('trust_cache' in line or '_amfi' in line or '_sart_' in line
            for line in nm.splitlines()):
            raise RuntimeError('Unexpected Apple monitor/trust-cache provider in firmware pmap')
        undefined = run(['llvm-nm','--undefined-only',str(obj)],name=obj.stem+'-undefined').stdout.splitlines()
        exported = run(['llvm-nm','--extern-only','--defined-only','--format=posix',str(obj)],
                       name=obj.stem+'-exports').stdout.splitlines()
        exported = [s.split()[0] for s in exported if s.split()]
        if rel.endswith('/startup.c') and not {'_vm_mem_bootstrap','_sched_init','_task_init','_thread_init'}.issubset(set(undefined)):
            raise RuntimeError('Bootstrap no longer references substantive Mach initialization')
        if rel.endswith('/startup.c') and any('trust_cache' in s or 'code_signing_init' in s for s in undefined):
            raise RuntimeError('Unexpected Apple userland trust-cache dependency in firmware bootstrap')
        objects.append({'source':rel,'source_sha256':digest(source/rel),'object':obj.name,'object_sha256':digest(obj),
                        'object_file_bytes':len(raw),'required_symbol':selected_units.get(rel),'required_symbol_type':binding,
                        'required_symbols':required_symbols,
                        'defined_external_symbols':exported,'undefined_symbols':undefined})
    selected_definitions = {s for item in objects for s in item['defined_external_symbols']}
    missing_symbols = sorted({s for item in objects for s in item['undefined_symbols']} - selected_definitions)
    report = {'schema_version':1,'label':'BUILT_ARM64','scope':'REAL_XNU_CORE_OBJECTS_ONLY_NOT_LINKED_OR_EXECUTED',
              'upstream_commit':lock['xnu']['commit'],'patches':patches,'port_id':port_id,'build_id':build_id,
              'inputs':build_inputs,'profile':'atlanticlab','config_makefile_sha256':digest(config/'Makefile'),
              'kernel_linked':False,'xnu_executed':False,'phone_accessed':False,
              'object_sizes_are_not_runtime_ram':True,'host_generator_sanitizers':['address','undefined'],
              'host_generator_leak_check':False,'selected_defines':defines,'commands':commands,'steps':steps,
              'compiler':subprocess.check_output([target_compiler,'--version'],text=True).splitlines()[0],
              'layout_provider':provider,
              'generator_versions':{name:subprocess.check_output([name,'--version'],text=True).splitlines()[0]
                                    for name in ['bison','flex','csh']},
              'config_headers':[{'path':p.relative_to(out).as_posix(),'sha256':digest(p)} for p in sorted(config.glob('*.h'))],
              'version_header_sha256':digest(version),
              'assym':{'source_sha256':digest(source/'osfmk/arm64/genassym.c'),'assembly_sha256':digest(genassym),
                       'header_sha256':digest(assym),'definitions':assym_values,'extraction':'strict-decimal-ascii-no-fallback',
                       'target_layout_assertions_passed':True},
              'virtual_link_address':'0xfffffff007004000','physical_link_or_load_address':None,
              'selected_object_symbol_inventory':{'scope':'NAME_INVENTORY_ONLY_NOT_A_LINK_OR_RELOCATION_CHECK',
                  'defined_external_count':len(selected_definitions),'unprovided_symbols':missing_symbols},
              'generated_headers':[{'path':p.relative_to(out).as_posix(),'sha256':digest(p),
                                    'role':generated_roles[p]} for p in generated],
              'objects':objects,'failed_units':failures}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'label':report['label'],'compiler':report['compiler'],'compiled_units':len(objects),'failed_units':len(failures),
                      'kernel_linked':False,'xnu_executed':False,'report':str(out/'report.json')}))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
