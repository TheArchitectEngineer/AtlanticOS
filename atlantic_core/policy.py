"""Deterministic, non-blocking BIOS policy. All effects are host simulations."""
from dataclasses import dataclass, field
from enum import StrEnum
import math


class State(StrEnum):
    COUNTDOWN = "COUNTDOWN"
    RECOVERY = "RECOVERY"
    MENU = "MENU"
    SETUP = "SETUP"
    CONFIRM = "CONFIRM"
    DIAGNOSTICS = "DIAGNOSTICS"
    HANDED_OFF = "HANDED_OFF"
    POWERED_OFF = "POWERED_OFF"
    RESTARTED = "RESTARTED"


@dataclass(frozen=True)
class Target:
    id: str
    label: str
    available: bool = False
    verified: bool = False
    reason: str = "UNIMPLEMENTED"

    @property
    def enabled(self):
        return self.available and self.verified


@dataclass
class MockBSP:
    """No device IO, commands, slots, network sockets or host power operations."""
    targets: dict = field(default_factory=dict)
    android_fallback: bool = False
    framebuffer: bool = True
    power_supported: bool = False
    network: bool = False
    handoff_fail_at: str | None = None
    quiesce_fail: bool = False
    effects: list = field(default_factory=list)

    def quiesce(self):
        self.effects.append("mock:quiesce")
        return not self.quiesce_fail

    def handoff(self, target):
        self.effects.append(f"mock:prepare:{target}")
        if self.handoff_fail_at == "prepare":
            return False
        if not self.quiesce():
            return False
        self.effects.append("mock:stop-network-and-clear-secrets")
        if self.handoff_fail_at == "commit":
            return False
        self.effects.append(f"mock:transfer:{target}")
        return True


@dataclass
class Debouncer:
    raw: bool = False
    stable: bool = False
    changed_at: int = 0

    def sample(self, pressed, now, delay):
        if pressed != self.raw:
            self.raw, self.changed_at = pressed, now
        if self.raw != self.stable and now - self.changed_at >= delay:
            self.stable = self.raw
            return "press" if self.stable else "release"
        return None


class BIOS:
    DEBOUNCE_US = 30_000
    LONG_POWER_US = 1_500_000
    TIMEOUT_US = 5_000_000
    TARGET_NAMES = (
        ("android", "Boot Android"), ("uefi", "Boot UEFI / Windows ARM64"),
        ("usb", "Boot USB"), ("sd", "Boot microSD"),
        ("internal", "Boot internal partition"), ("file", "Boot from filesystem"),
    )

    def __init__(self, bsp=None, now=0, setup_requested=False):
        self.bsp = bsp or MockBSP()
        self.now = self.started = now
        self.state = State.RECOVERY
        self.reason = "RECOVERY"
        self.message = "Android fallback UNVERIFIED. Maintenance only."
        self.keys = {k: Debouncer(changed_at=now) for k in ("up", "down", "power")}
        self.selection = 0
        self.pending = None
        self.confirm_yes = False
        self.power_started = None
        self.power_long = False
        self.network_enabled = self.vnc_enabled = False
        self.verbose = True
        self.logs = []
        self._first_sample = True
        self._held_down_initially = False
        if setup_requested:
            self.open_menu("CONFIG")
        elif self.android_safe():
            self.state, self.reason, self.message = State.COUNTDOWN, "DEFAULT", ""
        self.log("start", state=self.state, reason=self.reason)

    def log(self, event, **details):
        self.logs.append({"us": self.now, "event": event, **details})

    def android_safe(self):
        t = self.bsp.targets.get("android")
        return bool(self.bsp.android_fallback and t and t.enabled)

    def seconds(self):
        return max(1, math.ceil((self.TIMEOUT_US - (self.now - self.started)) / 1_000_000))

    def open_menu(self, reason):
        self.state, self.reason, self.selection = State.MENU, reason, 0
        self.log("menu", reason=reason)

    def entries(self):
        result = []
        for ident, label in self.TARGET_NAMES:
            target = self.bsp.targets.get(ident)
            enabled = bool(target and target.enabled)
            if ident == "android":
                enabled = enabled and self.android_safe()
            result.append((ident, label, enabled,
                           target.reason if target else "UNIMPLEMENTED"))
        result += [("setup", "BIOS Setup", True, "HOST_TESTED"),
                   ("vnc", "Optional VNC", False, "UNIMPLEMENTED - no listener"),
                   ("off", "Power Off", self.bsp.power_supported, "mock only"),
                   ("restart", "Restart", self.bsp.power_supported, "mock only"),
                   ("diagnostics", "Recovery / Diagnostics", True, "HOST_TESTED")]
        return result

    def recover(self, message, reason="FALLBACK"):
        self.state, self.reason, self.message = State.RECOVERY, reason, message
        self.network_enabled = self.vnc_enabled = False
        self.log("recovery", reason=reason, message=message)

    def sample(self, now, keys=None):
        """Clock and raw key snapshot; call at least every 10 ms in real-time UI.

        Raw Down cancels auto boot immediately, then opens setup after debounce.
        This conservative latch prevents a press just before the deadline being lost.
        It can delay boot after contact noise; it cannot cause an unsafe auto boot.
        """
        if type(now) is not int or now < self.now:
            self.recover("Monotonic clock failure")
            return
        self.now = now
        if self.state in (State.HANDED_OFF, State.POWERED_OFF, State.RESTARTED):
            return  # A committed transfer/power action has no returning UI context.
        keys = keys or set()
        if not keys <= self.keys.keys():
            raise ValueError("unknown key")
        if self._first_sample:
            self._held_down_initially = "down" in keys
            self._first_sample = False
        if "down" in keys and self.state == State.COUNTDOWN:
            self.log("countdown-cancelled", cause="raw-down")
            self.state = State.RECOVERY
            self.message = "Volume Down detected; waiting for debounce."
        for name, key in self.keys.items():
            edge = key.sample(name in keys, now, self.DEBOUNCE_US)
            if edge == "press":
                if name == "down" and self.state in (State.COUNTDOWN, State.RECOVERY):
                    self.open_menu("KEY_HELD" if self._held_down_initially else "KEY_PRESSED")
                    self._held_down_initially = False
                elif name in ("up", "down"):
                    self.navigate(-1 if name == "up" else 1)
                elif name == "power":
                    self.power_started, self.power_long = now, False
            if edge == "release" and name == "power":
                # Duration uses the raw release timestamp, so release-debounce cannot
                # turn a short press into a long one at the threshold.
                duration = key.changed_at - self.power_started if self.power_started is not None else 0
                if not self.power_long:
                    if duration >= self.LONG_POWER_US:
                        self.request_confirmation("off")
                    else:
                        self.activate()
                self.power_started = None
        p = self.keys["power"]
        if (p.stable and p.raw and self.power_started is not None and not self.power_long
                and now - self.power_started >= self.LONG_POWER_US):
            self.power_long = True
            self.request_confirmation("off")
        if self.state == State.COUNTDOWN and now - self.started >= self.TIMEOUT_US:
            self.boot("android")

    def navigate(self, direction):
        if self.state == State.MENU:
            self.selection = (self.selection + direction) % len(self.entries())
        elif self.state == State.SETUP:
            self.selection = (self.selection + direction) % 6
        elif self.state == State.CONFIRM:
            self.confirm_yes = not self.confirm_yes

    def activate(self, origin="local"):
        if self.state == State.MENU:
            ident, _, enabled, why = self.entries()[self.selection]
            if not enabled:
                self.message = f"UNAVAILABLE: {why}"
                self.log("target-denied", target=ident)
            elif ident == "setup":
                self.state, self.selection = State.SETUP, 0
            elif ident == "diagnostics":
                self.state = State.DIAGNOSTICS
            elif ident in ("off", "restart"):
                self.request_confirmation(ident)
            else:
                self.boot(ident)
        elif self.state == State.RECOVERY:
            self.open_menu("RECOVERY")
        elif self.state == State.DIAGNOSTICS:
            self.open_menu("RECOVERY")
        elif self.state == State.SETUP:
            if self.selection == 0:
                self.verbose = not self.verbose
            elif self.selection == 5:
                self.open_menu("CONFIG")
            else:
                self.message = "Locked in Phase 1: safe Android default, 5 s, network OFF."
        elif self.state == State.CONFIRM:
            action = self.pending
            self.pending = None
            if not self.confirm_yes:
                self.open_menu("CONFIG")
            elif origin != "local":
                self.recover("Physical confirmation required")
            elif not self.bsp.power_supported or not self.bsp.quiesce():
                self.recover("Power request failed; hardware unchanged")
            else:
                self.network_enabled = self.vnc_enabled = False
                self.bsp.effects.append(f"mock:power:{action}")
                self.state = State.POWERED_OFF if action == "off" else State.RESTARTED
                self.log("power-request", action=action, scope="HOST_SIMULATION")

    def request_confirmation(self, action):
        if action not in ("off", "restart"):
            raise ValueError("unknown power action")
        if not self.bsp.power_supported:
            self.message = "Power method UNSUPPORTED"
            return
        self.state, self.pending, self.confirm_yes = State.CONFIRM, action, False

    def boot(self, ident):
        t = self.bsp.targets.get(ident)
        if not t or not t.enabled or (ident == "android" and not self.android_safe()):
            self.recover("Target unavailable or not verified")
            return
        self.network_enabled = self.vnc_enabled = False
        if not self.bsp.handoff(ident):
            self.recover("Partial handoff failed. No blind retry; independent recovery required.")
            return
        self.state = State.HANDED_OFF
        self.message = f"SIMULATED transfer to {ident}. No operating system was booted."
        self.log("handoff", target=ident, scope="HOST_SIMULATION")

    def request_vnc(self, local_consent=False, authenticated=False, protected_channel=False):
        # Security gate is exercised; transport/server intentionally absent.
        if not all((local_consent, authenticated, protected_channel, self.bsp.network)):
            self.log("vnc-denied")
            return "DENIED"
        self.log("vnc-unimplemented")
        return "UNIMPLEMENTED"

    def watchdog_fault(self):
        self.recover("Watchdog fault: do not guess PMIC/firmware reset method")

    def lines(self):
        lines = ["AtlanticOS / AtlanticBIOS 0.1", "HOST_TESTED - POLICY SIMULATOR / NO XNU",
                 "Moto G20 / Unisoc T700 - hardware UNTESTED", "", f"STATE: {self.state}  ENTRY: {self.reason}"]
        if self.state == State.COUNTDOWN:
            lines += ["", "Press Volume Down to enter AtlanticOS.",
                      f"Booting Android in {self.seconds()} seconds...", "", "Android route: MOCK fixture only"]
        elif self.state == State.MENU:
            lines += ["", "AtlanticBIOS Setup / Boot Menu"]
            for i, (_, label, enabled, _) in enumerate(self.entries()):
                lines.append(f"{'>' if i == self.selection else ' '} {label} {'[READY MOCK]' if enabled and i < 6 else '[UNAVAILABLE]' if not enabled else ''}")
        elif self.state == State.SETUP:
            settings = [f"Verbose logs: {'ON' if self.verbose else 'OFF'} (session)",
                        "Default: Android only with verified fallback", "Countdown: 5 seconds",
                        "Network / VNC / Wi-Fi: OFF", "Signatures: fail closed / verifier absent", "Back"]
            lines += ["", "BIOS Setup - Phase 1"] + [f"{'>' if i == self.selection else ' '} {s}" for i, s in enumerate(settings)]
        elif self.state == State.CONFIRM:
            lines += ["", f"Confirm {self.pending}? LOCAL INPUT REQUIRED", f"{'>' if not self.confirm_yes else ' '} Cancel", f"{'>' if self.confirm_yes else ' '} Confirm (MOCK only)"]
        elif self.state == State.DIAGNOSTICS:
            lines += ["", "No AtlanticOS device evidence collected.", "No physical storage interface exists in this tool.",
                      "Network OFF / VNC server UNIMPLEMENTED", "XNU port UNIMPLEMENTED / device RAM UNMEASURED", f"Audit events: {len(self.logs)}", "Power: return to menu"]
        else:
            lines += ["", "Safe maintenance / independent Android recovery", "Power short: open menu. Volume Down: enter setup."]
        if self.message:
            lines += ["", self.message]
        return lines + ["", "Volume +/-: navigate | Power short: select", "Power hold 1.5 s: shutdown dialog | Network OFF"]
