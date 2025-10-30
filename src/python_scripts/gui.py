'''
Vas a ser mi programador de interfaz gráfica en python tkinter. Vengo del mundo de Java así que muchas referencias serán respecto al mundo de swing. Contexto: la GUI no va a ser más que una ventana para seleccionar los módulos y la configuración de estos módulos (que al cerrar la ventana se traduce a una estructura de datos) de un experimento de psychopy. La idea es configurar el experimento de psychopy desde aquí.

Especificaciones: cuento con dos archivos .py; gui.py y gui_config_manager.py. En config manager almaceno el codigo con un diccionario de los módulos disponibles (que luego lee psychopy) y funciones como save_config_to_file, load_saved_configuration... en gui.py unicamente debo tener aspectos gráficos.

El codigo debe estar bien estructurado y tener al principio una sección de confiugración global donde almacene los ratios, ya que quiero trabajar con un layout en el root tipo 'border layout'. Adjunto ejemplo a continuación. Muy inmportante la opción de debug, para poder visualizar los paneles, también en el ejemplo. 

El código debe ser en ingles (nombres de variables)
'''


import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageSequence
import json
# from python_scripts 
import gui_config_manager
import matplotlib.colors as mcolors

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
FONT_SCALE = 1.3#1.85#1.30 # Default - changed dynamically below
TITLE_SIZE = 60 
PANEL_TITLE_SIZE = 15 
TEXT_SIZE = 11
TOOLTIP_SIZE = 10

SHOW_GIF_TOOLTIPS = True
TOOLTIP_GIF_SCALE = 0.2 # Scale factor for tooltip GIFs


# BANNER CONFIG
LOGO_SIZE = (180, 150)   # tamaño máximo del logo (ancho, alto)
BANNER_BG = "#ffffff"  # azul grisáceo elegante
TITLE_FG = "#261866"

# COLORS
BASE_COLOR = "#261866"

GIF_CACHE = {}  # Cache por ruta

##############################################################

def scaled_font(base_size, weight="normal", family="Arial"):
        return (family, int(base_size * FONT_SCALE), weight)

def _normalize_color(color_str):
    try:
        return mcolors.to_hex(color_str)
    except ValueError:
        return "#000000"
    
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
    def __init__(self, parent, general_config_dict, tooltip_factory, on_run=None, on_load=None, compute_time_fn=None, on_language_change=None):
        self.parent = parent
        self.general_config = general_config_dict
        self.create_tooltip = tooltip_factory
        self.on_run = on_run or (lambda cfg: print("Run with config:", cfg))
        self.on_load = on_load or (lambda: print("Load config not connected"))
        self.compute_estimated_time = compute_time_fn or (lambda modules: 0)
        self.on_language_change = on_language_change or (lambda: None)

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
            
            total = self.compute_estimated_time(gui_config_manager.modules)
            self.time_label.config(text=f"⏱️ {total} min")
        except Exception as e:
            print(f"[ERROR] Estimating time: {e}")

    # --------- builders ----------
    def _build(self):
        if hasattr(self, 'frame'):
            self.frame.destroy()

        # Root frame of the panel
        self.frame = tk.Frame(self.parent, background=self.BG,  highlightbackground=BASE_COLOR, highlightthickness=1)
        self.frame.pack(fill="x", padx=10, pady=5)

        # Header
        header = tk.Frame(self.frame, bg=BASE_COLOR)
        header.pack(fill="x")
        title_lbl = tk.Label(
            header,
            text="GENERAL CONFIGURATION",
            bg=BASE_COLOR,
            fg="white",
            font=scaled_font(PANEL_TITLE_SIZE, "bold"),
            padx=10, pady=4,
            anchor="center"
        )
        title_lbl.pack(fill="x")

        # Column container
        col_container = tk.Frame(self.frame, background=self.BG)
        col_container.pack(fill="x", padx=10, pady=5)

        # 🔹 Crear columnas PRIMERO
        self.columns = []
        for i in range(self.NUM_COLUMNS + 1):  # +1 columna para botones
            col = tk.Frame(col_container, background=self.BG)
            col.pack(side="left", expand=True, fill="both", padx=5)
            self.columns.append(col)

        # 🔹 Poblar campos en las primeras columnas
        keys = list(self.general_config.keys())
        if "language" in keys:
            keys.remove("language")
            keys.insert(0, "language")

        per_col = (len(keys) + self.NUM_COLUMNS - 1) // self.NUM_COLUMNS
        for idx, key in enumerate(keys):
            col_idx = min(idx // per_col, self.NUM_COLUMNS - 1)
            self._create_field(self.columns[col_idx], key, self.general_config[key])

        # 🔹 AHORA usar la última columna (botones + tiempo)
        right_col = self.columns[-1]

        # Contenedor horizontal para botones + tiempo
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
            command=self.on_load
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
            command=gui_config_manager.save_configuration_to_file,
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
            if cfg["value"] is None:
                cfg["value"] = cfg.get("default")

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
            if cfg["value"] is None:
                cfg["value"] = cfg.get("default")
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

        if gif_path:
            print(f"Attaching tooltip with gif: {tip}, gif: {gif_path}")
            self.create_tooltip(widget, tip, gif_path)

        elif tip:
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
        self.on_language_change()

    def _refresh_texts(self):
        """Refresh label texts and tooltips in-place without rebuilding layout."""

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
    Creates a module panel directly inside the given parent frame.
    - Title (translated)
    - Dynamic list of test checkboxes (with tooltips)
    - Bottom-centered 'Advanced options' button opening a Toplevel
    - Keeps `modules[module_key]['tests'][test_key]['selected']` in sync
    """
    def __init__(self, parent, module_key, module_data, get_current_language, tooltip_factory,
                 on_open_advanced=None, on_test_toggle=None):
        self.parent = parent
        self.module_key = module_key
        self.module_data = module_data
        self.get_lang = get_current_language
        self.create_tooltip = tooltip_factory
        self.on_open_advanced = on_open_advanced  # optional callback(panel)->None
        self.on_test_toggle = on_test_toggle

        # Keep references for refresh
        self.title_label = None
        self.advanced_btn = None
        self.test_widgets = []  # list of dicts: { 'key', 'var', 'cb', 'tooltip_text' }

        self._build()

    # ---------- UI build ----------
    def _build(self):
        # Clear the container frame first
        for child in self.parent.winfo_children():
            child.destroy()

        # Title with background banner (top centered)
        header = tk.Frame(self.parent, bg=BASE_COLOR)
        header.pack(fill="x")

        self.title_label = tk.Label(
            header,
            text=self._module_title(),
            font=scaled_font(PANEL_TITLE_SIZE, "bold"),
            bg=BASE_COLOR,
            fg="white",
            anchor="center",
            pady=6
        )
        self.title_label.pack(fill="x")

        # Checkbox de selección global ===
        self.select_all_var = tk.BooleanVar(value=self._all_tests_selected())
        select_all_cb = ttk.Checkbutton(
            self.parent,
            text=self._select_all_text(),
            variable=self.select_all_var,
            command=self._on_select_all_toggle
        )
        select_all_cb.pack(anchor="nw", pady=(6, 4), padx=(20, 0))

        # Tests (left aligned)
        self.test_widgets.clear()
        for test_key, test_data in self.module_data.get("tests", {}).items():
            self._add_test_checkbox(test_key, test_data)

        # Advanced options button (bottom-centered)
        self.advanced_btn = tk.Button(
            self.parent,
            text=self._advanced_text(),
            command=self._open_advanced_window,
            bg="#2980b9",
            fg="white",
            activebackground="#3498db",
            relief="raised"
        )
        self.advanced_btn.pack(side="bottom", pady=6)

    def _add_test_checkbox(self, test_key, test_data):
        lang = self.get_lang()
        name = test_data.get("name", {}).get(lang, test_key)
        enabled = test_data.get("enabled", True)
        selected = bool(test_data.get("selected", False))

        var = tk.BooleanVar(value=selected)

        def on_toggle():
            self.module_data["tests"][test_key]["selected"] = var.get()
            self._update_module_selected_flag()
            if callable(self.on_test_toggle):
                self.on_test_toggle()

        cb = ttk.Checkbutton(self.parent, text=name, variable=var, command=on_toggle)
        if not enabled:
            cb.state(["disabled"])
        cb.pack(anchor="nw", pady=2, padx=(40, 0))

        # --- Tooltip + GIF (compatibilidad con create_tooltip antigua) ---
        tooltip_text = test_data.get("tooltip", {}).get(lang, "")
        gif_path = test_data.get("gif_source", None)
        try:
            # nueva firma: (widget, text, gif_path)
            self.create_tooltip(cb, tooltip_text, gif_path)
            #self.tooltip_factory(cb, tooltip_text, gif_path)
        except TypeError:
            # firma antigua: (widget, text)
            self.create_tooltip(cb, tooltip_text)

        self.test_widgets.append({
            "key": test_key,
            "var": var,
            "cb": cb,
            "tooltip_text": tooltip_text,
        })

    def _select_all_text(self):
        return {
            "es": "Seleccionar todo",
            "en": "Select all",
            "eu": "Hautatu denak"
        }.get(self.get_lang(), "Select all")
    
    def _on_select_all_toggle(self):
        select_all = self.select_all_var.get()

        for item in self.test_widgets:
            var = item["var"]
            cb = item["cb"]
            test_key = item["key"]

            if "disabled" not in cb.state():  # solo afecta a los habilitados
                var.set(select_all)
                self.module_data["tests"][test_key]["selected"] = select_all
                
        self._update_module_selected_flag()

        if callable(self.on_test_toggle):
            self.on_test_toggle()

    def _all_tests_selected(self):
        for test_data in self.module_data.get("tests", {}).values():
            if test_data.get("enabled", True) and not test_data.get("selected", False):
                return False
        return True

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
        lang = self.get_lang()

        top = tk.Toplevel(self.parent)
        top.title(self.module_data["name"].get(lang, self.module_key))
        top.geometry("720x560")
        top.grab_set()

        # style = ttk.Style()
        # style.configure("Custom.TNotebook.Tab", font=scaled_font(TEXT_SIZE))

        style = ttk.Style()
        # style.theme_use("clam")

        unique_style = "AdvancedWindow.TNotebook"
        unique_tab_style = f"{unique_style}.Tab"

        # 🔹 Heredamos el layout del notebook base
        style.layout(unique_style, style.layout("TNotebook"))
        style.layout(unique_tab_style, style.layout("TNotebook.Tab"))

        # Estilo base del notebook
        style.configure(
            unique_style,
            background="#f5f5f5",
            borderwidth=0,
            padding=[6, 6]
        )

        # Estilo de las pestañas
        style.configure(
            unique_tab_style,
            font=scaled_font(TEXT_SIZE - 2, "bold"),
            padding=[10, 5],
            background="#e6e6e6",
            foreground="#5E5E5E",
            borderwidth=0
        ) 

        style.map(
            unique_tab_style,
            background=[ # not working
                ("selected", "#751010"),
                ("active", "#f0f0f0")
            ],
            foreground=[
                ("selected", BASE_COLOR),
                ("active", "#686868")
            ]
        )


        notebook = ttk.Notebook(top, style=unique_style)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # === Pestaña de configuración general del módulo ===
        if "config" in self.module_data:
            general_config = self.module_data["config"]
            frame = self._build_config_frame(notebook, general_config, is_grouped=True)
            tab_label = {
                "es": "Configuración general",
                "en": "General settings",
                "eu": "Ezarpen orokorrak"
            }.get(lang, "Settings")
            notebook.add(frame, text=tab_label)

        # === Pestañas por test con configuración individual ===
        for test_key, test_data in self.module_data.get("tests", {}).items():
            if "config" in test_data:
                frame = self._build_config_frame(notebook, test_data["config"], is_grouped=False)
                test_name = test_data.get("name", {}).get(lang, test_key)
                notebook.add(frame, text=test_name)

    def _build_config_frame(self, parent, config_dict, is_grouped=False):
        frame = tk.Frame(parent, background="#f7f7f7")

        if is_grouped:
            # Agrupado por secciones (ej. grating, noise, etc.)
            for group_key, group_fields in config_dict.items():
                group_label = {
                    "grating": {"es": "Estímulo Gabor", "en": "Gabor stimulus", "eu": "Gabor estimulu"},
                    "noise": {"es": "Ruido visual", "en": "Visual noise", "eu": "Zarata bisuala"},
                    "experiment_params": {"es": "Parámetros del experimento", "en": "Experiment parameters", "eu": "Esperimentuaren parametroak"},
                    "staircase_test": {"es": "Test de umbral", "en": "Threshold test", "eu": "Atalase proba"},
                }.get(group_key, {})

                title = group_label.get(self.get_lang(), group_key.capitalize())

                section = tk.LabelFrame(
                    frame, text=title,
                    font=scaled_font(TEXT_SIZE, "bold"),
                    background="#f7f7f7", bd=1, relief="groove", labelanchor="n"
                )
                section.pack(fill="x", padx=10, pady=6)

                self._fill_fields(section, group_fields)

        else:
            # Diccionario plano
            self._fill_fields(frame, config_dict)
        
        # ======== ACTION BUTTONS (Save + Reset) ========
        btn_texts_save = {
            "es": "Guardar y cerrar",
            "en": "Save and Close",
            "eu": "Gorde eta itxi"
        }
        btn_texts_reset = {
            "es": "Restablecer valores por defecto",
            "en": "Reset to default values",
            "eu": "Balio lehenetsiak berrezarri"
        }

        idioma = self.get_lang()
        btn_save_text = btn_texts_save.get(idioma, "Save and Close")
        btn_reset_text = btn_texts_reset.get(idioma, "Reset to default values")

        def save_and_close():
            parent.winfo_toplevel().destroy()  # cierra la ventana superior

        def reset_to_defaults():
            """
            Restablece todos los valores del diccionario a su valor 'default'
            y actualiza los widgets correspondientes.
            """
            def recursive_reset(config):
                for key, item in config.items():
                    if isinstance(item, dict) and "value" in item:
                        default_val = item.get("default")
                        item["value"] = default_val
                    elif isinstance(item, dict):
                        recursive_reset(item)

            recursive_reset(config_dict)
            # Recrear los widgets de configuración desde cero
            for child in frame.winfo_children():
                child.destroy()
            # reconstruir la parte visible
            if is_grouped:
                for group_key, group_fields in config_dict.items():
                    group_label = {
                        "grating": {"es": "Estímulo Gabor", "en": "Gabor stimulus", "eu": "Gabor estimulu"},
                        "noise": {"es": "Ruido visual", "en": "Visual noise", "eu": "Zarata bisuala"},
                        "experiment_params": {"es": "Parámetros del experimento", "en": "Experiment parameters", "eu": "Esperimentuaren parametroak"},
                        "staircase_test": {"es": "Test de umbral", "en": "Threshold test", "eu": "Atalase proba"},
                    }.get(group_key, {})
                    title = group_label.get(self.get_lang(), group_key.capitalize())
                    section = tk.LabelFrame(
                        frame, text=title,
                        font=scaled_font(TEXT_SIZE, "bold"),
                        background="#f7f7f7", bd=1, relief="groove", labelanchor="n"
                    )
                    section.pack(fill="x", padx=10, pady=6)
                    self._fill_fields(section, group_fields)
            else:
                self._fill_fields(frame, config_dict)

            # volver a poner los botones
            btn_frame = tk.Frame(frame, bg="#f7f7f7")
            btn_frame.pack(fill="x", pady=(10, 10))
            ttk.Button(btn_frame, text=btn_reset_text, command=reset_to_defaults).pack(side="left", padx=(10, 5))
            ttk.Button(btn_frame, text=btn_save_text, command=save_and_close).pack(side="right", padx=(5, 10))

        # Frame para agrupar botones
        btn_frame = tk.Frame(frame, bg="#f7f7f7")
        btn_frame.pack(fill="x", pady=(10, 10))

        ttk.Button(btn_frame, text=btn_reset_text, command=reset_to_defaults).pack(side="left", padx=(10, 5))
        ttk.Button(btn_frame, text=btn_save_text, command=save_and_close).pack(side="right", padx=(5, 10))

        return frame

    def _fill_fields(self, parent, config_dict):
        for key, item in config_dict.items():
            label_text = item.get("variable_display_name", {}).get(self.get_lang(), key)
            tooltip = item.get("tooltip", {}).get(self.get_lang(), "")
            value = item.get("value")
            #print(f"Filling field {key} with value: {value}")
            if value is None:
                value = item.get("default")
                item["value"] = value

            ftype = item.get("type")
            options = item.get("options", [])

            container = tk.Frame(parent, bg="#f7f7f7")
            container.pack(fill="x", padx=10, pady=4)

            label = tk.Label(container, text=label_text + ":", bg="#f7f7f7", font=scaled_font(TEXT_SIZE))
            label.pack(side="left", padx=(0, 10))

            if ftype == bool:
                var = tk.BooleanVar(value=value)
                cb = ttk.Checkbutton(container, variable=var)
                cb.pack(side="left")
                cb.config(command=lambda v=var, i=item: i.update({"value": v.get()}))
                #self.create_tooltip(cb, tooltip)
                self.create_tooltip(cb, tooltip)

            elif ftype == str and options:
                var = tk.StringVar(value=value)
                combo = ttk.Combobox(container, textvariable=var, values=options, state="readonly", width=15)
                combo.pack(side="left")
                combo.bind("<<ComboboxSelected>>", lambda e, v=var, i=item: i.update({"value": v.get()}))
                self.create_tooltip(combo, tooltip)

            elif ftype == "color":
                var = tk.StringVar(value=value or "#000000")

                color_frame = tk.Frame(container, bg="#f7f7f7")
                color_frame.pack(side="left")

                # Preview del color
                preview = tk.Canvas(color_frame, width=22, height=22, bg=var.get(), highlightthickness=1, highlightbackground="#aaa")
                preview.pack(side="left", padx=(0, 5))

                # Entry para mostrar código de color
                color_code = tk.Entry(color_frame, textvariable=var, width=8, justify="center", state="readonly", readonlybackground="#f0f0f0")
                color_code.pack(side="left", padx=(0, 5))

                # Traducciones del texto del botón
                btn_texts = {
                    "es": "Seleccionar",
                    "en": "Select",
                    "eu": "Hautatu"
                }

                btn_text = btn_texts.get(self.get_lang(), "Select")

                # Botón para abrir color picker
                def pick_color(v=var, p=preview, i=item):
                    selected = colorchooser.askcolor(color=v.get(), title=btn_text)
                    if selected[1]:
                        v.set(selected[1])
                        i["value"] = selected[1]
                        p.config(bg=selected[1])

                btn = ttk.Button(color_frame, text=btn_text, command=pick_color, width=10)
                btn.pack(side="left")

                self.create_tooltip(btn, tooltip)

            elif ftype == list and isinstance(value, list) and len(value) == 2:
                var1 = tk.StringVar(value=str(value[0]))
                var2 = tk.StringVar(value=str(value[1]))

                entry1 = ttk.Entry(container, textvariable=var1, width=8)
                entry1.pack(side="left", padx=(0, 4))
                entry2 = ttk.Entry(container, textvariable=var2, width=8)
                entry2.pack(side="left", padx=(0, 4))

                def commit_list(event=None):
                    try:
                        v1 = float(var1.get())
                        v2 = float(var2.get())
                        item["value"] = [v1, v2]
                    except ValueError:
                        pass  # No actualices si hay valores no válidos

                entry1.bind("<FocusOut>", commit_list)
                entry1.bind("<Return>", commit_list)
                entry2.bind("<FocusOut>", commit_list)
                entry2.bind("<Return>", commit_list)

                self.create_tooltip(entry1, tooltip)
                self.create_tooltip(entry2, tooltip)

            elif ftype in (int, float, str):
                var = tk.StringVar(value=str(value))
                entry = ttk.Entry(container, textvariable=var, width=15)
                entry.pack(side="left")

                def commit(event=None, v=var, i=item, typ=ftype):
                    val = v.get()
                    try:
                        if typ == int:
                            val = int(val)
                        elif typ == float:
                            val = float(val)
                    except ValueError:
                        pass
                    i["value"] = val

                entry.bind("<FocusOut>", commit)
                entry.bind("<Return>", commit)
                self.create_tooltip(entry, tooltip)

    def _update_module_selected_flag(self):
        """
        Actualiza el flag 'selected' del módulo si al menos uno de sus tests está seleccionado.
        """
        any_selected = any(
            test["selected"]
            for test in self.module_data.get("tests", {}).values()
            if test.get("enabled", True)
        )
        self.module_data["selected"] = any_selected

    def refresh_language(self):
        """Re-label module title, tests and button after language change."""
        # Title
        self.title_label.config(text=self._module_title())
        # Tests
        for item in self.test_widgets:
            test_key = item["key"]
            test_data = self.module_data["tests"][test_key]
            name = test_data.get("name", {}).get(self.get_lang(), test_key)
            item["cb"].config(text=name)
            # Re-attach tooltip with new language
            new_tip = test_data.get("tooltip", {}).get(self.get_lang(), "")
            self.create_tooltip(item["cb"], new_tip)
        # Button
        self.advanced_btn.config(text=self._advanced_text())

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
            font=scaled_font(PANEL_TITLE_SIZE, "bold"),
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
        current_value = cfg.get("value")
        if current_value is None:
            current_value = cfg.get("default")
            cfg["value"] = current_value  # sincroniza


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
        
        # ======== COLOR PICKER =========
        elif field_type == "color":
            var = tk.StringVar(value=current_value)

            # Contenedor para color + botón
            color_frame = tk.Frame(block, bg=self.BG)
            color_frame.pack(side="left", padx=5)

            # Preview del color
            preview = tk.Canvas(color_frame, width=22, height=22, bg=current_value, highlightthickness=1, highlightbackground="#aaa")
            preview.pack(side="left", padx=(0, 5))

            # Botón para abrir el color picker
            color_btn = ttk.Button(
                color_frame,
                text="Seleccionar",
                command=lambda k=key, v=var, p=preview: self._pick_color(k, v, p),
                width=10
            )
            color_btn.pack(side="left")

            self.create_tooltip(color_btn, self._tooltip(cfg))
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

    def _pick_color(self, key, var, preview_widget):
        """Abre el selector de color y actualiza el valor del campo."""
        initial_color = var.get() or "#000000"
        color = colorchooser.askcolor(initialcolor=initial_color, title="Selecciona un color")

        if color[1] is not None:
            hex_color = color[1]
            var.set(hex_color)
            self._update_value(key, hex_color)
            preview_widget.config(bg=hex_color)


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

class BegibraintoolGUI:
    def __init__(self):

        #from python_scripts import gui_config_manager
        self.gui_config_manager = gui_config_manager
        self.general_config = gui_config_manager.general_config
        self.advanced_config = gui_config_manager.advanced_config
        self.modules = gui_config_manager.modules

        self.root = tk.Tk()
        self.root.title("Begibraintool Configuration")

        # Calculate screen size and apply ratios
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = int(screen_w * WINDOW_WIDTH_RATIO)
        win_h = int(screen_h * WINDOW_HEIGHT_RATIO)

        # Center window
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")

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

        style = ttk.Style()
        #style.theme_use("default")  # Usa el tema por defecto, o cambia según tu necesidad

        style.configure("TLabel",       font=scaled_font(11))
        style.configure("TButton",      font=scaled_font(12))
        style.configure("TRadiobutton", font=scaled_font(11))
        style.configure("TCheckbutton", font=scaled_font(11))
        style.configure("TCombobox",    font=scaled_font(11))
        style.configure("TEntry",       font=scaled_font(11))

        # (Opcional: para estados seleccionados, etc.)
        # style.map("TCheckbutton",
        #     foreground=[("active", "black"), ("selected", "black")],
        #     background=[("active", "white"), ("selected", "white")]
        #         )
        
        self._build_layout(win_w, win_h)

    
    def _on_run_clicked(self, config_values):
            self.root.quit()
            self.root.destroy()

    def _build_layout(self, win_w, win_h):
        # Configure root grid (3x3 like BorderLayout)
        self.root.grid_rowconfigure(0, weight=0)         # north row
        self.root.grid_rowconfigure(1, weight=1)         # center row
        self.root.grid_rowconfigure(2, weight=0)         # south row
        self.root.grid_columnconfigure(0, weight=0)      # west column
        self.root.grid_columnconfigure(1, weight=1)      # center column
        self.root.grid_columnconfigure(2, weight=0)      # east column

        ######################################################
        ##____________ROOT PANEL: BORDER LAYOUT____________###
        ######################################################

        # North
        self.frame_north = tk.Frame(self.root)
        self.debug_frame(self.frame_north, "lightblue")
        self.frame_north.grid(row=0, column=0, columnspan=3, sticky="nsew")

        # South
        self.frame_south = tk.Frame(self.root)
        self.debug_frame(self.frame_south, "lightgreen")
        self.frame_south.grid(row=2, column=0, columnspan=3, sticky="nsew")

        # West
        self.frame_west = tk.Frame(self.root)
        self.debug_frame(self.frame_west, "lightyellow")
        self.frame_west.grid(row=1, column=0, sticky="nsew")

        # East
        self.frame_east = tk.Frame(self.root)
        self.debug_frame(self.frame_east, "lightpink")
        self.frame_east.grid(row=1, column=2, sticky="nsew")

        # Centerself.
        self.frame_center = tk.Frame(self.root)
        self.debug_frame(self.frame_center, "lightgray")
        self.frame_center.grid(row=1, column=1, sticky="nsew")

        # =======================
        # Configure size proportions
        # =======================
        # North and South heights
        self.root.grid_rowconfigure(0, minsize=int(win_h * NORTH_RATIO))  
        self.root.grid_rowconfigure(2, minsize=int(win_h * SOUTH_RATIO))  

        # Center frame takes all remaining space, divide it internally
        self.frame_center.grid_rowconfigure(0, weight=1)
        self.frame_center.grid_rowconfigure(1, weight=1)
        self.frame_center.grid_rowconfigure(2, weight=1)

        # Set explicit heights inside center frame
        center_total_height = win_h * (1 - NORTH_RATIO - SOUTH_RATIO)  # height left after north & south
        self.frame_center.grid_rowconfigure(0, minsize=int(center_total_height * CENTER_TOP_RATIO))
        self.frame_center.grid_rowconfigure(1, minsize=int(center_total_height * CENTER_MIDDLE_RATIO))
        self.frame_center.grid_rowconfigure(2, minsize=int(center_total_height * CENTER_BOTTOM_RATIO))
        self.frame_center.grid_columnconfigure(0, weight=1)

        # =======================
        # Inner frames in center
        # =======================
        self.frame_center_top = tk.Frame(self.frame_center)
        self.debug_frame(self.frame_center_top, "orange")
        self.frame_center_top.grid(row=0, column=0, sticky="nsew")

        ######################################################
        ##____________CENTER PANEL: BORDER LAYOUT____________###
        ######################################################
        # frame_center_middle es el panel de módulos
        #
        self.frame_center_middle = tk.Frame(self.frame_center)
        self.debug_frame(self.frame_center_middle, "violet")
        self.frame_center_middle.grid(row=1, column=0, sticky="nsew")

        self.frame_center_bottom = tk.Frame(self.frame_center)
        self.debug_frame(self.frame_center_bottom, "cyan")
        self.frame_center_bottom.grid(row=2, column=0, sticky="nsew")

        # =======================
        # Divide middle frame into three columns (modules)
        # =======================
        self.frame_center_middle.grid_columnconfigure(0, weight=1, uniform="module")
        self.frame_center_middle.grid_columnconfigure(1, weight=1, uniform="module")
        self.frame_center_middle.grid_columnconfigure(2, weight=1, uniform="module")
        self.frame_center_middle.grid_rowconfigure(0, weight=1)

        # Module frames
        module1_frame = tk.Frame(
            self.frame_center_middle,
            #relief="groove",  # borde
            #bd=2,              # grosor del borde
            highlightbackground=BASE_COLOR,
            highlightthickness=1
        )
        self.debug_frame(module1_frame, "salmon")  # solo colorea si DEBUG_LAYOUT = True
        module1_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        module2_frame = tk.Frame(
            self.frame_center_middle,
            # relief="groove",
            # bd=2
            highlightbackground=BASE_COLOR,
            highlightthickness=1
        )
        self.debug_frame(module2_frame, "khaki")
        module2_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        module3_frame = tk.Frame(
            self.frame_center_middle,
            # relief="groove",
            # bd=2
            highlightbackground=BASE_COLOR,
            highlightthickness=1
        )
        self.debug_frame(module3_frame, "lightseagreen")
        module3_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)


        self.banner = TopBanner(
            parent=self.frame_north,
            logo_path=r"C:\Users\akoun\Desktop\Biocruces\begibraintool\src\images\logo_BBT_no_bg.png",
            title_text="BEGIBRAINTOOL",
            bg=BANNER_BG,
            fg=TITLE_FG,
            logo_size=LOGO_SIZE,
            on_run=lambda: self._on_run_clicked(self._snapshot_general_config()),
            get_time_estimate=lambda: self.compute_estimated_time(self.modules)
        )

        self.general_panel = GeneralConfigPanel(
            parent=self.frame_center_top,
            general_config_dict=self.general_config,
            tooltip_factory=self.create_tooltip,
            on_run=self._on_run_clicked,
            on_load=self.load_configuration_from_file,
            compute_time_fn=self.compute_estimated_time,
            on_language_change=self.refresh_all_language
        )

        # Advanced options panel (bottom center)
        self.advanced_panel = AdvancedOptionsPanel(
            parent=self.frame_center_bottom,
            config_dict=self.advanced_config,
            get_current_language=lambda: self.general_config["language"]["value"] or self.general_config["language"]["default"],
            tooltip_factory=self.create_tooltip,
            num_columns=3
        )

        # Create module panels dynamically
        self.module_panels = []
        lang_fn = lambda: (self.general_config["language"]["value"] or self.general_config["language"]["default"])

        module_frames = [module1_frame, module2_frame, module3_frame]

        for idx, (module_key, module_data) in enumerate(self.modules.items()):
            if idx >= len(module_frames):
                break
            panel = ModuleSelectionPanel(
                parent=module_frames[idx],
                module_key=module_key,
                module_data=module_data,
                get_current_language=lang_fn,
                tooltip_factory=self.create_tooltip,
                on_test_toggle=self.general_panel.update_time
            )

            self.module_panels.append(panel)

    def debug_frame(self, frame, color="red"):
        """If DEBUG_LAYOUT is active, add border and background color to the frame."""
        if DEBUG_LAYOUT:
            frame.config(borderwidth=3, relief="solid")
            try:
                frame.config(background=color)
            except tk.TclError:
                print("ttk.Frame does not support background directly, switch to tk.Frame if needed")
                pass

    def create_tooltip(self, widget, text, gif_path=None):
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
            tooltip.config(bg="#ffffe0")

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

    def update_config_values(self, target: dict, source):
        """Merge seguro: respeta la estructura destino.
        - dict+dict -> merge recursivo
        - dict+escalar -> si 'value' en destino, asigna ahí
        - escalar -> ignora (no machacamos estructuras)
        """
        if not isinstance(source, dict):
            return

        def _merge(dst, src):
            for k, sv in src.items():
                if k not in dst:
                    # si quieres, puedes permitir claves nuevas:
                    # dst[k] = copy.deepcopy(sv)
                    continue

                tv = dst[k]

                if isinstance(tv, dict) and isinstance(sv, dict):
                    _merge(tv, sv)

                elif isinstance(tv, dict) and not isinstance(sv, dict):
                    # típico caso: en JSON guardaste sólo el valor
                    if "value" in tv:
                        tv["value"] = sv
                    else:
                        # no hay campo 'value': mejor no romper estructura
                        # dst[k] = tv  # no hacemos nada
                        pass

                else:
                    # ambos escalares, o dst escalar: puedes permitir overwrite
                    dst[k] = sv

        _merge(target, source)

    def load_configuration_from_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Cargar configuración"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 1) merge seguro SOBRE self.*, no sobre gui_config_manager
            self.update_config_values(self.general_config,  data.get("general_config", {}))
            self.update_config_values(self.advanced_config, data.get("advanced_config", {}))
            self.update_config_values(self.modules,         data.get("modules", {}))

            # 2) refrescar UI
            self.general_panel._build()
            self.refresh_all_language()
            self.advanced_panel._build()
            for p in self.module_panels:
                p._build()

            messagebox.showinfo("Éxito", "Configuración cargada correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

    def compute_estimated_time(self,modules_dict):
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

    def refresh_all_language(self):
        for panel in self.module_panels:
            panel.refresh_language()
        self.advanced_panel.refresh_language()

    # def update_config_values(self, target_dict, source_dict):
    #     for key, value in source_dict.items():
    #         if key in target_dict:
    #             if isinstance(target_dict[key], dict) and isinstance(value, dict):
    #                 target_dict[key].update(value)
    #             else:
    #                 target_dict[key] = value
    
    def _snapshot_general_config(self):
        snap = {}
        for k, v in self.general_config.items():
            if isinstance(v, dict):
                snap[k] = v.get("value", v.get("default"))
            else:
                snap[k] = v
        return snap

    def run(self):
        """Lanza el mainloop y devuelve los diccionarios de configuracion."""
        self.root.mainloop()
        return self.general_config, self.advanced_config, self.modules

############################################################################################################################################################
##____________MAIN WINDOW____________####____________MAIN WINDOW____________####____________MAIN WINDOW____________####____________MAIN WINDOW____________##
############################################################################################################################################################
# gui = BegibraintoolGUI()
# general_config, advanced_config, modules = gui.run()
# print("General config:", general_config)
# print("Advanced config:", advanced_config)
# print("Modules:", modules)