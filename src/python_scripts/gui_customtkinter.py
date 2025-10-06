
import tkinter as tk
import customtkinter as ctk

ctk.set_appearance_mode("light")  # o "dark"
ctk.set_default_color_theme("blue")  # Puedes personalizarlo más

BASE_COLOR = "#261866"  # mismo que en tu código

from tkinter import ttk
from python_scripts.gui_config_manager import modules, general_config, advanced_config
from PIL import Image, ImageTk, ImageSequence
from tkinter import filedialog

##############################################################
##############################################################
# _________________ GLOBAL CONFIGURATION _________________ #
##############################################################
##############################################################

DEBUG_LAYOUT = False  # Enable/disable debug layout colors

WINDOW_WIDTH_RATIO = 0.9
WINDOW_HEIGHT_RATIO = 0.8

NORTH_RATIO = 0.15
SOUTH_RATIO = 0.05

CENTER_TOP_RATIO = 0.25
CENTER_MIDDLE_RATIO = 0.5
CENTER_BOTTOM_RATIO = 0.25

#FONT SIZE CONFIG
FONT_SCALE = 1.0 # Default - changed dynamically below
TITLE_SIZE = 60 
PANEL_TITLE_SIZE = 15 
TEXT_SIZE = 13
TOOLTIP_SIZE = 10

SHOW_GIF_TOOLTIPS = True
TOOLTIP_GIF_SCALE = 0.2 # Scale factor for tooltip GIFs

ROUNDED_RADIUS = 7  # Corner radius for rounded frames


# BANNER CONFIG
LOGO_SIZE = (180, 150)   # tamaño máximo del logo (ancho, alto)
BANNER_BG = "#ffffff"  # azul grisáceo elegante
TITLE_FG = "#261866"

# COLORS
BASE_COLOR = "#261866"



##############################################################

def debug_frame(frame, color="red"):
    """If DEBUG_LAYOUT is active, add border and background color to the frame."""
    if DEBUG_LAYOUT:
        frame.config(borderwidth=3, relief="solid")
        try:
            frame.config(background=color)
        except tk.TclError:
            print("ttk.Frame does not support background directly, switch to tk.Frame if needed")
            pass

from PIL import Image, ImageTk, ImageSequence
import os

# Escalado para tooltips con GIFs
TOOLTIP_GIF_SCALE = 0.1
GIF_CACHE = {}  # Cache por ruta

def create_tooltip(widget, text, gif_path=None):
    tooltip = None
    gif_frames = []
    gif_label = None
    gif_job = None

    def load_gif(path, screen_width):
        if path in GIF_CACHE:
            return GIF_CACHE[path]
        try:
            original = Image.open(path)
            w, h = original.size
            target_w = int(screen_width * TOOLTIP_GIF_SCALE)
            target_h = int(target_w * h / w)

            frames = [
                ImageTk.PhotoImage(frame.resize((target_w, target_h), Image.LANCZOS))
                for frame in ImageSequence.Iterator(original)
            ]
            GIF_CACHE[path] = frames
            return frames
        except Exception as e:
            print(f"[Tooltip GIF] Error cargando '{path}': {e}")
            return []

    def enter(event):
        nonlocal tooltip, gif_label, gif_frames, gif_job

        if tooltip is not None:
            return  # Ya está visible (previene múltiples)

        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.config(bg="#ffffe0")  # ⚠️ Misma textura que antes

        frame = tk.Frame(tooltip, bg="#ffffe0", padx=6, pady=5)
        frame.pack()

        lbl = tk.Label(frame, text=text, bg="#ffffe0", justify="left",
                       anchor="w", wraplength=300,
                       font=scaled_font(TOOLTIP_SIZE, "bold", family="tahoma"))
        lbl.pack(anchor="w")

        if gif_path and SHOW_GIF_TOOLTIPS:
            screen_w = widget.winfo_screenwidth()
            gif_frames = load_gif(gif_path, screen_w)
            if gif_frames:
                gif_label = tk.Label(frame, bg="#ffffe0")
                gif_label.pack(anchor="center", pady=(6, 2))

                def animate(i=0):
                    nonlocal gif_job
                    if not gif_frames:
                        return
                    gif_label.config(image=gif_frames[i])
                    gif_job = gif_label.after(100, animate, (i + 1) % len(gif_frames))

                animate()

        # Posición al lado del cursor
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + 20
        tooltip.geometry(f"+{x}+{y}")
        tooltip.deiconify()

    def leave(event):
        nonlocal tooltip, gif_label, gif_job

        if tooltip:
            if gif_label and gif_job:
                gif_label.after_cancel(gif_job)
                gif_job = None
            tooltip.destroy()
            tooltip = None

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

    return None, None  # Ya no devolvemos elementos de UI



def _on_run_clicked(snapshot):
    # Aquí ya tienes todos los valores finales elegidos por el usuario
    print("[RUN] Final configuration snapshot:")
    for k, v in snapshot.items():
        print(f" - {k}: {v}")

def compute_estimated_time(modules_dict):
    """
    Compute total estimated time from selected tests in modules.
    Returns total in minutes (int).
    """
    total = 0
    for module in modules_dict.values():
        for test in module.get("tests", {}).values():
            if test.get("selected", False):
                total += int(test.get("estimated_time", 0))
    return total

def refresh_all_language():
    for panel in module_panels:
        panel.refresh_language()
    advanced_panel.refresh_language()

def scaled_font(base_size, weight="normal", family="Arial"):
    return (family, int(base_size * FONT_SCALE), weight)

class TopBanner:
    """
    Banner con 3 zonas:
      - Left: logo (frame de tamaño fijo = logo_size)
      - Center: título (expansible)
      - Right: tiempo + botón Run (frame de tamaño fijo = logo_size)
    """
    def __init__(self, parent, logo_path=None, title_text="BEGIBRAINTOOL",
                 bg="#4f5a65", fg="white", logo_size=(160, 160),
                 on_run=None, get_time_estimate=None):

        self.parent = parent
        self.logo_path = logo_path
        self.title_text = title_text
        self.bg = bg
        self.fg = fg
        self.logo_size = logo_size
        self.logo_image = None  # keep ref
        self.on_run = on_run or (lambda: print("[RUN] Triggered"))
        self.get_time_estimate = get_time_estimate or (lambda: 0)

        self._build()

    # ---------------- internal build ----------------
    def _build(self):
        self.parent.configure(bg=self.bg)
        self.parent.grid_rowconfigure(0, weight=1, minsize=self.logo_size[1] + 20)
        self.parent.grid_columnconfigure(0, weight=0, minsize=self.logo_size[0] + 20)
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure(2, weight=0, minsize=self.logo_size[0] + 20)

        self._build_left()
        self._build_center()
        self._build_right()

    def _build_left(self):
        self.left = tk.Frame(self.parent, bg=self.bg, width=self.logo_size[0], height=self.logo_size[1])
        self.left.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=10)
        self.left.grid_propagate(False)

        if self.logo_path:
            try:
                img = Image.open(self.logo_path)
                img.thumbnail(self.logo_size, Image.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(img)
                self.parent._image_ref_logo = self.logo_image
                tk.Label(self.left, image=self.logo_image, bg=self.bg).pack(expand=True)
                return
            except Exception as e:
                print(f"[WARNING] Could not load logo: {e}")

        tk.Label(self.left, text="Logo", font=("Arial", 10), bg=self.bg, fg=self.fg).pack(expand=True)

    def _build_center(self):
        self.center = tk.Frame(self.parent, bg=self.bg)
        self.center.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.center.grid_rowconfigure(0, weight=1)
        self.center.grid_columnconfigure(0, weight=1)

        self.title_label = tk.Label(
            self.center,
            text=self.title_text,
            font=scaled_font(TITLE_SIZE, "bold"),
            bg=self.bg,
            fg=self.fg,
            anchor="center",
        )
        self.title_label.grid(row=0, column=0, sticky="nsew")

    def _build_right(self):
        self.right = tk.Frame(self.parent, bg=self.bg, width=self.logo_size[0], height=self.logo_size[1])
        self.right.grid(row=0, column=2, sticky="nsew", padx=(10, 10), pady=10)
        self.right.grid_propagate(False)

        self.right.grid_rowconfigure(0, weight=0)
        self.right.grid_rowconfigure(1, weight=1)
        self.right.grid_columnconfigure(0, weight=1)

        # Botón Run
        run_btn = tk.Button(
            self.right,
            text="▶ Run",
            font=scaled_font(20, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#2ecc71",
            activeforeground="white",
            command=self.on_run
        )
        run_btn.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

    # ---------------- public helpers ----------------
    def update_time_label(self):
        """Llamar cuando cambie la selección de tests para refrescar el tiempo."""
        if hasattr(self, "time_label"):
            self.time_label.config(text=self._time_text())

class GeneralConfigPanel:
    """
    Builds a dynamic General Configuration panel from `general_config`.
    - Distributes items into 3 columns + right column with Run button.
    - Supports 'radio_button', bool, str (with options => Combobox), and 'file_path' types.
    - Localizes labels/tooltips using general_config["language"].
    - Keeps general_config[...] ["value"] in sync with UI.
    """
    def __init__(self, parent, general_config_dict, tooltip_factory, on_run=None):
        self.parent = parent
        self.general_config = general_config_dict
        self.create_tooltip = tooltip_factory
        self.on_run = on_run or (lambda cfg: print("Run with config:", cfg))

        self.BG = "#f7f7f7"
        self.FONT_TITLE = scaled_font(PANEL_TITLE_SIZE, "bold")
        self.NUM_COLUMNS = 3  # +1 implicit for Run at the right
        self.field_vars = {}  # key -> tk.Variable | (tick_var, path_var)
        self.lang_var = None  # reference for language Combo

        self._build()

    # --------- helpers (i18n) ----------
    def _current_lang(self):
        item = self.general_config.get("language", {})
        val = item.get("value")
        if not val:
            val = item.get("default", "en")
        return val

    def _vname(self, item):
        lang = self._current_lang()
        return item.get("variable_display_name", {}).get(lang, "")

    def _tooltip(self, item):
        lang = self._current_lang()
        return item.get("tooltip", {}).get(lang, "")

    def _label(self, parent, text):
        if not text:
            return None
        lbl = ttk.Label(parent, text=text)
        lbl.pack(anchor="w")
        return lbl
    
    def update_time(self):
        """
        Updates the estimated time label using external compute_estimated_time().
        """
        try:
            #from python_scripts.gui_config_manager import modules  # o ajústalo según tu estructura real
            total = compute_estimated_time(modules)
            self.time_label.config(text=f"⏱️ {total} min")
        except Exception as e:
            print(f"[ERROR] Estimating time: {e}")

    def _handle_load(self):
        filepath = filedialog.askopenfilename(title="Cargar configuración", filetypes=[("Config JSON", "*.json")])
        if filepath:
            import json
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for key, val in data.items():
                    if key in self.general_config:
                        self.general_config[key]["value"] = val
                self._refresh_texts()
                print(f"[LOAD] Configuración cargada desde {filepath}")
            except Exception as e:
                print(f"[ERROR] al cargar: {e}")

    def _handle_save(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Config JSON", "*.json")])
        if filepath:
            import json
            try:
                snapshot = {key: cfg.get("value", cfg.get("default")) for key, cfg in self.general_config.items()}
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(snapshot, f, indent=4)
                print(f"[SAVE] Configuración guardada en {filepath}")
            except Exception as e:
                print(f"[ERROR] al guardar: {e}")


    # --------- builders ----------
    def _build(self):
        # Frame exterior redondeado con fondo BASE_COLOR
        self.frame = ctk.CTkFrame(self.parent, corner_radius=12, fg_color=BASE_COLOR)
        self.frame.pack(fill="x", padx=10, pady=5)

        # Título del panel, dentro del marco exterior
        title_lbl = ctk.CTkLabel(
            master=self.frame,
            text="GENERAL CONFIGURATION",
            font=self.FONT_TITLE,
            text_color="white",
            anchor="center"
        )
        title_lbl.pack(fill="x", padx=10, pady=(10, 4))

        # Subframe blanco para el contenido, sin bordes redondeados
        content_frame = ctk.CTkFrame(self.frame, corner_radius=0, fg_color=self.BG)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Column container (para campos)
        col_container = tk.Frame(content_frame, background=self.BG)
        col_container.pack(fill="x", padx=10, pady=5)

        # Crear columnas
        self.columns = []
        for i in range(self.NUM_COLUMNS + 1):  # +1 columna para botones
            col = tk.Frame(col_container, background=self.BG)
            col.pack(side="left", expand=True, fill="both", padx=5)
            self.columns.append(col)

        # Poblar campos en las primeras columnas
        keys = list(self.general_config.keys())
        if "language" in keys:
            keys.remove("language")
            keys.insert(0, "language")

        per_col = (len(keys) + self.NUM_COLUMNS - 1) // self.NUM_COLUMNS
        for idx, key in enumerate(keys):
            col_idx = min(idx // per_col, self.NUM_COLUMNS - 1)
            self._create_field(self.columns[col_idx], key, self.general_config[key])

        # Columna derecha para botones y tiempo
        right_col = self.columns[-1]

        top_row = tk.Frame(right_col, background=self.BG)
        top_row.pack(fill="x", pady=(10, 15))

        # Botón Cargar 📂
        load_btn = tk.Button(
            top_row,
            text="📂",
            font=scaled_font(20, "bold"),
            bg="#2980b9",
            fg="white",
            width=3,
            command=self._handle_load
        )
        load_btn.pack(side="left", padx=(0, 5))

        # Botón Guardar 💾
        save_btn = tk.Button(
            top_row,
            text="💾",
            font=scaled_font(20, "bold"),
            bg="#27ae60",
            fg="white",
            width=3,
            command=self._handle_save
        )
        save_btn.pack(side="left", padx=(0, 5))

        # Tiempo estimado grande ⏱️
        self.time_label = tk.Label(
            top_row,
            text="⏱️ 0 min",
            font=scaled_font(18, "bold"),
            fg="black",
            background=self.BG
        )
        self.time_label.pack(side="left", padx=(10, 0))


    def _create_field(self, parent, key, cfg):
        ftype = cfg.get("type")
        # Container frame for spacing
        block = tk.Frame(parent, background=self.BG)
        block.pack(fill="x", pady=4, anchor="w")

        # For checkbuttons we sometimes prefer the label inline, but keep a header when provided
        label_text = self._vname(cfg)
        header = self._label(block, f"{label_text}:") if (label_text and ftype not in (bool, "file_path")) else None

        # ---- radio_button
        if ftype == "radio_button":
            default = cfg.get("default")
            var = tk.StringVar(value=cfg.get("value", default))
            row = tk.Frame(block, background=self.BG)
            row.pack(anchor="w")
            for opt in cfg.get("options", []):
                text = opt.capitalize()
                rb = ttk.Radiobutton(row, text=text, variable=var, value=opt,
                                     command=lambda k=key, v=var: self._update_value(k, v.get()))
                rb.pack(side="left", padx=(0, 6))
            self._maybe_tooltip(row, cfg)
            self.field_vars[key] = var
            # initial sync
            self._update_value(key, var.get())

        # ---- bool
        elif ftype == bool:
            current = cfg.get("value", cfg.get("default", False))
            var = tk.BooleanVar(value=current)
            cb_text = label_text or key.replace("_", " ").capitalize()
            cb = ttk.Checkbutton(block, text=cb_text, variable=var,
                                 command=lambda k=key, v=var: self._update_value(k, v.get()))
            cb.pack(anchor="w")
            self._maybe_tooltip(cb, cfg)
            self.field_vars[key] = var
            self._update_value(key, var.get())

        # ---- str with options => Combobox (language fits here)
        elif ftype == str and "options" in cfg:
            default = cfg.get("default")
            var = tk.StringVar(value=cfg.get("value", default))
            combo = ttk.Combobox(block, textvariable=var, values=cfg["options"], state="readonly", width=14)
            combo.pack(anchor="w")
            self._maybe_tooltip(combo, cfg)
            self.field_vars[key] = var
            self._update_value(key, var.get())

            # Special: When language changes, refresh texts
            if key == "language":
                self.lang_var = var
                combo.bind("<<ComboboxSelected>>", self._on_language_change)

        # ---- file_path
        elif ftype == "file_path":
            tick_var = tk.BooleanVar(value=bool(cfg.get("value")))
            path_var = tk.StringVar(value=cfg.get("value") or "")

            def toggle_state():
                st = "normal" if tick_var.get() else "disabled"
                entry.config(state=st)
                browse_btn.config(state=st)
                # If disabled, we set None (or empty) in config
                self._update_value(key, path_var.get() if tick_var.get() else "")

            cb_text = label_text or key.replace("_", " ").capitalize()
            cb = ttk.Checkbutton(block, text=cb_text, variable=tick_var, command=toggle_state)
            cb.pack(anchor="w")

            row = tk.Frame(block, background=self.BG)
            row.pack(fill="x")
            entry = ttk.Entry(row, textvariable=path_var, width=28, state="disabled")
            entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

            def browse():
                path = filedialog.askopenfilename(title="Select file", filetypes=[("All files", "*.*")])
                if path:
                    path_var.set(path)
                    self._update_value(key, path if tick_var.get() else "")

            browse_btn = ttk.Button(row, text="Browse", command=browse, state="disabled")
            browse_btn.pack(side="left")

            self._maybe_tooltip(cb, cfg)
            self.field_vars[key] = (tick_var, path_var)
            toggle_state()  # initialize state

        # ---- plain str / numeric fallback (if ever needed)
        else:
            # Fallback entry (kept simple)
            val = cfg.get("value", cfg.get("default", ""))
            var = tk.StringVar(value=str(val) if val is not None else "")
            ent = ttk.Entry(block, textvariable=var, width=20)
            ent.pack(anchor="w")
            self._maybe_tooltip(ent, cfg)
            ent.bind("<FocusOut>", lambda e, k=key, v=var: self._update_value(k, v.get()))
            ent.bind("<Return>",  lambda e, k=key, v=var: self._update_value(k, v.get()))
            self.field_vars[key] = var
            self._update_value(key, var.get())

    def _maybe_tooltip(self, widget, cfg):
        tip = self._tooltip(cfg)
        gif_path = cfg.get("gif_source", None)
        #print(f"Checking tooltip for {cfg} -> {tip}, gif: {gif_path}")
        if gif_path:
            print(f"Attaching tooltip with gif: {tip}, gif: {gif_path}")
            self.create_tooltip(widget, tip, gif_path)
        if tip:
            print(f"Attaching tooltip: {tip}, gif: {gif_path}")
            self.create_tooltip(widget, tip)


    def _update_value(self, key, value):
        # Keep general_config[key]["value"] updated
        if key in self.general_config:
            self.general_config[key]["value"] = value

    def _on_language_change(self, event=None):
        # Update general_config and re-render texts/tooltips
        new_lang = self.lang_var.get()
        self._update_value("language", new_lang)
        self._refresh_texts()
        refresh_all_language()

    def _refresh_texts(self):
        """Refresh label texts and tooltips in-place without rebuilding layout."""

        # Walk through all children and update labels/tooltips according to current language
        def refresh_block(block, key, cfg):
            # Update first label in block if present (header)
            children = block.winfo_children()
            # If the first child is a TLabel (header ending ":"), update it
            if children and isinstance(children[0], ttk.Label):
                vname = self._vname(cfg)
                if vname:
                    children[0].config(text=f"{vname}:")
            # Update checkbutton label for bool / file_path
            for ch in children:
                # ttk.Checkbutton keeps text config
                try:
                    if isinstance(ch, ttk.Checkbutton):
                        vname = self._vname(cfg)
                        if vname:
                            ch.config(text=vname if cfg.get("type") == bool else vname)
                except tk.TclError:
                    pass
            # Tooltips
            tip = self._tooltip(cfg)
            if tip:
                # reattach tooltip on top-most interactive child
                target = None
                for ch in children:
                    if isinstance(ch, (ttk.Checkbutton, ttk.Combobox, ttk.Entry, tk.Entry, tk.Button, ttk.Button, tk.Frame)):
                        target = ch
                        break
                if target:
                    self.create_tooltip(target, tip)

        # Iterate blocks by scanning the layout created in _create_field
        key_idx = 0
        per_col = (len(self.general_config.keys()) + self.NUM_COLUMNS - 1) // self.NUM_COLUMNS
        for col_i in range(self.NUM_COLUMNS):  # only the first 3 columns contain fields
            col = self.columns[col_i]
            for block in col.winfo_children():
                # blocks created by _create_field are tk.Frame; map back to key order
                if key_idx >= len(self.general_config):
                    break
                # Compute which key this block belongs to (robust mapping via field_vars order)
                # Safer: iterate general_config keys in the same order used in _build
                pass
        # Simpler: Full rebuild is the most reliable for i18n changes:
        self.frame.destroy()
        self._build()
        self.update_time()

    def _handle_run(self):
        # Produce a clean dict snapshot with user selections
        snapshot = {}
        for key, cfg in self.general_config.items():
            val = cfg.get("value", cfg.get("default"))
            snapshot[key] = val
        self.on_run(snapshot)

class ModuleSelectionPanel:
    """
    Panel con cabecera tipo banner y cuerpo con esquinas redondeadas
    usando customtkinter.
    """
    def __init__(self, parent, module_key, module_data, get_current_language, tooltip_factory,
                 on_open_advanced=None, on_test_toggle=None):
        self.parent = parent
        self.module_key = module_key
        self.module_data = module_data
        self.get_lang = get_current_language
        self.create_tooltip = tooltip_factory
        self.on_open_advanced = on_open_advanced
        self.on_test_toggle = on_test_toggle

        # referencias
        self.title_label = None
        self.advanced_btn = None
        self.test_widgets = []

        self._build()

    def _build(self):
        for child in self.parent.winfo_children():
            child.destroy()

        # === Contenedor principal con esquinas ===
        container = ctk.CTkFrame(self.parent, corner_radius=15, fg_color="transparent")
        container.pack(fill="x", pady=10, padx=10)

        # === Banner/header redondeado arriba ===
        header = ctk.CTkFrame(
            container,
            corner_radius=15,
            fg_color=BASE_COLOR,
        )
        header.pack(fill="x", side="top")

        self.title_label = ctk.CTkLabel(
            header,
            text=self._module_title(),
            font=("Arial", 16, "bold"),
            text_color="white",
            pady=8
        )
        self.title_label.pack(fill="x")

        # === Cuerpo (tests + botón) redondeado abajo ===
        body = ctk.CTkFrame(
            container,
            corner_radius=15,
            fg_color="white"
        )
        body.pack(fill="both", expand=True, side="top")

        # Tests
        self.test_widgets.clear()
        for test_key, test_data in self.module_data.get("tests", {}).items():
            self._add_test_checkbox(body, test_key, test_data)

        # Botón de opciones avanzadas
        self.advanced_btn = ctk.CTkButton(
            body,
            text=self._advanced_text(),
            command=self._open_advanced_window,
            fg_color="#2980b9",
            text_color="white",
            hover_color="#3498db"
        )
        self.advanced_btn.pack(side="bottom", pady=8)

    def _add_test_checkbox(self, parent, test_key, test_data):
        lang = self.get_lang()
        name = test_data.get("name", {}).get(lang, test_key)
        enabled = test_data.get("enabled", True)
        selected = bool(test_data.get("selected", False))

        var = ctk.BooleanVar(value=selected)

        def on_toggle():
            self.module_data["tests"][test_key]["selected"] = var.get()
            if callable(self.on_test_toggle):
                self.on_test_toggle()

        cb = ctk.CTkCheckBox(parent, text=name, variable=var, command=on_toggle)
        if not enabled:
            cb.configure(state="disabled")
        cb.pack(anchor="w", pady=2, padx=20)

        tooltip_text = test_data.get("tooltip", {}).get(lang, "")
        gif_path = test_data.get("gif_source", None)
        self.create_tooltip(cb, tooltip_text, gif_path)

        self.test_widgets.append({
            "key": test_key,
            "var": var,
            "cb": cb,
            "tooltip_text": tooltip_text,
        })

    def _module_title(self):
        lang = self.get_lang()
        return self.module_data.get("name", {}).get(lang, self.module_key)

    def _advanced_text(self):
        lang = self.get_lang()
        return {
            "es": "Opciones avanzadas",
            "en": "ADVANCED CONFIGURATION",
            "eu": "Aukera aurreratuak",
        }.get(lang, "ADVANCED CONFIGURATION")

    def _open_advanced_window(self):
        if self.on_open_advanced:
            self.on_open_advanced(self)
        # Aquí puedes abrir tu ModuleAdvancedWindow si lo necesitas

    def refresh_language(self):
        self.title_label.configure(text=self._module_title())
        for item in self.test_widgets:
            test_key = item["key"]
            test_data = self.module_data["tests"][test_key]
            name = test_data.get("name", {}).get(self.get_lang(), test_key)
            item["cb"].configure(text=name)
            new_tip = test_data.get("tooltip", {}).get(self.get_lang(), "")
            self.create_tooltip(item["cb"], new_tip)
        self.advanced_btn.configure(text=self._advanced_text())

        
class AdvancedOptionsPanel:
    """
    Creates a dynamic panel for advanced_config items.
    - Uses multi-language support from general_config["language"].
    - Organizes items into multiple columns.
    - Supports bool, str with options (combobox), and int/float/free entry.
    """
    def __init__(self, parent, config_dict, get_current_language, tooltip_factory, num_columns=3):
        self.parent = parent
        self.config = config_dict
        self.get_lang = get_current_language  # function returning "es", "en", or "eu"
        self.create_tooltip = tooltip_factory
        self.num_columns = num_columns
        self.vars = {}  # key -> tk.Variable

        self.BG = "#f7f7f7"
        self.FONT_TITLE = scaled_font(12, "bold")

        self._build()

    def _vname(self, key, item):
        lang = self.get_lang()
        return item.get("variable_display_name", {}).get(lang) or key.replace("_", " ").capitalize()

    def _tooltip(self, item):
        lang = self.get_lang()
        return item.get("tooltip", {}).get(lang, "")

    def _build(self):
        # Clear old widgets
        for child in self.parent.winfo_children():
            child.destroy()

        self.frame = tk.Frame(self.parent, background=self.BG, highlightbackground=BASE_COLOR, highlightthickness=1)
        self.frame.pack(fill="x", padx=10, pady=5)

        # Banner del panel
        header = tk.Label(
            self.frame,
            text="ADVANCED OPTIONS",
            font=self.FONT_TITLE,
            bg=BASE_COLOR,
            fg="white",
            anchor="center",
            padx=10,
            pady=6
        )
        header.pack(fill="x")

        # Subcontenedor para columnas
        cols_frame = tk.Frame(self.frame, background=self.BG)
        cols_frame.pack(fill="x", padx=10, pady=10)

        # Crear columnas horizontales (con pack left)
        self.columns = []
        for i in range(self.num_columns):
            col = tk.Frame(cols_frame, background=self.BG)
            col.pack(side="left", expand=True, fill="both", padx=5)
            self.columns.append(col)

        # Distribute items into columns
        keys = list(self.config.keys())
        per_column = (len(keys) + self.num_columns - 1) // self.num_columns

        for idx, key in enumerate(keys):
            col_idx = idx // per_column
            col = self.columns[col_idx]
            cfg = self.config[key]
            self._create_field(col, key, cfg)

    def _create_field(self, parent, key, cfg):
        field_type = cfg.get("type")
        opts = cfg.get("options")
        current_value = cfg.get("value", cfg.get("default"))

        # Container frame
        block = tk.Frame(parent, background=self.BG)
        block.pack(anchor="w", pady=2, fill="x")

        label_text = self._vname(key, cfg)

        # Add label to left unless bool (where we use inline text)
        if field_type != bool:
            lbl = tk.Label(block, text=label_text + ":", background=self.BG, font=scaled_font(TEXT_SIZE))
            lbl.pack(side="left", padx=(0, 10))

        # ======== BOOL =========
        if field_type == bool:
            var = tk.BooleanVar(value=current_value)
            cb = ttk.Checkbutton(block, text=label_text, variable=var)
            cb.pack(side="left")
            cb.config(command=lambda k=key, v=var: self._update_value(k, v.get()))
            self.create_tooltip(cb, self._tooltip(cfg))
            self.vars[key] = var
            self._update_value(key, var.get())

        # ======== COMBOBOX (str with options) =========
        elif field_type == str and opts:
            var = tk.StringVar(value=current_value)
            combo = ttk.Combobox(block, textvariable=var, values=opts, state="readonly", width=15)
            combo.pack(side="left")
            combo.bind("<<ComboboxSelected>>", lambda e, k=key, v=var: self._update_value(k, v.get()))
            self.create_tooltip(combo, self._tooltip(cfg))
            self.vars[key] = var
            self._update_value(key, var.get())

        # ======== TEXT ENTRY (generic str/int/float) =========
        elif field_type in (int, float) or (field_type == str and not opts):
            var = tk.StringVar(value=str(current_value) if current_value is not None else "")
            entry = ttk.Entry(block, textvariable=var, width=15)
            entry.pack(side="left")

            def commit(event=None, k=key, var_ref=var, typ=field_type):
                val = var_ref.get()
                try:
                    if typ == int:
                        val = int(val)
                    elif typ == float:
                        val = float(val)
                except ValueError:
                    pass
                self._update_value(k, val)

            entry.bind("<FocusOut>", commit)
            entry.bind("<Return>", commit)

            self.create_tooltip(entry, self._tooltip(cfg))
            self.vars[key] = var
            self._update_value(key, var.get())

    def _update_value(self, key, value):
        if key in self.config:
            self.config[key]["value"] = value

    def refresh_language(self):
        """Refresh labels and tooltips after language change."""
        self.frame.destroy()
        self._build()

class ModuleAdvancedWindow:
    def __init__(self, parent, module_data, get_current_language, tooltip_factory):
        self.parent = parent
        self.module_data = module_data
        self.lang_fn = get_current_language
        self.tooltip_factory = tooltip_factory

        # Crear ventana emergente
        self.top = tk.Toplevel(self.parent)
        self.top.title(self._module_title())
        self.top.geometry("600x480")
        self.top.grab_set()

        self._build()


    def _module_title(self):
        return self.module_data.get("name", {}).get(self.lang_fn(), "Module")


    def _tooltip(self, item):
        return item.get("tooltip", {}).get(self.get_lang(), "")

    def _vname(self, key, item):
        return item.get("variable_display_name", {}).get(self.get_lang(), key.replace("_", " ").capitalize())
    
    def _tab_label(self, key):
        return {
            "es": "Configuración general",
            "en": "General settings",
            "eu": "Ezarpen orokorrak"
        }.get(self.lang_fn(), "Settings")

    def _group_label(self, key):
        labels = {
            "grating": {
                "es": "Estímulo Gabor",
                "en": "Gabor stimulus",
                "eu": "Gabor estimulu"
            },
            "noise": {
                "es": "Ruido visual",
                "en": "Visual noise",
                "eu": "Zarata bisuala"
            },
            "experiment_params": {
                "es": "Parámetros del experimento",
                "en": "Experiment parameters",
                "eu": "Esperimentuaren parametroak"
            },
            "staircase_test": {
                "es": "Test de umbral",
                "en": "Threshold test",
                "eu": "Atalase proba"
            }
        }
        return labels.get(key, {}).get(self.lang_fn(), key.replace("_", " ").capitalize())


    def _build(self):
        self.notebook = ttk.Notebook(self.top)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # === Pestaña de configuración general del módulo ===
        if "config" in self.module_data:
            module_cfg = self.module_data["config"]
            frame = self._create_config_frame(module_cfg)
            self.notebook.add(frame, text=self._tab_label("module_config"))

        # === Pestañas por test con configuración ===
        tests = self.module_data.get("tests", {})
        for test_key, test_data in tests.items():
            if "config" in test_data:
                test_cfg = test_data["config"]
                frame = self._create_config_frame(test_cfg)
                test_name = test_data.get("name", {}).get(self.lang_fn(), test_key)
                self.notebook.add(frame, text=test_name)


    def _create_config_frame(self, config_dict):
        frame = tk.Frame(self.notebook, background="#f7f7f7")

        # Detectar si es un diccionario plano (campo único con "type") o agrupado
        is_flat = all("type" in field for field in config_dict.values())

        if is_flat:
            # Diccionario plano → meter en una sola columna
            panel = AdvancedOptionsPanel(
                parent=frame,
                config_dict=config_dict,
                get_current_language=self.lang_fn,
                tooltip_factory=self.tooltip_factory,
                num_columns=2
            )
        else:
            # Diccionario agrupado por secciones → crear subpaneles por grupo
            row = 0
            for group_name, group_fields in config_dict.items():
                subframe = tk.LabelFrame(
                    frame,
                    text=self._group_label(group_name),
                    font=scaled_font(TEXT_SIZE, "bold"),
                    relief="groove",
                    bd=2,
                    labelanchor="n",
                    background="#f7f7f7"
                )
                subframe.grid(row=row, column=0, sticky="nsew", padx=10, pady=6)
                row += 1
                AdvancedOptionsPanel(
                    parent=subframe,
                    config_dict=group_fields,
                    get_current_language=self.lang_fn,
                    tooltip_factory=self.tooltip_factory,
                    num_columns=2
                )
        return frame

    def _update(self, var, cfg, key, value=None):
        val = var.get() if value is None else value
        cfg["value"] = val


############################################################################################################################################################
##____________MAIN WINDOW____________####____________MAIN WINDOW____________####____________MAIN WINDOW____________####____________MAIN WINDOW____________##
############################################################################################################################################################

root = tk.Tk()
root.title("Begibraintool Configuration")

# Calculate screen size and apply ratios
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
win_w = int(screen_w * WINDOW_WIDTH_RATIO)
win_h = int(screen_h * WINDOW_HEIGHT_RATIO)

# Center window
x = (screen_w - win_w) // 2
y = (screen_h - win_h) // 2
root.geometry(f"{win_w}x{win_h}+{x}+{y}")

# Recalculate font scale based on screen width
if screen_w >= 3840:    # 4K screen
    FONT_SCALE = 1.6
elif screen_w >= 2560:  # WQHD
    FONT_SCALE = 1.3
elif screen_w >= 1920:  # Full HD
    FONT_SCALE = 1.1
else:
    FONT_SCALE = 1.0

# FONTS AND STYLE
# ========= ttk.Style with scaled fonts =========
style = ttk.Style()
#style.theme_use("default")  # Usa el tema por defecto, o cambia según tu necesidad

style.configure("TLabel", font=scaled_font(11))
style.configure("TButton", font=scaled_font(12))
style.configure("TRadiobutton", font=scaled_font(11))
style.configure("TCheckbutton", font=scaled_font(11))
style.configure("TCombobox", font=scaled_font(11))
style.configure("TEntry", font=scaled_font(11))

# (Opcional: para estados seleccionados, etc.)
style.map("TCheckbutton",
    foreground=[("active", "black"), ("selected", "black")],
    background=[("active", "white"), ("selected", "white")]
)



# Configure root grid (3x3 like BorderLayout)
root.grid_rowconfigure(0, weight=0)         # north row
root.grid_rowconfigure(1, weight=1)         # center row
root.grid_rowconfigure(2, weight=0)         # south row
root.grid_columnconfigure(0, weight=0)      # west column
root.grid_columnconfigure(1, weight=1)      # center column
root.grid_columnconfigure(2, weight=0)      # east column

######################################################
##____________ROOT PANEL: BORDER LAYOUT____________###
######################################################

# North
frame_north = tk.Frame(root)
debug_frame(frame_north, "lightblue")
frame_north.grid(row=0, column=0, columnspan=3, sticky="nsew")

# South
frame_south = tk.Frame(root)
debug_frame(frame_south, "lightgreen")
frame_south.grid(row=2, column=0, columnspan=3, sticky="nsew")

# West
frame_west = tk.Frame(root)
debug_frame(frame_west, "lightyellow")
frame_west.grid(row=1, column=0, sticky="nsew")

# East
frame_east = tk.Frame(root)
debug_frame(frame_east, "lightpink")
frame_east.grid(row=1, column=2, sticky="nsew")

# Center
frame_center = tk.Frame(root)
debug_frame(frame_center, "lightgray")
frame_center.grid(row=1, column=1, sticky="nsew")

# =======================
# Configure size proportions
# =======================
# North and South heights
root.grid_rowconfigure(0, minsize=int(win_h * NORTH_RATIO))  
root.grid_rowconfigure(2, minsize=int(win_h * SOUTH_RATIO))  

# Center frame takes all remaining space, divide it internally
frame_center.grid_rowconfigure(0, weight=1)
frame_center.grid_rowconfigure(1, weight=1)
frame_center.grid_rowconfigure(2, weight=1)

# Set explicit heights inside center frame
center_total_height = win_h * (1 - NORTH_RATIO - SOUTH_RATIO)  # height left after north & south
frame_center.grid_rowconfigure(0, minsize=int(center_total_height * CENTER_TOP_RATIO))
frame_center.grid_rowconfigure(1, minsize=int(center_total_height * CENTER_MIDDLE_RATIO))
frame_center.grid_rowconfigure(2, minsize=int(center_total_height * CENTER_BOTTOM_RATIO))
frame_center.grid_columnconfigure(0, weight=1)

# =======================
# Inner frames in center
# =======================
frame_center_top = tk.Frame(frame_center)
debug_frame(frame_center_top, "orange")
frame_center_top.grid(row=0, column=0, sticky="nsew")

######################################################
##____________CENTER PANEL: BORDER LAYOUT____________###
######################################################
# frame_center_middle es el panel de módulos
#
frame_center_middle = tk.Frame(frame_center)
debug_frame(frame_center_middle, "violet")
frame_center_middle.grid(row=1, column=0, sticky="nsew")

frame_center_bottom = tk.Frame(frame_center)
debug_frame(frame_center_bottom, "cyan")
frame_center_bottom.grid(row=2, column=0, sticky="nsew")

# =======================
# Divide middle frame into three columns (modules)
# =======================
frame_center_middle.grid_columnconfigure(0, weight=1, uniform="module")
frame_center_middle.grid_columnconfigure(1, weight=1, uniform="module")
frame_center_middle.grid_columnconfigure(2, weight=1, uniform="module")
frame_center_middle.grid_rowconfigure(0, weight=1)

# Module frames
module1_frame = ctk.CTkFrame(
    master=frame_center_middle,
    fg_color="white",            
    corner_radius=ROUNDED_RADIUS,              
    border_width=1,               
    border_color=BASE_COLOR
)
debug_frame(module1_frame, "salmon")  # solo colorea si DEBUG_LAYOUT = True
module1_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

module2_frame = ctk.CTkFrame(
    master=frame_center_middle,
    fg_color="white",            
    corner_radius=ROUNDED_RADIUS,              
    border_width=1,               
    border_color=BASE_COLOR
)
debug_frame(module2_frame, "khaki")
module2_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

module3_frame = ctk.CTkFrame(
    master=frame_center_middle,
    fg_color="white",            
    corner_radius=ROUNDED_RADIUS,              
    border_width=1,               
    border_color=BASE_COLOR       
)
debug_frame(module3_frame, "lightseagreen")
module3_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

banner = TopBanner(
    parent=frame_north,
    logo_path=r"C:\Users\akoun\Desktop\Biocruces\begibraintool\src\images\logo_BBT_no_bg.png",
    title_text="BEGIBRAINTOOL",
    bg=BANNER_BG,
    fg=TITLE_FG,
    logo_size=LOGO_SIZE,
    on_run=lambda: _on_run_clicked({k: v.get("value", v.get("default")) for k, v in general_config.items()}),
    get_time_estimate=lambda: compute_estimated_time(modules)
)

general_panel = GeneralConfigPanel(
    parent=frame_center_top,
    general_config_dict=general_config,
    tooltip_factory=create_tooltip,
    on_run=_on_run_clicked
)

# Advanced options panel (bottom center)
advanced_panel = AdvancedOptionsPanel(
    parent=frame_center_bottom,
    config_dict=advanced_config,
    get_current_language=lambda: general_config["language"]["value"] or general_config["language"]["default"],
    tooltip_factory=create_tooltip,
    num_columns=3
)

# Create module panels dynamically
module_panels = []
lang_fn = lambda: (general_config["language"]["value"] or general_config["language"]["default"])

module_frames = [module1_frame, module2_frame, module3_frame]

for idx, (module_key, module_data) in enumerate(modules.items()):
    if idx >= len(module_frames):
        break
    panel = ModuleSelectionPanel(
        parent=module_frames[idx],
        module_key=module_key,
        module_data=module_data,
        get_current_language=lang_fn,
        tooltip_factory=create_tooltip,
        on_test_toggle=general_panel.update_time
    )

    module_panels.append(panel)



#############  MAIN LOOP  #########################################
root.mainloop()
############################################################################################################################################################
