"""Reproducible host suite, UI captures, real monotonic replay and host RAM.

Never opens devices or network. Reports are HOST_TESTED, not firmware results.
"""
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlantic_core.framebuffer import render_png, PATTERNS
from atlantic_core.policy import BIOS, MockBSP, Target, State
from atlantic_core.validation import config_encode


def host_memory():
    if os.name == 'nt':
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)] + [(name,ctypes.c_size_t) for name in
                ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
                 'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]
        kernel = ctypes.WinDLL('kernel32',use_last_error=True)
        psapi = ctypes.WinDLL('psapi',use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(counters),counters.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return {'method':'GetProcessMemoryInfo','rss_bytes':counters.WorkingSetSize,
                'peak_rss_bytes':counters.PeakWorkingSetSize}
    import resource
    maximum = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {'method':'getrusage','peak_rss_bytes':maximum*(1 if sys.platform == 'darwin' else 1024)}


def main():
    out = ROOT/'work/validation'
    out.mkdir(parents=True,exist_ok=True)
    unit = subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],
                          cwd=ROOT,capture_output=True,text=True)
    (out/'tests.log').write_text(unit.stdout+unit.stderr,encoding='utf-8', newline="\n")
    if unit.returncode:
        print(unit.stdout+unit.stderr)
        raise SystemExit(unit.returncode)
    spec = importlib.util.spec_from_file_location('host_simulator',ROOT/'tools/host-simulator/simulate.py')
    sim = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sim)
    tracemalloc.start()
    baseline = host_memory()
    for path in sorted((ROOT/'tests/fixtures').glob('*.json')):
        bios, report = sim.run_scenario(path)
        (out/(path.stem+'.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8', newline="\n")
        (out/(path.stem+'.png')).write_bytes(render_png(bios.lines()))
    # Capture actual policy screens with exact strings using same renderer as GUI.
    bios = sim.make_bios(True)
    (out/'countdown-5.png').write_bytes(render_png(bios.lines()))
    bios.open_menu('CONFIG')
    bios.selection = 6
    bios.activate()
    (out/'setup.png').write_bytes(render_png(bios.lines()))
    bios.request_confirmation('off')
    (out/'power-confirmation.png').write_bytes(render_png(bios.lines()))
    # GUI smoke test when explicitly available on Windows: construct Tk/PhotoImage
    # offscreen, validate pixels, then destroy. Does not open a persistent window.
    tk_report = {'status':'NOT_RUN','reason':'optional Tk GUI backend'}
    if os.name == 'nt':
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        photo = tk.PhotoImage(data=__import__('base64').b64encode(render_png(bios.lines())))
        assert (photo.width(),photo.height()) == (1000,760)
        root.update_idletasks()
        root.destroy()
        tk_report = {'status':'HOST_TESTED','tk_version':str(tk.TkVersion),
                     'scope':'offscreen Tk PNG display construction; no human click test'}
    (out/'tk-smoke.json').write_text(json.dumps(tk_report,indent=2)+'\n',encoding='utf-8', newline="\n")
    # Corrupt settings exercise through simulator entry point, not just helper.
    corrupt = sim.make_bios(True, config=b'{"truncated":')
    assert corrupt.state == State.RECOVERY
    valid = sim.make_bios(True, config=config_encode({'verbose':False}))
    assert not valid.verbose and valid.state == State.COUNTDOWN
    (out/'config-integration.json').write_text(json.dumps({'label':'HOST_TESTED',
        'truncated_config':str(corrupt.state),'valid_config_verbose':valid.verbose,
        'fallback_capability_from_config':False},indent=2)+'\n',encoding='utf-8', newline="\n")
    b = sim.make_bios(True)
    start = time.monotonic_ns()
    seen, max_gap, last_us = [], 0, 0
    while b.state == State.COUNTDOWN:
        now = (time.monotonic_ns()-start)//1000
        max_gap = max(max_gap,now-last_us)
        last_us = now
        b.sample(now)
        if b.state == State.COUNTDOWN and (not seen or seen[-1]['display'] != b.seconds()):
            seen.append({'us':now,'display':b.seconds()})
        time.sleep(0.01)
    elapsed_us = (time.monotonic_ns()-start)//1000
    assert [item['display'] for item in seen] == [5,4,3,2,1]
    assert b.state == State.HANDED_OFF and elapsed_us >= 5_000_000
    # No upper scheduling guarantee on a general-purpose host: record lateness.
    timer = {'label':'HOST_TESTED','scope':'REAL_HOST_CLOCK_MOCK_ANDROID',
             'clock':'time.monotonic_ns','elapsed_us':elapsed_us,'max_sample_gap_us':max_gap,
             'displayed':seen,'effects':b.bsp.effects,'device_timer_verified':False}
    (out/'realtime-timer.json').write_text(json.dumps(timer,indent=2)+'\n',encoding='utf-8', newline="\n")
    current,peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    memory = {'label':'HOST_TESTED','scope':'VALIDATION_PROCESS_NOT_XNU_FIRMWARE',
              'python':platform.python_version(),'os':platform.system()+' '+platform.release(),
              'baseline':baseline,'after_render_and_timer':host_memory(),
              'tracemalloc_current_bytes':current,'tracemalloc_peak_bytes':peak,
              'firmware_resident_bytes':None,'device_target_pass':None,
              'framebuffer_host_rgb_bytes':1000*760*3,
              'font_glyphs':len(PATTERNS),'font_min_bitpacked_bytes':(len(PATTERNS)*35+7)//8}
    (out/'host-memory.json').write_text(json.dumps(memory,indent=2)+'\n',encoding='utf-8', newline="\n")
    source_paths = sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(
        part in {'work','.git','xnu-upstream','__pycache__','evidence'} for part in p.relative_to(ROOT).parts))
    sources = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    (out/'source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n',encoding='utf-8', newline="\n")
    summary = {'label':'HOST_TESTED','unit_exit_code':unit.returncode,'scenarios':4,
               'real_time_countdown':True,'firmware_built':False,'device_verified':False,
               'source_hashes_sha256':hashlib.sha256((out/'source-hashes.json').read_bytes()).hexdigest()}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8', newline="\n")
    print(json.dumps(summary,indent=2))
    print(json.dumps(memory,indent=2))
    print('Reports:',out)


if __name__ == '__main__':
    main()
