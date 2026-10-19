"""Run from repository root: python tools/host-simulator/simulate.py --gui.

Interactive Tk, console and deterministic scenarios use the SAME policy model.
No device APIs are imported. The countdown uses time.monotonic_ns(), not sleep.
"""
import argparse
import base64
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from atlantic_core.policy import BIOS, MockBSP, Target, State
from atlantic_core.framebuffer import render_png
from atlantic_core.validation import config_load


def make_bios(demo=False, framebuffer=True, config=None):
    bsp = MockBSP(framebuffer=framebuffer)
    if demo:
        bsp.android_fallback, bsp.power_supported = True, True
        bsp.targets['android'] = Target('android', 'Android MOCK', True, True, 'HOST FIXTURE ONLY')
    bios = BIOS(bsp)
    if config is not None:
        values, status = config_load(config)
        bios.verbose = values['verbose']
        bios.log('config', status=status)
        if status != 'OK':
            bios.recover('Configuration corrupt/unsupported; safe defaults, maintenance only.')
    return bios


def run_scenario(path):
    scenario = json.loads(Path(path).read_text(encoding='utf-8'))
    bios = make_bios(scenario.get('mock_android', False))
    frames = [{'us': 0, 'state': bios.state, 'lines': bios.lines()}]
    for event in scenario['samples']:
        bios.sample(event['us'], set(event.get('keys', [])))
        frames.append({'us': bios.now, 'state': bios.state, 'lines': bios.lines()})
    if 'expected' in scenario and bios.state != scenario['expected']:
        raise AssertionError(f'{path}: {bios.state} != {scenario["expected"]}')
    return bios, {'label': 'HOST_TESTED', 'scope': 'SIMULATED_POLICY_NO_XNU',
                  'scenario': Path(path).name, 'frames': frames, 'logs': bios.logs,
                  'effects': bios.bsp.effects}


def gui(bios):
    import tkinter as tk
    root = tk.Tk()
    root.title('AtlanticBIOS - HOST SIMULATOR / no XNU / no device IO')
    keys = set()
    panel = tk.Label(root, bg='#0c1626')
    panel.pack()
    if not bios.bsp.framebuffer:
        root.destroy()
        return console(bios)
    controls = tk.Frame(root)
    controls.pack(fill='x')
    for key, name in [('up', 'Volume Up'), ('down', 'Volume Down'), ('power', 'Power')]:
        button = tk.Button(controls, text=name, width=20, takefocus=False)
        button.bind('<ButtonPress-1>', lambda e, k=key: keys.add(k))
        button.bind('<ButtonRelease-1>', lambda e, k=key: keys.discard(k))
        button.pack(side='left', padx=4, pady=6)
    tk.Label(root, text='Arrow keys = Volume | Enter = Power | hold Enter 1.5 s | close window = exit host tool').pack()
    mapping = {'Up':'up', 'Down':'down', 'Return':'power'}
    root.bind('<KeyPress>', lambda e: keys.add(mapping[e.keysym]) if e.keysym in mapping else None)
    root.bind('<KeyRelease>', lambda e: keys.discard(mapping[e.keysym]) if e.keysym in mapping else None)
    root.bind('<FocusOut>', lambda e: keys.clear())
    start = time.monotonic_ns()
    last = None
    def tick():
        nonlocal last
        bios.sample((time.monotonic_ns()-start)//1000, keys)
        view = bios.lines()
        if view != last:
            panel.image = tk.PhotoImage(data=base64.b64encode(render_png(view)))
            panel.configure(image=panel.image)
            last = view
        root.after(10, tick)
    tick()
    root.mainloop()


def console(bios):
    """Console fallback: polling on Windows/POSIX, no framebuffer required.

    d/u/p = 80ms button pulse; l = long Power; q = exit. Real held buttons are
    represented in GUI/scenarios. Platform console raw mode is restored on exit.
    """
    import os
    start, last, pulses = time.monotonic_ns(), None, {}
    def loop(read):
        nonlocal last
        while True:
            now = (time.monotonic_ns()-start)//1000
            char = read()
            if char == 'q':
                break
            if char in ('u','d','p','l'):
                pulses[{'u':'up','d':'down','p':'power','l':'power'}[char]] = now+(1_650_000 if char == 'l' else 80_000)
            bios.sample(now, {k for k, until in pulses.items() if now < until})
            view = '\n'.join(bios.lines())
            if view != last:
                print('\x1b[2J\x1b[H'+view+'\nConsole: u/d/p/l/q', flush=True)
                last = view
            time.sleep(0.01)
    if os.name == 'nt':
        import msvcrt
        loop(lambda: msvcrt.getwch() if msvcrt.kbhit() else '')
    else:
        import select
        import termios
        import tty
        saved = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            loop(lambda: sys.stdin.read(1) if select.select([sys.stdin], [], [], 0)[0] else '')
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, saved)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--console', action='store_true')
    parser.add_argument('--mock-android', action='store_true', help='fixture only: simulate independently verified Android route')
    parser.add_argument('--no-framebuffer', action='store_true')
    parser.add_argument('--scenario', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--capture', type=Path)
    parser.add_argument('--config', type=Path, help='host JSON file only; no capability or fallback fields accepted')
    args = parser.parse_args()
    if args.scenario:
        bios, report = run_scenario(args.scenario)
        print('\n'.join(bios.lines()))
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline="\n")
        if args.capture:
            args.capture.parent.mkdir(parents=True, exist_ok=True)
            args.capture.write_bytes(render_png(bios.lines()))
    else:
        config = None
        if args.config:
            if args.config.suffix.lower() != '.json' or not args.config.is_file() or args.config.is_symlink():
                parser.error('--config requires a regular .json host file')
            with args.config.open('rb') as stream:
                config = stream.read(4097)
        bios = make_bios(args.mock_android, not args.no_framebuffer, config)
        if args.gui:
            gui(bios)
        elif args.console:
            console(bios)
        else:
            print('\n'.join(bios.lines()))


if __name__ == '__main__':
    main()
