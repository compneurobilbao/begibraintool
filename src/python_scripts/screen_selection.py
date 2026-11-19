"""Output monitor and window mode of the experiment, chosen in the begibraintool GUI.

Ported from the eye tracking demo (``eye_tracking_demo/python_scripts/demo_gui.py``).
Builder writes the screen number, window size and full-screen flag of the experiment
as constants (Screen = 2, [1920, 1080], Full-screen window = False). The GUI runs in
Before Experiment (CONFIGURATION_ROUTINE / EXT_MODULE_SELECTION_GUI), so the window
arguments are replaced when the window is created, by wrapping ``visual.Window.__init__``
with ``window_kwargs(selection)``.

Monitors are detected with pyglet, the library PsychoPy uses to open the window: the
index of a screen here is PsychoPy's ``screen`` argument in code (from 0; Builder's
*Screen* parameter starts at 1).

Window modes (WINDOW_MODES):

* ``fullscreen``  exclusive full screen at the native resolution. Best timing. Screen
                  capture (Gazepoint's live view and recording, OBS...) only sees what
                  is behind it.
* ``borderless``  a borderless, always-on-top window over the whole monitor, which
                  screen capture sees. It is 1 px taller than the monitor (the extra row
                  is off-screen): when an OpenGL window in the foreground matches the
                  monitor exactly, Windows and the graphics driver promote it to
                  exclusive full screen and it can no longer be captured (checked on a
                  2880x1800 laptop screen with GDI captures). It goes through the Windows
                  compositor (DWM): typically one extra, variable frame of delay (about
                  17-33 ms at 60 Hz, not measured), and the flip() time comes before the
                  image is really shown. Do not use it for timing-sensitive tests
                  (saccades/antisaccades latencies, reaction times, brief presentations).
* ``window``      3/4 of the monitor, centred, with borders. Testing only: the gaze does
                  not match the stimuli.
* ``builder``     the window set in Builder (today 1920x1080 with borders, not full
                  screen), on the selected monitor. The previous behaviour of
                  begibraintool. The size is in physical pixels (the process is DPI
                  aware): on the lab 4K monitor at 3840x2160 it covers a quarter of the
                  screen and the stimuli ('height' units) are drawn at half size.

Default mode: ``borderless``. The user chose Builder's non-full-screen window so that
Gazepoint could capture the experiment (2026-11-18); the borderless window keeps that
and covers the whole monitor at its native resolution, as the pilot's full screen did
(PsychoPy logs of the pilot: 3840x2160 on the lab monitor). A selection remembered on
the computer (last_screen_selection.json) takes precedence.

DPI: call ``make_dpi_aware()`` before measuring the monitors and before creating the
Tk window. PsychoPy's Qt info dialog makes the process per-monitor DPI aware after the
GUI anyway; without the call a monitor with Windows scaling is measured in scaled
pixels (a 2880x1800 laptop at 200 % reads 1440x900). ``window_kwargs()`` measures the
monitor again when the window is created.
"""
import ctypes
import json
import os
import sys

DEFAULT_MODE = "borderless"

# key -> label / description per language (es, en, eu)
WINDOW_MODES = {
    "fullscreen": {
        "label": {"es": "Pantalla completa",
                  "en": "Full screen",
                  "eu": "Pantaila osoa"},
        "tooltip": {"es": "Pantalla completa exclusiva a la resolución nativa. Mejor timing. "
                          "Gazepoint (vista en directo y grabación) no puede capturarla. "
                          "Úsala para las pruebas sensibles al tiempo: sácadas y antisácadas, "
                          "tiempos de reacción y presentaciones breves.",
                    "en": "Exclusive full screen at the native resolution. Best timing. "
                          "Gazepoint (live view and recording) cannot capture it. "
                          "Use it for timing-sensitive tests: saccades and antisaccades, "
                          "reaction times and brief presentations.",
                    "eu": "Pantaila osoa bereizmen natiboan. Denbora-zehaztasun onena. "
                          "Gazepoint-ek ezin du kapturatu."},
    },
    "borderless": {
        "label": {"es": "Ventana a pantalla completa (capturable)",
                  "en": "Borderless full-screen window (capturable)",
                  "eu": "Pantaila osoko leihoa (kapturagarria)"},
        "tooltip": {"es": "Ventana sin bordes que ocupa todo el monitor y siempre está encima. "
                          "Gazepoint, OBS y otras capturadoras pueden verla y grabarla. "
                          "Pasa por el compositor de Windows: añade normalmente al menos un "
                          "fotograma de retraso variable. No la uses para sácadas, antisácadas, "
                          "tiempos de reacción ni presentaciones breves. Si haces clic en otra "
                          "ventana, vuelve a hacer clic en el experimento.",
                    "en": "Borderless always-on-top window covering the whole monitor. "
                          "Gazepoint, OBS and other capture tools can see and record it. "
                          "It goes through the Windows compositor: usually at least one "
                          "variable frame of extra delay. Do not use it for saccades, "
                          "antisaccades, reaction times or brief presentations. If you click "
                          "another window, click the experiment again.",
                    "eu": "Monitor osoa betetzen duen ertzik gabeko leihoa, kapturagarria. "
                          "Gutxienez fotograma bateko atzerapena gehitzen du."},
    },
    "window": {
        "label": {"es": "Ventana pequeña (solo pruebas)",
                  "en": "Small window (testing only)",
                  "eu": "Leiho txikia (probak soilik)"},
        "tooltip": {"es": "Ventana de 3/4 del monitor con bordes. Solo para probar: "
                          "la mirada no coincide con los estímulos.",
                    "en": "Window of 3/4 of the monitor with borders. Testing only: "
                          "the gaze does not match the stimuli.",
                    "eu": "Monitorearen 3/4eko leihoa. Probetarako soilik."},
    },
    "builder": {
        "label": {"es": "Ventana de Builder (1920×1080, como hasta ahora)",
                  "en": "Builder window (1920×1080, as before)",
                  "eu": "Builder-eko leihoa (1920×1080, orain arte bezala)"},
        "tooltip": {"es": "La ventana configurada en Builder (hoy 1920×1080 con bordes, sin "
                          "pantalla completa), en el monitor elegido. Es el comportamiento "
                          "anterior de begibraintool. Son píxeles físicos: en un monitor "
                          "4K a 3840×2160 ocupa un cuarto de la pantalla y los estímulos "
                          "salen a la mitad de tamaño.",
                    "en": "The window set in Builder (today 1920×1080 with borders, not full "
                          "screen), on the selected monitor. The previous behaviour of "
                          "begibraintool. Physical pixels: on a 4K monitor at 3840×2160 it "
                          "covers a quarter of the screen and the stimuli are drawn at half size.",
                    "eu": "Builder-en konfiguratutako leihoa, aukeratutako monitorean. 4K "
                          "monitore batean pantailaren laurdena betetzen du."},
    },
}

# warning shown by the GUI when a mode other than full screen is chosen
MODE_WARNINGS = {
    "borderless": {"es": "⚠ Timing peor que en pantalla completa: no la uses para sácadas, "
                         "antisácadas ni tiempos de reacción.",
                   "en": "⚠ Worse timing than full screen: do not use it for saccades, "
                         "antisaccades or reaction times.",
                   "eu": "⚠ Pantaila osoa baino denbora-zehaztasun txarragoa."},
    "window": {"es": "⚠ Solo para pruebas: la mirada no coincide con los estímulos.",
               "en": "⚠ Testing only: the gaze does not match the stimuli.",
               "eu": "⚠ Probetarako soilik."},
    "builder": {"es": "⚠ Ventana fija de 1920×1080 px: en un monitor 4K ocupa un cuarto de la "
                      "pantalla y los estímulos salen a la mitad de tamaño.",
                "en": "⚠ Fixed 1920×1080 px window: on a 4K monitor it covers a quarter of the "
                      "screen and the stimuli are drawn at half size.",
                "eu": "⚠ 1920×1080 px-ko leiho finkoa: 4K monitore batean pantailaren laurdena."},
}


def make_dpi_aware():
    """Per-monitor DPI awareness (v2), as PsychoPy's Qt info dialog sets it later anyway.

    Without it, a monitor with Windows scaling is measured in scaled pixels (a 2880x1800
    laptop at 200 % reads 1440x900) until that dialog opens; with it, the GUI lists the
    native resolutions and the window is created with the real monitor size. Call it
    before creating any Tk window."""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))   # PER_MONITOR_AWARE_V2
    except (AttributeError, OSError):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)                       # PER_MONITOR (Windows 8.1)
        except (AttributeError, OSError):
            pass


def detect_screens():
    """Monitors as PsychoPy will see them: [{'index', 'width', 'height', 'x', 'y'}, ...]."""
    try:
        import pyglet
        try:
            display = pyglet.canvas.get_display()          # pyglet 1.x (PsychoPy 2025.1)
        except AttributeError:
            display = pyglet.display.get_display()         # pyglet 2.x
        screens = display.get_screens()
        return [dict(index=i, width=s.width, height=s.height, x=s.x, y=s.y) for i, s in enumerate(screens)]
    except Exception as e:  # noqa: BLE001
        print(f"screen_selection: could not detect the monitors ({e}); assuming 1920x1080")
        return [dict(index=0, width=1920, height=1080, x=0, y=0)]


def screen_label(screen, lang="es"):
    """'Pantalla 2: 1920 × 1080 (principal)' for the GUI (Builder numbering, from 1)."""
    word = {"es": "Pantalla", "en": "Screen", "eu": "Pantaila"}.get(lang, "Screen")
    main = {"es": "principal", "en": "main", "eu": "nagusia"}.get(lang, "main")
    txt = f"{word} {screen['index'] + 1}:  {screen['width']} × {screen['height']}"
    if screen.get("x") == 0 and screen.get("y") == 0:
        txt += f"  ({main})"
    return txt


def window_mode(selection):
    """Window mode of a selection (DEFAULT_MODE if missing or unknown)."""
    mode = (selection or {}).get("window_mode")
    return mode if mode in WINDOW_MODES else DEFAULT_MODE


def window_kwargs(selection):
    """visual.Window arguments for the selected monitor and mode (see the module docstring).

    The monitor is measured again here, when the window is created: its size depends on
    the DPI awareness of the process, which can change after the GUI."""
    screens = detect_screens()
    s = next((x for x in screens if x["index"] == (selection or {}).get("screen")), screens[-1])
    mode = window_mode(selection)
    if mode == "fullscreen":
        return dict(screen=s["index"], fullscr=True, size=[s["width"], s["height"]])
    if mode == "borderless":
        return dict(screen=s["index"], fullscr=False, size=[s["width"], s["height"] + 1], pos=[0, 0], allowGUI=False)
    if mode == "window":
        return dict(screen=s["index"], fullscr=False, size=[int(s["width"] * 0.75), int(s["height"] * 0.75)],
                    pos=None, allowGUI=True)
    return dict(screen=s["index"])          # builder: keep Builder's size / full-screen flag


def keep_on_top(win):
    """Borderless mode: keep the PsychoPy window above other windows and the taskbar of its
    monitor (also when the presenter clicks on Gazepoint on the other monitor) and give it
    the keyboard focus. Windows only; a no-op elsewhere."""
    if sys.platform != "win32":
        return
    try:
        hwnd = win.winHandle._hwnd
        HWND_TOPMOST, SWP_NOSIZE, SWP_NOMOVE = -1, 0x0001, 0x0002
        ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
        win.winHandle.activate()
    except Exception as e:  # noqa: BLE001
        print(f"screen_selection: could not keep the window on top ({e})")


def default_selection(screens=None, last=None):
    """Remembered selection if its monitor still exists, else the last monitor (usually the
    external one, as Builder's Screen = 2) in DEFAULT_MODE."""
    screens = screens or detect_screens()
    last = last or {}
    idx = last.get("screen")
    if not any(s["index"] == idx for s in screens):
        idx = screens[-1]["index"]
    return {"screen": idx, "window_mode": window_mode(last)}


def load_selection(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_selection(path, selection, screens=None):
    """Remember the selection (monitor index, its size and the window mode) in a JSON file."""
    screens = screens or detect_screens()
    s = next((x for x in screens if x["index"] == selection.get("screen")), None)
    data = dict(screen=selection.get("screen"), window_mode=window_mode(selection),
                screen_size=[s["width"], s["height"]] if s else None)
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        print(f"screen_selection: could not save the selection ({e})")
    return data
