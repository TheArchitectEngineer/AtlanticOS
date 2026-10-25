SOURCE_DIR=/mnt/g/AtlanticOS/work/xnu-lab-sources/25598af2b83969b1
export CONFIG_DEFINES = -DMACH -DMULTICAST -DCONFIG_KN_HASHSIZE="48" -DCONFIG_NC_HASH="2048" -DCONFIG_VFS_NAMES="3072" -DCONFIG_MAX_CLUSTERS="4" -DCONFIG_MIN_NBUF="80" -DCONFIG_MIN_NIOBUF="64" -DCONFIG_NMBCLUSTERS="((1024 * 256) / MCLBYTES)" -DCONFIG_TCBHASHSIZE="128" -DCONFIG_AIO_MAX="20" -DCONFIG_AIO_PROCESS_MAX="8" -DCONFIG_AIO_THREAD_COUNT="2" -DCONFIG_MAXVIFS="16" -DCONFIG_MFCTBLSIZ="128" -DCONFIG_MSG_BSIZE_REL="16384" -DCONFIG_MSG_BSIZE_DEV="131072" -DCONFIG_MSG_BSIZE="CONFIG_MSG_BSIZE_DEV" -DCONFIG_IPC_TABLE_ENTRIES_SIZE_MAX="3145728" -DCONFIG_IPC_TABLE_REQUEST_SIZE_MAX="1048576" -DCONFIG_IPC_KERNEL_MAP_SIZE="32" -DCONFIG_EMBEDDED -DCONFIG_PMAP_PPL -DNOS_ARM_ASM -DNOS_ARM_PMAP -DCONFIG_MAX_THREADS="500" -DCONFIG_BLOCKS -DDEVELOPMENT -DCONFIG_THREAD_MAX="1536" -DCONFIG_TASK_MAX="512" -DCONFIG_ZONE_MAP_MIN="120586240" -DCONFIG_SCHED_TIMESHARE_CORE -DCONFIG_SCHED_DEFERRED_AST -DCONFIG_TASKWATCH -DCONFIG_COALITIONS -DSERIAL_CONSOLE -DVIDEO_CONSOLE -DCONFIG_ATLANTIC_FIRMWARE
OSFMK_MACHINE=arm64
#
# Mach Operating System
# Copyright (c) 1986 Carnegie-Mellon University
# All rights reserved.  The CMU software License Agreement specifies
# the terms and conditions for use and redistribution.
#

export MakeInc_cmd=${SRCROOT}/makedefs/MakeInc.cmd
export MakeInc_def=${SRCROOT}/makedefs/MakeInc.def
export MakeInc_rule=${SRCROOT}/makedefs/MakeInc.rule
export MakeInc_dir=${SRCROOT}/makedefs/MakeInc.dir

include $(MakeInc_cmd)
include $(MakeInc_def)

#
# XXX: CFLAGS
#
CFLAGS+= -include meta_features.h -DMACH_KERNEL_PRIVATE -DMACH_KERNEL
SFLAGS+= -include meta_features.h

ifeq ($(KSANCOV),1)
# Don't instrument functions called by the ksancov runtime. SanitizeCoverage does
# not support denylists, so exclude the whole file.
machine_routines.o_CFLAGS_RM = $(KCOV_CFLAGS)
machine_routines_common.o_CFLAGS_RM = $(KCOV_CFLAGS)
pcb_native.o_CFLAGS_RM = $(KCOV_CFLAGS)
endif

#
# XXX: INCFLAGS to include libsa prototypes
#
INCFLAGS_MAKEFILE= -I$(SOURCE)libsa

#
# Directories for generated files
#
COMP_SUBDIRS = \
	atm \
	default_pager \
	device \
	kern \
	mach \
	UserNotification \
	gssd \
	kextd \
	lockd

#
#  Make sure we don't remove this by accident if interrupted at the wrong
#  time.
#
.PRECIOUS: Makefile

#
#  Theses macros are filled in by the config program depending on the
#  current configuration.  The MACHDEP macro is replaced by the
#  contents of the machine dependent makefile template and the others
#  are replaced by the corresponding symbol definitions for the
#  configuration.
#

OBJS=gssd_mach.o lockd_mach.o KUNCUserNotifications.o kern_stackshot.o \
	testpoints.o exclaves_test_stackshot.o kdp_common.o ipc_entry.o \
	ipc_eventlink.o ipc_hash.o ipc_importance.o ipc_init.o \
	ipc_kmsg.o ipc_mqueue.o ipc_notify.o ipc_object.o ipc_policy.o \
	ipc_port.o ipc_pset.o ipc_right.o ipc_space.o ipc_service_port.o \
	ipc_voucher.o mach_debug.o mach_kernelrpc.o mach_msg.o \
	mach_port.o affinity.o ast.o backtrace.o btlog.o build_config.o \
	clock.o clock_oldops.o coalition.o compact_id.o core_analytics.o \
	counter_common.o debug.o ext_paniclog.o energy_perf.o \
	exception.o exclaves.o exclaves_aoe.o exclaves_boot.o \
	exclaves_conclave.o exclaves_driverkit.o exclaves_frame_mint.o \
	exclaves_inspection.o exclaves_log.o exclaves_memory.o \
	exclaves_panic.o exclaves_resource.o exclaves_sensor.o \
	exclaves_shared_memory.o exclaves_storage.o exclaves_tests.o \
	exclaves_upcalls.o exclaves_xnuproxy.o extmod_statistics.o \
	host.o host_notify.o ipc_clock.o ipc_host.o ipc_kobject.o \
	ipc_mig.o ipc_misc.o ipc_tt.o kalloc.o kern_apfs_reflock.o \
	ktrace_background_notify.o ledger.o lock_group.o lock_mtx.o \
	lock_ptr.o lock_rw.o lock_ticket.o locks.o machine.o mk_sp.o \
	mk_timer.o mpsc_ring.o mpsc_queue.o page_decrypt.o printf.o \
	priority.o processor.o recount.o restartable.o sched_average.o \
	sched_amp.o sched_amp_common.o sched_common.o sched_dualq.o \
	sched_prim.o sched_rt.o sfi.o smr.o stack.o startup.o \
	static_if_common.o sync_sema.o syscall_subr.o syscall_sw.o \
	task.o task_policy.o task_ref.o test_lock.o test_mpsc_queue.o \
	thread.o thread_act.o thread_call.o thread_group.o \
	thread_policy.o thread_test_context.o timeout.o timer.o \
	timer_call.o turnstile.o ux_handler.o waitq.o work_interval.o \
	workload_config.o zalloc.o zalloc_bounds.o remote_time.o \
	memset_s.o task_ident.o socd_client.o clock_server.o \
	clock_reply_user.o exc_user.o mach_eventlink_server.o \
	host_priv_server.o ktrace_background_user.o mach_exc_user.o \
	mach_host_server.o mach_notify_user.o mach_port_server.o \
	mach_vm_server.o mach_voucher_server.o memory_entry_server.o \
	resource_notify_user.o restartable_server.o \
	audit_triggers_user.o task_access_user.o corpse.o kern_cdata.o \
	vm_parameter_validation_kern.o bcopy_test.o bank.o \
	coalition_notification_user.o vfs_nspace_user.o \
	doubleagent_mig_user.o processor_server.o processor_set_server.o \
	task_server.o thread_act_server.o vm32_map_server.o \
	mach_test_upcall_user.o analytics.o vm_sanitize_telemetry.o \
	vm_compressor.o vm_compressor_pager.o \
	vm_compressor_backing_store.o vm_compressor_algorithms.o lz4.o \
	device_vm.o memory_object.o vm_debug.o vm_fault.o vm_init.o \
	vm_kern.o vm_map.o vm_map_store.o vm_map_store_ll.o \
	vm_map_store_rb.o vm_memory_entry.o vm_memtag.o vm_object.o \
	vm_pageout.o vm_pmap.o vm_purgeable.o vm_resident.o \
	vm_shared_region.o vm_shared_region_pager.o vm_dyld_pager.o \
	vm_swapfile_pager.o vm_upl.o vm_user.o vm32_user.o vm_sanitize.o \
	vm_sanitize_error_compat.o kext_alloc.o kmod.o subrs.o \
	kpc_common.o cpc.o serial_general.o serial_console.o \
	video_scroll.o video_console.o cc_clear.o cc_cmp_safe.o \
	cc_abort.o cc_try_abort.o cc_dit.o cccbc.o ccdrbg.o \
	ccdrbg_nisthmac.o ccdigest_init.o ccdigest_update.o ccgcm.o \
	ccmode_gcm_gf_mult.o ccmode_gcm_mult_h.o cchkdf.o cchmac.o \
	cchmac_init.o cchmac_update.o cchmac_final.o \
	ccdigest_final_64be.o ccsha256_di.o ccsha256_initial_state.o \
	ccsha256_K.o ccsha256_ltc_compress.o ccsha256_ltc_di.o \
	prng_random.o entropy.o vm_apple_protect.o pmap.o pmap_cs.o \
	pmap_data.o pmap_iommu.o pmap_misc.o pmap_ppl_interface.o \
	WKdmDecompress_16k.o WKdmCompress_16k.o WKdmDecompress_4k.o \
	WKdmCompress_4k.o WKdmData.o lz4_decode_arm64.o \
	lz4_encode_arm64.o amcc_rorgn_ppl.o amcc_rorgn_ppl_amcc.o \
	amcc_rorgn_common.o amcc_rorgn_pv_ctrr.o bcopy.o bzero.o \
	caches.o caches_asm.o copyio.o cpu.o cpu_common.o cpuid.o data.o \
	dbgwrap.o arm_timer.o arm_init.o arm_vm_init.o arm64_hypercall.o \
	io_map.o loose_ends.o locks_arm.o locore.o iofilter_asm.o \
	iofilter.o gxf_exceptions.o lowmem_vectors.o sleh.o start.o \
	pinst.o cswitch.o machine_cpuid.o machine_routines_common.o \
	machine_routines.o machine_routines_asm.o machine_task.o \
	machine_routines_apple.o pal_routines.o preemption_disable.o \
	memcmp_zero.o strnlen.o strncmp.o model_dep.o pcb.o rtclock.o \
	status.o status_shared.o commpage.o sme.o static_if.o \
	sha256_compress_arm64.o counter.o 

LIBOBJS=

CFILES=\
	./gssd/gssd_mach.c \
	./lockd/lockd_mach.c \
	$(SOURCE_DIR)/osfmk/UserNotification/KUNCUserNotifications.c \
	$(SOURCE_DIR)/osfmk/kern/kern_stackshot.c \
	$(SOURCE_DIR)/osfmk/kern/testpoints.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_test_stackshot.c \
	$(SOURCE_DIR)/osfmk/kdp/kdp_common.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_entry.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_eventlink.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_hash.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_importance.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_init.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_kmsg.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_mqueue.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_notify.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_object.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_policy.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_port.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_pset.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_right.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_space.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_service_port.c \
	$(SOURCE_DIR)/osfmk/ipc/ipc_voucher.c \
	$(SOURCE_DIR)/osfmk/ipc/mach_debug.c \
	$(SOURCE_DIR)/osfmk/ipc/mach_kernelrpc.c \
	$(SOURCE_DIR)/osfmk/ipc/mach_msg.c \
	$(SOURCE_DIR)/osfmk/ipc/mach_port.c \
	$(SOURCE_DIR)/osfmk/kern/affinity.c \
	$(SOURCE_DIR)/osfmk/kern/ast.c \
	$(SOURCE_DIR)/osfmk/kern/backtrace.c \
	$(SOURCE_DIR)/osfmk/kern/btlog.c \
	$(SOURCE_DIR)/osfmk/kern/build_config.c \
	$(SOURCE_DIR)/osfmk/kern/clock.c \
	$(SOURCE_DIR)/osfmk/kern/clock_oldops.c \
	$(SOURCE_DIR)/osfmk/kern/coalition.c \
	$(SOURCE_DIR)/osfmk/kern/compact_id.c \
	$(SOURCE_DIR)/osfmk/kern/core_analytics.c \
	$(SOURCE_DIR)/osfmk/kern/counter_common.c \
	$(SOURCE_DIR)/osfmk/kern/debug.c \
	$(SOURCE_DIR)/osfmk/kern/ext_paniclog.c \
	$(SOURCE_DIR)/osfmk/kern/energy_perf.c \
	$(SOURCE_DIR)/osfmk/kern/exception.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_aoe.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_boot.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_conclave.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_driverkit.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_frame_mint.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_inspection.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_log.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_memory.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_panic.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_resource.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_sensor.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_shared_memory.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_storage.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_tests.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_upcalls.c \
	$(SOURCE_DIR)/osfmk/kern/exclaves_xnuproxy.c \
	$(SOURCE_DIR)/osfmk/kern/extmod_statistics.c \
	$(SOURCE_DIR)/osfmk/kern/host.c \
	$(SOURCE_DIR)/osfmk/kern/host_notify.c \
	$(SOURCE_DIR)/osfmk/kern/ipc_clock.c \
	$(SOURCE_DIR)/osfmk/kern/ipc_host.c \
	$(SOURCE_DIR)/osfmk/kern/ipc_kobject.c \
	$(SOURCE_DIR)/osfmk/kern/ipc_mig.c \
	$(SOURCE_DIR)/osfmk/kern/ipc_misc.c \
	$(SOURCE_DIR)/osfmk/kern/ipc_tt.c \
	$(SOURCE_DIR)/osfmk/kern/kalloc.c \
	$(SOURCE_DIR)/osfmk/kern/kern_apfs_reflock.c \
	$(SOURCE_DIR)/osfmk/kern/ktrace_background_notify.c \
	$(SOURCE_DIR)/osfmk/kern/ledger.c \
	$(SOURCE_DIR)/osfmk/kern/lock_group.c \
	$(SOURCE_DIR)/osfmk/kern/lock_mtx.c \
	$(SOURCE_DIR)/osfmk/kern/lock_ptr.c \
	$(SOURCE_DIR)/osfmk/kern/lock_rw.c \
	$(SOURCE_DIR)/osfmk/kern/lock_ticket.c \
	$(SOURCE_DIR)/osfmk/kern/locks.c \
	$(SOURCE_DIR)/osfmk/kern/machine.c \
	$(SOURCE_DIR)/osfmk/kern/mk_sp.c \
	$(SOURCE_DIR)/osfmk/kern/mk_timer.c \
	$(SOURCE_DIR)/osfmk/kern/mpsc_ring.c \
	$(SOURCE_DIR)/osfmk/kern/mpsc_queue.c \
	$(SOURCE_DIR)/osfmk/kern/page_decrypt.c \
	$(SOURCE_DIR)/osfmk/kern/printf.c \
	$(SOURCE_DIR)/osfmk/kern/priority.c \
	$(SOURCE_DIR)/osfmk/kern/processor.c \
	$(SOURCE_DIR)/osfmk/kern/recount.c \
	$(SOURCE_DIR)/osfmk/kern/restartable.c \
	$(SOURCE_DIR)/osfmk/kern/sched_average.c \
	$(SOURCE_DIR)/osfmk/kern/sched_amp.c \
	$(SOURCE_DIR)/osfmk/kern/sched_amp_common.c \
	$(SOURCE_DIR)/osfmk/kern/sched_common.c \
	$(SOURCE_DIR)/osfmk/kern/sched_dualq.c \
	$(SOURCE_DIR)/osfmk/kern/sched_prim.c \
	$(SOURCE_DIR)/osfmk/kern/sched_rt.c \
	$(SOURCE_DIR)/osfmk/kern/sfi.c \
	$(SOURCE_DIR)/osfmk/kern/smr.c \
	$(SOURCE_DIR)/osfmk/kern/stack.c \
	$(SOURCE_DIR)/osfmk/kern/startup.c \
	$(SOURCE_DIR)/osfmk/kern/static_if_common.c \
	$(SOURCE_DIR)/osfmk/kern/sync_sema.c \
	$(SOURCE_DIR)/osfmk/kern/syscall_subr.c \
	$(SOURCE_DIR)/osfmk/kern/syscall_sw.c \
	$(SOURCE_DIR)/osfmk/kern/task.c \
	$(SOURCE_DIR)/osfmk/kern/task_policy.c \
	$(SOURCE_DIR)/osfmk/kern/task_ref.c \
	$(SOURCE_DIR)/osfmk/kern/test_lock.c \
	$(SOURCE_DIR)/osfmk/kern/test_mpsc_queue.c \
	$(SOURCE_DIR)/osfmk/kern/thread.c \
	$(SOURCE_DIR)/osfmk/kern/thread_act.c \
	$(SOURCE_DIR)/osfmk/kern/thread_call.c \
	$(SOURCE_DIR)/osfmk/kern/thread_group.c \
	$(SOURCE_DIR)/osfmk/kern/thread_policy.c \
	$(SOURCE_DIR)/osfmk/kern/thread_test_context.c \
	$(SOURCE_DIR)/osfmk/kern/timeout.c \
	$(SOURCE_DIR)/osfmk/kern/timer.c \
	$(SOURCE_DIR)/osfmk/kern/timer_call.c \
	$(SOURCE_DIR)/osfmk/kern/turnstile.c \
	$(SOURCE_DIR)/osfmk/kern/ux_handler.c \
	$(SOURCE_DIR)/osfmk/kern/waitq.c \
	$(SOURCE_DIR)/osfmk/kern/work_interval.c \
	$(SOURCE_DIR)/osfmk/kern/workload_config.c \
	$(SOURCE_DIR)/osfmk/kern/zalloc.c \
	$(SOURCE_DIR)/osfmk/kern/zalloc_bounds.c \
	$(SOURCE_DIR)/osfmk/kern/remote_time.c \
	$(SOURCE_DIR)/osfmk/kern/memset_s.c \
	$(SOURCE_DIR)/osfmk/kern/task_ident.c \
	$(SOURCE_DIR)/osfmk/kern/socd_client.c \
	./mach/clock_server.c \
	./mach/clock_reply_user.c \
	./mach/exc_user.c \
	./mach/mach_eventlink_server.c \
	./mach/host_priv_server.c \
	./mach/ktrace_background_user.c \
	./mach/mach_exc_user.c \
	./mach/mach_host_server.c \
	./mach/mach_notify_user.c \
	./mach/mach_port_server.c \
	./mach/mach_vm_server.c \
	./mach/mach_voucher_server.c \
	./mach/memory_entry_server.c \
	./mach/resource_notify_user.c \
	./mach/restartable_server.c \
	./mach/audit_triggers_user.c \
	./mach/task_access_user.c \
	$(SOURCE_DIR)/osfmk/corpses/corpse.c \
	$(SOURCE_DIR)/osfmk/kern/kern_cdata.c \
	$(SOURCE_DIR)/osfmk/tests/vm_parameter_validation_kern.c \
	$(SOURCE_DIR)/osfmk/tests/bcopy_test.c \
	$(SOURCE_DIR)/osfmk/bank/bank.c \
	./mach/coalition_notification_user.c \
	./mach/vfs_nspace_user.c \
	./mach/doubleagent_mig_user.c \
	./mach/processor_server.c \
	./mach/processor_set_server.c \
	./mach/task_server.c \
	./mach/thread_act_server.c \
	./mach/vm32_map_server.c \
	./mach/mach_test_upcall_user.c \
	$(SOURCE_DIR)/osfmk/vm/analytics.c \
	$(SOURCE_DIR)/osfmk/vm/vm_sanitize_telemetry.c \
	$(SOURCE_DIR)/osfmk/vm/vm_compressor.c \
	$(SOURCE_DIR)/osfmk/vm/vm_compressor_pager.c \
	$(SOURCE_DIR)/osfmk/vm/vm_compressor_backing_store.c \
	$(SOURCE_DIR)/osfmk/vm/vm_compressor_algorithms.c \
	$(SOURCE_DIR)/osfmk/vm/lz4.c \
	$(SOURCE_DIR)/osfmk/vm/device_vm.c \
	$(SOURCE_DIR)/osfmk/vm/memory_object.c \
	$(SOURCE_DIR)/osfmk/vm/vm_debug.c \
	$(SOURCE_DIR)/osfmk/vm/vm_fault.c \
	$(SOURCE_DIR)/osfmk/vm/vm_init.c \
	$(SOURCE_DIR)/osfmk/vm/vm_kern.c \
	$(SOURCE_DIR)/osfmk/vm/vm_map.c \
	$(SOURCE_DIR)/osfmk/vm/vm_map_store.c \
	$(SOURCE_DIR)/osfmk/vm/vm_map_store_ll.c \
	$(SOURCE_DIR)/osfmk/vm/vm_map_store_rb.c \
	$(SOURCE_DIR)/osfmk/vm/vm_memory_entry.c \
	$(SOURCE_DIR)/osfmk/vm/vm_memtag.c \
	$(SOURCE_DIR)/osfmk/vm/vm_object.c \
	$(SOURCE_DIR)/osfmk/vm/vm_pageout.c \
	$(SOURCE_DIR)/osfmk/vm/vm_pmap.c \
	$(SOURCE_DIR)/osfmk/vm/vm_purgeable.c \
	$(SOURCE_DIR)/osfmk/vm/vm_resident.c \
	$(SOURCE_DIR)/osfmk/vm/vm_shared_region.c \
	$(SOURCE_DIR)/osfmk/vm/vm_shared_region_pager.c \
	$(SOURCE_DIR)/osfmk/vm/vm_dyld_pager.c \
	$(SOURCE_DIR)/osfmk/vm/vm_swapfile_pager.c \
	$(SOURCE_DIR)/osfmk/vm/vm_upl.c \
	$(SOURCE_DIR)/osfmk/vm/vm_user.c \
	$(SOURCE_DIR)/osfmk/vm/vm32_user.c \
	$(SOURCE_DIR)/osfmk/vm/vm_sanitize.c \
	$(SOURCE_DIR)/osfmk/vm/vm_sanitize_error_compat.c \
	$(SOURCE_DIR)/osfmk/kern/kext_alloc.c \
	$(SOURCE_DIR)/osfmk/kern/kmod.c \
	$(SOURCE_DIR)/osfmk/device/subrs.c \
	$(SOURCE_DIR)/osfmk/kern/kpc_common.c \
	$(SOURCE_DIR)/osfmk/kern/cpc.c \
	$(SOURCE_DIR)/osfmk/console/serial_general.c \
	$(SOURCE_DIR)/osfmk/console/serial_console.c \
	$(SOURCE_DIR)/osfmk/console/video_scroll.c \
	$(SOURCE_DIR)/osfmk/console/video_console.c \
	$(SOURCE_DIR)/osfmk/corecrypto/cc_clear.c \
	$(SOURCE_DIR)/osfmk/corecrypto/cc_cmp_safe.c \
	$(SOURCE_DIR)/osfmk/corecrypto/cc_abort.c \
	$(SOURCE_DIR)/osfmk/corecrypto/cc_try_abort.c \
	$(SOURCE_DIR)/osfmk/corecrypto/cc_dit.c \
	$(SOURCE_DIR)/osfmk/corecrypto/cccbc.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccdrbg.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccdrbg_nisthmac.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccdigest_init.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccdigest_update.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccgcm.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccmode_gcm_gf_mult.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccmode_gcm_mult_h.c \
	$(SOURCE_DIR)/osfmk/corecrypto/cchkdf.c \
	$(SOURCE_DIR)/osfmk/corecrypto/cchmac.c \
	$(SOURCE_DIR)/osfmk/corecrypto/cchmac_init.c \
	$(SOURCE_DIR)/osfmk/corecrypto/cchmac_update.c \
	$(SOURCE_DIR)/osfmk/corecrypto/cchmac_final.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccdigest_final_64be.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccsha256_di.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccsha256_initial_state.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccsha256_K.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccsha256_ltc_compress.c \
	$(SOURCE_DIR)/osfmk/corecrypto/ccsha256_ltc_di.c \
	$(SOURCE_DIR)/osfmk/prng/prng_random.c \
	$(SOURCE_DIR)/osfmk/prng/entropy.c \
	$(SOURCE_DIR)/osfmk/vm/vm_apple_protect.c \
	$(SOURCE_DIR)/osfmk/arm/pmap/pmap.c \
	$(SOURCE_DIR)/osfmk/arm/pmap/pmap_cs.c \
	$(SOURCE_DIR)/osfmk/arm/pmap/pmap_data.c \
	$(SOURCE_DIR)/osfmk/arm/pmap/pmap_iommu.c \
	$(SOURCE_DIR)/osfmk/arm/pmap/pmap_misc.c \
	$(SOURCE_DIR)/osfmk/arm/pmap/pmap_ppl_interface.c \
	$(SOURCE_DIR)/osfmk/arm64/amcc_rorgn_ppl.c \
	$(SOURCE_DIR)/osfmk/arm64/amcc_rorgn_ppl_amcc.c \
	$(SOURCE_DIR)/osfmk/arm64/amcc_rorgn_common.c \
	$(SOURCE_DIR)/osfmk/arm64/amcc_rorgn_pv_ctrr.c \
	$(SOURCE_DIR)/osfmk/arm/caches.c \
	$(SOURCE_DIR)/osfmk/arm64/copyio.c \
	$(SOURCE_DIR)/osfmk/arm64/cpu.c \
	$(SOURCE_DIR)/osfmk/arm/cpu_common.c \
	$(SOURCE_DIR)/osfmk/arm/cpuid.c \
	$(SOURCE_DIR)/osfmk/arm64/dbgwrap.c \
	$(SOURCE_DIR)/osfmk/arm/arm_timer.c \
	$(SOURCE_DIR)/osfmk/arm/arm_init.c \
	$(SOURCE_DIR)/osfmk/arm64/arm_vm_init.c \
	$(SOURCE_DIR)/osfmk/arm64/arm64_hypercall.c \
	$(SOURCE_DIR)/osfmk/arm/io_map.c \
	$(SOURCE_DIR)/osfmk/arm64/loose_ends.c \
	$(SOURCE_DIR)/osfmk/arm/locks_arm.c \
	$(SOURCE_DIR)/osfmk/arm64/iofilter.c \
	$(SOURCE_DIR)/osfmk/arm64/lowmem_vectors.c \
	$(SOURCE_DIR)/osfmk/arm64/sleh.c \
	$(SOURCE_DIR)/osfmk/arm/machine_cpuid.c \
	$(SOURCE_DIR)/osfmk/arm/machine_routines_common.c \
	$(SOURCE_DIR)/osfmk/arm64/machine_routines.c \
	$(SOURCE_DIR)/osfmk/arm64/machine_task.c \
	$(SOURCE_DIR)/osfmk/arm/machine_routines_apple.c \
	$(SOURCE_DIR)/osfmk/arm/pal_routines.c \
	$(SOURCE_DIR)/osfmk/arm/preemption_disable.c \
	$(SOURCE_DIR)/osfmk/arm/model_dep.c \
	$(SOURCE_DIR)/osfmk/arm64/pcb.c \
	$(SOURCE_DIR)/osfmk/arm/rtclock.c \
	$(SOURCE_DIR)/osfmk/arm64/status.c \
	$(SOURCE_DIR)/osfmk/arm/status_shared.c \
	$(SOURCE_DIR)/osfmk/arm/commpage/commpage.c \
	$(SOURCE_DIR)/osfmk/arm64/sme.c \
	$(SOURCE_DIR)/osfmk/arm64/static_if.c \
	$(SOURCE_DIR)/osfmk/arm/counter.c 
COBJS=gssd_mach.o lockd_mach.o KUNCUserNotifications.o kern_stackshot.o \
	testpoints.o exclaves_test_stackshot.o kdp_common.o ipc_entry.o \
	ipc_eventlink.o ipc_hash.o ipc_importance.o ipc_init.o \
	ipc_kmsg.o ipc_mqueue.o ipc_notify.o ipc_object.o ipc_policy.o \
	ipc_port.o ipc_pset.o ipc_right.o ipc_space.o ipc_service_port.o \
	ipc_voucher.o mach_debug.o mach_kernelrpc.o mach_msg.o \
	mach_port.o affinity.o ast.o backtrace.o btlog.o build_config.o \
	clock.o clock_oldops.o coalition.o compact_id.o core_analytics.o \
	counter_common.o debug.o ext_paniclog.o energy_perf.o \
	exception.o exclaves.o exclaves_aoe.o exclaves_boot.o \
	exclaves_conclave.o exclaves_driverkit.o exclaves_frame_mint.o \
	exclaves_inspection.o exclaves_log.o exclaves_memory.o \
	exclaves_panic.o exclaves_resource.o exclaves_sensor.o \
	exclaves_shared_memory.o exclaves_storage.o exclaves_tests.o \
	exclaves_upcalls.o exclaves_xnuproxy.o extmod_statistics.o \
	host.o host_notify.o ipc_clock.o ipc_host.o ipc_kobject.o \
	ipc_mig.o ipc_misc.o ipc_tt.o kalloc.o kern_apfs_reflock.o \
	ktrace_background_notify.o ledger.o lock_group.o lock_mtx.o \
	lock_ptr.o lock_rw.o lock_ticket.o locks.o machine.o mk_sp.o \
	mk_timer.o mpsc_ring.o mpsc_queue.o page_decrypt.o printf.o \
	priority.o processor.o recount.o restartable.o sched_average.o \
	sched_amp.o sched_amp_common.o sched_common.o sched_dualq.o \
	sched_prim.o sched_rt.o sfi.o smr.o stack.o startup.o \
	static_if_common.o sync_sema.o syscall_subr.o syscall_sw.o \
	task.o task_policy.o task_ref.o test_lock.o test_mpsc_queue.o \
	thread.o thread_act.o thread_call.o thread_group.o \
	thread_policy.o thread_test_context.o timeout.o timer.o \
	timer_call.o turnstile.o ux_handler.o waitq.o work_interval.o \
	workload_config.o zalloc.o zalloc_bounds.o remote_time.o \
	memset_s.o task_ident.o socd_client.o clock_server.o \
	clock_reply_user.o exc_user.o mach_eventlink_server.o \
	host_priv_server.o ktrace_background_user.o mach_exc_user.o \
	mach_host_server.o mach_notify_user.o mach_port_server.o \
	mach_vm_server.o mach_voucher_server.o memory_entry_server.o \
	resource_notify_user.o restartable_server.o \
	audit_triggers_user.o task_access_user.o corpse.o kern_cdata.o \
	vm_parameter_validation_kern.o bcopy_test.o bank.o \
	coalition_notification_user.o vfs_nspace_user.o \
	doubleagent_mig_user.o processor_server.o processor_set_server.o \
	task_server.o thread_act_server.o vm32_map_server.o \
	mach_test_upcall_user.o analytics.o vm_sanitize_telemetry.o \
	vm_compressor.o vm_compressor_pager.o \
	vm_compressor_backing_store.o vm_compressor_algorithms.o lz4.o \
	device_vm.o memory_object.o vm_debug.o vm_fault.o vm_init.o \
	vm_kern.o vm_map.o vm_map_store.o vm_map_store_ll.o \
	vm_map_store_rb.o vm_memory_entry.o vm_memtag.o vm_object.o \
	vm_pageout.o vm_pmap.o vm_purgeable.o vm_resident.o \
	vm_shared_region.o vm_shared_region_pager.o vm_dyld_pager.o \
	vm_swapfile_pager.o vm_upl.o vm_user.o vm32_user.o vm_sanitize.o \
	vm_sanitize_error_compat.o kext_alloc.o kmod.o subrs.o \
	kpc_common.o cpc.o serial_general.o serial_console.o \
	video_scroll.o video_console.o cc_clear.o cc_cmp_safe.o \
	cc_abort.o cc_try_abort.o cc_dit.o cccbc.o ccdrbg.o \
	ccdrbg_nisthmac.o ccdigest_init.o ccdigest_update.o ccgcm.o \
	ccmode_gcm_gf_mult.o ccmode_gcm_mult_h.o cchkdf.o cchmac.o \
	cchmac_init.o cchmac_update.o cchmac_final.o \
	ccdigest_final_64be.o ccsha256_di.o ccsha256_initial_state.o \
	ccsha256_K.o ccsha256_ltc_compress.o ccsha256_ltc_di.o \
	prng_random.o entropy.o vm_apple_protect.o pmap.o pmap_cs.o \
	pmap_data.o pmap_iommu.o pmap_misc.o pmap_ppl_interface.o \
	amcc_rorgn_ppl.o amcc_rorgn_ppl_amcc.o amcc_rorgn_common.o \
	amcc_rorgn_pv_ctrr.o caches.o copyio.o cpu.o cpu_common.o \
	cpuid.o dbgwrap.o arm_timer.o arm_init.o arm_vm_init.o \
	arm64_hypercall.o io_map.o loose_ends.o locks_arm.o iofilter.o \
	lowmem_vectors.o sleh.o machine_cpuid.o \
	machine_routines_common.o machine_routines.o machine_task.o \
	machine_routines_apple.o pal_routines.o preemption_disable.o \
	model_dep.o pcb.o rtclock.o status.o status_shared.o commpage.o \
	sme.o static_if.o counter.o 

CXXFILES=
CXXOBJS=

SFILES=\
	$(SOURCE_DIR)/osfmk/arm64/WKdmDecompress_16k.s \
	$(SOURCE_DIR)/osfmk/arm64/WKdmCompress_16k.s \
	$(SOURCE_DIR)/osfmk/arm64/WKdmDecompress_4k.s \
	$(SOURCE_DIR)/osfmk/arm64/WKdmCompress_4k.s \
	$(SOURCE_DIR)/osfmk/arm64/WKdmData.s \
	$(SOURCE_DIR)/osfmk/arm64/lz4_decode_arm64.s \
	$(SOURCE_DIR)/osfmk/arm64/lz4_encode_arm64.s \
	$(SOURCE_DIR)/osfmk/arm64/bcopy.s \
	$(SOURCE_DIR)/osfmk/arm64/bzero.s \
	$(SOURCE_DIR)/osfmk/arm64/caches_asm.s \
	$(SOURCE_DIR)/osfmk/arm/data.s \
	$(SOURCE_DIR)/osfmk/arm64/locore.s \
	$(SOURCE_DIR)/osfmk/arm64/iofilter_asm.s \
	$(SOURCE_DIR)/osfmk/arm64/gxf_exceptions.s \
	$(SOURCE_DIR)/osfmk/arm64/start.s \
	$(SOURCE_DIR)/osfmk/arm64/pinst.s \
	$(SOURCE_DIR)/osfmk/arm64/cswitch.s \
	$(SOURCE_DIR)/osfmk/arm64/machine_routines_asm.s \
	$(SOURCE_DIR)/osfmk/arm64/memcmp_zero.s \
	$(SOURCE_DIR)/osfmk/arm64/strnlen.s \
	$(SOURCE_DIR)/osfmk/arm64/strncmp.s \
	$(SOURCE_DIR)/osfmk/arm64/corecrypto/sha256_compress_arm64.s 
SOBJS=WKdmDecompress_16k.o WKdmCompress_16k.o WKdmDecompress_4k.o \
	WKdmCompress_4k.o WKdmData.o lz4_decode_arm64.o \
	lz4_encode_arm64.o bcopy.o bzero.o caches_asm.o data.o locore.o \
	iofilter_asm.o gxf_exceptions.o start.o pinst.o cswitch.o \
	machine_routines_asm.o memcmp_zero.o strnlen.o strncmp.o \
	sha256_compress_arm64.o 

######################################################################
#BEGIN	Machine dependent Makefile fragment for arm64
######################################################################

CWARNFLAGS = $(CWARNFLAGS_STD) -Wshorten-64-to-32

# Files that must go in the __HIB segment:
UNCONFIGURED_HIB_FILES=					\
           hibernate_restore.o          \
           bcopy.o			\
           bzero.o			\
           cc_clear.o			\
           cc_dit.o			\
           ccdigest_init.o		\
           ccdigest_update.o		\
           ccdigest_final_64be.o	\
           cchmac.o			\
           cchmac_init.o		\
           cchmac_update.o		\
           cchmac_final.o		\
           ccsha256_K.o			\
           ccsha256_initial_state.o	\
           sha256_compress_arm64.o	\
           memset_s.o


HIB_FILES=$(filter $(UNCONFIGURED_HIB_FILES),$(OBJS))

define ADD_HIB_CFLAGS
# Unconfigured __HIB files must be Mach-O for "setsegname"
$(1)_CFLAGS_ADD += $(CFLAGS_NOLTO_FLAG)
# KASAN must be disabled for unconfigured __HIB files
# because the kasan runtime isn't available during hibernation resume
$(1)_CFLAGS_ADD += -fno-sanitize=address -UKASAN
# Stack protector and stack check must be disabled because the stack protector runtime isn't available
$(1)_CFLAGS_ADD += -fno-stack-protector -fno-stack-check
# Profiling information and code coverage must be disabled for __HIB files (see rdar://104951137)
$(1)_CFLAGS_ADD += -fno-profile-instr-generate -fno-coverage-mapping
endef

$(foreach FILE,$(UNCONFIGURED_HIB_FILES),$(eval $(call ADD_HIB_CFLAGS,$(FILE))))

lz4.o_CFLAGS_ADD += -fbuiltin -O3
vfp_state_test.o_CFLAGS_ADD += -mno-implicit-float


######################################################################
#END	Machine dependent Makefile fragment for arm64
######################################################################

# Ease debuggability of VM test code as much as possible.
vm_tests.o_CFLAGS_ADD += -g

#
# vm_sanitize/vm_sanitize_error_compat use the UBSan verifier to detect
# potential undefined behavior at compile time. The verifier inspects the
# compiled object files to detect calls to the UBSan minimal runtime.
#
# False positives are possible if checks are generated where UB is not actually
# possible. If possible, code should be re-architected to allow the compiler
# to optimize out the checks; if not __attribute__((nosanitize)) can be used.
#
# As of the time of writing, we enable all checks except the following:
#   `alignment` since it generates checks for calls to os_xyz_overflow()
#   `bool` since it generates checks most times bools are used
#   `function` since it generates checks for any non-trivial usage of function
#		pointers, and there is no way to do runtime type checking to eliminate
# 		these checks.
#   `null` since it generates NULL checks on typically non-null arguments.
#   	Marking these arguments using __attribute__(nonnull) may have an
#		undesired effect of optimizing out explicitly written NULL checks.
#   `unreachable` since it generates a check after each panic()
#   `obj-cast`,`return`,`vptr` since they are not relevant to C code
#
VM_UBSAN_CHECKS = bounds, builtin, enum, float-cast-overflow, \
	float-divide-by-zero, implicit-signed-integer-truncation, \
	implicit-unsigned-integer-truncation, integer-divide-by-zero, \
	nonnull-attribute, nullability-arg, nullability-assign, nullability-return, \
	object-size, pointer-overflow, returns-nonnull-attribute, shift, \
	signed-integer-overflow, unsigned-integer-overflow, unsigned-shift-base, \
	vla-bound
VM_UBSAN_FLAGS = -fsanitize=$(subst ${} ${},,${VM_UBSAN_CHECKS})

#
# KASAN and coverage configurations have different code generation than customer
# release kernels, and are not frequently built at desk like development kernels.
# Build-time UBSan "violations" that affect only these kernels are likely to be
# false positives and have no real-world security impact regardless.
#
ifeq ($(KASAN),1)
# UBSan build-time validations disabled on KASAN builds
else ifeq ($(BUILD_CODE_COVERAGE),1)
# UBSan build-time validations disabled on code coverage builds
else
	vm_sanitize.o_CFLAGS_ADD += ${VM_UBSAN_FLAGS}
	vm_sanitize.o_VERIFIER = VERIFIER_NO_UBSAN_CHECKS
	vm_sanitize_error_compat.o_CFLAGS_ADD += ${VM_UBSAN_FLAGS}
	vm_sanitize_error_compat.o_VERIFIER = VERIFIER_NO_UBSAN_CHECKS
endif

cccbc.o_INCFLAGS += -I${SRCROOT}/EXTERNAL_HEADERS/corecrypto
ccdrbg.o_INCFLAGS += -I${SRCROOT}/EXTERNAL_HEADERS/corecrypto
ccgcm.o_INCFLAGS += -I${SRCROOT}/EXTERNAL_HEADERS/corecrypto
ccmode_gcm_gf_mult.o_INCFLAGS += -I${SRCROOT}/EXTERNAL_HEADERS/corecrypto
ccmode_gcm_mult_h.o_INCFLAGS += -I${SRCROOT}/EXTERNAL_HEADERS/corecrypto

#
# Enforce semantic types
#

SEMANTIC_TYPES_SRC = $(notdir $(wildcard ${SRCROOT}/osfmk/vm/*.c))
SEMANTIC_TYPES_OBJ = $(SEMANTIC_TYPES_SRC:.c=.o)

define FORCE_UNSAFE_TYPES
$1_CFLAGS_ADD += -DVM_UNSAFE_TYPES
endef

$(foreach file,$(SEMANTIC_TYPES_OBJ),$(eval $(call FORCE_UNSAFE_TYPES, $(file))))

#
# Diagnostic opt-outs.  We need to make this list empty.
#
# DO NOT ADD MORE HERE.
#
# -Wno-format-nonliteral
ktest_emit.o_CWARNFLAGS_ADD += -Wno-format-nonliteral
# -Wno-atomic-implicit-seq-cst
mp.o_CWARNFLAGS_ADD += -Wno-atomic-implicit-seq-cst
pmCPU.o_CWARNFLAGS_ADD += -Wno-atomic-implicit-seq-cst
pmap_pcid.o_CWARNFLAGS_ADD += -Wno-atomic-implicit-seq-cst
xcpm_dvfs.o_CWARNFLAGS_ADD += -Wno-atomic-implicit-seq-cst
xcpm_fi.o_CWARNFLAGS_ADD += -Wno-atomic-implicit-seq-cst
xcpm_idle.o_CWARNFLAGS_ADD += -Wno-atomic-implicit-seq-cst
# -Wno-cast-align
bsd_i386.o_CWARNFLAGS_ADD += -Wno-cast-align
ccdigest_final_64be.o_CWARNFLAGS_ADD += -Wno-cast-align
ccdigest_init.o_CWARNFLAGS_ADD += -Wno-cast-align
ccdigest_update.o_CWARNFLAGS_ADD += -Wno-cast-align
cchmac_final.o_CWARNFLAGS_ADD += -Wno-cast-align
cchmac_init.o_CWARNFLAGS_ADD += -Wno-cast-align
ccmode_gcm_gf_mult.o_CWARNFLAGS_ADD += -Wno-cast-align
ccmode_gcm_mult_h.o_CWARNFLAGS_ADD += -Wno-cast-align
commpage.o_CWARNFLAGS_ADD += -Wno-cast-align
cpu_threads.o_CWARNFLAGS_ADD += -Wno-cast-align
host.o_CWARNFLAGS_ADD += -Wno-cast-align
kdp_machdep.o_CWARNFLAGS_ADD += -Wno-cast-align
kdp_udp.o_CWARNFLAGS_ADD += -Wno-cast-align
kdp_x86_common.o_CWARNFLAGS_ADD += -Wno-cast-align
locks_i386.o_CWARNFLAGS_ADD += -Wno-cast-align
machine_task.o_CWARNFLAGS_ADD += -Wno-cast-align
model_dep.o_CWARNFLAGS_ADD += -Wno-cast-align
mp_desc.o_CWARNFLAGS_ADD += -Wno-cast-align
pcb.o_CWARNFLAGS_ADD += -Wno-cast-align
pcb_native.o_CWARNFLAGS_ADD += -Wno-cast-align
processor.o_CWARNFLAGS_ADD += -Wno-cast-align
status.o_CWARNFLAGS_ADD += -Wno-cast-align
task.o_CWARNFLAGS_ADD += -Wno-cast-align
task_policy.o_CWARNFLAGS_ADD += -Wno-cast-align
video_console.o_CWARNFLAGS_ADD += -Wno-cast-align
# -Wno-implicit-int-conversion
acpi.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
commpage.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
cpu.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
cpu_threads.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
kdebug_trigger.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
kern_stackshot.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
lapic_native.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
loose_ends.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
lz4.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
model_dep.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
mp.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
mp_desc.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
pcb.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
pcb_native.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
pmap_pcid.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
pmap_x86_common.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
sched_clutch.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
trap.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
uat.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
video_console.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
xcpm_dvfs.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
xcpm_ioctl.o_CWARNFLAGS_ADD += -Wno-implicit-int-conversion
# -Wno-shorten-64-to-32
arm_vm_init.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
backtrace.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
btlog.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
caches.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
callstack.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
clock.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
clock_oldops.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
iokit_rpc.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
ipc_kmsg.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
ipc_pset.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
ipc_right.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
kdp_core.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
kdp_vm.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
kern_cdata.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
kern_stackshot.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
loose_ends.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
mach_msg.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
machine_routines.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
mk_timer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
model_dep.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
pcb.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
pmap.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
processor_core.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
rtclock.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
status.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
telemetry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
vm_init.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
vm_kern.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
vm_object.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
vm_shared_region_pager.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
vm_dyld_pager.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
vm_swapfile_pager.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
vm_user.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
# -Wno-sign-conversion
Diagnostics.o_CWARNFLAGS_ADD += -Wno-sign-conversion
acpi.o_CWARNFLAGS_ADD += -Wno-sign-conversion
action.o_CWARNFLAGS_ADD += -Wno-sign-conversion
affinity.o_CWARNFLAGS_ADD += -Wno-sign-conversion
alternate_debugger.o_CWARNFLAGS_ADD += -Wno-sign-conversion
arcade.o_CWARNFLAGS_ADD += -Wno-sign-conversion
arm_init.o_CWARNFLAGS_ADD += -Wno-sign-conversion
arm_timer.o_CWARNFLAGS_ADD += -Wno-sign-conversion
arm_vm_init.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ast.o_CWARNFLAGS_ADD += -Wno-sign-conversion
backtrace.o_CWARNFLAGS_ADD += -Wno-sign-conversion
bank.o_CWARNFLAGS_ADD += -Wno-sign-conversion
bitmap_test.o_CWARNFLAGS_ADD += -Wno-sign-conversion
bsd_arm64.o_CWARNFLAGS_ADD += -Wno-sign-conversion
bsd_i386.o_CWARNFLAGS_ADD += -Wno-sign-conversion
bsd_i386_native.o_CWARNFLAGS_ADD += -Wno-sign-conversion
bsd_kern.o_CWARNFLAGS_ADD += -Wno-sign-conversion
bsd_vm.o_CWARNFLAGS_ADD += -Wno-sign-conversion
btlog.o_CWARNFLAGS_ADD += -Wno-sign-conversion
caches.o_CWARNFLAGS_ADD += -Wno-sign-conversion
callstack.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ccdrbg_nisthmac.o_CWARNFLAGS_ADD += -Wno-sign-conversion
cchmac.o_CWARNFLAGS_ADD += -Wno-sign-conversion
cchmac_final.o_CWARNFLAGS_ADD += -Wno-sign-conversion
cchmac_init.o_CWARNFLAGS_ADD += -Wno-sign-conversion
clock.o_CWARNFLAGS_ADD += -Wno-sign-conversion
clock_oldops.o_CWARNFLAGS_ADD += -Wno-sign-conversion
coalition.o_CWARNFLAGS_ADD += -Wno-sign-conversion
commpage.o_CWARNFLAGS_ADD += -Wno-sign-conversion
copyio.o_CWARNFLAGS_ADD += -Wno-sign-conversion
corpse.o_CWARNFLAGS_ADD += -Wno-sign-conversion
cpu.o_CWARNFLAGS_ADD += -Wno-sign-conversion
cpu_common.o_CWARNFLAGS_ADD += -Wno-sign-conversion
cpu_threads.o_CWARNFLAGS_ADD += -Wno-sign-conversion
cpu_topology.o_CWARNFLAGS_ADD += -Wno-sign-conversion
cpuid.o_CWARNFLAGS_ADD += -Wno-sign-conversion
dbgwrap.o_CWARNFLAGS_ADD += -Wno-sign-conversion
debug.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ecc_logging.o_CWARNFLAGS_ADD += -Wno-sign-conversion
entropy.o_CWARNFLAGS_ADD += -Wno-sign-conversion
exception.o_CWARNFLAGS_ADD += -Wno-sign-conversion
fpu.o_CWARNFLAGS_ADD += -Wno-sign-conversion
host.o_CWARNFLAGS_ADD += -Wno-sign-conversion
host_notify.o_CWARNFLAGS_ADD += -Wno-sign-conversion
hv.o_CWARNFLAGS_ADD += -Wno-sign-conversion
i386_init.o_CWARNFLAGS_ADD += -Wno-sign-conversion
i386_timer.o_CWARNFLAGS_ADD += -Wno-sign-conversion
i386_vm_init.o_CWARNFLAGS_ADD += -Wno-sign-conversion
iokit_rpc.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_eventlink.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_host.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_importance.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_init.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_kmsg.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_kobject.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_mqueue.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_object.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_port.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_pset.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_right.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_space.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_tt.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ipc_voucher.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kalloc.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kdp.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kdp_core.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kdp_machdep.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kdp_serial.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kdp_vm.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kern_monotonic.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kern_stackshot.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kernel_tests.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kext_alloc.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kpc.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kpc_arm.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kpc_common.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kpc_x86.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kperf.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kperf_kpc.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kperf_mp.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kperf_timer.o_CWARNFLAGS_ADD += -Wno-sign-conversion
kperfbsd.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ktest_emit.o_CWARNFLAGS_ADD += -Wno-sign-conversion
lapic_native.o_CWARNFLAGS_ADD += -Wno-sign-conversion
lazy.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ledger.o_CWARNFLAGS_ADD += -Wno-sign-conversion
lockdown_mode.o_CWARNFLAGS_ADD += -Wno-sign-conversion
locks.o_CWARNFLAGS_ADD += -Wno-sign-conversion
locks_arm.o_CWARNFLAGS_ADD += -Wno-sign-conversion
locks_i386.o_CWARNFLAGS_ADD += -Wno-sign-conversion
locks_i386_opt.o_CWARNFLAGS_ADD += -Wno-sign-conversion
loose_ends.o_CWARNFLAGS_ADD += -Wno-sign-conversion
lowmem_vectors.o_CWARNFLAGS_ADD += -Wno-sign-conversion
lz4.o_CWARNFLAGS_ADD += -Wno-sign-conversion
mach_debug.o_CWARNFLAGS_ADD += -Wno-sign-conversion
mach_kernelrpc.o_CWARNFLAGS_ADD += -Wno-sign-conversion
mach_port.o_CWARNFLAGS_ADD += -Wno-sign-conversion
machdep_call.o_CWARNFLAGS_ADD += -Wno-sign-conversion
machine.o_CWARNFLAGS_ADD += -Wno-sign-conversion
machine_check.o_CWARNFLAGS_ADD += -Wno-sign-conversion
machine_remote_time.o_CWARNFLAGS_ADD += -Wno-sign-conversion
machine_routines.o_CWARNFLAGS_ADD += -Wno-sign-conversion
machine_routines_common.o_CWARNFLAGS_ADD += -Wno-sign-conversion
machine_task.o_CWARNFLAGS_ADD += -Wno-sign-conversion
meminfo.o_CWARNFLAGS_ADD += -Wno-sign-conversion
memory_object.o_CWARNFLAGS_ADD += -Wno-sign-conversion
mk_sp.o_CWARNFLAGS_ADD += -Wno-sign-conversion
mk_timer.o_CWARNFLAGS_ADD += -Wno-sign-conversion
model_dep.o_CWARNFLAGS_ADD += -Wno-sign-conversion
monotonic_arm64.o_CWARNFLAGS_ADD += -Wno-sign-conversion
monotonic_x86_64.o_CWARNFLAGS_ADD += -Wno-sign-conversion
mp.o_CWARNFLAGS_ADD += -Wno-sign-conversion
mp_desc.o_CWARNFLAGS_ADD += -Wno-sign-conversion
mp_native.o_CWARNFLAGS_ADD += -Wno-sign-conversion
mpsc_queue.o_CWARNFLAGS_ADD += -Wno-sign-conversion
mtrr.o_CWARNFLAGS_ADD += -Wno-sign-conversion
pal_routines.o_CWARNFLAGS_ADD += -Wno-sign-conversion
pcb.o_CWARNFLAGS_ADD += -Wno-sign-conversion
pcb_native.o_CWARNFLAGS_ADD += -Wno-sign-conversion
pet.o_CWARNFLAGS_ADD += -Wno-sign-conversion
platform_tests.o_CWARNFLAGS_ADD += -Wno-sign-conversion
pmCPU.o_CWARNFLAGS_ADD += -Wno-sign-conversion
pmap.o_CWARNFLAGS_ADD += -Wno-sign-conversion
pmap_common.o_CWARNFLAGS_ADD += -Wno-sign-conversion
pmap_pcid.o_CWARNFLAGS_ADD += -Wno-sign-conversion
pmap_tests.o_CWARNFLAGS_ADD += -Wno-sign-conversion
pmap_x86_common.o_CWARNFLAGS_ADD += -Wno-sign-conversion
printf.o_CWARNFLAGS_ADD += -Wno-sign-conversion
priority.o_CWARNFLAGS_ADD += -Wno-sign-conversion
prng_random.o_CWARNFLAGS_ADD += -Wno-sign-conversion
processor.o_CWARNFLAGS_ADD += -Wno-sign-conversion
remote_time.o_CWARNFLAGS_ADD += -Wno-sign-conversion
rtclock.o_CWARNFLAGS_ADD += -Wno-sign-conversion
sart.o_CWARNFLAGS_ADD += -Wno-sign-conversion
sched_amp.o_CWARNFLAGS_ADD += -Wno-sign-conversion
sched_amp_common.o_CWARNFLAGS_ADD += -Wno-sign-conversion
sched_average.o_CWARNFLAGS_ADD += -Wno-sign-conversion
sched_clutch.o_CWARNFLAGS_ADD += -Wno-sign-conversion
sched_dualq.o_CWARNFLAGS_ADD += -Wno-sign-conversion
sched_prim.o_CWARNFLAGS_ADD += -Wno-sign-conversion
serial_console.o_CWARNFLAGS_ADD += -Wno-sign-conversion
serial_general.o_CWARNFLAGS_ADD += -Wno-sign-conversion
sfi.o_CWARNFLAGS_ADD += -Wno-sign-conversion
shart.o_CWARNFLAGS_ADD += -Wno-sign-conversion
sleh.o_CWARNFLAGS_ADD += -Wno-sign-conversion
stack.o_CWARNFLAGS_ADD += -Wno-sign-conversion
startup.o_CWARNFLAGS_ADD += -Wno-sign-conversion
status.o_CWARNFLAGS_ADD += -Wno-sign-conversion
status_shared.o_CWARNFLAGS_ADD += -Wno-sign-conversion
subrs.o_CWARNFLAGS_ADD += -Wno-sign-conversion
sync_sema.o_CWARNFLAGS_ADD += -Wno-sign-conversion
syscall_subr.o_CWARNFLAGS_ADD += -Wno-sign-conversion
t8020dart.o_CWARNFLAGS_ADD += -Wno-sign-conversion
task.o_CWARNFLAGS_ADD += -Wno-sign-conversion
task_policy.o_CWARNFLAGS_ADD += -Wno-sign-conversion
telemetry.o_CWARNFLAGS_ADD += -Wno-sign-conversion
test_lock.o_CWARNFLAGS_ADD += -Wno-sign-conversion
test_thread_call.o_CWARNFLAGS_ADD += -Wno-sign-conversion
thread_call.o_CWARNFLAGS_ADD += -Wno-sign-conversion
thread_group.o_CWARNFLAGS_ADD += -Wno-sign-conversion
thread_policy.o_CWARNFLAGS_ADD += -Wno-sign-conversion
timer_call.o_CWARNFLAGS_ADD += -Wno-sign-conversion
trap.o_CWARNFLAGS_ADD += -Wno-sign-conversion
trustcache.o_CWARNFLAGS_ADD += -Wno-sign-conversion
turnstile.o_CWARNFLAGS_ADD += -Wno-sign-conversion
uat.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ucode.o_CWARNFLAGS_ADD += -Wno-sign-conversion
ux_handler.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vfp_state_test.o_CWARNFLAGS_ADD += -Wno-sign-conversion
video_console.o_CWARNFLAGS_ADD += -Wno-sign-conversion
video_scroll.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm32_user.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_compressor.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_compressor_algorithms.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_compressor_backing_store.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_compressor_pager.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_fault.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_kern.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_map.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_map_store_ll.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_map_store_rb.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_object.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_pageout.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_phantom_cache.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_purgeable.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_resident.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_shared_region.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vm_user.o_CWARNFLAGS_ADD += -Wno-sign-conversion
vmx_cpu.o_CWARNFLAGS_ADD += -Wno-sign-conversion
waitq.o_CWARNFLAGS_ADD += -Wno-sign-conversion
work_interval.o_CWARNFLAGS_ADD += -Wno-sign-conversion
xcpm_dvfs.o_CWARNFLAGS_ADD += -Wno-sign-conversion
xcpm_fi.o_CWARNFLAGS_ADD += -Wno-sign-conversion
xcpm_idle.o_CWARNFLAGS_ADD += -Wno-sign-conversion
xcpm_ioctl.o_CWARNFLAGS_ADD += -Wno-sign-conversion
# -Wno-xnu-typed-allocators
kalloc.o_CWARNFLAGS_ADD += -Wno-xnu-typed-allocators
exclaves_conclave_launcher.tightbeam.o_CWARNFLAGS_ADD += -Wno-unused-parameter
# -Wno-vla
exclaves_boot.o_CWARNFLAGS_ADD += -Wno-vla
exclaves_xnuproxy.o_CWARNFLAGS_ADD += -Wno-vla
machine.o_CWARNFLAGS_ADD += -Wno-vla
pmap.o_CWARNFLAGS_ADD += -Wno-vla
ppl_hib.o_CWARNFLAGS_ADD += -Wno-vla
processor_core.o_CWARNFLAGS_ADD += -Wno-vla
sleh.o_CWARNFLAGS_ADD += -Wno-vla
vm_reclaim.o_CWARNFLAGS_ADD += -Wno-vla
# -Wno-enum-compare
exclaves_memory.o_CWARNFLAGS_ADD += -Wno-enum-compare
lock_mtx.o_CWARNFLAGS_ADD += -Wno-enum-compare
pmap.o_CWARNFLAGS_ADD += -Wno-enum-compare

# Rebuild if per-file overrides change
${OBJS}: $(firstword $(MAKEFILE_LIST))

# Rebuild if global compile flags change
$(COBJS): .CFLAGS
.CFLAGS: ALWAYS
	$(_v)$(REPLACECONTENTS) $@ $(KCC) $(CFLAGS) $(INCFLAGS)
$(CXXOBJS): .CXXFLAGS
.CXXFLAGS: ALWAYS
	$(_v)$(REPLACECONTENTS) $@ $(KC++) $(CXXFLAGS) $(INCFLAGS)
$(SOBJS): .SFLAGS
.SFLAGS: ALWAYS
	$(_v)$(REPLACECONTENTS) $@ $(S_KCC) $(SFLAGS) $(INCFLAGS)

$(COMPONENT).filelist: $(OBJS)
	$(_v)for hib_file in ${HIB_FILES};		\
	do	\
                $(SEG_HACK) -n __HIB -o $${hib_file}__ $${hib_file} || exit 1; \
                mv $${hib_file}__ $${hib_file} || exit 1; \
	done
	@$(LOG_LDFILELIST) "$(COMPONENT)"
	$(_v)for obj in ${OBJS}; do	\
		 $(ECHO) $(TARGET)/$(CURRENT_KERNEL_CONFIG)/$${obj}; \
	done > $(COMPONENT).filelist

ifeq ($(XNU_LibAllFiles),1)
LIBOBJS := $(OBJS)
endif

$(COMPONENT).libfilelist: $(LIBOBJS)
	@$(LOG_LDFILELIST) "lib$(COMPONENT)"
	$(_v)for obj in ${LIBOBJS}; do	\
		 $(ECHO) $(TARGET)/$(CURRENT_KERNEL_CONFIG)/$${obj}; \
	done > $(COMPONENT).libfilelist

ifeq ($(RC_ProjectName),xnu_libraries)
do_all: $(COMPONENT).libfilelist
else
do_all: $(COMPONENT).filelist
endif

do_build_all:: do_all

# genassym.o actually is an assembly file,
# we name it genassym.o to help with the automatic
# dependency generation

GENASSYM_LOCATION = $(CURRENT_ARCH_CONFIG_LC)

ifeq ($(CURRENT_ARCH_CONFIG_LC),x86_64)
GENASSYM_LOCATION = i386
else ifeq ($(CURRENT_ARCH_CONFIG_LC),x86_64h)
GENASSYM_LOCATION = i386
endif

-include genassym.d
genassym.o: .CFLAGS $(firstword $(MAKEFILE_LIST))
genassym.o: $(SOURCE_DIR)/$(COMPONENT)/$(GENASSYM_LOCATION)/genassym.c
	@$(LOG_GENASSYM) "$<"
	$(_v)${GENASSYM_KCC} ${CFLAGS} ${CFLAGS_NOLTO_FLAG} -fno-integrated-as -MD -S -o ${@} ${INCFLAGS} $<

assym.s: genassym.o
	$(_v)sed -e '/^[[:space:]]*DEFINITION__define__/!d;{N;s/\n//;}' -e 's/^[[:space:]]*DEFINITION__define__\([^:]*\):.*ascii.*\"[\$$]*\([-0-9\#]*\)\".*$$/#define \1 \2/' -e 'p'  -e 's/#//2' -e 's/^[[:space:]]*#define \([A-Za-z0-9_]*\)[[:space:]]*[\$$#]*\([-0-9]*\).*$$/#define \1_NUM \2/' genassym.o > $@

${SOBJS}: assym.s

-include gssd_mach.d
gssd_mach.o: gssd/gssd_mach.c
	${C_RULE_0}
	${C_RULE_1A} gssd/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include lockd_mach.d
lockd_mach.o: lockd/lockd_mach.c
	${C_RULE_0}
	${C_RULE_1A} lockd/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include KUNCUserNotifications.d
KUNCUserNotifications.o: $(SOURCE_DIR)/osfmk/UserNotification/KUNCUserNotifications.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/UserNotification/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include kern_stackshot.d
kern_stackshot.o: $(SOURCE_DIR)/osfmk/kern/kern_stackshot.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include testpoints.d
testpoints.o: $(SOURCE_DIR)/osfmk/kern/testpoints.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_test_stackshot.d
exclaves_test_stackshot.o: $(SOURCE_DIR)/osfmk/kern/exclaves_test_stackshot.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include kdp_common.d
kdp_common.o: $(SOURCE_DIR)/osfmk/kdp/kdp_common.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kdp/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_entry.d
ipc_entry.o: $(SOURCE_DIR)/osfmk/ipc/ipc_entry.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_eventlink.d
ipc_eventlink.o: $(SOURCE_DIR)/osfmk/ipc/ipc_eventlink.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_hash.d
ipc_hash.o: $(SOURCE_DIR)/osfmk/ipc/ipc_hash.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_importance.d
ipc_importance.o: $(SOURCE_DIR)/osfmk/ipc/ipc_importance.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_init.d
ipc_init.o: $(SOURCE_DIR)/osfmk/ipc/ipc_init.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_kmsg.d
ipc_kmsg.o: $(SOURCE_DIR)/osfmk/ipc/ipc_kmsg.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_mqueue.d
ipc_mqueue.o: $(SOURCE_DIR)/osfmk/ipc/ipc_mqueue.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_notify.d
ipc_notify.o: $(SOURCE_DIR)/osfmk/ipc/ipc_notify.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_object.d
ipc_object.o: $(SOURCE_DIR)/osfmk/ipc/ipc_object.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_policy.d
ipc_policy.o: $(SOURCE_DIR)/osfmk/ipc/ipc_policy.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_port.d
ipc_port.o: $(SOURCE_DIR)/osfmk/ipc/ipc_port.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_pset.d
ipc_pset.o: $(SOURCE_DIR)/osfmk/ipc/ipc_pset.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_right.d
ipc_right.o: $(SOURCE_DIR)/osfmk/ipc/ipc_right.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_space.d
ipc_space.o: $(SOURCE_DIR)/osfmk/ipc/ipc_space.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_service_port.d
ipc_service_port.o: $(SOURCE_DIR)/osfmk/ipc/ipc_service_port.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_voucher.d
ipc_voucher.o: $(SOURCE_DIR)/osfmk/ipc/ipc_voucher.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mach_debug.d
mach_debug.o: $(SOURCE_DIR)/osfmk/ipc/mach_debug.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mach_kernelrpc.d
mach_kernelrpc.o: $(SOURCE_DIR)/osfmk/ipc/mach_kernelrpc.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mach_msg.d
mach_msg.o: $(SOURCE_DIR)/osfmk/ipc/mach_msg.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mach_port.d
mach_port.o: $(SOURCE_DIR)/osfmk/ipc/mach_port.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/ipc/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include affinity.d
affinity.o: $(SOURCE_DIR)/osfmk/kern/affinity.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ast.d
ast.o: $(SOURCE_DIR)/osfmk/kern/ast.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include backtrace.d
backtrace.o: $(SOURCE_DIR)/osfmk/kern/backtrace.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include btlog.d
btlog.o: $(SOURCE_DIR)/osfmk/kern/btlog.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include build_config.d
build_config.o: $(SOURCE_DIR)/osfmk/kern/build_config.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include clock.d
clock.o: $(SOURCE_DIR)/osfmk/kern/clock.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include clock_oldops.d
clock_oldops.o: $(SOURCE_DIR)/osfmk/kern/clock_oldops.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include coalition.d
coalition.o: $(SOURCE_DIR)/osfmk/kern/coalition.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include compact_id.d
compact_id.o: $(SOURCE_DIR)/osfmk/kern/compact_id.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include core_analytics.d
core_analytics.o: $(SOURCE_DIR)/osfmk/kern/core_analytics.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include counter_common.d
counter_common.o: $(SOURCE_DIR)/osfmk/kern/counter_common.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include debug.d
debug.o: $(SOURCE_DIR)/osfmk/kern/debug.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ext_paniclog.d
ext_paniclog.o: $(SOURCE_DIR)/osfmk/kern/ext_paniclog.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include energy_perf.d
energy_perf.o: $(SOURCE_DIR)/osfmk/kern/energy_perf.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exception.d
exception.o: $(SOURCE_DIR)/osfmk/kern/exception.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves.d
exclaves.o: $(SOURCE_DIR)/osfmk/kern/exclaves.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_aoe.d
exclaves_aoe.o: $(SOURCE_DIR)/osfmk/kern/exclaves_aoe.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_boot.d
exclaves_boot.o: $(SOURCE_DIR)/osfmk/kern/exclaves_boot.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_conclave.d
exclaves_conclave.o: $(SOURCE_DIR)/osfmk/kern/exclaves_conclave.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_driverkit.d
exclaves_driverkit.o: $(SOURCE_DIR)/osfmk/kern/exclaves_driverkit.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_frame_mint.d
exclaves_frame_mint.o: $(SOURCE_DIR)/osfmk/kern/exclaves_frame_mint.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_inspection.d
exclaves_inspection.o: $(SOURCE_DIR)/osfmk/kern/exclaves_inspection.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_log.d
exclaves_log.o: $(SOURCE_DIR)/osfmk/kern/exclaves_log.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_memory.d
exclaves_memory.o: $(SOURCE_DIR)/osfmk/kern/exclaves_memory.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_panic.d
exclaves_panic.o: $(SOURCE_DIR)/osfmk/kern/exclaves_panic.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_resource.d
exclaves_resource.o: $(SOURCE_DIR)/osfmk/kern/exclaves_resource.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_sensor.d
exclaves_sensor.o: $(SOURCE_DIR)/osfmk/kern/exclaves_sensor.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_shared_memory.d
exclaves_shared_memory.o: $(SOURCE_DIR)/osfmk/kern/exclaves_shared_memory.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_storage.d
exclaves_storage.o: $(SOURCE_DIR)/osfmk/kern/exclaves_storage.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_tests.d
exclaves_tests.o: $(SOURCE_DIR)/osfmk/kern/exclaves_tests.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_upcalls.d
exclaves_upcalls.o: $(SOURCE_DIR)/osfmk/kern/exclaves_upcalls.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exclaves_xnuproxy.d
exclaves_xnuproxy.o: $(SOURCE_DIR)/osfmk/kern/exclaves_xnuproxy.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include extmod_statistics.d
extmod_statistics.o: $(SOURCE_DIR)/osfmk/kern/extmod_statistics.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include host.d
host.o: $(SOURCE_DIR)/osfmk/kern/host.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include host_notify.d
host_notify.o: $(SOURCE_DIR)/osfmk/kern/host_notify.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_clock.d
ipc_clock.o: $(SOURCE_DIR)/osfmk/kern/ipc_clock.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_host.d
ipc_host.o: $(SOURCE_DIR)/osfmk/kern/ipc_host.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_kobject.d
ipc_kobject.o: $(SOURCE_DIR)/osfmk/kern/ipc_kobject.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_mig.d
ipc_mig.o: $(SOURCE_DIR)/osfmk/kern/ipc_mig.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_misc.d
ipc_misc.o: $(SOURCE_DIR)/osfmk/kern/ipc_misc.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ipc_tt.d
ipc_tt.o: $(SOURCE_DIR)/osfmk/kern/ipc_tt.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include kalloc.d
kalloc.o: $(SOURCE_DIR)/osfmk/kern/kalloc.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include kern_apfs_reflock.d
kern_apfs_reflock.o: $(SOURCE_DIR)/osfmk/kern/kern_apfs_reflock.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ktrace_background_notify.d
ktrace_background_notify.o: $(SOURCE_DIR)/osfmk/kern/ktrace_background_notify.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ledger.d
ledger.o: $(SOURCE_DIR)/osfmk/kern/ledger.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include lock_group.d
lock_group.o: $(SOURCE_DIR)/osfmk/kern/lock_group.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include lock_mtx.d
lock_mtx.o: $(SOURCE_DIR)/osfmk/kern/lock_mtx.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include lock_ptr.d
lock_ptr.o: $(SOURCE_DIR)/osfmk/kern/lock_ptr.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include lock_rw.d
lock_rw.o: $(SOURCE_DIR)/osfmk/kern/lock_rw.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include lock_ticket.d
lock_ticket.o: $(SOURCE_DIR)/osfmk/kern/lock_ticket.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include locks.d
locks.o: $(SOURCE_DIR)/osfmk/kern/locks.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include machine.d
machine.o: $(SOURCE_DIR)/osfmk/kern/machine.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mk_sp.d
mk_sp.o: $(SOURCE_DIR)/osfmk/kern/mk_sp.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mk_timer.d
mk_timer.o: $(SOURCE_DIR)/osfmk/kern/mk_timer.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mpsc_ring.d
mpsc_ring.o: $(SOURCE_DIR)/osfmk/kern/mpsc_ring.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mpsc_queue.d
mpsc_queue.o: $(SOURCE_DIR)/osfmk/kern/mpsc_queue.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include page_decrypt.d
page_decrypt.o_CFLAGS_ADD += ${CFLAGS_BOUND_CHECKS}
page_decrypt.o_CFLAGS_ADD += ${CFLAGS_BOUND_CHECKS_DISABLE_NEW_CHECKS}
page_decrypt.o: $(SOURCE_DIR)/osfmk/kern/page_decrypt.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include printf.d
printf.o: $(SOURCE_DIR)/osfmk/kern/printf.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include priority.d
priority.o: $(SOURCE_DIR)/osfmk/kern/priority.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include processor.d
processor.o: $(SOURCE_DIR)/osfmk/kern/processor.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include recount.d
recount.o: $(SOURCE_DIR)/osfmk/kern/recount.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include restartable.d
restartable.o: $(SOURCE_DIR)/osfmk/kern/restartable.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include sched_average.d
sched_average.o: $(SOURCE_DIR)/osfmk/kern/sched_average.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include sched_amp.d
sched_amp.o: $(SOURCE_DIR)/osfmk/kern/sched_amp.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include sched_amp_common.d
sched_amp_common.o: $(SOURCE_DIR)/osfmk/kern/sched_amp_common.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include sched_common.d
sched_common.o: $(SOURCE_DIR)/osfmk/kern/sched_common.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include sched_dualq.d
sched_dualq.o: $(SOURCE_DIR)/osfmk/kern/sched_dualq.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include sched_prim.d
sched_prim.o: $(SOURCE_DIR)/osfmk/kern/sched_prim.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include sched_rt.d
sched_rt.o: $(SOURCE_DIR)/osfmk/kern/sched_rt.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include sfi.d
sfi.o: $(SOURCE_DIR)/osfmk/kern/sfi.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include smr.d
smr.o: $(SOURCE_DIR)/osfmk/kern/smr.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include stack.d
stack.o: $(SOURCE_DIR)/osfmk/kern/stack.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include startup.d
startup.o: $(SOURCE_DIR)/osfmk/kern/startup.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include static_if_common.d
static_if_common.o: $(SOURCE_DIR)/osfmk/kern/static_if_common.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include sync_sema.d
sync_sema.o: $(SOURCE_DIR)/osfmk/kern/sync_sema.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include syscall_subr.d
syscall_subr.o: $(SOURCE_DIR)/osfmk/kern/syscall_subr.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include syscall_sw.d
syscall_sw.o: $(SOURCE_DIR)/osfmk/kern/syscall_sw.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include task.d
task.o: $(SOURCE_DIR)/osfmk/kern/task.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include task_policy.d
task_policy.o: $(SOURCE_DIR)/osfmk/kern/task_policy.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include task_ref.d
task_ref.o: $(SOURCE_DIR)/osfmk/kern/task_ref.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include test_lock.d
test_lock.o: $(SOURCE_DIR)/osfmk/kern/test_lock.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include test_mpsc_queue.d
test_mpsc_queue.o: $(SOURCE_DIR)/osfmk/kern/test_mpsc_queue.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include thread.d
thread.o: $(SOURCE_DIR)/osfmk/kern/thread.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include thread_act.d
thread_act.o: $(SOURCE_DIR)/osfmk/kern/thread_act.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include thread_call.d
thread_call.o: $(SOURCE_DIR)/osfmk/kern/thread_call.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include thread_group.d
thread_group.o: $(SOURCE_DIR)/osfmk/kern/thread_group.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include thread_policy.d
thread_policy.o: $(SOURCE_DIR)/osfmk/kern/thread_policy.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include thread_test_context.d
thread_test_context.o: $(SOURCE_DIR)/osfmk/kern/thread_test_context.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include timeout.d
timeout.o: $(SOURCE_DIR)/osfmk/kern/timeout.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include timer.d
timer.o: $(SOURCE_DIR)/osfmk/kern/timer.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include timer_call.d
timer_call.o: $(SOURCE_DIR)/osfmk/kern/timer_call.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include turnstile.d
turnstile.o: $(SOURCE_DIR)/osfmk/kern/turnstile.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ux_handler.d
ux_handler.o: $(SOURCE_DIR)/osfmk/kern/ux_handler.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include waitq.d
waitq.o: $(SOURCE_DIR)/osfmk/kern/waitq.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include work_interval.d
work_interval.o: $(SOURCE_DIR)/osfmk/kern/work_interval.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include workload_config.d
workload_config.o: $(SOURCE_DIR)/osfmk/kern/workload_config.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include zalloc.d
zalloc.o: $(SOURCE_DIR)/osfmk/kern/zalloc.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include zalloc_bounds.d
zalloc_bounds.o_CFLAGS_ADD += ${CFLAGS_BOUND_CHECKS}
zalloc_bounds.o_CFLAGS_ADD += ${CFLAGS_BOUND_CHECKS_DISABLE_NEW_CHECKS}
zalloc_bounds.o: $(SOURCE_DIR)/osfmk/kern/zalloc_bounds.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include remote_time.d
remote_time.o: $(SOURCE_DIR)/osfmk/kern/remote_time.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include memset_s.d
memset_s.o: $(SOURCE_DIR)/osfmk/kern/memset_s.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include task_ident.d
task_ident.o: $(SOURCE_DIR)/osfmk/kern/task_ident.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include socd_client.d
socd_client.o: $(SOURCE_DIR)/osfmk/kern/socd_client.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include clock_server.d
clock_server.o: mach/clock_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include clock_reply_user.d
clock_reply_user.o: mach/clock_reply_user.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include exc_user.d
exc_user.o: mach/exc_user.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mach_eventlink_server.d
mach_eventlink_server.o: mach/mach_eventlink_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include host_priv_server.d
host_priv_server.o: mach/host_priv_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ktrace_background_user.d
ktrace_background_user.o: mach/ktrace_background_user.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mach_exc_user.d
mach_exc_user.o: mach/mach_exc_user.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mach_host_server.d
mach_host_server.o: mach/mach_host_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mach_notify_user.d
mach_notify_user.o: mach/mach_notify_user.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mach_port_server.d
mach_port_server.o: mach/mach_port_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mach_vm_server.d
mach_vm_server.o: mach/mach_vm_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mach_voucher_server.d
mach_voucher_server.o: mach/mach_voucher_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include memory_entry_server.d
memory_entry_server.o: mach/memory_entry_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include resource_notify_user.d
resource_notify_user.o: mach/resource_notify_user.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include restartable_server.d
restartable_server.o: mach/restartable_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include audit_triggers_user.d
audit_triggers_user.o: mach/audit_triggers_user.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include task_access_user.d
task_access_user.o: mach/task_access_user.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include corpse.d
corpse.o: $(SOURCE_DIR)/osfmk/corpses/corpse.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corpses/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include kern_cdata.d
kern_cdata.o: $(SOURCE_DIR)/osfmk/kern/kern_cdata.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_parameter_validation_kern.d
vm_parameter_validation_kern.o: $(SOURCE_DIR)/osfmk/tests/vm_parameter_validation_kern.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/tests/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include bcopy_test.d
bcopy_test.o: $(SOURCE_DIR)/osfmk/tests/bcopy_test.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/tests/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include bank.d
bank.o: $(SOURCE_DIR)/osfmk/bank/bank.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/bank/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include coalition_notification_user.d
coalition_notification_user.o: mach/coalition_notification_user.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vfs_nspace_user.d
vfs_nspace_user.o: mach/vfs_nspace_user.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include doubleagent_mig_user.d
doubleagent_mig_user.o: mach/doubleagent_mig_user.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include processor_server.d
processor_server.o: mach/processor_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include processor_set_server.d
processor_set_server.o: mach/processor_set_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include task_server.d
task_server.o: mach/task_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include thread_act_server.d
thread_act_server.o: mach/thread_act_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm32_map_server.d
vm32_map_server.o: mach/vm32_map_server.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include mach_test_upcall_user.d
mach_test_upcall_user.o: mach/mach_test_upcall_user.c
	${C_RULE_0}
	${C_RULE_1A} mach/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include analytics.d
analytics.o: $(SOURCE_DIR)/osfmk/vm/analytics.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_sanitize_telemetry.d
vm_sanitize_telemetry.o: $(SOURCE_DIR)/osfmk/vm/vm_sanitize_telemetry.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_compressor.d
vm_compressor.o: $(SOURCE_DIR)/osfmk/vm/vm_compressor.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_compressor_pager.d
vm_compressor_pager.o: $(SOURCE_DIR)/osfmk/vm/vm_compressor_pager.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_compressor_backing_store.d
vm_compressor_backing_store.o: $(SOURCE_DIR)/osfmk/vm/vm_compressor_backing_store.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_compressor_algorithms.d
vm_compressor_algorithms.o: $(SOURCE_DIR)/osfmk/vm/vm_compressor_algorithms.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include lz4.d
lz4.o: $(SOURCE_DIR)/osfmk/vm/lz4.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include device_vm.d
device_vm.o: $(SOURCE_DIR)/osfmk/vm/device_vm.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include memory_object.d
memory_object.o: $(SOURCE_DIR)/osfmk/vm/memory_object.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_debug.d
vm_debug.o: $(SOURCE_DIR)/osfmk/vm/vm_debug.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_fault.d
vm_fault.o: $(SOURCE_DIR)/osfmk/vm/vm_fault.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_init.d
vm_init.o: $(SOURCE_DIR)/osfmk/vm/vm_init.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_kern.d
vm_kern.o: $(SOURCE_DIR)/osfmk/vm/vm_kern.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_map.d
vm_map.o: $(SOURCE_DIR)/osfmk/vm/vm_map.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_map_store.d
vm_map_store.o: $(SOURCE_DIR)/osfmk/vm/vm_map_store.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_map_store_ll.d
vm_map_store_ll.o: $(SOURCE_DIR)/osfmk/vm/vm_map_store_ll.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_map_store_rb.d
vm_map_store_rb.o: $(SOURCE_DIR)/osfmk/vm/vm_map_store_rb.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_memory_entry.d
vm_memory_entry.o: $(SOURCE_DIR)/osfmk/vm/vm_memory_entry.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_memtag.d
vm_memtag.o: $(SOURCE_DIR)/osfmk/vm/vm_memtag.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_object.d
vm_object.o: $(SOURCE_DIR)/osfmk/vm/vm_object.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_pageout.d
vm_pageout.o: $(SOURCE_DIR)/osfmk/vm/vm_pageout.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_pmap.d
vm_pmap.o: $(SOURCE_DIR)/osfmk/vm/vm_pmap.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_purgeable.d
vm_purgeable.o: $(SOURCE_DIR)/osfmk/vm/vm_purgeable.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_resident.d
vm_resident.o: $(SOURCE_DIR)/osfmk/vm/vm_resident.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_shared_region.d
vm_shared_region.o: $(SOURCE_DIR)/osfmk/vm/vm_shared_region.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_shared_region_pager.d
vm_shared_region_pager.o: $(SOURCE_DIR)/osfmk/vm/vm_shared_region_pager.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_dyld_pager.d
vm_dyld_pager.o: $(SOURCE_DIR)/osfmk/vm/vm_dyld_pager.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_swapfile_pager.d
vm_swapfile_pager.o: $(SOURCE_DIR)/osfmk/vm/vm_swapfile_pager.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_upl.d
vm_upl.o: $(SOURCE_DIR)/osfmk/vm/vm_upl.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_user.d
vm_user.o: $(SOURCE_DIR)/osfmk/vm/vm_user.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm32_user.d
vm32_user.o: $(SOURCE_DIR)/osfmk/vm/vm32_user.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_sanitize.d
vm_sanitize.o: $(SOURCE_DIR)/osfmk/vm/vm_sanitize.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_sanitize_error_compat.d
vm_sanitize_error_compat.o: $(SOURCE_DIR)/osfmk/vm/vm_sanitize_error_compat.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include kext_alloc.d
kext_alloc.o: $(SOURCE_DIR)/osfmk/kern/kext_alloc.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include kmod.d
kmod.o: $(SOURCE_DIR)/osfmk/kern/kmod.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include subrs.d
subrs.o: $(SOURCE_DIR)/osfmk/device/subrs.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/device/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include kpc_common.d
kpc_common.o: $(SOURCE_DIR)/osfmk/kern/kpc_common.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cpc.d
cpc.o: $(SOURCE_DIR)/osfmk/kern/cpc.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/kern/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include serial_general.d
serial_general.o: $(SOURCE_DIR)/osfmk/console/serial_general.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/console/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include serial_console.d
serial_console.o: $(SOURCE_DIR)/osfmk/console/serial_console.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/console/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include video_scroll.d
video_scroll.o: $(SOURCE_DIR)/osfmk/console/video_scroll.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/console/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include video_console.d
video_console.o: $(SOURCE_DIR)/osfmk/console/video_console.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/console/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cc_clear.d
cc_clear.o: $(SOURCE_DIR)/osfmk/corecrypto/cc_clear.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cc_cmp_safe.d
cc_cmp_safe.o: $(SOURCE_DIR)/osfmk/corecrypto/cc_cmp_safe.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cc_abort.d
cc_abort.o: $(SOURCE_DIR)/osfmk/corecrypto/cc_abort.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cc_try_abort.d
cc_try_abort.o: $(SOURCE_DIR)/osfmk/corecrypto/cc_try_abort.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cc_dit.d
cc_dit.o: $(SOURCE_DIR)/osfmk/corecrypto/cc_dit.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cccbc.d
cccbc.o: $(SOURCE_DIR)/osfmk/corecrypto/cccbc.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccdrbg.d
ccdrbg.o: $(SOURCE_DIR)/osfmk/corecrypto/ccdrbg.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccdrbg_nisthmac.d
ccdrbg_nisthmac.o: $(SOURCE_DIR)/osfmk/corecrypto/ccdrbg_nisthmac.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccdigest_init.d
ccdigest_init.o: $(SOURCE_DIR)/osfmk/corecrypto/ccdigest_init.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccdigest_update.d
ccdigest_update.o: $(SOURCE_DIR)/osfmk/corecrypto/ccdigest_update.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccgcm.d
ccgcm.o: $(SOURCE_DIR)/osfmk/corecrypto/ccgcm.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccmode_gcm_gf_mult.d
ccmode_gcm_gf_mult.o: $(SOURCE_DIR)/osfmk/corecrypto/ccmode_gcm_gf_mult.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccmode_gcm_mult_h.d
ccmode_gcm_mult_h.o: $(SOURCE_DIR)/osfmk/corecrypto/ccmode_gcm_mult_h.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cchkdf.d
cchkdf.o: $(SOURCE_DIR)/osfmk/corecrypto/cchkdf.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cchmac.d
cchmac.o: $(SOURCE_DIR)/osfmk/corecrypto/cchmac.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cchmac_init.d
cchmac_init.o: $(SOURCE_DIR)/osfmk/corecrypto/cchmac_init.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cchmac_update.d
cchmac_update.o: $(SOURCE_DIR)/osfmk/corecrypto/cchmac_update.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cchmac_final.d
cchmac_final.o: $(SOURCE_DIR)/osfmk/corecrypto/cchmac_final.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccdigest_final_64be.d
ccdigest_final_64be.o: $(SOURCE_DIR)/osfmk/corecrypto/ccdigest_final_64be.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccsha256_di.d
ccsha256_di.o: $(SOURCE_DIR)/osfmk/corecrypto/ccsha256_di.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccsha256_initial_state.d
ccsha256_initial_state.o: $(SOURCE_DIR)/osfmk/corecrypto/ccsha256_initial_state.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccsha256_K.d
ccsha256_K.o: $(SOURCE_DIR)/osfmk/corecrypto/ccsha256_K.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccsha256_ltc_compress.d
ccsha256_ltc_compress.o: $(SOURCE_DIR)/osfmk/corecrypto/ccsha256_ltc_compress.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include ccsha256_ltc_di.d
ccsha256_ltc_di.o: $(SOURCE_DIR)/osfmk/corecrypto/ccsha256_ltc_di.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/corecrypto/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include prng_random.d
prng_random.o: $(SOURCE_DIR)/osfmk/prng/prng_random.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/prng/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include entropy.d
entropy.o: $(SOURCE_DIR)/osfmk/prng/entropy.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/prng/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include vm_apple_protect.d
vm_apple_protect.o: $(SOURCE_DIR)/osfmk/vm/vm_apple_protect.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/vm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include pmap.d
pmap.o: $(SOURCE_DIR)/osfmk/arm/pmap/pmap.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/pmap/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include pmap_cs.d
pmap_cs.o: $(SOURCE_DIR)/osfmk/arm/pmap/pmap_cs.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/pmap/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include pmap_data.d
pmap_data.o: $(SOURCE_DIR)/osfmk/arm/pmap/pmap_data.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/pmap/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include pmap_iommu.d
pmap_iommu.o: $(SOURCE_DIR)/osfmk/arm/pmap/pmap_iommu.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/pmap/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include pmap_misc.d
pmap_misc.o: $(SOURCE_DIR)/osfmk/arm/pmap/pmap_misc.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/pmap/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include pmap_ppl_interface.d
pmap_ppl_interface.o: $(SOURCE_DIR)/osfmk/arm/pmap/pmap_ppl_interface.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/pmap/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include WKdmDecompress_16k.d
WKdmDecompress_16k.o: $(SOURCE_DIR)/osfmk/arm64/WKdmDecompress_16k.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include WKdmCompress_16k.d
WKdmCompress_16k.o: $(SOURCE_DIR)/osfmk/arm64/WKdmCompress_16k.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include WKdmDecompress_4k.d
WKdmDecompress_4k.o: $(SOURCE_DIR)/osfmk/arm64/WKdmDecompress_4k.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include WKdmCompress_4k.d
WKdmCompress_4k.o: $(SOURCE_DIR)/osfmk/arm64/WKdmCompress_4k.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include WKdmData.d
WKdmData.o: $(SOURCE_DIR)/osfmk/arm64/WKdmData.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include lz4_decode_arm64.d
lz4_decode_arm64.o: $(SOURCE_DIR)/osfmk/arm64/lz4_decode_arm64.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include lz4_encode_arm64.d
lz4_encode_arm64.o: $(SOURCE_DIR)/osfmk/arm64/lz4_encode_arm64.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include amcc_rorgn_ppl.d
amcc_rorgn_ppl.o: $(SOURCE_DIR)/osfmk/arm64/amcc_rorgn_ppl.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include amcc_rorgn_ppl_amcc.d
amcc_rorgn_ppl_amcc.o: $(SOURCE_DIR)/osfmk/arm64/amcc_rorgn_ppl_amcc.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include amcc_rorgn_common.d
amcc_rorgn_common.o: $(SOURCE_DIR)/osfmk/arm64/amcc_rorgn_common.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include amcc_rorgn_pv_ctrr.d
amcc_rorgn_pv_ctrr.o: $(SOURCE_DIR)/osfmk/arm64/amcc_rorgn_pv_ctrr.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include bcopy.d
bcopy.o: $(SOURCE_DIR)/osfmk/arm64/bcopy.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include bzero.d
bzero.o: $(SOURCE_DIR)/osfmk/arm64/bzero.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include caches.d
caches.o: $(SOURCE_DIR)/osfmk/arm/caches.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include caches_asm.d
caches_asm.o: $(SOURCE_DIR)/osfmk/arm64/caches_asm.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include copyio.d
copyio.o: $(SOURCE_DIR)/osfmk/arm64/copyio.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cpu.d
cpu.o: $(SOURCE_DIR)/osfmk/arm64/cpu.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cpu_common.d
cpu_common.o: $(SOURCE_DIR)/osfmk/arm/cpu_common.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include cpuid.d
cpuid.o: $(SOURCE_DIR)/osfmk/arm/cpuid.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include data.d
data.o: $(SOURCE_DIR)/osfmk/arm/data.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${S_RULE_1B}
	${S_RULE_2}
-include dbgwrap.d
dbgwrap.o: $(SOURCE_DIR)/osfmk/arm64/dbgwrap.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include arm_timer.d
arm_timer.o: $(SOURCE_DIR)/osfmk/arm/arm_timer.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include arm_init.d
arm_init.o: $(SOURCE_DIR)/osfmk/arm/arm_init.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include arm_vm_init.d
arm_vm_init.o: $(SOURCE_DIR)/osfmk/arm64/arm_vm_init.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include arm64_hypercall.d
arm64_hypercall.o: $(SOURCE_DIR)/osfmk/arm64/arm64_hypercall.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include io_map.d
io_map.o: $(SOURCE_DIR)/osfmk/arm/io_map.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include loose_ends.d
loose_ends.o: $(SOURCE_DIR)/osfmk/arm64/loose_ends.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include locks_arm.d
locks_arm.o: $(SOURCE_DIR)/osfmk/arm/locks_arm.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include locore.d
locore.o: $(SOURCE_DIR)/osfmk/arm64/locore.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include iofilter_asm.d
iofilter_asm.o: $(SOURCE_DIR)/osfmk/arm64/iofilter_asm.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include iofilter.d
iofilter.o: $(SOURCE_DIR)/osfmk/arm64/iofilter.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include gxf_exceptions.d
gxf_exceptions.o: $(SOURCE_DIR)/osfmk/arm64/gxf_exceptions.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include lowmem_vectors.d
lowmem_vectors.o: $(SOURCE_DIR)/osfmk/arm64/lowmem_vectors.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include sleh.d
sleh.o: $(SOURCE_DIR)/osfmk/arm64/sleh.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include start.d
start.o: $(SOURCE_DIR)/osfmk/arm64/start.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include pinst.d
pinst.o: $(SOURCE_DIR)/osfmk/arm64/pinst.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include cswitch.d
cswitch.o: $(SOURCE_DIR)/osfmk/arm64/cswitch.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include machine_cpuid.d
machine_cpuid.o: $(SOURCE_DIR)/osfmk/arm/machine_cpuid.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include machine_routines_common.d
machine_routines_common.o: $(SOURCE_DIR)/osfmk/arm/machine_routines_common.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include machine_routines.d
machine_routines.o: $(SOURCE_DIR)/osfmk/arm64/machine_routines.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include machine_routines_asm.d
machine_routines_asm.o: $(SOURCE_DIR)/osfmk/arm64/machine_routines_asm.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include machine_task.d
machine_task.o: $(SOURCE_DIR)/osfmk/arm64/machine_task.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include machine_routines_apple.d
machine_routines_apple.o: $(SOURCE_DIR)/osfmk/arm/machine_routines_apple.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include pal_routines.d
pal_routines.o: $(SOURCE_DIR)/osfmk/arm/pal_routines.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include preemption_disable.d
preemption_disable.o: $(SOURCE_DIR)/osfmk/arm/preemption_disable.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include memcmp_zero.d
memcmp_zero.o: $(SOURCE_DIR)/osfmk/arm64/memcmp_zero.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include strnlen.d
strnlen.o: $(SOURCE_DIR)/osfmk/arm64/strnlen.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include strncmp.d
strncmp.o: $(SOURCE_DIR)/osfmk/arm64/strncmp.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${S_RULE_1B}
	${S_RULE_2}
-include model_dep.d
model_dep.o: $(SOURCE_DIR)/osfmk/arm/model_dep.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include pcb.d
pcb.o: $(SOURCE_DIR)/osfmk/arm64/pcb.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include rtclock.d
rtclock.o: $(SOURCE_DIR)/osfmk/arm/rtclock.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include status.d
status.o: $(SOURCE_DIR)/osfmk/arm64/status.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include status_shared.d
status_shared.o: $(SOURCE_DIR)/osfmk/arm/status_shared.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include commpage.d
commpage.o: $(SOURCE_DIR)/osfmk/arm/commpage/commpage.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/commpage/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include sme.d
sme.o: $(SOURCE_DIR)/osfmk/arm64/sme.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include static_if.d
static_if.o: $(SOURCE_DIR)/osfmk/arm64/static_if.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}
-include sha256_compress_arm64.d
sha256_compress_arm64.o: $(SOURCE_DIR)/osfmk/arm64/corecrypto/sha256_compress_arm64.s
	${S_RULE_0}
	${S_RULE_1A} $(SOURCE_DIR)/osfmk/arm64/corecrypto/${S_RULE_1B}
	${S_RULE_2}
-include counter.d
counter.o: $(SOURCE_DIR)/osfmk/arm/counter.c
	${C_RULE_0}
	${C_RULE_1A} $(SOURCE_DIR)/osfmk/arm/${C_RULE_1B}
	${C_RULE_2}
	${C_RULE_3}
	${C_RULE_4}

include $(MakeInc_rule)
include $(MakeInc_dir)
