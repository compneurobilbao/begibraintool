import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from python_scripts.gui_config_manager_old import general_config, modules, load_saved_configuration, save_configuration, reset_configuration, save_config_to_file

# === DEBUG: Visualizar contenedores ===
DEBUG_LAYOUT = False  # <--- activa o desactiva el modo depuración

def debug_frame(frame, color="red"):
    """Si DEBUG_LAYOUT está activo, añade borde y color al frame."""
    if DEBUG_LAYOUT:
        frame.config(borderwidth=3, relief="solid")
        try:
            frame.config(background=color)
        except tk.TclError:
            print("ttk.Frame no soporta background directamente, cambiar a tk.Frame si hace falta")
            pass

# === Función auxiliar para activar/desactivar widgets ===
def toggle_advanced_config(state_var, widgets):
    """Activa/desactiva widgets del panel avanzado."""
    enabled = state_var.get()
    state = "normal" if enabled else "disabled"
    for w in widgets:
        # Para los widgets con .config(state=...)
        if isinstance(w, (ttk.Entry, ttk.Checkbutton, ttk.Radiobutton, ttk.Button)):
            w.config(state=state)
        elif isinstance(w, ttk.Label):
            # Los labels no tienen 'state', cambiamos foreground
            w.config(foreground="black" if enabled else "gray")

def update_module_from_tests(module_id):
    """
    Marca automáticamente el módulo como seleccionado si al menos un test está seleccionado.
    """
    any_test_selected = any(test_var.get() for test_var in test_vars[module_id].values())
    module_vars[module_id].set(any_test_selected)

def update_tests(module_id, var):
    """
    Actualiza los estados de los tests al seleccionar/deseleccionar un módulo.
    """
    is_selected = var.get()
    for test_id, test in modules[module_id]["tests"].items():
        if test["enabled"]:
            test_vars[module_id][test_id].set(is_selected)

def create_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.wm_overrideredirect(True)
    tooltip.withdraw()
    label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, font=("tahoma", 8))
    label.pack()

    def enter(event):
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + 20
        tooltip.wm_geometry(f"+{x}+{y}")
        tooltip.deiconify()

    def leave(event):
        tooltip.withdraw()

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

def create_option_with_tooltip(parent, text, variable=None, values=None, tooltip_text="", width=12):
    """
    Crea un frame horizontal con:
    - Checkbutton (o Combobox si values != None)
    - Label 'ⓘ' con tooltip
    - Lo empaqueta automáticamente dentro del parent

    Args:
        parent: frame padre donde se añadirá
        text: texto del Checkbutton o Combobox
        variable: tk.Variable asociada
        values: lista de valores si quieres un Combobox en lugar de Checkbutton
        tooltip_text: texto para el tooltip del 'i'
        width: ancho del Combobox (si se usa)
    Returns:
        widget principal creado (Checkbutton o Combobox)
    """
    frame = ttk.Frame(parent)
    frame.pack(anchor="w", padx=10, pady=2)

    if values is None:
        # Crear Checkbutton
        widget = ttk.Checkbutton(frame, text=text, variable=variable)
    else:
        # Crear Combobox
        widget = ttk.Combobox(frame, textvariable=variable, values=values, state="readonly", width=width)
    widget.pack(side="left")

    # Crear icono informativo con tooltip
    info_label = ttk.Label(frame, text="ⓘ", foreground="blue")
    info_label.pack(side="left", padx=5)
    create_tooltip(info_label, tooltip_text)

    return widget


def save_selection():
    """
    Guarda los valores seleccionados en el diccionario original y cierra la ventana.
    """
    for module_id, module in modules.items():
        module["selected"] = module_vars[module_id].get()
        for test_id, test in module["tests"].items():
            test["selected"] = test_vars[module_id][test_id].get()

            # Guardar los campos especiales del test_4 del módulo 1
            if module_id == "module_1" and test_id == "test_4":
                test.setdefault("config", {})
                test["config"]["screen_width_cm"] = width_var.get()
                test["config"]["distance_to_screen_cm"] = distance_var.get()
                test["config"]["screen_resolution_dpi"] = dpi_var.get()
                
                # Guardar las frecuencias espaciales (Magno, Parvo, Neutro)
                test["config"]["magno_low_sf"] = magno_low_var.get()
                test["config"]["magno_high_sf"] = magno_high_var.get()
                test["config"]["parvo_low_sf"] = parvo_low_var.get()
                test["config"]["parvo_high_sf"] = parvo_high_var.get()
                test["config"]["neutro_low_sf"] = neutro_low_var.get()
                test["config"]["neutro_high_sf"] = neutro_high_var.get()
                test["config"]["difficulty_mode"] = difficulty_var.get()

    # Guardar valores de configuración general
    general_config["feedback"] = feedback_var.get()
    general_config["logs"] = logs_var.get()
    general_config["full_screen_noise"] = noise_var.get()
    general_config["gabor_texture"] = mask_var.get()
    general_config["pretest_standard_values"] = pretest_values_var.get()
    general_config["remember_protocol"] = remember_var.get()
    general_config["tutorial"] = remember_var.get()
    general_config["generate_report"] = generate_report_var.get()
    general_config["screen_width"] = width_var.get()
    general_config["screen_distance"] = distance_var.get()
    general_config["screen_dpi"] = dpi_var.get()
    
    
    # GUARDAR EN JSON SI SE HA SELECCIONADO LA OPCION
    if general_config["remember_protocol"]:
        save_configuration(general_config, modules)
    else:
        reset_configuration()

    root.destroy()

    
def update_difficulty(*args):
    mode = difficulty_var.get()

    # Lista de entradas personalizadas
    entries = [
        magno_low_entry, magno_high_entry,
        parvo_low_entry, parvo_high_entry,
        neutro_low_entry, neutro_high_entry
    ]

    if mode == "custom":
        # Habilitar entradas
        for e in entries:
            e.config(state="normal")
    else:
        # Deshabilitar entradas
        for e in entries:
            e.config(state="disabled")

        # Poner valores predefinidos
        if mode == "easy":
            magno_low_var.set("0.5"); magno_high_var.set("2.0")
            parvo_low_var.set("2.0"); parvo_high_var.set("4.0")
            neutro_low_var.set("1.0"); neutro_high_var.set("3.0")
        elif mode == "medium":
            magno_low_var.set("0.5"); magno_high_var.set("3.0")
            parvo_low_var.set("3.0"); parvo_high_var.set("6.0")
            neutro_low_var.set("2.0"); neutro_high_var.set("5.0")
        elif mode == "hard":
            magno_low_var.set("1.0"); magno_high_var.set("4.0")
            parvo_low_var.set("4.0"); parvo_high_var.set("8.0")
            neutro_low_var.set("3.0"); neutro_high_var.set("6.0")
    
# Update module selection from file
# Marcar automaticamente si se ha seleccionado la opcion
# Intentar cargar configuración previa si remember_protocol esta activo
saved_general, saved_modules = load_saved_configuration()
print(saved_general)
print(saved_modules)
if saved_general and saved_modules:
    general_config.update(saved_general)
    for module_id in modules:
        if module_id in saved_modules:
            modules[module_id]["selected"] = saved_modules[module_id].get("selected", False)
            for test_id in modules[module_id]["tests"]:
                modules[module_id]["tests"][test_id]["selected"] = saved_modules[module_id]["tests"].get(test_id, {}).get("selected", False)
                # Si tiene config especial, como test_4
                if "config" in modules[module_id]["tests"][test_id]:
                    modules[module_id]["tests"][test_id]["config"].update(
                        saved_modules[module_id]["tests"].get(test_id, {}).get("config", {})
                    )

############################################################################################################################################################
##____________MAIN WINDOW____________####____________MAIN WINDOW____________####____________MAIN WINDOW____________####____________MAIN WINDOW____________##
############################################################################################################################################################

# Crear la ventana principal
root = tk.Tk()
root.title("Select Modules and Tests")

# === MODULOS ===
module_vars = {}
test_vars = {}

# === FUENTES EN NEGRITA ===
style = ttk.Style()
bold_small_font = tkfont.Font(family="TkDefaultFont", size=14, weight="bold")
style.configure("Bold.TCheckbutton", font=bold_small_font)

# Frame superior para los módulos (contenedor horizontal)
modules_frame = tk.Frame(root)
modules_frame.pack(fill="x", padx=10, pady=20)
debug_frame(modules_frame, "lightblue") # Debug

for idx, (module_id, module) in enumerate(modules.items()):
    # Frame individual para cada módulo (columna)
    module_frame = tk.LabelFrame(modules_frame)#, text=module["name"]
    # module_frame.grid(row=0, column=idx, padx=10, sticky="n")
    module_frame.grid(row=0, column=idx, padx=10, sticky="nsew")  # importante nsew
    debug_frame(module_frame, "red")

    modules_frame.grid_columnconfigure(idx, weight=1)

    module_vars[module_id] = tk.BooleanVar(value=module["selected"])
    module_checkbox = ttk.Checkbutton(
        module_frame,
        text=module["name"],
        variable=module_vars[module_id],
        command=lambda mid=module_id, var=module_vars[module_id]: update_tests(mid, var),
        style="Bold.TCheckbutton"
    )

    module_checkbox.pack(anchor="w", fill="x")  # fill x para que se estire
    
    test_vars[module_id] = {}
    for test_id, test in module["tests"].items():
        test_vars[module_id][test_id] = tk.BooleanVar(value=test["selected"])
        test_checkbox = ttk.Checkbutton(
            module_frame,
            text=test["name"],
            variable=test_vars[module_id][test_id],
            command=lambda mid=module_id: update_module_from_tests(mid),
            state=tk.NORMAL if test["enabled"] else tk.DISABLED
        )
        test_checkbox.pack(anchor="w", padx=15)

    ##########################################################################################################
    # === CONFIGURACIÓN AVANZADA PARA MÓDULO 1 ===
    ##########################################################################################################
    if module_id == "module_1":
        
        advanced_config_frame = ttk.LabelFrame(module_frame, text="Configuración avanzada")
        advanced_config_frame.pack(fill="x", padx=5, pady=20)

        adv_enabled_var = tk.BooleanVar(value=False)
        adv_toggle = ttk.Checkbutton(
            advanced_config_frame,
            text="Habilitar configuración avanzada",
            variable=adv_enabled_var
        )
        adv_toggle.pack(anchor="w", padx=5, pady=3)

        # === variables comunes ===
        width_var = tk.StringVar(value="40")
        distance_var = tk.StringVar(value="57")
        dpi_var = tk.StringVar(value="244")

        # Frame para pantalla
        screen_frame = ttk.Frame(advanced_config_frame)
        screen_frame.pack(anchor="w", padx=20, pady=2)

        # Ancho
        width_label = ttk.Label(screen_frame, text="Ancho pantalla (cm)")
        width_label.grid(row=0, column=0, sticky="w")
        width_entry = ttk.Entry(screen_frame, textvariable=width_var, width=10)
        width_entry.grid(row=0, column=1, padx=5)
        info1 = ttk.Label(screen_frame, text="ⓘ", foreground="blue")
        info1.grid(row=0, column=2)
        create_tooltip(info1, "Ancho físico de la pantalla en centímetros.")

        # Distancia
        distance_label = ttk.Label(screen_frame, text="Distancia a pantalla (cm)")
        distance_label.grid(row=1, column=0, sticky="w")
        distance_entry = ttk.Entry(screen_frame, textvariable=distance_var, width=10)
        distance_entry.grid(row=1, column=1, padx=5)
        info2 = ttk.Label(screen_frame, text="ⓘ", foreground="blue")
        info2.grid(row=1, column=2)
        create_tooltip(info2, "Distancia desde el observador a la pantalla en centímetros.")

        # DPI
        dpi_label = ttk.Label(screen_frame, text="Resolución (DPI)")
        dpi_label.grid(row=2, column=0, sticky="w")
        dpi_entry = ttk.Entry(screen_frame, textvariable=dpi_var, width=10)
        dpi_entry.grid(row=2, column=1, padx=5)
        info3 = ttk.Label(screen_frame, text="ⓘ", foreground="blue")
        info3.grid(row=2, column=2)
        create_tooltip(info3, "Resolución de la pantalla en puntos por pulgada (DPI).\nCalcula el valor en https://pixelcalculator.com/es")

        # === variables para SF y dificultad (test_5) ===
        difficulty_var = tk.StringVar(value="custom")
        magno_low_var = tk.StringVar(value="0.1")
        magno_high_var = tk.StringVar(value="2.0")
        parvo_low_var = tk.StringVar(value="1.0")
        parvo_high_var = tk.StringVar(value="8.0")
        neutro_low_var = tk.StringVar(value="1.0")
        neutro_high_var = tk.StringVar(value="4.0")

        def update_difficulty(*args):
            entries = [magno_low_entry, magno_high_entry,
                    parvo_low_entry, parvo_high_entry,
                    neutro_low_entry, neutro_high_entry]
            if difficulty_var.get() == "custom":
                for e in entries: e.config(state="normal")
            else:
                for e in entries: e.config(state="disabled")
                if difficulty_var.get() == "easy":
                    magno_low_var.set("0.5"); magno_high_var.set("2.0")
                    parvo_low_var.set("2.0"); parvo_high_var.set("4.0")
                    neutro_low_var.set("1.0"); neutro_high_var.set("3.0")
                elif difficulty_var.get() == "medium":
                    magno_low_var.set("0.5"); magno_high_var.set("3.0")
                    parvo_low_var.set("3.0"); parvo_high_var.set("6.0")
                    neutro_low_var.set("2.0"); neutro_high_var.set("5.0")
                elif difficulty_var.get() == "hard":
                    magno_low_var.set("1.0"); magno_high_var.set("4.0")
                    parvo_low_var.set("4.0"); parvo_high_var.set("8.0")
                    neutro_low_var.set("3.0"); neutro_high_var.set("6.0")

        difficulty_var.trace_add("write", update_difficulty)

        difficulty_frame = ttk.LabelFrame(advanced_config_frame, text="Modo de dificultad")
        difficulty_frame.pack(anchor="w", padx=20, pady=5)
        rb_easy = ttk.Radiobutton(difficulty_frame, text="Fácil", variable=difficulty_var, value="easy").pack(side="left", padx=5)
        rb_medium = ttk.Radiobutton(difficulty_frame, text="Medio", variable=difficulty_var, value="medium").pack(side="left", padx=5)
        rb_hard = ttk.Radiobutton(difficulty_frame, text="Difícil", variable=difficulty_var, value="hard").pack(side="left", padx=5)
        rb_custom = ttk.Radiobutton(difficulty_frame, text="Custom", variable=difficulty_var, value="custom").pack(side="left", padx=5)


        sf_frame = ttk.LabelFrame(difficulty_frame, text="Frecuencias espaciales (ciclos/°)")
        sf_frame.pack(anchor="w", padx=20, pady=5)

        magno_low_entry = ttk.Entry(sf_frame, textvariable=magno_low_var, width=8)
        magno_low_entry.grid(row=0, column=1, padx=5)
        magno_high_entry = ttk.Entry(sf_frame, textvariable=magno_high_var, width=8)
        magno_high_entry.grid(row=0, column=2, padx=5)

        parvo_low_entry = ttk.Entry(sf_frame, textvariable=parvo_low_var, width=8)
        parvo_low_entry.grid(row=1, column=1, padx=5)
        parvo_high_entry = ttk.Entry(sf_frame, textvariable=parvo_high_var, width=8)
        parvo_high_entry.grid(row=1, column=2, padx=5)

        neutro_low_entry = ttk.Entry(sf_frame, textvariable=neutro_low_var, width=8)
        neutro_low_entry.grid(row=2, column=1, padx=5)
        neutro_high_entry = ttk.Entry(sf_frame, textvariable=neutro_high_var, width=8)
        neutro_high_entry.grid(row=2, column=2, padx=5)

        

        # === widgets a desactivar/activar cuando se cambia adv_toggle ===
        adv_entries = [width_entry, distance_entry, dpi_entry,
               magno_low_entry, magno_high_entry,
               parvo_low_entry, parvo_high_entry,
               neutro_low_entry, neutro_high_entry]
        
        adv_radiobuttons = [rb_easy, rb_medium, rb_hard, rb_custom]

        adv_labels = [width_label, distance_label, dpi_label]

        adv_widgets = adv_entries + adv_radiobuttons + adv_labels

        adv_enabled_var.trace_add("write",
        lambda *args, var=adv_enabled_var, widgets=adv_widgets: toggle_advanced_config(var, widgets))

        toggle_advanced_config(adv_enabled_var, adv_widgets)
    
    ##########################################################################################################
    # === CONFIGURACIÓN AVANZADA PARA MÓDULO 2 ===
    ##########################################################################################################
    if module_id == "module_2":
        advanced_config_frame = ttk.LabelFrame(module_frame, text="Configuración avanzada")
        advanced_config_frame.pack(fill="x", padx=5, pady=20)

        adv_enabled_var = tk.BooleanVar(value=False)
        adv_toggle = ttk.Checkbutton(
            advanced_config_frame,
            text="Habilitar configuración avanzada",
            variable=adv_enabled_var
        )
        adv_toggle.pack(anchor="w", padx=5, pady=3)

        # === variables específicas del módulo 2 ===
        # (Ninguna por ahora, pero se pueden añadir aquí)

        adv_widgets = []  # Lista de widgets a desactivar/activar

        adv_enabled_var.trace_add("write",
            lambda *args, var=adv_enabled_var, widgets=adv_widgets: toggle_advanced_config(var, widgets))

        toggle_advanced_config(adv_enabled_var, adv_widgets)

    ##########################################################################################################
    # === CONFIGURACIÓN AVANZADA PARA MÓDULO 3 ===
    ##########################################################################################################
    if module_id == "module_3":
        advanced_config_frame = ttk.LabelFrame(module_frame, text="Configuración avanzada")
        advanced_config_frame.pack(fill="x", padx=5, pady=20)

        adv_enabled_var = tk.BooleanVar(value=False)
        adv_toggle = ttk.Checkbutton(
            advanced_config_frame,
            text="Habilitar configuración avanzada",
            variable=adv_enabled_var
        )
        adv_toggle.pack(anchor="w", padx=5, pady=3)

        # === variables específicas del módulo 3 ===
        # (Ninguna por ahora, pero se pueden añadir aquí)

        adv_widgets = []  # Lista de widgets a desactivar/activar

        adv_enabled_var.trace_add("write",
            lambda *args, var=adv_enabled_var, widgets=adv_widgets: toggle_advanced_config(var, widgets))

        toggle_advanced_config(adv_enabled_var, adv_widgets)

#############################################################################
## PANEL DE CONFIGURACIÓN GENERAL + PANEL DE INFORME ##
#############################################################################

# Frame contenedor horizontal
config_container_frame = tk.Frame(root)
config_container_frame.pack(fill="x", padx=10, pady=20)
debug_frame(config_container_frame, "green")  # Debug opcional

# Panel izquierdo: opciones generales
config_frame = tk.LabelFrame(config_container_frame, text="Opciones de configuración generales")
config_frame.pack(side="left", fill="both", expand=True, padx=5)
debug_frame(config_frame, "pink")

# Panel derecho: informe al final del experimento
report_frame = tk.LabelFrame(config_container_frame, text="Opciones de informe final")
report_frame.pack(side="left", fill="both", expand=True, padx=5)
debug_frame(report_frame, "yellow")

# === Variables ===
feedback_var = tk.BooleanVar(value=general_config["feedback"])
logs_var = tk.BooleanVar(value=general_config["logs"])
noise_var = tk.BooleanVar(value=general_config["full_screen_noise"])
mask_var = tk.StringVar(value="gauss")  # Valor por defecto
pretest_values_var = tk.BooleanVar(value=general_config["pretest_standard_values"])
remember_var = tk.BooleanVar(value=general_config["remember_protocol"])
tutorial_var = tk.BooleanVar(value=general_config["tutorial"])
generate_report_var = tk.BooleanVar(value=general_config.get("generate_report", False))
# NO FUNCIONA - REFVISAR
# distance_var = tk.StringVar(value=general_config.get("screen_distance", "0"))
# width_var = tk.StringVar(value=general_config.get("screen_width", "0"))
# dpi_var = tk.StringVar(value=general_config.get("screen_dpi", 0))

# === Checkboxes en panel izquierdo ===
feedback_checkbox = create_option_with_tooltip(
    config_frame,
    text="Enable Feedback",
    variable=feedback_var,
    tooltip_text="Muestra retroalimentación visual/sonora al usuario."
)

logs_checkbox = create_option_with_tooltip(
    config_frame,
    text="Enable Logs",
    variable=logs_var,
    tooltip_text="Guarda un registro de las acciones realizadas durante el test."
)

noise_checkbox = create_option_with_tooltip(
    config_frame,
    text="Full Screen Noise",
    variable=noise_var,
    tooltip_text="Activa ruido en toda la pantalla durante el test."
)

mask_combobox = create_option_with_tooltip(
    config_frame,
    text="Mask type",
    variable=mask_var,
    values=["gauss", "circle"],
    tooltip_text="Selecciona el tipo de textura de Gabor a usar."
)

pretest_checkbox = create_option_with_tooltip(
    config_frame,
    text="Use standard values for pretest",
    variable=pretest_values_var,
    tooltip_text="Usa valores estándar predefinidos en lugar de personalizados para el pretest."
)

remember_checkbox = create_option_with_tooltip(
    config_frame,
    text="Remember last protocol configuration",
    variable=remember_var,
    tooltip_text="Guarda y recupera automáticamente la configuración del último protocolo."
)

tutorial_checkbox = create_option_with_tooltip(
    config_frame,
    text="Tutorial before test",
    variable=tutorial_var,
    tooltip_text="Muestra un tutorial previo al test para guiar al usuario."
)

# === Panel derecho ===
generate_report_checkbox = create_option_with_tooltip(
    report_frame,
    text="Generate report at the end",
    variable=generate_report_var,
    tooltip_text="Si está activado, se generará un informe al final del experimento."
)
config_buttons_frame = ttk.LabelFrame(config_frame, text="Guardar / Cargar protocolo")
config_buttons_frame.pack(fill="x", padx=10, pady=10)

# Entry para mostrar ruta del archivo
file_entry = ttk.Entry(config_buttons_frame, width=50)
file_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)

# Botón Guardar
save_button = ttk.Button(config_buttons_frame, text="Guardar", command=save_config_to_file)
save_button.pack(side="left", padx=5, pady=5)

# Botón Cargar
load_button = ttk.Button(config_buttons_frame, text="Cargar")#, command=load_config_from_file)
load_button.pack(side="left", padx=5, pady=5)

#############################################################################



# Botón para guardar y cerrar
save_button = ttk.Button(root, text="Continue", command=save_selection)
save_button.pack(pady=20)

# Ejecutar la ventana
root.mainloop()

# Mostrar toda la configuración por consola
print("\n--- Configuración general ---")
print(general_config)

print("\n--- Configuración de módulos y tests ---")
for module_id, module in modules.items():
    print(f"\n{module['name']} (selected: {module['selected']})")
    for test_id, test in module["tests"].items():
        print(f"  - {test['name']} (selected: {test['selected']})")
        if "config" in test:
            for key, val in test["config"].items():
                print(f"      {key}: {val}")