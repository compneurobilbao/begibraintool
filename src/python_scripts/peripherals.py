"""Detection of the begibraintool peripherals for the GUI panel "Detected peripherals".

All of them are USB devices. The present USB devices are listed with the Windows
configuration manager (cfgmgr32, no extra packages), and matched by vendor/product id
or by the name the device reports. Gazepoint Control (Open Gaze API, TCP
127.0.0.1:4242) is also asked for the eye tracker model and the biometrics dial.

Peripheral         How it is detected
-----------------  -------------------------------------------------------------------
Button box (BBTK)  USB VID_04D8&PID_0001, reported as "BBTK Response Box" (HID keyboard)
Eye tracker        USB camera of the GP3 HD: Point Grey/FLIR Chameleon3, VID_1E10
                   (PID_3300 on the lab unit). Green when Gazepoint Control also answers
                   (PsychoPy records through it); amber when only the USB camera is found.
Biometrics (ET)    A valid value of the biometrics dial (DIALV=1, also GSRV/HRV) from
                   Gazepoint Control. Amber when only its USB serial adapter (FTDI
                   FT232R, VID_0403&PID_6001) is found: open Gazepoint Control.
DVS camera         Prophesee EVK4 (begitrack project), VID_04B4&PID_00F5
EEG                Not integrated yet: always "not connected".

The ids were read from the Windows device history of the development laptop
(2026-11-18). If a unit has other ids, add them to PERIPHERALS.
"""
import ctypes
import re
import socket
import sys
import time

STATE_OK, STATE_PARTIAL, STATE_MISSING = "ok", "partial", "missing"
STATE_COLORS = {STATE_OK: "#3cb043", STATE_PARTIAL: "#f0a202", STATE_MISSING: "#e0282e"}
STATE_TEXT = {
    STATE_OK: {"es": "Conectado", "en": "Connected", "eu": "Konektatuta"},
    STATE_PARTIAL: {"es": "Parcial", "en": "Partial", "eu": "Partziala"},
    STATE_MISSING: {"es": "No conectado", "en": "Not connected", "eu": "Ez dago konektatuta"},
}

# usb: list of (VID, PID or None for any PID); names: substrings of the reported names
PERIPHERALS = [
    {"key": "button_box",
     "name": {"es": "Botonera", "en": "Button box", "eu": "Botoi-panela"},
     "usb": [("04D8", "0001")], "names": ["BBTK"]},
    {"key": "eye_tracker",
     "name": {"es": "Eye tracker", "en": "Eye tracker", "eu": "Eye tracker"},
     "usb": [("1E10", None)], "names": ["Chameleon3", "Gazepoint", "GP3"]},
    {"key": "biometrics",
     "name": {"es": "Biometría eye tracker", "en": "Eye tracker biometrics", "eu": "Eye tracker biometria"},
     "usb": [("0403", "6001")], "names": []},
    {"key": "dvs_camera",
     "name": {"es": "Cámara DVS", "en": "DVS camera", "eu": "DVS kamera"},
     "usb": [("04B4", "00F5")], "names": ["EVK4", "Prophesee"]},
    {"key": "eeg",
     "name": {"es": "EEG", "en": "EEG", "eu": "EEG"},
     "usb": [], "names": []},
]

GAZEPOINT_ADDRESS = ("127.0.0.1", 4242)

_VIDPID_RE = re.compile(r"VID_([0-9A-F]{4})&PID_([0-9A-F]{4})", re.I)
_ATTR_RE = re.compile(r'(\w+)="([^"]*)"')


# --------------------------------------------------------------------------- USB
class _GUID(ctypes.Structure):
    _fields_ = [("Data1", ctypes.c_ulong), ("Data2", ctypes.c_ushort),
                ("Data3", ctypes.c_ushort), ("Data4", ctypes.c_ubyte * 8)]


class _DEVPROPKEY(ctypes.Structure):
    _fields_ = [("fmtid", _GUID), ("pid", ctypes.c_ulong)]


def _devpropkey(d1, d2, d3, d4, pid):
    return _DEVPROPKEY(_GUID(d1, d2, d3, (ctypes.c_ubyte * 8)(*d4)), pid)


# DEVPKEY_Device_BusReportedDeviceDesc and DEVPKEY_Device_FriendlyName / DeviceDesc
_BUS_DESC = _devpropkey(0x540B947E, 0x8B40, 0x45BC, [0xA8, 0xA2, 0x6A, 0x0B, 0x89, 0x4C, 0xBD, 0xA2], 4)
_FRIENDLY = _devpropkey(0xA45C254E, 0xDF1C, 0x4EFD, [0x80, 0x20, 0x67, 0xD1, 0x46, 0xA8, 0x50, 0xE0], 14)
_DEV_DESC = _devpropkey(0xA45C254E, 0xDF1C, 0x4EFD, [0x80, 0x20, 0x67, 0xD1, 0x46, 0xA8, 0x50, 0xE0], 2)


def _string_property(cfg, devinst, key):
    prop_type = ctypes.c_ulong(0)
    size = ctypes.c_ulong(0)
    cfg.CM_Get_DevNode_PropertyW(devinst, ctypes.byref(key), ctypes.byref(prop_type), None, ctypes.byref(size), 0)
    if not size.value:
        return ""
    buf = ctypes.create_string_buffer(size.value)
    if cfg.CM_Get_DevNode_PropertyW(devinst, ctypes.byref(key), ctypes.byref(prop_type), buf,
                                    ctypes.byref(size), 0) != 0:
        return ""
    return buf.raw[:size.value].decode("utf-16-le", "ignore").rstrip("\x00")


def list_usb_devices():
    """Present USB devices: [{'id', 'vid', 'pid', 'names'}], or None if not available."""
    if sys.platform != "win32":
        return None
    try:
        cfg = ctypes.WinDLL("cfgmgr32")
        CM_GETIDLIST_FILTER_ENUMERATOR, CM_GETIDLIST_FILTER_PRESENT = 0x1, 0x100
        flags = CM_GETIDLIST_FILTER_ENUMERATOR | CM_GETIDLIST_FILTER_PRESENT
        ids = None
        for _ in range(3):                      # the list can grow between the two calls
            size = ctypes.c_ulong(0)
            if cfg.CM_Get_Device_ID_List_SizeW(ctypes.byref(size), ctypes.c_wchar_p("USB"), flags) != 0:
                return None
            buf = ctypes.create_unicode_buffer(size.value + 1)
            if cfg.CM_Get_Device_ID_ListW(ctypes.c_wchar_p("USB"), buf, size.value + 1, flags) == 0:
                ids = [s for s in buf[:size.value].split("\x00") if s]
                break
        if ids is None:
            return None
        devices = []
        for dev_id in ids:
            m = _VIDPID_RE.search(dev_id)
            names = []
            devinst = ctypes.c_ulong(0)
            if cfg.CM_Locate_DevNodeW(ctypes.byref(devinst), ctypes.c_wchar_p(dev_id), 0) == 0:
                for key in (_BUS_DESC, _FRIENDLY, _DEV_DESC):
                    name = _string_property(cfg, devinst, key)
                    if name and name not in names:
                        names.append(name)
            devices.append({"id": dev_id, "vid": m.group(1).upper() if m else "",
                            "pid": m.group(2).upper() if m else "", "names": names})
        return devices
    except (OSError, AttributeError, ValueError) as e:
        print(f"peripherals: could not list the USB devices ({e})")
        return None


def _match_usb(devices, spec):
    """First present device matching the peripheral spec (ids or reported names).
    Whole devices come before their interfaces (&MI_xx), whose names are generic."""
    for dev in sorted(devices or [], key=lambda d: "&MI_" in d["id"].upper()):
        for vid, pid in spec.get("usb", []):
            if dev["vid"] == vid and (pid is None or dev["pid"] == pid):
                return dev
        for word in spec.get("names", []):
            if any(word.lower() in n.lower() for n in dev["names"]):
                return dev
    return None


# --------------------------------------------------------------------- Gazepoint
def probe_gazepoint(address=GAZEPOINT_ADDRESS, connect_timeout=0.5, listen=1.2):
    """Ask Gazepoint Control for the tracker model and a few records with the biometrics.

    Returns {'api': bool, 'product': str|None, 'records': int, 'dial_valid': bool,
    'gsr_valid': bool, 'hr_valid': bool}. Only enables data on its own connection and
    never disables anything, so a recording running in Gazepoint Analysis is not touched."""
    out = {"api": False, "product": None, "records": 0,
           "dial_valid": False, "gsr_valid": False, "hr_valid": False}
    try:
        sock = socket.create_connection(address, timeout=connect_timeout)
    except OSError:
        return out
    out["api"] = True
    try:
        sock.settimeout(0.2)
        for cmd in ('<GET ID="PRODUCT_ID" />', '<SET ID="ENABLE_SEND_DIAL" STATE="1" />',
                    '<SET ID="ENABLE_SEND_GSR" STATE="1" />', '<SET ID="ENABLE_SEND_HR" STATE="1" />',
                    '<SET ID="ENABLE_SEND_DATA" STATE="1" />'):
            sock.sendall((cmd + "\r\n").encode("utf-8"))
        buf = ""
        t_end = time.monotonic() + listen
        while time.monotonic() < t_end:
            try:
                chunk = sock.recv(8192)
            except socket.timeout:
                continue
            if not chunk:
                break
            buf += chunk.decode("utf-8", "replace")
            for tag in re.findall(r"<(?:ACK|REC)\s[^>]*/>", buf):
                attrs = dict(_ATTR_RE.findall(tag))
                if tag.startswith("<ACK") and attrs.get("ID") == "PRODUCT_ID":
                    out["product"] = " ".join(v for v in (attrs.get("VALUE"), attrs.get("BUS"),
                                                          attrs.get("RATE") and attrs["RATE"] + " Hz") if v)
                elif tag.startswith("<REC"):
                    out["records"] += 1
                    out["dial_valid"] |= attrs.get("DIALV") == "1"
                    out["gsr_valid"] |= attrs.get("GSRV") == "1"
                    out["hr_valid"] |= attrs.get("HRV") == "1"
            buf = buf[buf.rfind("/>") + 2:] if "/>" in buf else buf[-4096:]
            if out["product"] and out["dial_valid"]:
                break
    except OSError:
        pass
    finally:
        try:
            sock.close()
        except OSError:
            pass
    return out


# ------------------------------------------------------------------------- all
def detect_all():
    """{key: {'state': ok|partial|missing, 'detail': {lang: text}}} for every peripheral."""
    devices = list_usb_devices()
    gp = probe_gazepoint()
    usb = {p["key"]: _match_usb(devices, p) for p in PERIPHERALS}
    result = {}

    def put(key, state, es, en):
        result[key] = {"state": state, "detail": {"es": es, "en": en, "eu": en}}

    def usb_txt(dev):
        return f"{dev['names'][0] if dev['names'] else ''} ({dev['vid']}:{dev['pid']})".strip()

    no_usb_list = devices is None
    # button box
    if usb["button_box"]:
        put("button_box", STATE_OK, f"USB: {usb_txt(usb['button_box'])}", f"USB: {usb_txt(usb['button_box'])}")
    else:
        put("button_box", STATE_MISSING, "No se encuentra la botonera BBTK por USB.",
            "The BBTK button box is not found on USB.")
    # eye tracker
    cam = usb["eye_tracker"]
    control_es = f"Gazepoint Control abierto ({gp['product']})" if gp["product"] else "Gazepoint Control abierto"
    control_en = f"Gazepoint Control running ({gp['product']})" if gp["product"] else "Gazepoint Control running"
    if cam and gp["api"]:
        put("eye_tracker", STATE_OK, f"USB: {usb_txt(cam)}. {control_es}.", f"USB: {usb_txt(cam)}. {control_en}.")
    elif cam:
        put("eye_tracker", STATE_PARTIAL,
            f"USB: {usb_txt(cam)}. Gazepoint Control está cerrado: ábrelo para calibrar y grabar.",
            f"USB: {usb_txt(cam)}. Gazepoint Control is closed: open it to calibrate and record.")
    elif gp["api"] and no_usb_list:
        put("eye_tracker", STATE_OK, f"{control_es}.", f"{control_en}.")
    elif gp["api"]:
        put("eye_tracker", STATE_PARTIAL, f"{control_es}, pero no se encuentra la cámara del GP3 por USB.",
            f"{control_en}, but the GP3 camera is not found on USB.")
    else:
        put("eye_tracker", STATE_MISSING, "No se encuentra la cámara del GP3 por USB.",
            "The GP3 camera is not found on USB.")
    # biometrics (a valid dial value is enough)
    signals = [n for n, k in (("dial", "dial_valid"), ("GSR", "gsr_valid"), ("HR", "hr_valid")) if gp[k]]
    if signals:
        put("biometrics", STATE_OK, f"Señales válidas en Gazepoint: {', '.join(signals)}.",
            f"Valid signals in Gazepoint: {', '.join(signals)}.")
    elif usb["biometrics"]:
        why_es = "sin valor del dial" if gp["api"] else "Gazepoint Control cerrado"
        why_en = "no dial value" if gp["api"] else "Gazepoint Control closed"
        put("biometrics", STATE_PARTIAL, f"USB serie detectado ({usb_txt(usb['biometrics'])}), {why_es}.",
            f"USB serial adapter found ({usb_txt(usb['biometrics'])}), {why_en}.")
    else:
        put("biometrics", STATE_MISSING,
            "Sin valor del dial en Gazepoint Control." if gp["api"] else "Gazepoint Control cerrado y sin USB de la biometría.",
            "No dial value in Gazepoint Control." if gp["api"] else "Gazepoint Control closed and no biometrics USB.")
    # DVS camera
    if usb["dvs_camera"]:
        put("dvs_camera", STATE_OK, f"USB: {usb_txt(usb['dvs_camera'])}", f"USB: {usb_txt(usb['dvs_camera'])}")
    else:
        put("dvs_camera", STATE_MISSING, "No se encuentra la cámara Prophesee EVK4 por USB.",
            "The Prophesee EVK4 camera is not found on USB.")
    # EEG
    put("eeg", STATE_MISSING, "Integración del EEG pendiente (módulo 4).", "EEG integration pending (Module 4).")
    if no_usb_list:
        for key in ("button_box", "dvs_camera"):
            result[key]["detail"] = {"es": "No se pueden listar los USB en este sistema.",
                                     "en": "USB devices cannot be listed on this system.",
                                     "eu": "USB devices cannot be listed on this system."}
    return result


def summary(result):
    """'button_box=ok;eye_tracker=partial;...' to store with the session data."""
    return ";".join(f"{k}={v['state']}" for k, v in result.items())


if __name__ == "__main__":
    for dev in list_usb_devices() or []:
        print(dev)
    print(probe_gazepoint())
    for k, v in detect_all().items():
        print(f"{k:12s} {v['state']:8s} {v['detail']['es']}")
