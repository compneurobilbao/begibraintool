"""Gazepoint GP3 HD client for begibraintool (Open Gaze API, TCP 127.0.0.1:4242).

Ported from the eye tracking demo (``eye_tracking_demo/python_scripts/gazepoint_client.py``),
where it is tested with the GP3 HD at a stable 150 Hz. Changes for begibraintool:
it also requests the left/right eye POG, the 3D eye position and the biometrics
(GSR, heart rate, dial), which Module 3 uses, and ``loop_detail()`` builds the
detail of the routine markers.

It is an ADDITIONAL acquisition path. The analysis (``data_analytics_code``) still
reads the Gazepoint Analysis exports and synchronises them with ``expStart`` +
``<Routine>.started``. Keep recording with Gazepoint Analysis in parallel until this
path is validated.

The data stream is read in a background thread, so the PsychoPy frame loop is never
blocked by ``socket.recv`` (the GP_data_adq_backend* routines did a blocking recv on
every frame). The client:

* records every Gazepoint record to ``<datafile>_gazepoint.csv`` with the PsychoPy
  monotonic clock (``core.getTime()``) at reception, next to the Gazepoint fields;
* logs experiment events (routine onsets/offsets...) to ``<datafile>_events.csv``
  with the same clock, so gaze and stimuli can be aligned without clock conversions;
* writes every event label into the Gazepoint USER_DATA field, so the recording made
  in parallel with Gazepoint Analysis also carries the markers (column USER of the
  all_gaze export; not verified yet with the real Gazepoint Control);
* exposes the latest record (``latest()``) for live gaze displays.

Sample timing: ``t_psychopy`` is the arrival time of the TCP packet and has jitter.
For analysis rebuild the time of each sample from the Gazepoint ``TIME`` column:
``t = TIME + offset``, with ``offset`` the lower envelope (1st percentile) of
``t_psychopy - TIME``, recomputed after every ``TIME`` reset (e.g. after a
recalibration). See ``sample_times()`` below.

The reader thread starts at ``connect()``, so the socket is always drained (a client
that stops reading could make Gazepoint Control wait), but samples are only written
from ``start_recording()``. In the demo the thread started at ``start_recording()``:
the ~10 s of samples queued while the window was created were then written with the
arrival time of the backlog as ``t_psychopy``.

If Gazepoint Control is not running, ``connect()`` returns False after 2 s and the
experiment runs normally: events are still logged (``GAZEPOINT_NOT_CONNECTED``), no
gaze is recorded.

Usage in the .psyexp (CONFIGURATION_ROUTINE / GAZEPOINT_RECORDING):

* Begin Experiment: ``gp = GazepointClient(); gp.connect()``
* Begin Routine of the FIRST routine: ``gp.start_recording(filename)``. Never in Begin
  Experiment: just before the first routine PsychoPy calls
  ``ioServer.syncClock(globalClock)``, which changes the base of ``core.getTime()``.
* Each Frame: ``if frameN == 0: win.callOnFlip(gp.event, 'XXX_ONSET', detail)``;
  End Routine: ``gp.event('XXX_OFFSET', detail)``.
* End Experiment: ``gp.stop()`` (also registered with ``atexit``).
"""
import atexit
import csv
import os
import re
import socket
import threading

from psychopy import core, logging

# Data streamed by Gazepoint Control (docs/project_knowledge/gazepoint_data_parameters.json
# and "Gazepoint API.pdf" in the Gazepoint installation folder).
ENABLE_COMMANDS = [
    "ENABLE_SEND_COUNTER",      # CNT
    "ENABLE_SEND_TIME",         # TIME
    "ENABLE_SEND_TIME_TICK",    # TIME_TICK
    "ENABLE_SEND_POG_FIX",      # FPOGX FPOGY FPOGS FPOGD FPOGID FPOGV
    "ENABLE_SEND_POG_LEFT",     # LPOGX LPOGY LPOGV
    "ENABLE_SEND_POG_RIGHT",    # RPOGX RPOGY RPOGV
    "ENABLE_SEND_POG_BEST",     # BPOGX BPOGY BPOGV
    "ENABLE_SEND_PUPIL_LEFT",   # LPCX LPCY LPD LPS LPV
    "ENABLE_SEND_PUPIL_RIGHT",  # RPCX RPCY RPD RPS RPV
    "ENABLE_SEND_EYE_LEFT",     # LEYEX LEYEY LEYEZ LPUPILD LPUPILV
    "ENABLE_SEND_EYE_RIGHT",    # REYEX REYEY REYEZ RPUPILD RPUPILV
    "ENABLE_SEND_PUPILMM",      # LPMM LPMMV RPMM RPMMV
    "ENABLE_SEND_BLINK",        # BKID BKDUR BKPMIN
    "ENABLE_SEND_DIAL",         # DIAL DIALV          (biometrics kit)
    "ENABLE_SEND_GSR",          # GSR GSRV            (biometrics kit)
    "ENABLE_SEND_HR",           # HR HRV              (biometrics kit)
    "ENABLE_SEND_HR_PULSE",     # HRP                 (biometrics kit)
    "ENABLE_SEND_HR_IBI",       # HRIBI               (biometrics kit)
    "ENABLE_SEND_USER_DATA",    # USER
]
GAZE_FIELDS = ["CNT", "TIME", "TIME_TICK",
               "FPOGX", "FPOGY", "FPOGS", "FPOGD", "FPOGID", "FPOGV",
               "LPOGX", "LPOGY", "LPOGV", "RPOGX", "RPOGY", "RPOGV",
               "BPOGX", "BPOGY", "BPOGV",
               "LPCX", "LPCY", "LPD", "LPS", "LPV", "RPCX", "RPCY", "RPD", "RPS", "RPV",
               "LEYEX", "LEYEY", "LEYEZ", "LPUPILV", "REYEX", "REYEY", "REYEZ", "RPUPILV",
               "LPMM", "LPMMV", "RPMM", "RPMMV", "BKID", "BKDUR", "BKPMIN",
               "DIAL", "DIALV", "GSR", "GSRV", "HR", "HRV", "HRP", "HRIBI",
               "USER"]
REC_RE = re.compile(r"<REC\s+([^>]*?)/>")
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')
MARKER_SAFE_RE = re.compile(r"[^A-Za-z0-9_:.\-|]")


class GazepointClient:
    def __init__(self, host="127.0.0.1", port=4242, connect_timeout=2.0):
        self.host, self.port, self.connect_timeout = host, port, connect_timeout
        self.sock = None
        self.connected = False
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._latest = {}
        self._gaze_file = self._gaze_writer = None
        self._events_file = self._events_writer = None
        self.current_marker = ""
        self.event_times = {}           # last time (core.getTime) of each event name
        self.n_samples = 0
        atexit.register(self.stop)

    # ------------------------------------------------------------------ setup
    def connect(self):
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=self.connect_timeout)
            self.sock.settimeout(0.5)
            for cmd in ENABLE_COMMANDS + ["ENABLE_SEND_DATA"]:
                self._send(f'<SET ID="{cmd}" STATE="1" />')
            self.connected = True
            logging.exp(f"Gazepoint: connected to {self.host}:{self.port}")
            # read (and drop) the stream until start_recording(): keeps the socket drained
            # and latest() up to date
            self._running = True
            self._thread = threading.Thread(target=self._reader, name="gazepoint-reader", daemon=True)
            self._thread.start()
        except OSError as e:
            self.connected = False
            self.sock = None
            logging.warning(f"Gazepoint: NOT connected ({self.host}:{self.port}): {e}")
            print(f"WARNING: Gazepoint Control no detectado en {self.host}:{self.port}. "
                  "El experimento sigue sin grabar la mirada desde PsychoPy.")
        return self.connected

    def start_recording(self, data_file_stem):
        """Open <stem>_gazepoint.csv and <stem>_events.csv and start the reader thread."""
        folder = os.path.dirname(os.path.abspath(data_file_stem))
        os.makedirs(folder, exist_ok=True)
        self._events_file = open(f"{data_file_stem}_events.csv", "w", newline="", encoding="utf-8")
        self._events_writer = csv.writer(self._events_file)
        self._events_writer.writerow(["t_psychopy", "event", "detail", "last_gp_CNT", "last_gp_TIME"])
        if not self.connected:
            self.event("GAZEPOINT_NOT_CONNECTED")
            return
        gaze_file = open(f"{data_file_stem}_gazepoint.csv", "w", newline="", encoding="utf-8")
        gaze_writer = csv.writer(gaze_file)
        gaze_writer.writerow(["t_psychopy", "marker"] + GAZE_FIELDS)
        with self._lock:                 # the reader thread writes from the next record on
            self._gaze_file, self._gaze_writer = gaze_file, gaze_writer
        self.event("RECORDING_START")

    # ------------------------------------------------------------ reader thread
    def _reader(self):
        buf = ""
        while self._running:
            try:
                chunk = self.sock.recv(8192)
            except socket.timeout:
                continue
            except OSError:
                break
            if not chunk:
                break
            t = core.getTime()
            buf += chunk.decode("utf-8", "replace")
            last_end = 0
            for m in REC_RE.finditer(buf):
                rec = dict(ATTR_RE.findall(m.group(1)))
                last_end = m.end()
                if "CNT" not in rec and "FPOGX" not in rec:
                    continue
                with self._lock:
                    rec["t_psychopy"] = t
                    self._latest = rec
                    if self._gaze_writer is None or self._gaze_file.closed:
                        continue                       # not recording yet (or stopped)
                    self._gaze_writer.writerow([f"{t:.6f}", self.current_marker] +
                                               [rec.get(k, "") for k in GAZE_FIELDS])
                    self.n_samples += 1
                    if self.n_samples % 300 == 0:      # ~2 s at 150 Hz
                        self._gaze_file.flush()
            # keep only the unfinished tail of the stream
            buf = buf[last_end:] if last_end else buf[-4096:]

    # ----------------------------------------------------------------- public
    def latest(self):
        """Last record as floats: {'FPOGX', 'FPOGY', 'FPOGV', 'BPOGX', ...} or {} if none."""
        with self._lock:
            rec = dict(self._latest)
        out = {}
        for k, v in rec.items():
            try:
                out[k] = float(v)
            except (TypeError, ValueError):
                out[k] = v
        return out

    def event(self, name, detail=""):
        """Log an event with the PsychoPy clock and copy it to the Gazepoint USER field.

        Call it with win.callOnFlip(gp.event, ...) to time-stamp a stimulus onset."""
        t = core.getTime()
        label = MARKER_SAFE_RE.sub("_", f"{name}|{detail}" if detail else name)[:120]
        with self._lock:
            self.current_marker = label
            self.event_times[name] = t
            last = self._latest
            if self._events_writer is not None:
                self._events_writer.writerow([f"{t:.6f}", name, detail, last.get("CNT", ""), last.get("TIME", "")])
                self._events_file.flush()
        if self.connected:
            self._send(f'<SET ID="USER_DATA" VALUE="{label}" />')
        return t

    def flush(self):
        """Write the buffered samples/events to disk (e.g. before reading them mid-session)."""
        with self._lock:
            for f in (self._gaze_file, self._events_file):
                if f is not None and not f.closed:
                    f.flush()

    def stop(self):
        if self._events_writer is not None and not self._events_file.closed:
            self.event("RECORDING_STOP")
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
        with self._lock:
            for f in (self._gaze_file, self._events_file):
                if f is not None and not f.closed:
                    f.close()
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None
        self.connected = False

    # ---------------------------------------------------------------- helpers
    def _send(self, msg):
        try:
            self.sock.sendall((msg + "\r\n").encode("utf-8"))
        except (OSError, AttributeError) as e:
            logging.warning(f"Gazepoint: could not send {msg}: {e}")


def loop_detail(loop):
    """Detail of a routine marker: '<loop name>:<trial index>' of the innermost loop.

    Joins the events with the PsychoPy CSV rows (column <loop name>.thisN)."""
    name = getattr(loop, "name", "") or ""
    n = getattr(loop, "thisN", None)
    return f"{name}:{n}" if n is not None else str(name)


def gaze_to_height_units(x_norm, y_norm, win_aspect):
    """Gazepoint screen fraction (origin top-left) -> PsychoPy 'height' units (origin centre)."""
    return (x_norm - 0.5) * win_aspect, 0.5 - y_norm


def sample_times(t_psychopy, gp_time, reset_jump=-0.5, percentile=1):
    """Time of each sample on the PsychoPy clock, rebuilt from the Gazepoint TIME column.

    ``t_psychopy`` is the arrival time of the TCP packet (jittered); ``TIME`` is exact.
    t = TIME + offset, with the offset the lower envelope (1st percentile) of
    t_psychopy - TIME, recomputed after every TIME reset (Gazepoint restarts TIME after
    a recalibration). Same method as prepare_gaze() in the eye tracking demo.
    Arguments are array-likes of the same length; returns a numpy array."""
    import numpy as np
    tp = np.asarray(t_psychopy, dtype=float)
    tm = np.asarray(gp_time, dtype=float)
    if not len(tm) or np.isnan(tm).mean() > 0.1:
        return tp.copy()
    seg = np.concatenate([[0], np.cumsum(np.diff(tm) < reset_jump)])
    t = np.full(len(tm), np.nan)
    for s in np.unique(seg):
        m = seg == s
        off = np.nanpercentile(tp[m] - tm[m], percentile)
        t[m] = tm[m] + off
    return t
