#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2024.2.4),
    on mayo 12, 2025, at 16:15
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

# --- Import packages ---
from psychopy import locale_setup
from psychopy import prefs
from psychopy import plugins
plugins.activatePlugins()
prefs.hardware['audioLib'] = 'ptb'
prefs.hardware['audioLatencyMode'] = '3'
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, hardware
from psychopy.tools import environmenttools
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER, priority)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

import psychopy.iohub as io
from psychopy.hardware import keyboard

# Run 'Before Experiment' code from GLOBAL_VARIABLES_AND_FUNCTIONS
# IMPORTS
from psychopy import core
import random
import threading
import time
import pandas as pd
import os

# DIRECTORIES
pretest_standard_thresholds_path = "./config_data/standard_thresholds.json"

#GLOBAL VARIABLES

# Grating config
global grating_mask
grating_mask = 'gauss'

# MODULE 1: pretest - staircase test params
n_reversals_to_average = 5
stop_reversals = 6
staircase_noise_duration = 0.5

# MODULE 1: Experiment params
stim_time = 2
response_time = 0.5 # time to answer after stimuli disapears 
global FEEDBACK
FEEDBACK = True # value changed in Begin Experiment
global noise_type
noise_type= 2 # 1: FULL WINDOW // 2: ONLY STIM. Value changed in Begin Experiment (GUI)
noise_field_size = [1.75,1]
noise_dots = 25000
grating_size = (0.5,0.5)

continueRoutine_ref = [True]

# MODULE 2:
# Eye Tracking Resting State
eye_tracking_resting_state_time = 60
eye_tracking_resting_state_background_color = 'black'

# Visual Search params
visual_search_image_time = 5
visual_search_wait_time = 1.5

# Eye Tracking DVS task params
dot_size            = 10/1000 # change this value to make it similar to the other dots
noise_dots_size     = 15 #dot_size

noise_dots_no       = 700
dot_coherence       = 0.0 # do not touch this 
#noise_dots_direction= 45.0
#noise_coherent_motion = 0.0 # bool

dot_speed           = 0.001
noise_dots_speed    = dot_speed

dot_border_color    = 'black'#border color of the main dot
dot_color           = 'white' 
noise_dots_color    = 'white'

noise_dots_lifetime = 200
field_size          = [1.5,1]

# MODULE 3:
# Pupilometry params: --> FROM CSV!!
#adaptation_time = 10#10*60 # 10 MINUTES
#flash_time = 1 # 1 s
#rest_time = 10 # 30 s

# Fearful & affective images params
autonomic_response_basal_time = 5
autonomic_response_image_time = 5
autonomic_response_recovery_time = 5

# FUNCTIONS
def comprobar_respuesta(orientacion):
    keys = event.getKeys()
    if ('right' in keys and orientacion == 45) or ('left' in keys and orientacion == 135): # Acierto:
        success                 = True
    elif 'right' in keys or 'left' in keys: # Respuesta incorrecta
        success                 = False
    else:
        success = None
    return success

def show_noise(dots_white, dots_black, duration, orientacion = None, feedback_txt = None):
    
    if noise_type == 1:
        dots_white.fieldShape = 'square'
        dots_black.fieldShape = 'square'
        dots_white.setSize(noise_field_size)
        dots_black.setSize(noise_field_size)
        
    elif noise_type == 2:
        dots_white.fieldShape = 'circle'
        dots_black.fieldShape = 'circle'
        dots_white.setSize(grating_size)
        dots_black.setSize(grating_size)
        
    # Habilitar los puntos de ruido
    dots_white.setAutoDraw(True)
    dots_black.setAutoDraw(True)

    noise_timer = core.Clock()
    noise_timer.reset()
    
    # Mostrar el ruido durante el tiempo de duración especificado
    while noise_timer.getTime() < duration:
        win.flip()  # Actualiza la ventana en cada frame para mantener la animación
        #igual se puede asignar una duración x al ruido y no tener que hacer esta guarrada
        # show feedback during noise
        if FEEDBACK and orientacion is not None and feedback_txt is not None:
            success = comprobar_respuesta(orientacion)
            if success is not None:
                show_feedback(feedback_txt, success)
    
    # Desactivar los puntos de ruido
    dots_white.setAutoDraw(False)
    dots_black.setAutoDraw(False)

def get_random_orientation():
    return random.choice([45, 135])

def get_threshold(test_var_name : str, results_csv_path):
    data = pd.read_csv(results_csv_path)

    # Filtrar filas con reversals
    reversal_data = data[data['reversals'] > 0]

    threshold = reversal_data[test_var_name].tail(n_reversals_to_average).mean()

    return threshold

def show_feedback(feedback_txt, success):
    if success != -1 and success:
        feedback_txt.setText("✓")
    elif success != -1 and not success:
        feedback_txt.setText("x")
    else:
        feedback_txt.setText("")
    
    # Función interna para borrar el texto después del ruido
    def clear_text():
        time.sleep(staircase_noise_duration)
        feedback_txt.setText("")  # Limpia el texto

    # Crear y lanzar el hilo para que borre el texto
    t = threading.Thread(target=clear_text)
    t.start()  # Inicia el hilo para que la ejecución principal continúe
    
    return


def load_sf():
    archivo_sf = f"./data/{expInfo['participant']}/sf_staircase_data_{expInfo['participant']}.csv"
    try:
        test_sf = get_threshold('spatial_frequency', archivo_sf)
        print(f'Se ha cargado la frecuencia espacial testada con un valor de {test_sf}')
        return test_sf

    except FileNotFoundError:
        print(f'Error: El archivo {archivo_sf} no fue encontrado.')
        return -1
        
    except Exception as e:
        print(f'Error al cargar la frecuencia espacial del archivo {archivo_sf}: {str(e)}')
        return -1
        
import matplotlib.pyplot as plt

def generate_staircase_test_graph(test_var_name: str, results_csv_path: str):
    # Comprobar si el archivo existe
    if not os.path.exists(results_csv_path):
        print(f"[AVISO] No se encontró el archivo: {results_csv_path}")
        return -1

    data = pd.read_csv(results_csv_path)

    # Filtrar filas con reversals
    reversal_data = data[data['reversals'] > 0]

    # Calcular el umbral como la media de las últimas n inversiones
    n_reversals_to_average = 9
    threshold = reversal_data[test_var_name].tail(n_reversals_to_average).mean()

    # Preparar carpeta de salida
    input_dir = os.path.dirname(results_csv_path)
    output_dir = os.path.join(input_dir, 'processed_data')
    os.makedirs(output_dir, exist_ok=True)

    # Crear nombre de archivo de salida
    filename = f'staircase_{test_var_name}.png'
    output_path = os.path.join(output_dir, filename)

    # Graficar
    plt.figure(figsize=(10, 6))
    plt.plot(data['trial'], data[test_var_name], marker='o', linestyle='-', label=f'Stimulus {test_var_name}')
    plt.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold = {threshold:.3f}')
    
    plt.xlabel('Number of Trials')
    plt.ylabel(f'Stimulus {test_var_name}')
    plt.title(f'Stimulus {test_var_name} Across Trials')
    plt.legend()
    plt.grid(True)

    # Guardar gráfico
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

    print(f"Umbral estimado: {threshold:.3f}")
    print(f"Gráfico guardado en: {output_path}")

    return threshold

# Run 'Before Experiment' code from DATA_MANAGEMENT
import json

# TEMPORAL --> Se debe cargar de memoria o inicializar con valores nulos
'''
threshold_values = {
    'spatial_frequency_threshold': 53.98,   # Flotante
    'flicker_threshold': 40.0,              # Flotante
    'contrast_threshold': 0.002,            # Flotante
    'color_threshold': {                    # Diccionario para colores con valores flotantes
        'red': 0.93,
        'green': 3.44
    }                 
}

threshold_values = {
    'spatial_frequency_threshold': None,  # Flotante
    'flicker_threshold': None,            # Flotante
    'contrast_threshold': None,           # Flotante
    'color_threshold': {}                 # Diccionario para colores con valores flotantes
}
'''
''' MODIFICAR EL DICCIONARIO
threshold_dict['spatial_frequency_threshold'] = spatial_frequency
threshold_dict['flicker_threshold'] = flicker
threshold_dict['contrast_threshold'] = contrast
threshold_dict['color_threshold'][color_name] = color_value
'''

# Run 'Before Experiment' code from MODULE_SELECTION_GUI
import tkinter as tk
from tkinter import ttk

#participant_id = f"{randint(0, 999999):06.0f}"

# Diccionario de configuración general
global general_config
general_config = {
    "feedback": False,
    "logs": False,
    "full_screen_noise": False,
    "gabor_texture": None,
    "pretest_standard_values": False
}

# Diccionario de módulos y tests con el nuevo parámetro "enabled"
modules = {
    "module_1": {
        "name": "MODULE 1: Spatial Vision (low level-stimuli and semantic stimuli)",
        "selected": False,
        "tests": {
            "pretest": {"name": "Threshold estimation test", "selected": False, "enabled": True},
            "test_1": {"name": "1.Spatial Frequency test", "selected": False, "enabled": True},
            "test_2": {"name": "2.Color Vision test", "selected": False, "enabled": True},
            "test_3": {"name": "3.Contrast Sensitivity test", "selected": False, "enabled": True},
            "test_4": {"name": "4.Semantic Stim Spatial Frequency test", "selected": False, "enabled": False},
            "test_5": {"name": "5.Semantic Stim Contrast Sensitivity test", "selected": False, "enabled": False},
            "test_6": {"name": "6.Semantic Stim Color Vision test", "selected": False, "enabled": False}
        }
    },
    "module_2": {
        "name": "MODULE 2: Dynamic Vision and Eye Tracking",
        "selected": False,
        "tests": {
            "test_1": {"name": "1.Fixation stability test (resting state eye-tracking test)", "selected": False, "enabled": True},
            "test_2": {"name": "2.Flicker fusion threshold test", "selected": False, "enabled": True},
            "test_3": {"name": "3.Saccadic and antisaccadic movement eye-tracking test", "selected": False, "enabled": True},
            "test_4": {"name": "4.Smooth pursuit eye-tracking test", "selected": False, "enabled": True},
            "test_5": {"name": "5.Visual search eye-tracking test", "selected": False, "enabled": True}
        }
    },
    "module_3": {
        "name": "MODULE 3: Dynamic Pupilometry and Autonomic Response (sweating and Heart Rate Variability) to Visual Stimuli",
        "selected": False,
        "tests": {
            "test_1": {"name": "1.Elementary full-field achromatic and chromatic light stimulus", "selected": False, "enabled": True},
            "test_2": {"name": "2.Fearful and affective semantic stimuli (images)", "selected": False, "enabled": True}
        }
    }
}

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

def save_selection():
    """
    Guarda los valores seleccionados en el diccionario original y cierra la ventana.
    """
    for module_id, module in modules.items():
        module["selected"] = module_vars[module_id].get()
        for test_id, test in module["tests"].items():
            test["selected"] = test_vars[module_id][test_id].get()
    
    # Guardar valores de configuración general
    general_config["feedback"] = feedback_var.get()
    general_config["logs"] = logs_var.get()
    general_config["full_screen_noise"] = noise_var.get()
    general_config["gabor_texture"] = mask_var.get()
    general_config["pretest_standard_values"] = pretest_values_var.get()
    
    global participant_id
    participant_id = participant_id_var.get()
    #expInfo['participant'] = participant_id

    root.destroy()

# Crear la ventana principal
root = tk.Tk()
root.title("Select Modules and Tests")

# Variables de control
module_vars = {}
test_vars = {}

# Frame superior para entrada de DNI, botón y mensaje de estado
top_frame = ttk.Frame(root)
top_frame.pack(side="top", fill="x", padx=10, pady=10)

dni_label = ttk.Label(top_frame, text="DNI:")
dni_label.pack(side="left")

dni_var = tk.StringVar()
dni_entry = ttk.Entry(top_frame, textvariable=dni_var)
dni_entry.pack(side="left", padx=5)

def comprobar_dni():
    # Aquí podrías poner tu lógica real de comprobación con una BBDD o archivo
    # Por ahora mostramos el texto "Datos encontrados"
    status_label.config(text="Datos encontrados", foreground="green")

comprobar_btn = ttk.Button(top_frame, text="Comprobar", command=comprobar_dni)
comprobar_btn.pack(side="left", padx=5)

# Etiqueta que se actualizará cuando se pulse el botón "Comprobar"
status_label = ttk.Label(top_frame, text="", foreground="green")
status_label.pack(side="left", padx=10)

# Campo de entrada para DNI del paciente y botón
participant_id_var = tk.StringVar()
participant_id_label = ttk.Label(top_frame, text="DNI del paciente:")
participant_id_label.pack(side="left", padx=(10, 5))

participant_id_entry = ttk.Entry(top_frame, textvariable=participant_id_var, width=20)
participant_id_entry.pack(side="left", padx=5)

comprobar_button = ttk.Button(top_frame, text="Comprobar")
comprobar_button.pack(side="left", padx=5)


# Crear widgets dinámicos
for module_id, module in modules.items():
    module_vars[module_id] = tk.BooleanVar(value=module["selected"])
    module_checkbox = ttk.Checkbutton(
        root, text=module["name"], variable=module_vars[module_id],
        command=lambda mid=module_id, var=module_vars[module_id]: update_tests(mid, var)
    )
    module_checkbox.pack(anchor="w", padx=10, pady=5)
    
    test_vars[module_id] = {}
    for test_id, test in module["tests"].items():
        test_vars[module_id][test_id] = tk.BooleanVar(value=test["selected"])
        test_checkbox = ttk.Checkbutton(
            root, text=test["name"], variable=test_vars[module_id][test_id],
            command=lambda mid=module_id: update_module_from_tests(mid),
            state=tk.NORMAL if test["enabled"] else tk.DISABLED
        )
        test_checkbox.pack(anchor="w", padx=30)

# Checkboxes para configuración general
feedback_var = tk.BooleanVar(value=general_config["feedback"])
logs_var = tk.BooleanVar(value=general_config["logs"])
noise_var = tk.BooleanVar(value=general_config["full_screen_noise"])
mask_var = tk.StringVar(value="gauss")  # Valor por defecto
pretest_values_var = tk.BooleanVar(value=general_config["pretest_standard_values"])

feedback_checkbox = ttk.Checkbutton(root, text="Enable Feedback", variable=feedback_var)
feedback_checkbox.pack(anchor="w", padx=10, pady=5)

logs_checkbox = ttk.Checkbutton(root, text="Enable Logs", variable=logs_var)
logs_checkbox.pack(anchor="w", padx=10, pady=5)

noise_checkbox = ttk.Checkbutton(root, text="Full Screen Noise", variable=noise_var)
noise_checkbox.pack(anchor="w", padx=10, pady=5)

mask_combobox = ttk.Combobox(root, textvariable=mask_var, values=["gauss", "circle"], state="readonly")
mask_combobox.pack(anchor="w", padx=10, pady=5)

noise_checkbox = ttk.Checkbutton(root, text="Use standard values for pretest", variable=pretest_values_var)
noise_checkbox.pack(anchor="w", padx=10, pady=5)

# Botón para guardar y cerrar
save_button = ttk.Button(root, text="Continue", command=save_selection)
save_button.pack(pady=20)

# Ejecutar la ventana
root.mainloop()

# Mostrar la selección final
print("Selección final:")
for module_id, module in modules.items():
    print(f"{module['name']}: {module['selected']}")
    for test_id, test in module["tests"].items():
        print(f"  - {test['name']}: {test['selected']} (Enabled: {test['enabled']})")
print(f"Feedback: {general_config['feedback']}")
print(f"Logs: {general_config['logs']}")
# Run 'Before Experiment' code from gabor_generator
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


def save_gabor_patch_image(frequency, size, c1, c2):
    amp, f = generate_gabor_patch(frequency, size)
    
    # Convertir colores a numpy arrays y expandir dimensiones para el canal de transparencia
    c1 = np.array(c1)
    c2 = np.array(c2)
    
    # Calcular los valores de color para el parche
    im_rgb_vals = (c1 * amp[:, :, None]) + (c2 * (1 - amp[:, :, None]))
    
    # Crear el canal de alfa (transparencia): 1 donde hay el parche, 0 en el fondo
    alpha_channel = f
    
    # Combinar los valores RGB con el canal alfa para crear una imagen RGBA
    im_rgba_vals = np.dstack((im_rgb_vals, alpha_channel))
    
    # Convertir a imagen
    im = Image.fromarray((im_rgba_vals * 255).astype('uint8'), 'RGBA')
    im.save(f"./images/custom_stim.png")

def generate_gabor_patch(frequency, size):
    im_range = np.arange(size)
    x, y = np.meshgrid(im_range, im_range)
    dx = x - size // 2
    dy = y - size // 2
    t = np.arctan2(dy, dx)
    r = np.sqrt(dx ** 2 + dy ** 2)
    x = r * np.cos(t)
    y = r * np.sin(t)
    
    amp = np.where(np.cos(2 * np.pi * (x * frequency)) >= 0, 1, 0)
    
    if grating_mask == 'circle':
        f = np.where(r <= size // 2, 1, 0)
    elif grating_mask == 'gauss':
        f = np.cos((np.pi * (r + size // 2)) / (size - 1) - np.pi / 2)
        f[r > size // 2] = 0
    else:
        f = 0
    
    return amp, f
    
def hsv_a_rgb(h, s, v):
    """
    Convierte un color desde HSV a RGB.

    Parámetros:
    h (float): Matiz (Hue) en grados (0-360).
    s (float): Saturación (Saturation) como porcentaje (0-100).
    v (float): Valor (Value) como porcentaje (0-100).

    Retorna:
    tuple: Una tupla con valores (R, G, B), cada uno en el rango de 0 a 255.
    """
    h = h % 360
    s /= 100
    v /= 100

    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    r = (r + m) * 255
    g = (g + m) * 255
    b = (b + m) * 255

    return int(round(r)), int(round(g)), int(round(b))


def normalizar_rgb(rgb):
    """
    Normaliza una tupla de valores RGB dividiendo cada componente por 255.

    Parámetros:
    rgb (tuple): Una tupla con valores (R, G, B), cada uno en el rango de 0 a 255.

    Retorna:
    tuple: Una tupla con valores normalizados (R, G, B), cada uno en el rango de 0 a 1.
    """
    return tuple(component / 255 for component in rgb)
# Run 'Before Experiment' code from code_14
import pandas as pd

opacidad = 1

# Run 'Before Experiment' code from gabor_generator_2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


def save_gabor_patch_image(frequency, size, c1, c2):
    amp, f = generate_gabor_patch(frequency, size)
    
    # Convertir colores a numpy arrays y expandir dimensiones para el canal de transparencia
    c1 = np.array(c1)
    c2 = np.array(c2)
    
    # Calcular los valores de color para el parche
    im_rgb_vals = (c1 * amp[:, :, None]) + (c2 * (1 - amp[:, :, None]))
    
    # Crear el canal de alfa (transparencia): 1 donde hay el parche, 0 en el fondo
    alpha_channel = f
    
    # Combinar los valores RGB con el canal alfa para crear una imagen RGBA
    im_rgba_vals = np.dstack((im_rgb_vals, alpha_channel))
    
    # Convertir a imagen
    im = Image.fromarray((im_rgba_vals * 255).astype('uint8'), 'RGBA')
    im.save(f"./images/custom_stim.png")

def generate_gabor_patch(frequency, size):
    im_range = np.arange(size)
    x, y = np.meshgrid(im_range, im_range)
    dx = x - size // 2
    dy = y - size // 2
    t = np.arctan2(dy, dx)
    r = np.sqrt(dx ** 2 + dy ** 2)
    x = r * np.cos(t)
    y = r * np.sin(t)
    
    amp = np.where(np.cos(2 * np.pi * (x * frequency)) >= 0, 1, 0)
    
    if grating_mask == 'circle':
        f = np.where(r <= size // 2, 1, 0)
    elif grating_mask == 'gauss':
        f = np.cos((np.pi * (r + size // 2)) / (size - 1) - np.pi / 2)
        f[r > size // 2] = 0
    else:
        f = 0
    
    return amp, f
    
def hsv_a_rgb(h, s, v):
    """
    Convierte un color desde HSV a RGB.

    Parámetros:
    h (float): Matiz (Hue) en grados (0-360).
    s (float): Saturación (Saturation) como porcentaje (0-100).
    v (float): Valor (Value) como porcentaje (0-100).

    Retorna:
    tuple: Una tupla con valores (R, G, B), cada uno en el rango de 0 a 255.
    """
    h = h % 360
    s /= 100
    v /= 100

    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    r = (r + m) * 255
    g = (g + m) * 255
    b = (b + m) * 255

    return int(round(r)), int(round(g)), int(round(b))


def normalizar_rgb(rgb):
    """
    Normaliza una tupla de valores RGB dividiendo cada componente por 255.

    Parámetros:
    rgb (tuple): Una tupla con valores (R, G, B), cada uno en el rango de 0 a 255.

    Retorna:
    tuple: Una tupla con valores normalizados (R, G, B), cada uno en el rango de 0 a 1.
    """
    return tuple(component / 255 for component in rgb)
# --- Setup global variables (available in all functions) ---
# create a device manager to handle hardware (keyboards, mice, mirophones, speakers, etc.)
deviceManager = hardware.DeviceManager()
# ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
# store info about the experiment session
psychopyVersion = '2024.2.4'
expName = 'begibraintool'  # from the Builder filename that created this script
# information about this experiment
expInfo = {
    'participant': f"{randint(0, 999999)}",
    'participant_2': 'f"{5-3}"',
    'test': 'f"El doble de {x := 5} es {x * 2}"',
    'software_version': '1',
    'date|hid': data.getDateStr(),
    'expName|hid': expName,
    'psychopyVersion|hid': psychopyVersion,
}

# --- Define some variables which will change depending on pilot mode ---
'''
To run in pilot mode, either use the run/pilot toggle in Builder, Coder and Runner, 
or run the experiment with `--pilot` as an argument. To change what pilot 
#mode does, check out the 'Pilot mode' tab in preferences.
'''
# work out from system args whether we are running in pilot mode
PILOTING = core.setPilotModeFromArgs()
# start off with values from experiment settings
_fullScr = True
_winSize = [1920, 1080]
# if in pilot mode, apply overrides according to preferences
if PILOTING:
    # force windowed mode
    if prefs.piloting['forceWindowed']:
        _fullScr = False
        # set window size
        _winSize = prefs.piloting['forcedWindowSize']

def showExpInfoDlg(expInfo):
    """
    Show participant info dialog.
    Parameters
    ==========
    expInfo : dict
        Information about this experiment.
    
    Returns
    ==========
    dict
        Information about this experiment.
    """
    # show participant info dialog
    dlg = gui.DlgFromDict(
        dictionary=expInfo, sortKeys=False, title=expName, alwaysOnTop=True
    )
    if dlg.OK == False:
        core.quit()  # user pressed cancel
    # return expInfo
    return expInfo


def setupData(expInfo, dataDir=None):
    """
    Make an ExperimentHandler to handle trials and saving.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    dataDir : Path, str or None
        Folder to save the data to, leave as None to create a folder in the current directory.    
    Returns
    ==========
    psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    # remove dialog-specific syntax from expInfo
    for key, val in expInfo.copy().items():
        newKey, _ = data.utils.parsePipeSyntax(key)
        expInfo[newKey] = expInfo.pop(key)
    
    # data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    if dataDir is None:
        dataDir = _thisDir
    filename = f'data/{expInfo["participant"]}/{expName}_{expInfo["date"]}'
    
    # make sure filename is relative to dataDir
    if os.path.isabs(filename):
        dataDir = os.path.commonprefix([dataDir, filename])
        filename = os.path.relpath(filename, dataDir)
    
    # an ExperimentHandler isn't essential but helps with data saving
    thisExp = data.ExperimentHandler(
        name=expName, version='',
        extraInfo=expInfo, runtimeInfo=None,
        originPath='C:\\Users\\akoun\\Desktop\\Biocruces\\begibraintool\\src\\begiBrainDemo_lastrun.py',
        savePickle=True, saveWideText=True,
        dataFileName=dataDir + os.sep + filename, sortColumns='time'
    )
    thisExp.setPriority('thisRow.t', priority.CRITICAL)
    thisExp.setPriority('expName', priority.LOW)
    # return experiment handler
    return thisExp


def setupLogging(filename):
    """
    Setup a log file and tell it what level to log at.
    
    Parameters
    ==========
    filename : str or pathlib.Path
        Filename to save log file and data files as, doesn't need an extension.
    
    Returns
    ==========
    psychopy.logging.LogFile
        Text stream to receive inputs from the logging system.
    """
    # set how much information should be printed to the console / app
    if PILOTING:
        logging.console.setLevel(
            prefs.piloting['pilotConsoleLoggingLevel']
        )
    else:
        logging.console.setLevel('warning')
    # save a log file for detail verbose info
    logFile = logging.LogFile(filename+'.log')
    if PILOTING:
        logFile.setLevel(
            prefs.piloting['pilotLoggingLevel']
        )
    else:
        logFile.setLevel(
            logging.getLevel('exp')
        )
    
    return logFile


def setupWindow(expInfo=None, win=None):
    """
    Setup the Window
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    win : psychopy.visual.Window
        Window to setup - leave as None to create a new window.
    
    Returns
    ==========
    psychopy.visual.Window
        Window in which to run this experiment.
    """
    if PILOTING:
        logging.debug('Fullscreen settings ignored as running in pilot mode.')
    
    if win is None:
        # if not given a window to setup, make one
        win = visual.Window(
            size=_winSize, fullscr=_fullScr, screen=1,
            winType='pyglet', allowGUI=True, allowStencil=False,
            monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
            backgroundImage='', backgroundFit='none',
            blendMode='avg', useFBO=True,
            units='height',
            checkTiming=False  # we're going to do this ourselves in a moment
        )
    else:
        # if we have a window, just set the attributes which are safe to set
        win.color = [0,0,0]
        win.colorSpace = 'rgb'
        win.backgroundImage = ''
        win.backgroundFit = 'none'
        win.units = 'height'
    if expInfo is not None:
        # get/measure frame rate if not already in expInfo
        if win._monitorFrameRate is None:
            win._monitorFrameRate = win.getActualFrameRate(infoMsg='Attempting to measure frame rate of screen, please wait...')
        expInfo['frameRate'] = win._monitorFrameRate
    win.hideMessage()
    # show a visual indicator if we're in piloting mode
    if PILOTING and prefs.piloting['showPilotingIndicator']:
        win.showPilotingIndicator()
    
    return win


def setupDevices(expInfo, thisExp, win):
    """
    Setup whatever devices are available (mouse, keyboard, speaker, eyetracker, etc.) and add them to 
    the device manager (deviceManager)
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window in which to run this experiment.
    Returns
    ==========
    bool
        True if completed successfully.
    """
    # --- Setup input devices ---
    ioConfig = {}
    
    # Setup iohub keyboard
    ioConfig['Keyboard'] = dict(use_keymap='psychopy')
    
    # Setup iohub experiment
    ioConfig['Experiment'] = dict(filename=thisExp.dataFileName)
    
    # Start ioHub server
    ioServer = io.launchHubServer(window=win, **ioConfig)
    
    # store ioServer object in the device manager
    deviceManager.ioServer = ioServer
    
    # create a default keyboard (e.g. to check for escape)
    if deviceManager.getDevice('defaultKeyboard') is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='iohub'
        )
    if deviceManager.getDevice('key_resp_4') is None:
        # initialise key_resp_4
        key_resp_4 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_4',
        )
    if deviceManager.getDevice('key_resp_skip_instructions_2') is None:
        # initialise key_resp_skip_instructions_2
        key_resp_skip_instructions_2 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_skip_instructions_2',
        )
    if deviceManager.getDevice('key_resp_16') is None:
        # initialise key_resp_16
        key_resp_16 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_16',
        )
    if deviceManager.getDevice('key_resp_19') is None:
        # initialise key_resp_19
        key_resp_19 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_19',
        )
    if deviceManager.getDevice('key_resp_14') is None:
        # initialise key_resp_14
        key_resp_14 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_14',
        )
    if deviceManager.getDevice('key_resp_20') is None:
        # initialise key_resp_20
        key_resp_20 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_20',
        )
    if deviceManager.getDevice('key_resp_15') is None:
        # initialise key_resp_15
        key_resp_15 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_15',
        )
    if deviceManager.getDevice('key_resp_21') is None:
        # initialise key_resp_21
        key_resp_21 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_21',
        )
    if deviceManager.getDevice('key_resp') is None:
        # initialise key_resp
        key_resp = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp',
        )
    if deviceManager.getDevice('key_resp_10') is None:
        # initialise key_resp_10
        key_resp_10 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_10',
        )
    if deviceManager.getDevice('key_resp_9') is None:
        # initialise key_resp_9
        key_resp_9 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_9',
        )
    if deviceManager.getDevice('key_resp_8') is None:
        # initialise key_resp_8
        key_resp_8 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_8',
        )
    if deviceManager.getDevice('key_resp_26') is None:
        # initialise key_resp_26
        key_resp_26 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_26',
        )
    if deviceManager.getDevice('key_resp_17') is None:
        # initialise key_resp_17
        key_resp_17 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_17',
        )
    if deviceManager.getDevice('key_resp_18') is None:
        # initialise key_resp_18
        key_resp_18 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_18',
        )
    if deviceManager.getDevice('key_resp_27') is None:
        # initialise key_resp_27
        key_resp_27 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_27',
        )
    if deviceManager.getDevice('key_resp_25') is None:
        # initialise key_resp_25
        key_resp_25 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_25',
        )
    if deviceManager.getDevice('key_resp_28') is None:
        # initialise key_resp_28
        key_resp_28 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_28',
        )
    if deviceManager.getDevice('key_resp_23') is None:
        # initialise key_resp_23
        key_resp_23 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_23',
        )
    if deviceManager.getDevice('key_resp_24') is None:
        # initialise key_resp_24
        key_resp_24 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_24',
        )
    if deviceManager.getDevice('key_resp_29') is None:
        # initialise key_resp_29
        key_resp_29 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_29',
        )
    # return True if completed successfully
    return True

def pauseExperiment(thisExp, win=None, timers=[], playbackComponents=[]):
    """
    Pause this experiment, preventing the flow from advancing to the next routine until resumed.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    timers : list, tuple
        List of timers to reset once pausing is finished.
    playbackComponents : list, tuple
        List of any components with a `pause` method which need to be paused.
    """
    # if we are not paused, do nothing
    if thisExp.status != PAUSED:
        return
    
    # start a timer to figure out how long we're paused for
    pauseTimer = core.Clock()
    # pause any playback components
    for comp in playbackComponents:
        comp.pause()
    # make sure we have a keyboard
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        defaultKeyboard = deviceManager.addKeyboard(
            deviceClass='keyboard',
            deviceName='defaultKeyboard',
            backend='ioHub',
        )
    # run a while loop while we wait to unpause
    while thisExp.status == PAUSED:
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=['escape']):
            endExperiment(thisExp, win=win)
        # sleep 1ms so other threads can execute
        clock.time.sleep(0.001)
    # if stop was requested while paused, quit
    if thisExp.status == FINISHED:
        endExperiment(thisExp, win=win)
    # resume any playback components
    for comp in playbackComponents:
        comp.play()
    # reset any timers
    for timer in timers:
        timer.addTime(-pauseTimer.getTime())


def run(expInfo, thisExp, win, globalClock=None, thisSession=None):
    """
    Run the experiment flow.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    psychopy.visual.Window
        Window in which to run this experiment.
    globalClock : psychopy.core.clock.Clock or None
        Clock to get global time from - supply None to make a new one.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    # mark experiment as started
    thisExp.status = STARTED
    # make sure window is set to foreground to prevent losing focus
    win.winHandle.activate()
    # make sure variables created by exec are available globally
    exec = environmenttools.setExecEnvironment(globals())
    # get device handles from dict of input devices
    ioServer = deviceManager.ioServer
    # get/create a default keyboard (e.g. to check for escape)
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='ioHub'
        )
    eyetracker = deviceManager.getDevice('eyetracker')
    # make sure we're running in the directory for this experiment
    os.chdir(_thisDir)
    # get filename from ExperimentHandler for convenience
    filename = thisExp.dataFileName
    frameTolerance = 0.001  # how close to onset before 'same' frame
    endExpNow = False  # flag for 'escape' or other condition => quit the exp
    # get frame duration from frame rate in expInfo
    if 'frameRate' in expInfo and expInfo['frameRate'] is not None:
        frameDur = 1.0 / round(expInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0  # could not measure, so guess
    
    # Start Code - component code to be run after the window creation
    
    # --- Initialize components for Routine "CONFIGURATION_ROUTINE" ---
    # Run 'Begin Experiment' code from code_4
    periphereal_region_diameter = 0
    
    ################################
    ## CONFIGURACION MODIFICABLE: ##
    ################################
    nombre_pantalla = 'pantalla4'
    distancia_eyetracker = 0.65 # m
    alpha = angulo_region_central = 9 # º DEG
    periphereal_region_result = visual.ShapeStim(
        win=win, name='periphereal_region_result',
        size=[1.0, 1.0], vertices='circle',
        ori=0.0, pos=(0, 0), draggable=False, anchor='center',
        lineWidth=2.0,
        colorSpace='rgb', lineColor=[-1.0000, -1.0000, -1.0000], fillColor=[0.0000, 0.0000, 0.0000],
        opacity=None, depth=-1.0, interpolate=True)
    key_resp_4 = keyboard.Keyboard(deviceName='key_resp_4')
    logs2 = visual.TextStim(win=win, name='logs2',
        text=None,
        font='Open Sans',
        pos=(0, 0), draggable=False, height=0.03, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    # Run 'Begin Experiment' code from GLOBAL_VARIABLES_AND_FUNCTIONS
    stop_reversals = 5
    continueRoutine_ref = [True]
    
    global general_config, noise_type, grating_mask
    
    FEEDBACK = general_config["feedback"]
    if general_config["full_screen_noise"]: # 1: FULL WINDOW // 2: ONLY STIM.
        noise_type = 1
        print("Stablished noise type 1")
    else:
        noise_type = 2
        print("Stablished noise type 2")
    
    grating_mask = general_config["gabor_texture"]
    
    
    # DVS
    noise_dots_coherence = 0.0
    noise_coherent_motion = 0.0 # bool
    noise_dots_direction= 45.0
    desvio = 0
    # Run 'Begin Experiment' code from DATA_MANAGEMENT
    
    # Función para mostrar el diccionario completo al final del test
    def display_thresholds(threshold_dict):
        print("Valores de Umbrales del Paciente:")
        print(f"Frecuencia Espacial: {threshold_dict['spatial_frequency_threshold']}")
        print(f"Flicker: {threshold_dict['flicker_threshold']}")
        print(f"Contraste: {threshold_dict['contrast_threshold']}")
        print("Umbrales de Color:")
        for color, value in threshold_dict['color_threshold'].items():
            print(f"{color}: {value}")
    
    # Función para guardar el diccionario en un archivo JSON
    def save_thresholds_to_json(threshold_dict, filename=f"./data/{expInfo['participant']}/thresholds_{expInfo['participant']}.json"):
        with open(filename, 'w') as f:
            json.dump(threshold_dict, f, indent=4)  # indent para que el JSON sea legible
        print(f"Diccionario guardado en {filename}")
    
    # Función para cargar el diccionario desde un archivo JSON
    def load_thresholds_from_json(filename=f"./data/{expInfo['participant']}/thresholds_{expInfo['participant']}.json"):
        if not os.path.exists(filename):
            # Archivo no encontrado
            return -1
        else:
            # Archivo encontrado y valores cargados
            with open(filename, 'r') as f:
                threshold_dict = json.load(f)
            print(f"Diccionario cargado desde {filename}")
            return threshold_dict
    FPS_logs = visual.TextStim(win=win, name='FPS_logs',
        text=None,
        font='Open Sans',
        pos=(0.35, 0.35), draggable=False, height=0.025, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-8.0);
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "SPATIAL_FREQ_STAIRCASE_TEST" ---
    grating_7 = visual.GratingStim(
        win=win, name='grating_7',
        tex='sin', mask=grating_mask, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=grating_size, sf=None, phase=0.0,
        color=[1,1,1], colorSpace='rgb',
        opacity=None, contrast=1.0, blendmode='avg',
        texRes=512.0, interpolate=True, depth=0.0)
    dots_black_3 = visual.DotStim(
        win=win, name='dots_black_3',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None,
        depth=-1.0)
    dots_white_3 = visual.DotStim(
        win=win, name='dots_white_3',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[1.0,1.0,1.0], colorSpace='rgb', opacity=None,
        depth=-2.0)
    # Run 'Begin Experiment' code from code_20
    import random
    
    def get_random_orientation():
        return random.choice([45, 135])
    key_resp_16 = keyboard.Keyboard(deviceName='key_resp_16')
    logs_12 = visual.TextStim(win=win, name='logs_12',
        text='Any text\n\nincluding line breaks',
        font='Open Sans',
        pos=(0, -0.45), draggable=False, height=0.025, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-5.0);
    key_resp_19 = keyboard.Keyboard(deviceName='key_resp_19')
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "CONTRAST_STAIRCASE_TEST" ---
    key_resp_14 = keyboard.Keyboard(deviceName='key_resp_14')
    logs_10 = visual.TextStim(win=win, name='logs_10',
        text='Any text\n\nincluding line breaks',
        font='Open Sans',
        pos=(0, -0.45), draggable=False, height=0.025, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    grating = visual.GratingStim(
        win=win, name='grating',
        tex='sin', mask=grating_mask, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=grating_size, sf=None, phase=0.0,
        color=[1,1,1], colorSpace='rgb',
        opacity=None, contrast=1.0, blendmode='avg',
        texRes=512.0, interpolate=True, depth=-3.0)
    dots_white = visual.DotStim(
        win=win, name='dots_white',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[1.0,1.0,1.0], colorSpace='rgb', opacity=None,
        depth=-4.0)
    dots_black = visual.DotStim(
        win=win, name='dots_black',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None,
        depth=-5.0)
    key_resp_20 = keyboard.Keyboard(deviceName='key_resp_20')
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "COLOR_STAIRCASE_TEST" ---
    key_resp_15 = keyboard.Keyboard(deviceName='key_resp_15')
    logs_11 = visual.TextStim(win=win, name='logs_11',
        text='Any text\n\nincluding line breaks',
        font='Open Sans',
        pos=(0, -0.45), draggable=False, height=0.025, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    image_2 = visual.ImageStim(
        win=win,
        name='image_2', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=grating_size,
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=512.0, interpolate=True, depth=-4.0)
    dots_white_2 = visual.DotStim(
        win=win, name='dots_white_2',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[1.0000, 1.0000, 1.0000], colorSpace='rgb', opacity=None,
        depth=-5.0)
    dots_black_2 = visual.DotStim(
        win=win, name='dots_black_2',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None,
        depth=-6.0)
    key_resp_21 = keyboard.Keyboard(deviceName='key_resp_21')
    
    # --- Initialize components for Routine "LOAD_THRESHOLDS" ---
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "BL_1_SPATIAL_FREQ" ---
    dots_black_5 = visual.DotStim(
        win=win, name='dots_black_5',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None,
        depth=0.0)
    dots_white_5 = visual.DotStim(
        win=win, name='dots_white_5',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[1.0000, 1.0000, 1.0000], colorSpace='rgb', opacity=None,
        depth=-1.0)
    stim = visual.GratingStim(
        win=win, name='stim',
        tex='sqr', mask=grating_mask, anchor='center',
        ori=0.0, pos=[0,0], draggable=False, size=1.0, sf=1.0, phase=0.5,
        color='white', colorSpace='rgb',
        opacity=1.0, contrast=1.0, blendmode='avg',
        texRes=512.0, interpolate=True, depth=-2.0)
    key_resp = keyboard.Keyboard(deviceName='key_resp')
    logs_background_2 = visual.Rect(
        win=win, name='logs_background_2',
        width=(0.5, 1)[0], height=(0.5, 1)[1],
        ori=0.0, pos=(0.75, 0), draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor='white', fillColor='white',
        opacity=None, depth=-4.0, interpolate=True)
    logs = visual.TextStim(win=win, name='logs',
        text=None,
        font='Open Sans',
        pos=(-0.45, 0.45), draggable=False, height=0.035, wrapWidth=None, ori=0.0, 
        color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-5.0);
    logs_parametros_trial = visual.TextStim(win=win, name='logs_parametros_trial',
        text=None,
        font='Open Sans',
        pos=(0.5, 0), draggable=False, height=0.025, wrapWidth=None, ori=0.0, 
        color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-6.0);
    feedback_txt = visual.TextStim(win=win, name='feedback_txt',
        text=None,
        font='Open Sans',
        pos=(0, 0), draggable=False, height=0.085, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-7.0);
    # Run 'Begin Experiment' code from code
    from psychopy.iohub import launchHubServer
    
    io = launchHubServer()
    mouse = io.devices.mouse
    
    posicion_estimulo = (0,0)
    stim_x = 0
    stim_y = 0
    
    foveal_region_pos = [0,0]
    
    #other
    gaze_position = mouse.getPosition()
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "BL_2_COLOR" ---
    dots_black_6 = visual.DotStim(
        win=win, name='dots_black_6',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None,
        depth=0.0)
    dots_white_6 = visual.DotStim(
        win=win, name='dots_white_6',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[1.0000, 1.0000, 1.0000], colorSpace='rgb', opacity=None,
        depth=-1.0)
    key_resp_10 = keyboard.Keyboard(deviceName='key_resp_10')
    logs_background_10 = visual.Rect(
        win=win, name='logs_background_10',
        width=(0.5, 1)[0], height=(0.5, 1)[1],
        ori=0.0, pos=(0.75, 0), draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor='white', fillColor='white',
        opacity=None, depth=-3.0, interpolate=True)
    logs_parametros_trial_6 = visual.TextStim(win=win, name='logs_parametros_trial_6',
        text=None,
        font='Open Sans',
        pos=(0.5, 0), draggable=False, height=0.025, wrapWidth=None, ori=0.0, 
        color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-4.0);
    stim_img = visual.ImageStim(
        win=win,
        name='stim_img', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=grating_size,
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=512.0, interpolate=True, depth=-5.0)
    feedback_txt_2 = visual.TextStim(win=win, name='feedback_txt_2',
        text=None,
        font='Open Sans',
        pos=(0, 0), draggable=False, height=0.085, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-6.0);
    # Run 'Begin Experiment' code from code_14
    from psychopy.iohub import launchHubServer
    
    io = launchHubServer()
    mouse = io.devices.mouse
    
    posicion_estimulo = (0,0)
    stim_x = 0
    stim_y = 0
    
    foveal_region_pos = [0,0]
    
    #other
    gaze_position = mouse.getPosition()
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "BL_3_CONTRAST" ---
    dots_black_7 = visual.DotStim(
        win=win, name='dots_black_7',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None,
        depth=0.0)
    dots_white_7 = visual.DotStim(
        win=win, name='dots_white_7',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[1.0000, 1.0000, 1.0000], colorSpace='rgb', opacity=None,
        depth=-1.0)
    stim_5 = visual.GratingStim(
        win=win, name='stim_5',
        tex='sqr', mask=grating_mask, anchor='center',
        ori=0.0, pos=[0,0], draggable=False, size=1.0, sf=1.0, phase=0.5,
        color='white', colorSpace='rgb',
        opacity=1.0, contrast=1.0, blendmode='avg',
        texRes=512.0, interpolate=True, depth=-2.0)
    key_resp_9 = keyboard.Keyboard(deviceName='key_resp_9')
    logs_background_8 = visual.Rect(
        win=win, name='logs_background_8',
        width=(0.5, 1)[0], height=(0.5, 1)[1],
        ori=0.0, pos=(0.75, 0), draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor='white', fillColor='white',
        opacity=None, depth=-4.0, interpolate=True)
    logs_parametros_trial_5 = visual.TextStim(win=win, name='logs_parametros_trial_5',
        text=None,
        font='Open Sans',
        pos=(0.5, 0), draggable=False, height=0.025, wrapWidth=None, ori=0.0, 
        color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-5.0);
    feedback_txt_3 = visual.TextStim(win=win, name='feedback_txt_3',
        text=None,
        font='Open Sans',
        pos=(0, 0), draggable=False, height=0.085, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-6.0);
    # Run 'Begin Experiment' code from code_8
    from psychopy.iohub import launchHubServer
    
    io = launchHubServer()
    mouse = io.devices.mouse
    
    posicion_estimulo = (0,0)
    stim_x = 0
    stim_y = 0
    
    foveal_region_pos = [0,0]
    
    #other
    gaze_position = mouse.getPosition()
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "ET_RESTING_STATE" ---
    text_3 = visual.TextStim(win=win, name='text_3',
        text=None,
        font='Open Sans',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    key_resp_8 = keyboard.Keyboard(deviceName='key_resp_8')
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "ET_SCREEN_POINT_TASK" ---
    text_5 = visual.TextStim(win=win, name='text_5',
        text=None,
        font='Open Sans',
        pos=(0.5, 0.5), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    polygon_9 = visual.ShapeStim(
        win=win, name='polygon_9', vertices='cross',
        size=(0.04, 0.04),
        ori=0.0, pos=(0, 0), draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor=[1.0000, -1.0000, -1.0000], fillColor=[1.0000, -1.0000, -1.0000],
        opacity=None, depth=-2.0, interpolate=True)
    key_resp_26 = keyboard.Keyboard(deviceName='key_resp_26')
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "FFT_STAIRCASE_TEST" ---
    key_resp_17 = keyboard.Keyboard(deviceName='key_resp_17')
    logs_13 = visual.TextStim(win=win, name='logs_13',
        text=None,
        font='Open Sans',
        pos=(0, -0.45), draggable=False, height=0.025, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    dots_white_4 = visual.DotStim(
        win=win, name='dots_white_4',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[1.0,1.0,1.0], colorSpace='rgb', opacity=None,
        depth=-4.0)
    dots_black_4 = visual.DotStim(
        win=win, name='dots_black_4',
        nDots=noise_dots, dotSize=2.0,
        speed=0.1, dir=0.0, coherence=1.0,
        fieldPos=(0.0, 0.0), fieldSize=[1.75,1], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=3.0,
        color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None,
        depth=-5.0)
    key_resp_18 = keyboard.Keyboard(deviceName='key_resp_18')
    FPS_logs_2 = visual.TextStim(win=win, name='FPS_logs_2',
        text=None,
        font='Open Sans',
        pos=(0.35, 0.35), draggable=False, height=0.025, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-8.0);
    dot = visual.ShapeStim(
        win=win, name='dot',
        size=(0.25, 0.25), vertices='circle',
        ori=0.0, pos=(0, 0), draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor='white', fillColor='white',
        opacity=None, depth=-9.0, interpolate=True)
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "SACCADE_TASK" ---
    # Run 'Begin Experiment' code from code_12
    # GLOBAL VARIABLES: POSITION OF FIXATION POINT AND PERIPHEREAL STIMULI POSITION
    
    #3 POSSIBLE POSITIONS:
    FIXATION_POS = (0,0)
    PERIPHEREAL_POS_L = (-0.75,0)
    PERIPHEREAL_POS_R = (0.75,0)
    
    IPAST_stim_position = (0,0) # ESTE VALOR ES VARIABLE (CAMBIA SEGUN LA SECUENCIA IPAST)
    
    # OTHER
    REST_TIME = 1
    IPAST_fixation_cross_size = (0.05, 0.05)
    cross_1 = visual.ShapeStim(
        win=win, name='cross_1', vertices='cross',
        size=IPAST_fixation_cross_size,
        ori=0.0, pos=IPAST_stim_position, draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor='white', fillColor='white',
        opacity=None, depth=-1.0, interpolate=True)
    cross_2 = visual.ShapeStim(
        win=win, name='cross_2', vertices='cross',
        size=IPAST_fixation_cross_size,
        ori=0.0, pos=PERIPHEREAL_POS_L, draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor='white', fillColor='white',
        opacity=None, depth=-2.0, interpolate=True)
    cross_3 = visual.ShapeStim(
        win=win, name='cross_3', vertices='cross',
        size=IPAST_fixation_cross_size,
        ori=0.0, pos=PERIPHEREAL_POS_R, draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor='white', fillColor='white',
        opacity=None, depth=-3.0, interpolate=True)
    polygon_5 = visual.ShapeStim(
        win=win, name='polygon_5',
        size=(0.15, 0.15), vertices='circle',
        ori=0.0, pos=[0,0], draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor='white', fillColor='white',
        opacity=None, depth=-4.0, interpolate=True)
    key_resp_27 = keyboard.Keyboard(deviceName='key_resp_27')
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "DVS_COHERENCE" ---
    dots_2 = visual.DotStim(
        win=win, name='dots_2',
        nDots=noise_dots_no, dotSize=noise_dots_size,
        speed=noise_dots_speed, dir=1.0, coherence=noise_dots_coherence,
        fieldPos=(0.0, 0.0), fieldSize=[field_size[0]+0.5,field_size[1]+0.5], fieldAnchor='center', fieldShape='square',
        signalDots='same', noiseDots='direction',dotLife=noise_dots_lifetime,
        color=noise_dots_color, colorSpace='rgb', opacity=None,
        depth=0.0)
    dot_2 = visual.ShapeStim(
        win=win, name='dot_2',
        size=dot_size, vertices='circle',
        ori=0.0, pos=(0, 0), draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor=dot_border_color, fillColor=dot_color,
        opacity=None, depth=-1.0, interpolate=True)
    # Run 'Begin Experiment' code from code_26
    import numpy as np
    
    def move_dot_smooth(dot, dot_speed, field_size, current_angle, frames_in_direction, frame_count):
        """
        Mueve el punto 'dot' de forma suave dentro de los límites de la pantalla.
    
        dot: objeto visual de PsychoPy que se va a mover.
        dot_speed: velocidad del punto.
        field_size: tamaño del campo [ancho, alto] en unidades de PsychoPy.
        current_angle: ángulo actual de la dirección del punto.
        frames_in_direction: número de frames en los que el punto mantiene la misma dirección.
        frame_count: contador de frames que indica cuántos frames han pasado en la dirección actual.
    
        Returns:
        - new_angle: El ángulo actualizado para la próxima llamada.
        - frame_count: El contador de frames actualizado.
        """
        # Si hemos alcanzado el límite de frames para la dirección actual, cambiamos el ángulo
        if frame_count >= frames_in_direction:
            # Elegir un nuevo ángulo aleatorio cercano al actual para mantener la suavidad
            current_angle += np.random.uniform(-np.pi/8, np.pi/8)
            frame_count = 0  # Reiniciar el contador de frames en la nueva dirección
        else:
            frame_count += 1
    
        # Calcular el desplazamiento basado en el ángulo
        dx = dot_speed * np.cos(current_angle)
        dy = dot_speed * np.sin(current_angle)
    
        # Calcular la nueva posición
        new_x = dot.pos[0] + dx
        new_y = dot.pos[1] + dy
    
        # Verificar los límites de la pantalla y ajustar si es necesario
        if new_x < -field_size[0]/2:
            new_x = -field_size[0]/2
            current_angle = np.pi - current_angle  # Invertir dirección horizontal
        elif new_x > field_size[0]/2:
            new_x = field_size[0]/2
            current_angle = np.pi - current_angle
    
        if new_y < -field_size[1]/2:
            new_y = -field_size[1]/2
            current_angle = -current_angle  # Invertir dirección vertical
        elif new_y > field_size[1]/2:
            new_y = field_size[1]/2
            current_angle = -current_angle
    
        # Actualizar la posición del punto
        dot.pos = (new_x, new_y)
    
        return current_angle, frame_count
    
    def move_dot_lateral(dot, dot_speed, field_size, direction, frame_count):
        """
        Mueve el punto 'dot' de forma lineal lateral (derecha a izquierda) dentro de los límites del campo definido.
    
        dot: objeto visual de PsychoPy que se va a mover.
        dot_speed: velocidad del punto.
        field_size: tamaño del campo [ancho, alto] en unidades de PsychoPy.
        direction: dirección actual del movimiento, 1 para derecha y -1 para izquierda.
        frame_count: contador de frames que indica cuántos frames han pasado.
    
        Returns:
        - direction: La dirección actualizada para la próxima llamada.
        - frame_count: El contador de frames actualizado.
        """
        # Calcular el desplazamiento basado en la dirección
        dx = dot_speed * direction
        new_x = dot.pos[0] + dx
        new_y = dot.pos[1]  # Mantener y constante
    
        # Verificar los límites de la pantalla en el eje x y ajustar si es necesario
        if new_x < -field_size[0] / 2:
            new_x = -field_size[0] / 2
            direction *= -1  # Cambiar de dirección
        elif new_x > field_size[0] / 2:
            new_x = field_size[0] / 2
            direction *= -1  # Cambiar de dirección
    
        # Actualizar la posición del punto
        dot.pos = (new_x, new_y)
    
        return direction, frame_count + 1
    
    key_resp_25 = keyboard.Keyboard(deviceName='key_resp_25')
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "VISUAL_SEARCH_RINGS" ---
    rings_img = visual.ImageStim(
        win=win,
        name='rings_img', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=1.0,
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=512.0, interpolate=False, depth=-1.0)
    key_resp_28 = keyboard.Keyboard(deviceName='key_resp_28')
    # Run 'Begin Experiment' code from GP_data_adq_backend_3
    def convert_to_psychopy_units(FPOGX, FPOGY, screen_bounds):
        """
        Convierte las coordenadas normalizadas de Gazepoint a coordenadas centradas 
        en el sistema de PsychoPy.
    
        Parámetros:
        - FPOGX: Coordenada X normalizada de Gazepoint (0 a 1)
        - FPOGY: Coordenada Y normalizada de Gazepoint (0 a 1)
        - screen_bounds: Límites de la pantalla en PsychoPy, donde los valores
          se definen como (x_min, y_max, x_max, y_min)
    
        Retorna:
        - Coordenadas X y Y centradas en el sistema de PsychoPy
        """
        
        x_min, y_max, x_max, y_min = screen_bounds
    
        # Mapeo de FPOGX (0.0 a 1.0) a PsychoPy (x_min a x_max)
        x_psychopy = x_min + (FPOGX * (x_max - x_min))
    
        # Mapeo de FPOGY (0.0 a 1.0) a PsychoPy (y_min a y_max)
        y_psychopy = -(y_min + (FPOGY * (y_max - y_min)))
    
        return x_psychopy, y_psychopy
    
    
    screen_bounds = (-0.89, 0.5, 0.89, -0.5)  # Definir los límites de la pantalla en unidades PsychoPy (x_min, y_max, x_max, y_min)
    
    
    
    gaze = visual.ShapeStim(
        win=win, name='gaze',
        size=(0.05, 0.05), vertices='circle',
        ori=0.0, pos=[0,0], draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor=[1.0000, -1.0000, -1.0000], fillColor=[1.0000, -1.0000, -1.0000],
        opacity=0.4, depth=-4.0, interpolate=True)
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "PUPILOMETRY_TASK_adaptation_period" ---
    key_resp_23 = keyboard.Keyboard(deviceName='key_resp_23')
    
    # --- Initialize components for Routine "PUPILOMETRY_TASK_flash" ---
    text_4 = visual.TextStim(win=win, name='text_4',
        text=None,
        font='Open Sans',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    key_resp_24 = keyboard.Keyboard(deviceName='key_resp_24')
    
    # --- Initialize components for Routine "INSTRUCTIONS" ---
    logo_bio_2 = visual.ImageStim(
        win=win,
        name='logo_bio_2', 
        image='images/BIOBIZKAIA_horizontal_CMYK.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.45, 0.35), draggable=False, size=(0.4, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    logo_compneurolab_2 = visual.ImageStim(
        win=win,
        name='logo_compneurolab_2', 
        image='images/compneuro_horizontal.png', mask=None, anchor='center',
        ori=0.0, pos=(0.45, 0.35), draggable=False, size=(0.6, 0.2),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_title_2 = visual.TextStim(win=win, name='text_title_2',
        text='TEST DE EVALUACIÓN DE LOS SISTEMAS MAGNOCELULAR Y PARVOCELULAR',
        font='Open Sans',
        pos=(0, 0.1), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    text_instructions_2 = visual.TextStim(win=win, name='text_instructions_2',
        text=None,
        font='Open Sans',
        pos=(0, -0.20), draggable=False, height=0.035, wrapWidth=1.5, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    button_next_instruction_2 = visual.ButtonStim(win, 
        text='Siguiente -->', font='Arvo',
        pos=(0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_next_instruction_2',
        depth=-5
    )
    button_next_instruction_2.buttonClock = core.Clock()
    button_previous_instruction_2 = visual.ButtonStim(win, 
        text='<--Anterior', font='Arvo',
        pos=(-0.5, -0.4),
        letterHeight=0.03,
        size=(0.25, 0.15), 
        ori=0.0
        ,borderWidth=0.1,
        fillColor=[-1.0000, 0.0039, -1.0000], borderColor=None,
        color='white', colorSpace='rgb',
        opacity=None,
        bold=True, italic=False,
        padding=None,
        anchor='center',
        name='button_previous_instruction_2',
        depth=-6
    )
    button_previous_instruction_2.buttonClock = core.Clock()
    key_resp_skip_instructions_2 = keyboard.Keyboard(deviceName='key_resp_skip_instructions_2')
    
    # --- Initialize components for Routine "FEARFUL_AND_AFFECTIVE_IMAGES_TASK" ---
    img = visual.ImageStim(
        win=win,
        name='img', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=1.0,
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=512.0, interpolate=False, depth=-1.0)
    key_resp_29 = keyboard.Keyboard(deviceName='key_resp_29')
    logs_29 = visual.TextStim(win=win, name='logs_29',
        text=None,
        font='Open Sans',
        pos=(0.5, 0.35), draggable=False, height=0.025, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    
    # create some handy timers
    
    # global clock to track the time since experiment started
    if globalClock is None:
        # create a clock if not given one
        globalClock = core.Clock()
    if isinstance(globalClock, str):
        # if given a string, make a clock accoridng to it
        if globalClock == 'float':
            # get timestamps as a simple value
            globalClock = core.Clock(format='float')
        elif globalClock == 'iso':
            # get timestamps in ISO format
            globalClock = core.Clock(format='%Y-%m-%d_%H:%M:%S.%f%z')
        else:
            # get timestamps in a custom format
            globalClock = core.Clock(format=globalClock)
    if ioServer is not None:
        ioServer.syncClock(globalClock)
    logging.setDefaultClock(globalClock)
    # routine timer to track time remaining of each (possibly non-slip) routine
    routineTimer = core.Clock()
    win.flip()  # flip window to reset last flip timer
    # store the exact time the global clock started
    expInfo['expStart'] = data.getDateStr(
        format='%Y-%m-%d %Hh%M.%S.%f %z', fractionalSecondDigits=6
    )
    
    # --- Prepare to start Routine "CONFIGURATION_ROUTINE" ---
    # create an object to store info about Routine CONFIGURATION_ROUTINE
    CONFIGURATION_ROUTINE = data.Routine(
        name='CONFIGURATION_ROUTINE',
        components=[periphereal_region_result, key_resp_4, logs2, FPS_logs],
    )
    CONFIGURATION_ROUTINE.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # Run 'Begin Routine' code from code_4
    import json
    import math
    
    print(f"Participant info: {expInfo['participant']}")
    
    def calculate_diameter(excentricity, distance_to_screen, screen_height  = None):
        '''
        Calculates the diameter of circunference correspondint to the excentricity angle depending on the screen height and distance to screen.
        Params:
            -excentricity: angle of the excentricity in degrees
            -distance_to_screen: distance between patient and screen in meters
            -screen_height: height of the screen in meters (default is None, in this case the function will only return the diameter in unit that psychopy understands)
        Returns: 
            -diameter_unit: unit diameter (this is the diameter that psychopy understands, it should match with the diameter in meters when used)
            -diameter_m: diameter in meters (this is the real diameter it should have in the screen)
        '''
    
        if screen_height == None:
            diameter_m = 2 * distance_to_screen * math.sin(math.radians(excentricity))
            return None, diameter_m
        else:
            diameter_unit = (2 * distance_to_screen * math.sin(math.radians(excentricity)))/screen_height
            diameter_m = 2 * distance_to_screen * math.sin(math.radians(excentricity))
            return diameter_unit, diameter_m
    
    def calcular_posicion_stim(angulo_grados, excentricidad, altura_pantalla):
        # primero calculo el diametro en pantalla correspondiente a la excentricidad 
        diameter_unit, _ = calculate_diameter(excentricidad, 0.65, altura_pantalla)
        radius = diameter_unit / 2
        
        #hallo el punto donde mostrar el estimulo sobre la circunferencia de la excentricidad deseada
        theta = math.radians(angulo_grados)
        stim_x = radius * math.cos(theta)
        stim_y = radius * math.sin(theta)
        
        return stim_x, stim_y
    # Cargar el archivo JSON
    def cargar_configuracion(nombre_pantalla):
        with open('./config_data/screen_config.json', 'r') as file:
            config = json.load(file)
        
        # Seleccionar la configuración específica
        pantalla_config = config.get(nombre_pantalla)
        
        if pantalla_config:
            nombre = pantalla_config['nombre']
            tamanyo_pulgadas = pantalla_config['tamanyo']
            dim_y = pantalla_config['dim_y']
            frecuencia_monitor = pantalla_config['frecuencia']
            
            print(f'Se ha cargado la siguiente configuracion:\n'
                  f'Pantalla {nombre_pantalla} de {tamanyo_pulgadas} pulgadas con altura {dim_y} m')
            return nombre, tamanyo_pulgadas, dim_y,frecuencia_monitor
        else:
            print("Configuración de pantalla no encontrada.")
            return None, None, None, None  # Devolver None para cada valor esperado
    
    nombre, tamanyo_pulgadas, dim_y, frecuencia_monitor = cargar_configuracion(nombre_pantalla)
    
    
    if nombre:  # Comprobar que nombre no es None antes de usar las variables
        # Calcular el diámetro de la frontera de la periferia
       
        diameter_unit, diameter_m = calculate_diameter(alpha, distancia_eyetracker, dim_y)
        periphereal_region_diameter = diameter_unit
    
        log = f'Se ha cargado la configuracion de la {nombre_pantalla}:\n Pantalla {nombre} de {tamanyo_pulgadas} pulgadas con altura {dim_y} m y {frecuencia_monitor} Hz.'
        print(log)
        
    logs2.setText(
                 f'Se ha cargado la configuracion de la {nombre_pantalla}:\n Pantalla {nombre} de {tamanyo_pulgadas} pulgadas con altura {dim_y} m y {frecuencia_monitor} Hz.\n' 
                 f'Para una distancia de {distancia_eyetracker} m entre el sujeto y la pantalla, el diametro debe ser de {diameter_unit:.2f} u.\n'
                 f'El diámetro equivalente es de {diameter_m:.2f} m'
                 )
    periphereal_region_result.setSize(periphereal_region_diameter)
    # create starting attributes for key_resp_4
    key_resp_4.keys = []
    key_resp_4.rt = []
    _key_resp_4_allKeys = []
    # Run 'Begin Routine' code from FPS_counter
    tiempo_anterior = 0 
    fps = 0  # Variable para almacenar el FPS
    # store start times for CONFIGURATION_ROUTINE
    CONFIGURATION_ROUTINE.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    CONFIGURATION_ROUTINE.tStart = globalClock.getTime(format='float')
    CONFIGURATION_ROUTINE.status = STARTED
    thisExp.addData('CONFIGURATION_ROUTINE.started', CONFIGURATION_ROUTINE.tStart)
    CONFIGURATION_ROUTINE.maxDuration = None
    # keep track of which components have finished
    CONFIGURATION_ROUTINEComponents = CONFIGURATION_ROUTINE.components
    for thisComponent in CONFIGURATION_ROUTINE.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "CONFIGURATION_ROUTINE" ---
    CONFIGURATION_ROUTINE.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *periphereal_region_result* updates
        
        # if periphereal_region_result is starting this frame...
        if periphereal_region_result.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            periphereal_region_result.frameNStart = frameN  # exact frame index
            periphereal_region_result.tStart = t  # local t and not account for scr refresh
            periphereal_region_result.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(periphereal_region_result, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'periphereal_region_result.started')
            # update status
            periphereal_region_result.status = STARTED
            periphereal_region_result.setAutoDraw(True)
        
        # if periphereal_region_result is active this frame...
        if periphereal_region_result.status == STARTED:
            # update params
            pass
        
        # *key_resp_4* updates
        
        # if key_resp_4 is starting this frame...
        if key_resp_4.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_4.frameNStart = frameN  # exact frame index
            key_resp_4.tStart = t  # local t and not account for scr refresh
            key_resp_4.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_4, 'tStartRefresh')  # time at next scr refresh
            # update status
            key_resp_4.status = STARTED
            # keyboard checking is just starting
            key_resp_4.clock.reset()  # now t=0
        if key_resp_4.status == STARTED:
            theseKeys = key_resp_4.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
            _key_resp_4_allKeys.extend(theseKeys)
            if len(_key_resp_4_allKeys):
                key_resp_4.keys = _key_resp_4_allKeys[-1].name  # just the last key pressed
                key_resp_4.rt = _key_resp_4_allKeys[-1].rt
                key_resp_4.duration = _key_resp_4_allKeys[-1].duration
                # a response ends the routine
                continueRoutine = False
        
        # *logs2* updates
        
        # if logs2 is starting this frame...
        if logs2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            logs2.frameNStart = frameN  # exact frame index
            logs2.tStart = t  # local t and not account for scr refresh
            logs2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(logs2, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'logs2.started')
            # update status
            logs2.status = STARTED
            logs2.setAutoDraw(True)
        
        # if logs2 is active this frame...
        if logs2.status == STARTED:
            # update params
            pass
        # Run 'Each Frame' code from time_daemon
        if t>3:
            continueRoutine = False
        # Run 'Each Frame' code from FPS_counter
        tiempo_actual = t
        delta_tiempo = tiempo_actual - tiempo_anterior # tiempo desde el frame anterior
        
        if delta_tiempo > 0:
            fps = 1.0 / delta_tiempo  # Frecuencia: (1 / tiempo entre frames) (Hz)
        
        tiempo_anterior = tiempo_actual
        
        FPS_logs.text = f"FPS: {fps:.2f}"  # Mostrar con 2 decimales
        
        
        # *FPS_logs* updates
        
        # if FPS_logs is starting this frame...
        if FPS_logs.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            FPS_logs.frameNStart = frameN  # exact frame index
            FPS_logs.tStart = t  # local t and not account for scr refresh
            FPS_logs.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(FPS_logs, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'FPS_logs.started')
            # update status
            FPS_logs.status = STARTED
            FPS_logs.setAutoDraw(True)
        
        # if FPS_logs is active this frame...
        if FPS_logs.status == STARTED:
            # update params
            pass
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer], 
                playbackComponents=[]
            )
            # skip the frame we paused on
            continue
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            CONFIGURATION_ROUTINE.forceEnded = routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in CONFIGURATION_ROUTINE.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "CONFIGURATION_ROUTINE" ---
    for thisComponent in CONFIGURATION_ROUTINE.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for CONFIGURATION_ROUTINE
    CONFIGURATION_ROUTINE.tStop = globalClock.getTime(format='float')
    CONFIGURATION_ROUTINE.tStopRefresh = tThisFlipGlobal
    thisExp.addData('CONFIGURATION_ROUTINE.stopped', CONFIGURATION_ROUTINE.tStop)
    # check responses
    if key_resp_4.keys in ['', [], None]:  # No response was made
        key_resp_4.keys = None
    thisExp.addData('key_resp_4.keys',key_resp_4.keys)
    if key_resp_4.keys != None:  # we had a response
        thisExp.addData('key_resp_4.rt', key_resp_4.rt)
        thisExp.addData('key_resp_4.duration', key_resp_4.duration)
    thisExp.nextEntry()
    # the Routine "CONFIGURATION_ROUTINE" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # set up handler to look after randomisation of conditions etc
    MODULE_1 = data.TrialHandler2(
        name='MODULE_1',
        nReps=modules["module_1"]["selected"], 
        method='sequential', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=[None], 
        seed=None, 
    )
    thisExp.addLoop(MODULE_1)  # add the loop to the experiment
    thisMODULE_1 = MODULE_1.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisMODULE_1.rgb)
    if thisMODULE_1 != None:
        for paramName in thisMODULE_1:
            globals()[paramName] = thisMODULE_1[paramName]
    
    for thisMODULE_1 in MODULE_1:
        currentLoop = MODULE_1
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_1.rgb)
        if thisMODULE_1 != None:
            for paramName in thisMODULE_1:
                globals()[paramName] = thisMODULE_1[paramName]
        
        # set up handler to look after randomisation of conditions etc
        MODULE_1_PRETEST = data.TrialHandler2(
            name='MODULE_1_PRETEST',
            nReps=modules["module_1"]["tests"]["pretest"]["selected"], 
            method='sequential', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=[None], 
            seed=None, 
        )
        thisExp.addLoop(MODULE_1_PRETEST)  # add the loop to the experiment
        thisMODULE_1_PRETEST = MODULE_1_PRETEST.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_1_PRETEST.rgb)
        if thisMODULE_1_PRETEST != None:
            for paramName in thisMODULE_1_PRETEST:
                globals()[paramName] = thisMODULE_1_PRETEST[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisMODULE_1_PRETEST in MODULE_1_PRETEST:
            currentLoop = MODULE_1_PRETEST
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisMODULE_1_PRETEST.rgb)
            if thisMODULE_1_PRETEST != None:
                for paramName in thisMODULE_1_PRETEST:
                    globals()[paramName] = thisMODULE_1_PRETEST[paramName]
            
            # set up handler to look after randomisation of conditions etc
            spatial_freq_instructions = data.TrialHandler2(
                name='spatial_freq_instructions',
                nReps=1.0, 
                method='random', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/spatial_frequency_staircase_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(spatial_freq_instructions)  # add the loop to the experiment
            thisSpatial_freq_instruction = spatial_freq_instructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisSpatial_freq_instruction.rgb)
            if thisSpatial_freq_instruction != None:
                for paramName in thisSpatial_freq_instruction:
                    globals()[paramName] = thisSpatial_freq_instruction[paramName]
            
            for thisSpatial_freq_instruction in spatial_freq_instructions:
                currentLoop = spatial_freq_instructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                # abbreviate parameter names if possible (e.g. rgb = thisSpatial_freq_instruction.rgb)
                if thisSpatial_freq_instruction != None:
                    for paramName in thisSpatial_freq_instruction:
                        globals()[paramName] = thisSpatial_freq_instruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(spatial_freq_instructions, data.TrialHandler2) and thisSpatial_freq_instruction.thisN != spatial_freq_instructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                spatial_freq_instructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   spatial_freq_instructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   spatial_freq_instructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   spatial_freq_instructions.addData('button_next_instruction_2.timesOn', "")
                   spatial_freq_instructions.addData('button_next_instruction_2.timesOff', "")
                spatial_freq_instructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   spatial_freq_instructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   spatial_freq_instructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   spatial_freq_instructions.addData('button_previous_instruction_2.timesOn', "")
                   spatial_freq_instructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                spatial_freq_instructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    spatial_freq_instructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    spatial_freq_instructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
            # completed 1.0 repeats of 'spatial_freq_instructions'
            
            
            # --- Prepare to start Routine "SPATIAL_FREQ_STAIRCASE_TEST" ---
            # create an object to store info about Routine SPATIAL_FREQ_STAIRCASE_TEST
            SPATIAL_FREQ_STAIRCASE_TEST = data.Routine(
                name='SPATIAL_FREQ_STAIRCASE_TEST',
                components=[grating_7, dots_black_3, dots_white_3, key_resp_16, logs_12, key_resp_19],
            )
            SPATIAL_FREQ_STAIRCASE_TEST.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            dots_black_3.refreshDots()
            dots_white_3.refreshDots()
            # Run 'Begin Routine' code from code_20
            import csv
            
            # Variables estaticas
            sf_starting_value = 50
            sf_step_size = 15
            sf_starting_orientation = get_random_orientation()
            
            
            # Inicializacion de variables que posteriormente cambian
            sf = sf_starting_value
            step = sf_step_size
            staircase_test_orientation = sf_starting_orientation
            reversals = 0
            last_direction = None
            reversal_sf = []
            correct_responses = 0
            trials = []
            
            # Para almacenar las respuestas del participante
            response = None
            
            # Acciones inicio de rutina
            grating_7.sf = sf
            grating_7.ori = staircase_test_orientation
            
            dots_white_3.setAutoDraw(False)
            dots_black_3.setAutoDraw(False)
            
            #threshold_dict = load_thresholds_from_json()     #cargar diccionario
            threshold_dict = {}
            
            # create starting attributes for key_resp_16
            key_resp_16.keys = []
            key_resp_16.rt = []
            _key_resp_16_allKeys = []
            # create starting attributes for key_resp_19
            key_resp_19.keys = []
            key_resp_19.rt = []
            _key_resp_19_allKeys = []
            # store start times for SPATIAL_FREQ_STAIRCASE_TEST
            SPATIAL_FREQ_STAIRCASE_TEST.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            SPATIAL_FREQ_STAIRCASE_TEST.tStart = globalClock.getTime(format='float')
            SPATIAL_FREQ_STAIRCASE_TEST.status = STARTED
            thisExp.addData('SPATIAL_FREQ_STAIRCASE_TEST.started', SPATIAL_FREQ_STAIRCASE_TEST.tStart)
            SPATIAL_FREQ_STAIRCASE_TEST.maxDuration = None
            # keep track of which components have finished
            SPATIAL_FREQ_STAIRCASE_TESTComponents = SPATIAL_FREQ_STAIRCASE_TEST.components
            for thisComponent in SPATIAL_FREQ_STAIRCASE_TEST.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "SPATIAL_FREQ_STAIRCASE_TEST" ---
            # if trial has changed, end Routine now
            if isinstance(MODULE_1_PRETEST, data.TrialHandler2) and thisMODULE_1_PRETEST.thisN != MODULE_1_PRETEST.thisTrial.thisN:
                continueRoutine = False
            SPATIAL_FREQ_STAIRCASE_TEST.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *grating_7* updates
                
                # if grating_7 is starting this frame...
                if grating_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    grating_7.frameNStart = frameN  # exact frame index
                    grating_7.tStart = t  # local t and not account for scr refresh
                    grating_7.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(grating_7, 'tStartRefresh')  # time at next scr refresh
                    # update status
                    grating_7.status = STARTED
                    grating_7.setAutoDraw(True)
                
                # if grating_7 is active this frame...
                if grating_7.status == STARTED:
                    # update params
                    pass
                
                # *dots_black_3* updates
                
                # if dots_black_3 is starting this frame...
                if dots_black_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    dots_black_3.frameNStart = frameN  # exact frame index
                    dots_black_3.tStart = t  # local t and not account for scr refresh
                    dots_black_3.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(dots_black_3, 'tStartRefresh')  # time at next scr refresh
                    # update status
                    dots_black_3.status = STARTED
                    dots_black_3.setAutoDraw(True)
                
                # if dots_black_3 is active this frame...
                if dots_black_3.status == STARTED:
                    # update params
                    pass
                
                # *dots_white_3* updates
                
                # if dots_white_3 is starting this frame...
                if dots_white_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    dots_white_3.frameNStart = frameN  # exact frame index
                    dots_white_3.tStart = t  # local t and not account for scr refresh
                    dots_white_3.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(dots_white_3, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'dots_white_3.started')
                    # update status
                    dots_white_3.status = STARTED
                    dots_white_3.setAutoDraw(True)
                
                # if dots_white_3 is active this frame...
                if dots_white_3.status == STARTED:
                    # update params
                    pass
                # Run 'Each Frame' code from code_20
                keys = event.getKeys()
                
                if 's' in keys: # El paciente ve el estimulo
                    response = True
                elif 'n' in keys: # El paciente no ve las lineas
                    response = False
                elif 'right' in keys and staircase_test_orientation == 45: # Acierto
                    response = True
                elif 'left' in keys and staircase_test_orientation == 135: # Acierto
                    response = True
                elif 'right' in keys or 'left' in keys:
                    response = False
                
                # Lógica del staircase
                if response is not None:
                    if response:  # Respuesta correcta: el paciente ve las lineas del estimulo
                        correct_responses += 1
                        if correct_responses == 2:  # Después de 2 respuestas correctas consecutivas
                            correct_responses = 0
                            sf = max(0, sf + step)  # Aumentar las lineas
                            last_direction = "down"
                    else: 
                        sf = sf - step
                        correct_responses = 0
                        if last_direction == "down":
                            reversals += 1
                            reversal_sf.append(sf)
                            # Regla para aumentar la granularidad del test
                            if (reversals % 3 == 0) and reversals != 0:
                                step = step/2
                                print(f"Reversals = {reversals}; New step = {step}")
                                last_direction = "up"
                            else:
                                print(f'Reversal detected ({reversals})')
                        last_direction = "up"
                        
                    grating_7.setAutoDraw(False)
                    show_noise(dots_white_3, dots_black_3, staircase_noise_duration)
                    grating_7.setAutoDraw(True)
                    
                    # Actualizar el sf y orientacion del estímulo
                    grating_7.sf = sf
                    staircase_test_orientation = get_random_orientation()
                    grating_7.ori = staircase_test_orientation
                
                    
                    # Registrar la información del ensayo
                    trials.append({
                        'trial': len(trials) + 1,
                        'spatial_frequency': sf,
                        'response': response,
                        'reversals': reversals
                    })
                    
                    # Restablecer la respuesta para el siguiente ensayo
                    response = None
                        
                    # Regla de detencion
                    if reversals >= stop_reversals:
                        print(trials)
                        
                        # almaceno trials en 'data' para su posterior analisis (CSV)
                        staircase_data_filename = f"./data/{expInfo['participant']}/sf_staircase_data_{expInfo['participant']}.csv"
                
                        with open(staircase_data_filename, mode='w', newline='') as file:
                            writer = csv.DictWriter(file, fieldnames=['trial', 'spatial_frequency', 'response', 'reversals'])
                            writer.writeheader()
                            writer.writerows(trials)
                        
                        # Actualizar y almacenar el diccionario de thresholds
                        test_sf = get_threshold('spatial_frequency', staircase_data_filename)
                        print(f"Spatial Frequency Threshold for patient: {test_sf}")
                        threshold_dict['spatial_frequency_threshold'] = test_sf
                        save_thresholds_to_json(threshold_dict)
                        
                        continueRoutine = False
                
                #########################################################
                #############____________LOGS_________###################
                #########################################################
                if general_config["logs"]:
                    logs_12.text = f"Step Size = {step}"
                else:
                    logs_12.setAutoDraw(False)
                    
                dots_white_3.setAutoDraw(False)
                dots_black_3.setAutoDraw(False)
                
                # *key_resp_16* updates
                waitOnFlip = False
                
                # if key_resp_16 is starting this frame...
                if key_resp_16.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_16.frameNStart = frameN  # exact frame index
                    key_resp_16.tStart = t  # local t and not account for scr refresh
                    key_resp_16.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_16, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp_16.started')
                    # update status
                    key_resp_16.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_16.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_16.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp_16.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_16.getKeys(keyList=['s','n'], ignoreKeys=["escape"], waitRelease=False)
                    _key_resp_16_allKeys.extend(theseKeys)
                    if len(_key_resp_16_allKeys):
                        key_resp_16.keys = _key_resp_16_allKeys[-1].name  # just the last key pressed
                        key_resp_16.rt = _key_resp_16_allKeys[-1].rt
                        key_resp_16.duration = _key_resp_16_allKeys[-1].duration
                
                # *logs_12* updates
                
                # if logs_12 is starting this frame...
                if logs_12.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    logs_12.frameNStart = frameN  # exact frame index
                    logs_12.tStart = t  # local t and not account for scr refresh
                    logs_12.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(logs_12, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'logs_12.started')
                    # update status
                    logs_12.status = STARTED
                    logs_12.setAutoDraw(True)
                
                # if logs_12 is active this frame...
                if logs_12.status == STARTED:
                    # update params
                    pass
                
                # *key_resp_19* updates
                waitOnFlip = False
                
                # if key_resp_19 is starting this frame...
                if key_resp_19.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_19.frameNStart = frameN  # exact frame index
                    key_resp_19.tStart = t  # local t and not account for scr refresh
                    key_resp_19.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_19, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp_19.started')
                    # update status
                    key_resp_19.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_19.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_19.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp_19.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_19.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                    _key_resp_19_allKeys.extend(theseKeys)
                    if len(_key_resp_19_allKeys):
                        key_resp_19.keys = _key_resp_19_allKeys[-1].name  # just the last key pressed
                        key_resp_19.rt = _key_resp_19_allKeys[-1].rt
                        key_resp_19.duration = _key_resp_19_allKeys[-1].duration
                        # a response ends the routine
                        continueRoutine = False
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer], 
                        playbackComponents=[]
                    )
                    # skip the frame we paused on
                    continue
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    SPATIAL_FREQ_STAIRCASE_TEST.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in SPATIAL_FREQ_STAIRCASE_TEST.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "SPATIAL_FREQ_STAIRCASE_TEST" ---
            for thisComponent in SPATIAL_FREQ_STAIRCASE_TEST.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for SPATIAL_FREQ_STAIRCASE_TEST
            SPATIAL_FREQ_STAIRCASE_TEST.tStop = globalClock.getTime(format='float')
            SPATIAL_FREQ_STAIRCASE_TEST.tStopRefresh = tThisFlipGlobal
            thisExp.addData('SPATIAL_FREQ_STAIRCASE_TEST.stopped', SPATIAL_FREQ_STAIRCASE_TEST.tStop)
            # check responses
            if key_resp_16.keys in ['', [], None]:  # No response was made
                key_resp_16.keys = None
            MODULE_1_PRETEST.addData('key_resp_16.keys',key_resp_16.keys)
            if key_resp_16.keys != None:  # we had a response
                MODULE_1_PRETEST.addData('key_resp_16.rt', key_resp_16.rt)
                MODULE_1_PRETEST.addData('key_resp_16.duration', key_resp_16.duration)
            # check responses
            if key_resp_19.keys in ['', [], None]:  # No response was made
                key_resp_19.keys = None
            MODULE_1_PRETEST.addData('key_resp_19.keys',key_resp_19.keys)
            if key_resp_19.keys != None:  # we had a response
                MODULE_1_PRETEST.addData('key_resp_19.rt', key_resp_19.rt)
                MODULE_1_PRETEST.addData('key_resp_19.duration', key_resp_19.duration)
            # the Routine "SPATIAL_FREQ_STAIRCASE_TEST" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # set up handler to look after randomisation of conditions etc
            contrast_instructions = data.TrialHandler2(
                name='contrast_instructions',
                nReps=1.0, 
                method='random', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/contrast_staircase_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(contrast_instructions)  # add the loop to the experiment
            thisContrast_instruction = contrast_instructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisContrast_instruction.rgb)
            if thisContrast_instruction != None:
                for paramName in thisContrast_instruction:
                    globals()[paramName] = thisContrast_instruction[paramName]
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            
            for thisContrast_instruction in contrast_instructions:
                currentLoop = contrast_instructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                if thisSession is not None:
                    # if running in a Session with a Liaison client, send data up to now
                    thisSession.sendExperimentData()
                # abbreviate parameter names if possible (e.g. rgb = thisContrast_instruction.rgb)
                if thisContrast_instruction != None:
                    for paramName in thisContrast_instruction:
                        globals()[paramName] = thisContrast_instruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(contrast_instructions, data.TrialHandler2) and thisContrast_instruction.thisN != contrast_instructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                contrast_instructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   contrast_instructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   contrast_instructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   contrast_instructions.addData('button_next_instruction_2.timesOn', "")
                   contrast_instructions.addData('button_next_instruction_2.timesOff', "")
                contrast_instructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   contrast_instructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   contrast_instructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   contrast_instructions.addData('button_previous_instruction_2.timesOn', "")
                   contrast_instructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                contrast_instructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    contrast_instructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    contrast_instructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
                thisExp.nextEntry()
                
            # completed 1.0 repeats of 'contrast_instructions'
            
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # get names of stimulus parameters
            if contrast_instructions.trialList in ([], [None], None):
                params = []
            else:
                params = contrast_instructions.trialList[0].keys()
            # save data for this loop
            contrast_instructions.saveAsExcel(filename + '.xlsx', sheetName='contrast_instructions',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            
            # --- Prepare to start Routine "CONTRAST_STAIRCASE_TEST" ---
            # create an object to store info about Routine CONTRAST_STAIRCASE_TEST
            CONTRAST_STAIRCASE_TEST = data.Routine(
                name='CONTRAST_STAIRCASE_TEST',
                components=[key_resp_14, logs_10, grating, dots_white, dots_black, key_resp_20],
            )
            CONTRAST_STAIRCASE_TEST.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            # Run 'Begin Routine' code from code_18
            import csv
            import tkinter as tk
            from tkinter import messagebox
            
            # Variables estaticas
            contrast_starting_value = 0.25#0.05
            contrast_step_size = 0.02
            
            # Inicializacion de variables que posteriormente cambian
            contrast = contrast_starting_value
            staircase_test_orientation = get_random_orientation()
            step = contrast_step_size
            reversals = 0
            last_direction = None
            reversal_contrasts = []
            correct_responses = 0
            trials = []
            
            # Para almacenar las respuestas del participante
            response = None
            
            grating.contrast = contrast
            grating.ori = staircase_test_orientation
            
            # Cargar frecuencia espacial del test si se ha seleccionado la opcion
            # pretest_standard_thresholds_path = "./config_data/standard_thresholds.json"
            if general_config["pretest_standard_values"]:
                if not os.path.exists(pretest_standard_thresholds_path):
                    root = tk.Tk()
                    root.withdraw()  # Oculta la ventana principal
                    messagebox.showwarning("Advertencia", f"No se ha encontrado el archivo de configuración estándar. Compruebe la ruta {pretest_standard_thresholds_path}.")
                else:
                    _threshold_dict = load_thresholds_from_json(filename=pretest_standard_thresholds_path)
                    spatial_frequency = _threshold_dict['spatial_frequency_threshold']
                    threshold_dict = load_thresholds_from_json()  # archivo de usuario
                    print(f"Se ha establecido la frecuencia espacial DEFAULT del estímulo a un valor de {spatial_frequency} unidades.")
            else:
                threshold_dict = load_thresholds_from_json() # archivo de usuario
                spatial_frequency = threshold_dict['spatial_frequency_threshold']
                print(f"Se ha establecido la frecuencia espacial del estímulo a un valor de {spatial_frequency} unidades.")
            
            grating.sf = spatial_frequency
                
            dots_white.setAutoDraw(False)
            dots_black.setAutoDraw(False)
            # create starting attributes for key_resp_14
            key_resp_14.keys = []
            key_resp_14.rt = []
            _key_resp_14_allKeys = []
            dots_white.refreshDots()
            dots_black.refreshDots()
            # create starting attributes for key_resp_20
            key_resp_20.keys = []
            key_resp_20.rt = []
            _key_resp_20_allKeys = []
            # store start times for CONTRAST_STAIRCASE_TEST
            CONTRAST_STAIRCASE_TEST.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            CONTRAST_STAIRCASE_TEST.tStart = globalClock.getTime(format='float')
            CONTRAST_STAIRCASE_TEST.status = STARTED
            thisExp.addData('CONTRAST_STAIRCASE_TEST.started', CONTRAST_STAIRCASE_TEST.tStart)
            CONTRAST_STAIRCASE_TEST.maxDuration = None
            # keep track of which components have finished
            CONTRAST_STAIRCASE_TESTComponents = CONTRAST_STAIRCASE_TEST.components
            for thisComponent in CONTRAST_STAIRCASE_TEST.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "CONTRAST_STAIRCASE_TEST" ---
            # if trial has changed, end Routine now
            if isinstance(MODULE_1_PRETEST, data.TrialHandler2) and thisMODULE_1_PRETEST.thisN != MODULE_1_PRETEST.thisTrial.thisN:
                continueRoutine = False
            CONTRAST_STAIRCASE_TEST.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                # Run 'Each Frame' code from code_18
                keys = event.getKeys()
                
                if 's' in keys: # El paciente ve el estimulo
                    response = True
                elif 'n' in keys: # El paciente no ve las lineas
                    response = False
                elif 'right' in keys and staircase_test_orientation == 45: # Acierto
                    response = True
                elif 'left' in keys and staircase_test_orientation == 135: # Acierto
                    response = True
                elif 'right' in keys or 'left' in keys:
                    response = False
                
                # Lógica del staircase
                if response is not None:
                    if response:  # Respuesta correcta: el paciente ve el estimulo
                        correct_responses += 1
                        if correct_responses == 2:  # Después de 2 respuestas correctas consecutivas
                            correct_responses = 0
                            contrast = max(0, contrast - step)  # Disminuir el contraste
                            last_direction = "down"
                    else:  # Respuesta incorrecta: el paciente no ve el estimulo
                        contrast += step  # Aumentar el contraste
                        correct_responses = 0
                        if last_direction == "down":
                            reversals += 1
                            reversal_contrasts.append(contrast)
                            
                            if (reversals % 3 == 0) and reversals != 0:
                                step = step/2
                                print(f"Reversals = {reversals}; New step = {step}")
                                last_direction = "up"
                            else:
                                print('Reversal detected ({reversals})')
                        last_direction = "up"
                        
                    grating.setAutoDraw(False)
                    show_noise(dots_white, dots_black, staircase_noise_duration)
                    grating.setAutoDraw(True)
                    # Actualizar el contraste del estímulo
                    grating.contrast = contrast
                    staircase_test_orientation = get_random_orientation()
                    grating.ori = staircase_test_orientation
                    
                    # Registrar la información del ensayo
                    trials.append({
                        'trial': len(trials) + 1,
                        'contrast': contrast,
                        'response': response,
                        'reversals': reversals
                    })
                    
                    # Restablecer la respuesta para el siguiente ensayo
                    response = None
                
                    # Regla de detencion
                    if reversals >= stop_reversals:
                        print(trials)
                        # almaceno trials en 'data' para su posterior analisis
                        staircase_data_filename = f"./data/{expInfo['participant']}/contrast_staircase_data_{expInfo['participant']}.csv"
                        with open(staircase_data_filename, mode='w', newline='') as file:
                            writer = csv.DictWriter(file, fieldnames=['trial', 'contrast', 'response', 'reversals'])
                            writer.writeheader()
                            writer.writerows(trials)
                        
                        # Actualizar y almacenar el diccionario de thresholds
                        test_contrast = get_threshold('contrast', staircase_data_filename)
                        print(f"Contrast Threshold for patient: {test_contrast}")
                        threshold_dict['contrast_threshold'] = test_contrast
                        save_thresholds_to_json(threshold_dict)
                        
                        dots_white.setAutoDraw(False)
                        dots_black.setAutoDraw(False)    
                        continueRoutine = False
                
                #########################################################
                #############____________LOGS_________###################
                #########################################################
                if general_config["logs"]:
                    logs_10.text = f"Step Size = {step}"
                else:
                    logs_10.setAutoDraw(False)
                    
                dots_white.setAutoDraw(False)
                dots_black.setAutoDraw(False)
                
                # *key_resp_14* updates
                waitOnFlip = False
                
                # if key_resp_14 is starting this frame...
                if key_resp_14.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_14.frameNStart = frameN  # exact frame index
                    key_resp_14.tStart = t  # local t and not account for scr refresh
                    key_resp_14.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_14, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp_14.started')
                    # update status
                    key_resp_14.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_14.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_14.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp_14.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_14.getKeys(keyList=['s','n','right','left'], ignoreKeys=["escape"], waitRelease=False)
                    _key_resp_14_allKeys.extend(theseKeys)
                    if len(_key_resp_14_allKeys):
                        key_resp_14.keys = _key_resp_14_allKeys[-1].name  # just the last key pressed
                        key_resp_14.rt = _key_resp_14_allKeys[-1].rt
                        key_resp_14.duration = _key_resp_14_allKeys[-1].duration
                
                # *logs_10* updates
                
                # if logs_10 is starting this frame...
                if logs_10.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    logs_10.frameNStart = frameN  # exact frame index
                    logs_10.tStart = t  # local t and not account for scr refresh
                    logs_10.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(logs_10, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'logs_10.started')
                    # update status
                    logs_10.status = STARTED
                    logs_10.setAutoDraw(True)
                
                # if logs_10 is active this frame...
                if logs_10.status == STARTED:
                    # update params
                    pass
                
                # *grating* updates
                
                # if grating is starting this frame...
                if grating.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    grating.frameNStart = frameN  # exact frame index
                    grating.tStart = t  # local t and not account for scr refresh
                    grating.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(grating, 'tStartRefresh')  # time at next scr refresh
                    # update status
                    grating.status = STARTED
                    grating.setAutoDraw(True)
                
                # if grating is active this frame...
                if grating.status == STARTED:
                    # update params
                    pass
                
                # *dots_white* updates
                
                # if dots_white is starting this frame...
                if dots_white.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    dots_white.frameNStart = frameN  # exact frame index
                    dots_white.tStart = t  # local t and not account for scr refresh
                    dots_white.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(dots_white, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'dots_white.started')
                    # update status
                    dots_white.status = STARTED
                    dots_white.setAutoDraw(True)
                
                # if dots_white is active this frame...
                if dots_white.status == STARTED:
                    # update params
                    pass
                
                # *dots_black* updates
                
                # if dots_black is starting this frame...
                if dots_black.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    dots_black.frameNStart = frameN  # exact frame index
                    dots_black.tStart = t  # local t and not account for scr refresh
                    dots_black.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(dots_black, 'tStartRefresh')  # time at next scr refresh
                    # update status
                    dots_black.status = STARTED
                    dots_black.setAutoDraw(True)
                
                # if dots_black is active this frame...
                if dots_black.status == STARTED:
                    # update params
                    pass
                
                # *key_resp_20* updates
                waitOnFlip = False
                
                # if key_resp_20 is starting this frame...
                if key_resp_20.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_20.frameNStart = frameN  # exact frame index
                    key_resp_20.tStart = t  # local t and not account for scr refresh
                    key_resp_20.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_20, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp_20.started')
                    # update status
                    key_resp_20.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_20.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_20.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp_20.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_20.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                    _key_resp_20_allKeys.extend(theseKeys)
                    if len(_key_resp_20_allKeys):
                        key_resp_20.keys = _key_resp_20_allKeys[-1].name  # just the last key pressed
                        key_resp_20.rt = _key_resp_20_allKeys[-1].rt
                        key_resp_20.duration = _key_resp_20_allKeys[-1].duration
                        # a response ends the routine
                        continueRoutine = False
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer], 
                        playbackComponents=[]
                    )
                    # skip the frame we paused on
                    continue
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    CONTRAST_STAIRCASE_TEST.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in CONTRAST_STAIRCASE_TEST.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "CONTRAST_STAIRCASE_TEST" ---
            for thisComponent in CONTRAST_STAIRCASE_TEST.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for CONTRAST_STAIRCASE_TEST
            CONTRAST_STAIRCASE_TEST.tStop = globalClock.getTime(format='float')
            CONTRAST_STAIRCASE_TEST.tStopRefresh = tThisFlipGlobal
            thisExp.addData('CONTRAST_STAIRCASE_TEST.stopped', CONTRAST_STAIRCASE_TEST.tStop)
            # check responses
            if key_resp_14.keys in ['', [], None]:  # No response was made
                key_resp_14.keys = None
            MODULE_1_PRETEST.addData('key_resp_14.keys',key_resp_14.keys)
            if key_resp_14.keys != None:  # we had a response
                MODULE_1_PRETEST.addData('key_resp_14.rt', key_resp_14.rt)
                MODULE_1_PRETEST.addData('key_resp_14.duration', key_resp_14.duration)
            # check responses
            if key_resp_20.keys in ['', [], None]:  # No response was made
                key_resp_20.keys = None
            MODULE_1_PRETEST.addData('key_resp_20.keys',key_resp_20.keys)
            if key_resp_20.keys != None:  # we had a response
                MODULE_1_PRETEST.addData('key_resp_20.rt', key_resp_20.rt)
                MODULE_1_PRETEST.addData('key_resp_20.duration', key_resp_20.duration)
            # the Routine "CONTRAST_STAIRCASE_TEST" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # set up handler to look after randomisation of conditions etc
            color_instructions = data.TrialHandler2(
                name='color_instructions',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/color_staircase_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(color_instructions)  # add the loop to the experiment
            thisColor_instruction = color_instructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisColor_instruction.rgb)
            if thisColor_instruction != None:
                for paramName in thisColor_instruction:
                    globals()[paramName] = thisColor_instruction[paramName]
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            
            for thisColor_instruction in color_instructions:
                currentLoop = color_instructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                if thisSession is not None:
                    # if running in a Session with a Liaison client, send data up to now
                    thisSession.sendExperimentData()
                # abbreviate parameter names if possible (e.g. rgb = thisColor_instruction.rgb)
                if thisColor_instruction != None:
                    for paramName in thisColor_instruction:
                        globals()[paramName] = thisColor_instruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(color_instructions, data.TrialHandler2) and thisColor_instruction.thisN != color_instructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                color_instructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   color_instructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   color_instructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   color_instructions.addData('button_next_instruction_2.timesOn', "")
                   color_instructions.addData('button_next_instruction_2.timesOff', "")
                color_instructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   color_instructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   color_instructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   color_instructions.addData('button_previous_instruction_2.timesOn', "")
                   color_instructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                color_instructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    color_instructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    color_instructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
                thisExp.nextEntry()
                
            # completed 1.0 repeats of 'color_instructions'
            
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # get names of stimulus parameters
            if color_instructions.trialList in ([], [None], None):
                params = []
            else:
                params = color_instructions.trialList[0].keys()
            # save data for this loop
            color_instructions.saveAsExcel(filename + '.xlsx', sheetName='color_instructions',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            
            # set up handler to look after randomisation of conditions etc
            colors_to_test = data.TrialHandler2(
                name='colors_to_test',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('colors_to_test.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(colors_to_test)  # add the loop to the experiment
            thisColors_to_test = colors_to_test.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisColors_to_test.rgb)
            if thisColors_to_test != None:
                for paramName in thisColors_to_test:
                    globals()[paramName] = thisColors_to_test[paramName]
            
            for thisColors_to_test in colors_to_test:
                currentLoop = colors_to_test
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                # abbreviate parameter names if possible (e.g. rgb = thisColors_to_test.rgb)
                if thisColors_to_test != None:
                    for paramName in thisColors_to_test:
                        globals()[paramName] = thisColors_to_test[paramName]
                
                # --- Prepare to start Routine "COLOR_STAIRCASE_TEST" ---
                # create an object to store info about Routine COLOR_STAIRCASE_TEST
                COLOR_STAIRCASE_TEST = data.Routine(
                    name='COLOR_STAIRCASE_TEST',
                    components=[key_resp_15, logs_11, image_2, dots_white_2, dots_black_2, key_resp_21],
                )
                COLOR_STAIRCASE_TEST.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_19
                import csv
                # Variables estaticas
                saturation_starting_value = 55
                saturation_step_size = 5
                staircase_test_orientation = get_random_orientation()
                
                # Inicializacion de variables que posteriormente cambian
                saturation = saturation_starting_value
                step = saturation_step_size
                reversals = 0
                last_direction = None
                reversal_saturations = []
                correct_responses = 0
                trials = []
                
                # Para almacenar las respuestas del participante
                response = None
                
                dots_white_2.setAutoDraw(False)
                dots_black_2.setAutoDraw(False)
                
                # Tipo de test
                if color_saturation_type == 'low':
                    static_saturation = 0
                    saturation_starting_value = 15
                elif color_saturation_type == 'high':
                    static_saturation = 70
                    saturation_starting_value = 100
                elif color_saturation_type == 'medium':
                    static_saturation = 50
                    saturation_starting_value = 70
                else:
                    print("No se ha especificado un tipo de saturación a medir")
                    static_saturation = 0
                    saturation_starting_value = 0
                
                saturation = saturation_starting_value
                
                
                # Inicializacion de variables
                
                threshold_dict = load_thresholds_from_json() # archivo de usuario
                print(f"SE HA CARGADO THRESHOLD DICT EN COLOR: {threshold_dict}")
                
                if general_config["pretest_standard_values"]:
                    if not os.path.exists(pretest_standard_thresholds_path):
                        root = tk.Tk()
                        root.withdraw()  # Oculta la ventana principal
                        messagebox.showwarning("Advertencia", f"No se ha encontrado el archivo de configuración estándar. Compruebe la ruta {pretest_standard_thresholds_path}.")
                    else:
                        _threshold_dict = load_thresholds_from_json(filename=pretest_standard_thresholds_path)
                        spatial_frequency = _threshold_dict['spatial_frequency_threshold']
                        threshold_dict = load_thresholds_from_json()  # archivo de usuario
                        print(f"Se ha establecido la frecuencia espacial DEFAULT del estímulo a un valor de {spatial_frequency} unidades.")
                
                else:
                    spatial_frequency = threshold_dict['spatial_frequency_threshold']
                    print(f"Se ha establecido la frecuencia espacial del estímulo a un valor personalizado de {spatial_frequency} unidades.")
                
                
                if 'color_threshold' not in threshold_dict:
                    threshold_dict['color_threshold'] = {}
                
                
                frequency = spatial_frequency/500 # division para equiparar con psychopy
                size = 800
                c1_hsv = (color_h, static_saturation, color_v) # From XLS
                c2_hsv = (color_h, saturation, color_v)
                print(f"Testing color: {color_name}")
                
                image_2.ori = staircase_test_orientation
                
                # Generar el parche de Gabor
                save_gabor_patch_image(frequency, 
                                       size, 
                                       normalizar_rgb(hsv_a_rgb(*c1_hsv)), 
                                       normalizar_rgb(hsv_a_rgb(*c2_hsv)))
                # create starting attributes for key_resp_15
                key_resp_15.keys = []
                key_resp_15.rt = []
                _key_resp_15_allKeys = []
                # Run 'Begin Routine' code from gabor_generator
                
                
                
                
                dots_white_2.refreshDots()
                dots_black_2.refreshDots()
                # create starting attributes for key_resp_21
                key_resp_21.keys = []
                key_resp_21.rt = []
                _key_resp_21_allKeys = []
                # store start times for COLOR_STAIRCASE_TEST
                COLOR_STAIRCASE_TEST.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                COLOR_STAIRCASE_TEST.tStart = globalClock.getTime(format='float')
                COLOR_STAIRCASE_TEST.status = STARTED
                thisExp.addData('COLOR_STAIRCASE_TEST.started', COLOR_STAIRCASE_TEST.tStart)
                COLOR_STAIRCASE_TEST.maxDuration = None
                # keep track of which components have finished
                COLOR_STAIRCASE_TESTComponents = COLOR_STAIRCASE_TEST.components
                for thisComponent in COLOR_STAIRCASE_TEST.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "COLOR_STAIRCASE_TEST" ---
                # if trial has changed, end Routine now
                if isinstance(colors_to_test, data.TrialHandler2) and thisColors_to_test.thisN != colors_to_test.thisTrial.thisN:
                    continueRoutine = False
                COLOR_STAIRCASE_TEST.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    # Run 'Each Frame' code from code_19
                    keys = event.getKeys()
                    
                    if 's' in keys: # El paciente ve el estimulo
                        response = True
                    elif 'n' in keys: # El paciente no ve las lineas
                        response = False
                    elif 'right' in keys and staircase_test_orientation == 45: # Acierto
                        response = True
                    elif 'left' in keys and staircase_test_orientation == 135: # Acierto
                        response = True
                    elif 'right' in keys or 'left' in keys:
                        response = False
                    
                    # Lógica del staircase
                    if response is not None:
                        if response:  # Respuesta correcta: el paciente ve el estimulo
                            correct_responses += 1
                            if correct_responses == 2:  # Después de 2 respuestas correctas consecutivas
                                correct_responses = 0
                                saturation = max(0, saturation - step)
                                if saturation < static_saturation:
                                    # si pasa esto, el test se pasa de rosca. Hay que limitar el valor.
                                    saturation = static_saturation
                                last_direction = "down"
                        else:  # Respuesta incorrecta: el paciente no ve el estimulo
                            saturation += step  # Aumentar el contraste
                            if saturation > 100: # Limitar maximo para que no se pase de rosca
                                saturation = 100
                            correct_responses = 0
                            if last_direction == "down":
                                reversals += 1
                                reversal_saturations.append(saturation)
                                # Regla para aumentar la granularidad del test
                                if (reversals % 2 == 0) and reversals != 0:
                                    step = step/2
                                    print(f"Reversals = {reversals}; New step = {step}")
                                    last_direction = "up"
                                else:
                                    print(f'Reversal detected ({reversals})')
                            last_direction = "up"
                           
                        image_2.setAutoDraw(False)
                        show_noise(dots_white_2, dots_black_2, staircase_noise_duration)
                        image_2.setAutoDraw(True)
                        
                        # Actualizar el color y rotacion del estímulo
                        staircase_test_orientation = get_random_orientation()
                        image_2.ori = staircase_test_orientation
                        c2_hsv = (color_h, saturation, color_v)
                        print(f"Color 1: {c1_hsv}\nColor 2: {c2_hsv}\n")
                    
                    #logs.text = f'freq = {frequency:.2f}\nc1 = ({c1[0]:.2f}, {c1[1]:.2f}, {c1[2]:.2f})\nc2 = ({c2[0]:.2f}, {c2[1]:.2f}, {c2[2]:.2f})'
                    # Generar el parche de Gabor
                    
                        save_gabor_patch_image(frequency, 
                                           size, 
                                           normalizar_rgb(hsv_a_rgb(*c1_hsv)), 
                                           normalizar_rgb(hsv_a_rgb(*c2_hsv)))
                        
                        # Registrar la información del ensayo
                        trials.append({
                            'trial': len(trials) + 1,
                            'saturation': saturation,
                            'response': response,
                            'reversals': reversals
                        })
                        
                        # Restablecer la respuesta para el siguiente ensayo
                        response = None
                            
                        # Regla de detencion
                        if reversals >= stop_reversals:
                            print(trials)
                            # almaceno trials en 'data' para su posterior analisis
                            staircase_data_filename = f"./data/{expInfo['participant']}/saturation_staircase_data_{expInfo['participant']}_{color_name}.csv"#_{color_saturation_type}.csv"
                            with open(staircase_data_filename, mode='w', newline='') as file:
                                writer = csv.DictWriter(file, fieldnames=['trial', 'saturation', 'response', 'reversals'])
                                writer.writeheader()
                                writer.writerows(trials)
                            
                            # Actualizar y almacenar el diccionario de thresholds
                            test_saturation = get_threshold('saturation', staircase_data_filename)
                            print(f"Saturation Threshold for patient: {test_saturation}")
                            threshold_dict['color_threshold'][color_name] = test_saturation-static_saturation
                            save_thresholds_to_json(threshold_dict)
                            
                            
                            continueRoutine = False
                    
                        dots_white_2.setAutoDraw(False)
                        dots_black_2.setAutoDraw(False)
                        
                    #########################################################
                    #############____________LOGS_________###################
                    #########################################################
                    if general_config["logs"]:
                        logs_11.text = f"Step Size = {step}"
                    else:
                        logs_11.setAutoDraw(False)
                    
                    dots_white_2.setAutoDraw(False)
                    dots_black_2.setAutoDraw(False)
                    
                    # *key_resp_15* updates
                    waitOnFlip = False
                    
                    # if key_resp_15 is starting this frame...
                    if key_resp_15.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_15.frameNStart = frameN  # exact frame index
                        key_resp_15.tStart = t  # local t and not account for scr refresh
                        key_resp_15.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_15, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'key_resp_15.started')
                        # update status
                        key_resp_15.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_15.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_15.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_15.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_15.getKeys(keyList=['s','n'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_15_allKeys.extend(theseKeys)
                        if len(_key_resp_15_allKeys):
                            key_resp_15.keys = _key_resp_15_allKeys[-1].name  # just the last key pressed
                            key_resp_15.rt = _key_resp_15_allKeys[-1].rt
                            key_resp_15.duration = _key_resp_15_allKeys[-1].duration
                    
                    # *logs_11* updates
                    
                    # if logs_11 is starting this frame...
                    if logs_11.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logs_11.frameNStart = frameN  # exact frame index
                        logs_11.tStart = t  # local t and not account for scr refresh
                        logs_11.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logs_11, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'logs_11.started')
                        # update status
                        logs_11.status = STARTED
                        logs_11.setAutoDraw(True)
                    
                    # if logs_11 is active this frame...
                    if logs_11.status == STARTED:
                        # update params
                        pass
                    
                    # *image_2* updates
                    
                    # if image_2 is starting this frame...
                    if image_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        image_2.frameNStart = frameN  # exact frame index
                        image_2.tStart = t  # local t and not account for scr refresh
                        image_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(image_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'image_2.started')
                        # update status
                        image_2.status = STARTED
                        image_2.setAutoDraw(True)
                    
                    # if image_2 is active this frame...
                    if image_2.status == STARTED:
                        # update params
                        image_2.setImage('./images/custom_stim.png', log=False)
                    
                    # *dots_white_2* updates
                    
                    # if dots_white_2 is starting this frame...
                    if dots_white_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        dots_white_2.frameNStart = frameN  # exact frame index
                        dots_white_2.tStart = t  # local t and not account for scr refresh
                        dots_white_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(dots_white_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'dots_white_2.started')
                        # update status
                        dots_white_2.status = STARTED
                        dots_white_2.setAutoDraw(True)
                    
                    # if dots_white_2 is active this frame...
                    if dots_white_2.status == STARTED:
                        # update params
                        pass
                    
                    # *dots_black_2* updates
                    
                    # if dots_black_2 is starting this frame...
                    if dots_black_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        dots_black_2.frameNStart = frameN  # exact frame index
                        dots_black_2.tStart = t  # local t and not account for scr refresh
                        dots_black_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(dots_black_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        dots_black_2.status = STARTED
                        dots_black_2.setAutoDraw(True)
                    
                    # if dots_black_2 is active this frame...
                    if dots_black_2.status == STARTED:
                        # update params
                        pass
                    
                    # *key_resp_21* updates
                    waitOnFlip = False
                    
                    # if key_resp_21 is starting this frame...
                    if key_resp_21.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_21.frameNStart = frameN  # exact frame index
                        key_resp_21.tStart = t  # local t and not account for scr refresh
                        key_resp_21.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_21, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'key_resp_21.started')
                        # update status
                        key_resp_21.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_21.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_21.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_21.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_21.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_21_allKeys.extend(theseKeys)
                        if len(_key_resp_21_allKeys):
                            key_resp_21.keys = _key_resp_21_allKeys[-1].name  # just the last key pressed
                            key_resp_21.rt = _key_resp_21_allKeys[-1].rt
                            key_resp_21.duration = _key_resp_21_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        COLOR_STAIRCASE_TEST.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in COLOR_STAIRCASE_TEST.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "COLOR_STAIRCASE_TEST" ---
                for thisComponent in COLOR_STAIRCASE_TEST.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for COLOR_STAIRCASE_TEST
                COLOR_STAIRCASE_TEST.tStop = globalClock.getTime(format='float')
                COLOR_STAIRCASE_TEST.tStopRefresh = tThisFlipGlobal
                thisExp.addData('COLOR_STAIRCASE_TEST.stopped', COLOR_STAIRCASE_TEST.tStop)
                # check responses
                if key_resp_15.keys in ['', [], None]:  # No response was made
                    key_resp_15.keys = None
                colors_to_test.addData('key_resp_15.keys',key_resp_15.keys)
                if key_resp_15.keys != None:  # we had a response
                    colors_to_test.addData('key_resp_15.rt', key_resp_15.rt)
                    colors_to_test.addData('key_resp_15.duration', key_resp_15.duration)
                # check responses
                if key_resp_21.keys in ['', [], None]:  # No response was made
                    key_resp_21.keys = None
                colors_to_test.addData('key_resp_21.keys',key_resp_21.keys)
                if key_resp_21.keys != None:  # we had a response
                    colors_to_test.addData('key_resp_21.rt', key_resp_21.rt)
                    colors_to_test.addData('key_resp_21.duration', key_resp_21.duration)
                # the Routine "COLOR_STAIRCASE_TEST" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
            # completed 1.0 repeats of 'colors_to_test'
            
            thisExp.nextEntry()
            
        # completed modules["module_1"]["tests"]["pretest"]["selected"] repeats of 'MODULE_1_PRETEST'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if MODULE_1_PRETEST.trialList in ([], [None], None):
            params = []
        else:
            params = MODULE_1_PRETEST.trialList[0].keys()
        # save data for this loop
        MODULE_1_PRETEST.saveAsExcel(filename + '.xlsx', sheetName='MODULE_1_PRETEST',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        
        # --- Prepare to start Routine "LOAD_THRESHOLDS" ---
        # create an object to store info about Routine LOAD_THRESHOLDS
        LOAD_THRESHOLDS = data.Routine(
            name='LOAD_THRESHOLDS',
            components=[],
        )
        LOAD_THRESHOLDS.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        # Run 'Begin Routine' code from code_22
        import tkinter as tk
        from tkinter import messagebox
        import json
        
        # Llamada a la función
        threshold_dict = load_thresholds_from_json()
        
        # Manejo del resultado
        if threshold_dict == -1:
            # Crear ventana para manejar el caso de archivo no encontrado
            root = tk.Tk()
            root.withdraw()
            use_defaults = messagebox.askyesno(
                "Archivo no encontrado",
                "No se encontró el archivo de umbrales. ¿Desea usar valores por defecto?"
            )
            root.destroy()
            
            if use_defaults:
                # Valores por defecto
                threshold_dict = {
                    "spatial_frequency_threshold": 100,
                    "flicker_threshold": 50,
                    "contrast_threshold": 0.01,
                    "color_threshold": {
                        "green": 25,
                        "red": 25
                    }
                }
                print("Usando valores por defecto.")
            else:
                raise FileNotFoundError("El archivo de umbrales no se encontró y no se aceptaron valores por defecto.")
        
        else:
            # Mostrar los valores cargados en una ventana
            root = tk.Tk()
            root.withdraw()
            values = "\n".join([f"{key}: {value}" for key, value in threshold_dict.items()])
            messagebox.showinfo(
                f"Se cargaron los siguientes valores para el usuario {expInfo['participant']}:\n\n{values}\nSe ha establecido la siguiente configuración: {general_config}"
            )
            root.destroy()
        
        # Ahora `threshold_dict` contiene los valores seleccionados o los cargados
        print(threshold_dict)
        
        # store start times for LOAD_THRESHOLDS
        LOAD_THRESHOLDS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        LOAD_THRESHOLDS.tStart = globalClock.getTime(format='float')
        LOAD_THRESHOLDS.status = STARTED
        thisExp.addData('LOAD_THRESHOLDS.started', LOAD_THRESHOLDS.tStart)
        LOAD_THRESHOLDS.maxDuration = None
        # keep track of which components have finished
        LOAD_THRESHOLDSComponents = LOAD_THRESHOLDS.components
        for thisComponent in LOAD_THRESHOLDS.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "LOAD_THRESHOLDS" ---
        # if trial has changed, end Routine now
        if isinstance(MODULE_1, data.TrialHandler2) and thisMODULE_1.thisN != MODULE_1.thisTrial.thisN:
            continueRoutine = False
        LOAD_THRESHOLDS.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer], 
                    playbackComponents=[]
                )
                # skip the frame we paused on
                continue
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                LOAD_THRESHOLDS.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in LOAD_THRESHOLDS.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "LOAD_THRESHOLDS" ---
        for thisComponent in LOAD_THRESHOLDS.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for LOAD_THRESHOLDS
        LOAD_THRESHOLDS.tStop = globalClock.getTime(format='float')
        LOAD_THRESHOLDS.tStopRefresh = tThisFlipGlobal
        thisExp.addData('LOAD_THRESHOLDS.stopped', LOAD_THRESHOLDS.tStop)
        # the Routine "LOAD_THRESHOLDS" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
        
        # set up handler to look after randomisation of conditions etc
        MODULE_1_TEST_1 = data.TrialHandler2(
            name='MODULE_1_TEST_1',
            nReps=modules["module_1"]["tests"]["test_1"]["selected"], 
            method='sequential', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=[None], 
            seed=None, 
        )
        thisExp.addLoop(MODULE_1_TEST_1)  # add the loop to the experiment
        thisMODULE_1_TEST_1 = MODULE_1_TEST_1.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_1_TEST_1.rgb)
        if thisMODULE_1_TEST_1 != None:
            for paramName in thisMODULE_1_TEST_1:
                globals()[paramName] = thisMODULE_1_TEST_1[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisMODULE_1_TEST_1 in MODULE_1_TEST_1:
            currentLoop = MODULE_1_TEST_1
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisMODULE_1_TEST_1.rgb)
            if thisMODULE_1_TEST_1 != None:
                for paramName in thisMODULE_1_TEST_1:
                    globals()[paramName] = thisMODULE_1_TEST_1[paramName]
            
            # set up handler to look after randomisation of conditions etc
            BL1_instructions = data.TrialHandler2(
                name='BL1_instructions',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/BL1_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(BL1_instructions)  # add the loop to the experiment
            thisBL1_instruction = BL1_instructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisBL1_instruction.rgb)
            if thisBL1_instruction != None:
                for paramName in thisBL1_instruction:
                    globals()[paramName] = thisBL1_instruction[paramName]
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            
            for thisBL1_instruction in BL1_instructions:
                currentLoop = BL1_instructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                if thisSession is not None:
                    # if running in a Session with a Liaison client, send data up to now
                    thisSession.sendExperimentData()
                # abbreviate parameter names if possible (e.g. rgb = thisBL1_instruction.rgb)
                if thisBL1_instruction != None:
                    for paramName in thisBL1_instruction:
                        globals()[paramName] = thisBL1_instruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(BL1_instructions, data.TrialHandler2) and thisBL1_instruction.thisN != BL1_instructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                BL1_instructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   BL1_instructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   BL1_instructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   BL1_instructions.addData('button_next_instruction_2.timesOn', "")
                   BL1_instructions.addData('button_next_instruction_2.timesOff', "")
                BL1_instructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   BL1_instructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   BL1_instructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   BL1_instructions.addData('button_previous_instruction_2.timesOn', "")
                   BL1_instructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                BL1_instructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    BL1_instructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    BL1_instructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
                thisExp.nextEntry()
                
            # completed 1.0 repeats of 'BL1_instructions'
            
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # get names of stimulus parameters
            if BL1_instructions.trialList in ([], [None], None):
                params = []
            else:
                params = BL1_instructions.trialList[0].keys()
            # save data for this loop
            BL1_instructions.saveAsExcel(filename + '.xlsx', sheetName='BL1_instructions',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            
            # set up handler to look after randomisation of conditions etc
            trials_bl_1 = data.TrialHandler2(
                name='trials_bl_1',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('BL1.csv'), 
                seed=None, 
            )
            thisExp.addLoop(trials_bl_1)  # add the loop to the experiment
            thisTrials_bl_1 = trials_bl_1.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisTrials_bl_1.rgb)
            if thisTrials_bl_1 != None:
                for paramName in thisTrials_bl_1:
                    globals()[paramName] = thisTrials_bl_1[paramName]
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            
            for thisTrials_bl_1 in trials_bl_1:
                currentLoop = trials_bl_1
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                if thisSession is not None:
                    # if running in a Session with a Liaison client, send data up to now
                    thisSession.sendExperimentData()
                # abbreviate parameter names if possible (e.g. rgb = thisTrials_bl_1.rgb)
                if thisTrials_bl_1 != None:
                    for paramName in thisTrials_bl_1:
                        globals()[paramName] = thisTrials_bl_1[paramName]
                
                # --- Prepare to start Routine "BL_1_SPATIAL_FREQ" ---
                # create an object to store info about Routine BL_1_SPATIAL_FREQ
                BL_1_SPATIAL_FREQ = data.Routine(
                    name='BL_1_SPATIAL_FREQ',
                    components=[dots_black_5, dots_white_5, stim, key_resp, logs_background_2, logs, logs_parametros_trial, feedback_txt],
                )
                BL_1_SPATIAL_FREQ.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                dots_black_5.refreshDots()
                dots_white_5.refreshDots()
                stim.setColor([1,1,1], colorSpace='rgb')
                stim.setContrast(1.0)
                stim.setPos((stim_x, stim_y))
                stim.setSize(grating_size)
                # create starting attributes for key_resp
                key_resp.keys = []
                key_resp.rt = []
                _key_resp_allKeys = []
                # Run 'Begin Routine' code from code
                ####################################################
                ########____LOAD STAIRCASE TEST RESULTS____#########
                ####################################################
                #threshold_dict = load_thresholds_from_json()
                spatial_frequency_threshold = threshold_dict['spatial_frequency_threshold']
                
                
                ####################################################
                ###############____PARAMS CONFIG____################
                ####################################################
                posicion_estimulo = stim_x, stim_y = calcular_posicion_stim(posicion_angular, excentricidad, dim_y)
                diametros_central_periferica = calculate_diameter(9, 0.65, dim_y)
                diametros_estimulo = calculate_diameter(excentricidad, 0.65, dim_y)
                
                stim.sf = spatial_frequency_threshold + spatial_frequency_threshold*offset_porcentual/100
                stim.ori = orientacion
                
                
                #other
                
                gaze_position = mouse.getPosition()
                
                logs_parametros_trial.alignText='left'
                logs_parametros_trial.anchorHoriz='left'
                
                event.clearEvents()
                
                first_frame             = True
                flag_skip_all           = False
                flag_answer_registered  = False
                success                 = -1
                undecided               = False
                
                logs.setAutoDraw(False)
                logs_parametros_trial.setAutoDraw(False)
                logs_background_2.setAutoDraw(False)
                # store start times for BL_1_SPATIAL_FREQ
                BL_1_SPATIAL_FREQ.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                BL_1_SPATIAL_FREQ.tStart = globalClock.getTime(format='float')
                BL_1_SPATIAL_FREQ.status = STARTED
                thisExp.addData('BL_1_SPATIAL_FREQ.started', BL_1_SPATIAL_FREQ.tStart)
                BL_1_SPATIAL_FREQ.maxDuration = None
                # keep track of which components have finished
                BL_1_SPATIAL_FREQComponents = BL_1_SPATIAL_FREQ.components
                for thisComponent in BL_1_SPATIAL_FREQ.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "BL_1_SPATIAL_FREQ" ---
                # if trial has changed, end Routine now
                if isinstance(trials_bl_1, data.TrialHandler2) and thisTrials_bl_1.thisN != trials_bl_1.thisTrial.thisN:
                    continueRoutine = False
                BL_1_SPATIAL_FREQ.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *dots_black_5* updates
                    
                    # if dots_black_5 is starting this frame...
                    if dots_black_5.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        dots_black_5.frameNStart = frameN  # exact frame index
                        dots_black_5.tStart = t  # local t and not account for scr refresh
                        dots_black_5.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(dots_black_5, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        dots_black_5.status = STARTED
                        dots_black_5.setAutoDraw(True)
                    
                    # if dots_black_5 is active this frame...
                    if dots_black_5.status == STARTED:
                        # update params
                        pass
                    
                    # *dots_white_5* updates
                    
                    # if dots_white_5 is starting this frame...
                    if dots_white_5.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        dots_white_5.frameNStart = frameN  # exact frame index
                        dots_white_5.tStart = t  # local t and not account for scr refresh
                        dots_white_5.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(dots_white_5, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        dots_white_5.status = STARTED
                        dots_white_5.setAutoDraw(True)
                    
                    # if dots_white_5 is active this frame...
                    if dots_white_5.status == STARTED:
                        # update params
                        pass
                    
                    # *stim* updates
                    
                    # if stim is starting this frame...
                    if stim.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        stim.frameNStart = frameN  # exact frame index
                        stim.tStart = t  # local t and not account for scr refresh
                        stim.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(stim, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        stim.status = STARTED
                        stim.setAutoDraw(True)
                    
                    # if stim is active this frame...
                    if stim.status == STARTED:
                        # update params
                        pass
                    
                    # *key_resp* updates
                    
                    # if key_resp is starting this frame...
                    if key_resp.status == NOT_STARTED and t >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp.frameNStart = frameN  # exact frame index
                        key_resp.tStart = t  # local t and not account for scr refresh
                        key_resp.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp.status = STARTED
                        # keyboard checking is just starting
                        key_resp.clock.reset()  # now t=0
                    if key_resp.status == STARTED:
                        theseKeys = key_resp.getKeys(keyList=['space', 'right', 'left', 'down'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_allKeys.extend(theseKeys)
                        if len(_key_resp_allKeys):
                            key_resp.keys = _key_resp_allKeys[-1].name  # just the last key pressed
                            key_resp.rt = _key_resp_allKeys[-1].rt
                            key_resp.duration = _key_resp_allKeys[-1].duration
                    
                    # *logs_background_2* updates
                    
                    # if logs_background_2 is starting this frame...
                    if logs_background_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logs_background_2.frameNStart = frameN  # exact frame index
                        logs_background_2.tStart = t  # local t and not account for scr refresh
                        logs_background_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logs_background_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logs_background_2.status = STARTED
                        logs_background_2.setAutoDraw(True)
                    
                    # if logs_background_2 is active this frame...
                    if logs_background_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logs* updates
                    
                    # if logs is starting this frame...
                    if logs.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logs.frameNStart = frameN  # exact frame index
                        logs.tStart = t  # local t and not account for scr refresh
                        logs.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logs, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'logs.started')
                        # update status
                        logs.status = STARTED
                        logs.setAutoDraw(True)
                    
                    # if logs is active this frame...
                    if logs.status == STARTED:
                        # update params
                        pass
                    
                    # *logs_parametros_trial* updates
                    
                    # if logs_parametros_trial is starting this frame...
                    if logs_parametros_trial.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logs_parametros_trial.frameNStart = frameN  # exact frame index
                        logs_parametros_trial.tStart = t  # local t and not account for scr refresh
                        logs_parametros_trial.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logs_parametros_trial, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logs_parametros_trial.status = STARTED
                        logs_parametros_trial.setAutoDraw(True)
                    
                    # if logs_parametros_trial is active this frame...
                    if logs_parametros_trial.status == STARTED:
                        # update params
                        pass
                    
                    # *feedback_txt* updates
                    
                    # if feedback_txt is starting this frame...
                    if feedback_txt.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        feedback_txt.frameNStart = frameN  # exact frame index
                        feedback_txt.tStart = t  # local t and not account for scr refresh
                        feedback_txt.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(feedback_txt, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'feedback_txt.started')
                        # update status
                        feedback_txt.status = STARTED
                        feedback_txt.setAutoDraw(True)
                    
                    # if feedback_txt is active this frame...
                    if feedback_txt.status == STARTED:
                        # update params
                        pass
                    # Run 'Each Frame' code from code
                    ####################################################
                    ##############____ON SCREEN LOGS____################
                    ####################################################
                    #gaze_position = mouse.getPosition()
                    #logs_coordenadas_mirada.setText(f'{gaze_position[0]:.2f},{gaze_position[1]:.2f}')
                    
                    if general_config["logs"]:
                        logs_parametros_trial.setText(
                            f"Prueba 1 - Frecuencia espacial\n"
                            f"Intento: {intento}\n"
                            f"Orientación: {orientacion:.2f}\n"
                            f"Excentricidad: {excentricidad}º\n"
                            f"Posicion Estimulo: ({posicion_estimulo[0]:.2f}, {posicion_estimulo[1]:.2f})\n"
                            f"Tamaño Estímulo: {grating_size[0]:.2f}\n"
                            f"Tipo: {tipo}\n"
                            f"Umbral frecuencia espacial: {spatial_frequency_threshold:.2f}\n"
                            f"Offset aplicado: {offset_porcentual}\n"
                            f"SF mostrado: {spatial_frequency_threshold + spatial_frequency_threshold*offset_porcentual/100:.2f}" 
                        )
                    else:
                        logs.setAutoDraw(False)
                        logs_parametros_trial.setAutoDraw(False)
                        logs_background_2.setAutoDraw(False)
                    
                    ####################################################
                    ##########____GAZE VS REGION POSITION____###########
                    ####################################################
                    # Calcula la distancia del ratón al centro de foveal_region
                    #dist_from_center = ((gaze_position[0] - foveal_region_pos[0])**2 + (gaze_position[1] - foveal_region_pos[1])**2)**0.5
                    
                    # Comprueba si la distancia es menor que el radio de foveal_region
                    #if dist_from_center <= 0.25/2:#foveal_region.radius:
                    #    logs.setText("La mirada está dentro de la región")
                    
                    #else:
                    #    logs.setText("La mirada está fuera de la región")  
                    
                    ####################################################
                    ##############____EVENTS & STATES____###############
                    ####################################################
                        
                    flag_skip_all           = False
                    flag_answer_registered  = False
                    undecided               = False
                    success                 = -1
                    
                    # TODO: pasar a funcion
                    
                    keys = event.getKeys()
                    if 'space' in keys:
                        flag_skip_all = True
                        
                    elif 'right' in keys and orientacion == 45: # Acierto:
                        flag_answer_registered  = True
                        success                 = True
                    elif 'left' in keys and orientacion == 135: # Acierto:
                        flag_answer_registered  = True
                        success                 = True
                    elif 'right' in keys or 'left' in keys: # Respuesta incorrecta
                        flag_answer_registered  = True
                        success                 = False
                    elif 'down' in keys: # NS/NC
                        flag_answer_registered  = True
                        success                 = False
                        undecided               = True
                    
                    ####################################################
                    ###############____TIME & NOISE____#################
                    ####################################################
                    
                    if first_frame: # Ejecucion unica
                        dots_white_5.setAutoDraw(False)
                        dots_black_5.setAutoDraw(False)
                        first_time = False
                    
                    if (t>stim_time) or flag_answer_registered: # time exceeded OR answer registered
                        # SHOW RESULTS IF FEEDBACK ACTIVATED
                        if FEEDBACK:
                                print(f"El resultado es: {success}")
                                show_feedback(feedback_txt, success)
                        # SHOW NOISE
                        stim.setAutoDraw(False)
                        show_noise(dots_white_5, dots_black_5, response_time, orientacion, feedback_txt) #only one call
                        continueRoutine = False
                        
                    if flag_skip_all:
                        print("Se ha omitido el bloque BL_1 por activación del flag")
                        trials_bl_1.finished = True
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        BL_1_SPATIAL_FREQ.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in BL_1_SPATIAL_FREQ.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "BL_1_SPATIAL_FREQ" ---
                for thisComponent in BL_1_SPATIAL_FREQ.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for BL_1_SPATIAL_FREQ
                BL_1_SPATIAL_FREQ.tStop = globalClock.getTime(format='float')
                BL_1_SPATIAL_FREQ.tStopRefresh = tThisFlipGlobal
                thisExp.addData('BL_1_SPATIAL_FREQ.stopped', BL_1_SPATIAL_FREQ.tStop)
                # check responses
                if key_resp.keys in ['', [], None]:  # No response was made
                    key_resp.keys = None
                trials_bl_1.addData('key_resp.keys',key_resp.keys)
                if key_resp.keys != None:  # we had a response
                    trials_bl_1.addData('key_resp.rt', key_resp.rt)
                    trials_bl_1.addData('key_resp.duration', key_resp.duration)
                # the Routine "BL_1_SPATIAL_FREQ" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
                thisExp.nextEntry()
                
            # completed 1.0 repeats of 'trials_bl_1'
            
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # get names of stimulus parameters
            if trials_bl_1.trialList in ([], [None], None):
                params = []
            else:
                params = trials_bl_1.trialList[0].keys()
            # save data for this loop
            trials_bl_1.saveAsExcel(filename + '.xlsx', sheetName='trials_bl_1',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            thisExp.nextEntry()
            
        # completed modules["module_1"]["tests"]["test_1"]["selected"] repeats of 'MODULE_1_TEST_1'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if MODULE_1_TEST_1.trialList in ([], [None], None):
            params = []
        else:
            params = MODULE_1_TEST_1.trialList[0].keys()
        # save data for this loop
        MODULE_1_TEST_1.saveAsExcel(filename + '.xlsx', sheetName='MODULE_1_TEST_1',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        
        # set up handler to look after randomisation of conditions etc
        MODULE_1_TEST_2 = data.TrialHandler2(
            name='MODULE_1_TEST_2',
            nReps=modules["module_1"]["tests"]["test_2"]["selected"], 
            method='sequential', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=[None], 
            seed=None, 
        )
        thisExp.addLoop(MODULE_1_TEST_2)  # add the loop to the experiment
        thisMODULE_1_TEST_2 = MODULE_1_TEST_2.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_1_TEST_2.rgb)
        if thisMODULE_1_TEST_2 != None:
            for paramName in thisMODULE_1_TEST_2:
                globals()[paramName] = thisMODULE_1_TEST_2[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisMODULE_1_TEST_2 in MODULE_1_TEST_2:
            currentLoop = MODULE_1_TEST_2
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisMODULE_1_TEST_2.rgb)
            if thisMODULE_1_TEST_2 != None:
                for paramName in thisMODULE_1_TEST_2:
                    globals()[paramName] = thisMODULE_1_TEST_2[paramName]
            
            # set up handler to look after randomisation of conditions etc
            BL2_instructions = data.TrialHandler2(
                name='BL2_instructions',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/BL2_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(BL2_instructions)  # add the loop to the experiment
            thisBL2_instruction = BL2_instructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisBL2_instruction.rgb)
            if thisBL2_instruction != None:
                for paramName in thisBL2_instruction:
                    globals()[paramName] = thisBL2_instruction[paramName]
            
            for thisBL2_instruction in BL2_instructions:
                currentLoop = BL2_instructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                # abbreviate parameter names if possible (e.g. rgb = thisBL2_instruction.rgb)
                if thisBL2_instruction != None:
                    for paramName in thisBL2_instruction:
                        globals()[paramName] = thisBL2_instruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(BL2_instructions, data.TrialHandler2) and thisBL2_instruction.thisN != BL2_instructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                BL2_instructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   BL2_instructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   BL2_instructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   BL2_instructions.addData('button_next_instruction_2.timesOn', "")
                   BL2_instructions.addData('button_next_instruction_2.timesOff', "")
                BL2_instructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   BL2_instructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   BL2_instructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   BL2_instructions.addData('button_previous_instruction_2.timesOn', "")
                   BL2_instructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                BL2_instructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    BL2_instructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    BL2_instructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
            # completed 1.0 repeats of 'BL2_instructions'
            
            
            # set up handler to look after randomisation of conditions etc
            trials_bl_2 = data.TrialHandler2(
                name='trials_bl_2',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('BL2.csv'), 
                seed=None, 
            )
            thisExp.addLoop(trials_bl_2)  # add the loop to the experiment
            thisTrials_bl_2 = trials_bl_2.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisTrials_bl_2.rgb)
            if thisTrials_bl_2 != None:
                for paramName in thisTrials_bl_2:
                    globals()[paramName] = thisTrials_bl_2[paramName]
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            
            for thisTrials_bl_2 in trials_bl_2:
                currentLoop = trials_bl_2
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                if thisSession is not None:
                    # if running in a Session with a Liaison client, send data up to now
                    thisSession.sendExperimentData()
                # abbreviate parameter names if possible (e.g. rgb = thisTrials_bl_2.rgb)
                if thisTrials_bl_2 != None:
                    for paramName in thisTrials_bl_2:
                        globals()[paramName] = thisTrials_bl_2[paramName]
                
                # --- Prepare to start Routine "BL_2_COLOR" ---
                # create an object to store info about Routine BL_2_COLOR
                BL_2_COLOR = data.Routine(
                    name='BL_2_COLOR',
                    components=[dots_black_6, dots_white_6, key_resp_10, logs_background_10, logs_parametros_trial_6, stim_img, feedback_txt_2],
                )
                BL_2_COLOR.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                dots_black_6.refreshDots()
                dots_white_6.refreshDots()
                # create starting attributes for key_resp_10
                key_resp_10.keys = []
                key_resp_10.rt = []
                _key_resp_10_allKeys = []
                stim_img.setImage('./images/custom_stim.png')
                # Run 'Begin Routine' code from code_14
                import math
                import random
                    
                ####################################################
                ########____LOAD STAIRCASE TEST RESULTS____#########
                ####################################################
                #threshold_dict = load_thresholds_from_json()
                frecuencia_espacial = threshold_dict['spatial_frequency_threshold']
                saturation_threshold = threshold_dict['color_threshold'][color_name]
                
                ####################################################
                ###############____PARAMS CONFIG____################
                ####################################################
                posicion_estimulo = stim_x, stim_y = calcular_posicion_stim(posicion_angular, excentricidad, dim_y)
                diametros_central_periferica = calculate_diameter(9, 0.65, dim_y)
                diametros_estimulo = calculate_diameter(excentricidad, 0.65, dim_y)
                
                #stim_6.sf = frecuencia_espacial
                #stim_6.orientation = orientacion
                stim_img.ori = orientacion
                
                #other
                gaze_position = mouse.getPosition()
                
                logs_parametros_trial_6.alignText='left'
                logs_parametros_trial_6.anchorHoriz='left'
                
                event.clearEvents()
                
                first_frame             = True
                flag_skip_all           = False
                flag_answer_registered  = False
                success                 = -1
                undecided               = False
                # Run 'Begin Routine' code from gabor_generator_2
                frequency = frecuencia_espacial/500 # division para equiparar con unidades del parche de psychopy
                
                size = 800
                c1_hsv = [color_1_h,color_1_s,color_1_v] # color del excel
                
                c2_hsv = [color_1_h,
                          min(100, color_1_s + saturation_threshold * umbral_porcentual / 100),# color del excel con modificacion segun umbral sin que supere el valor 100
                          color_1_v]
                
                
                #logs.text = f'freq = {frequency:.2f}\nc1 = ({c1[0]:.2f}, {c1[1]:.2f}, {c1[2]:.2f})\nc2 = ({c2[0]:.2f}, {c2[1]:.2f}, {c2[2]:.2f})'
                # Generar el parche de Gabor
                save_gabor_patch_image(frequency, 
                                       size, 
                                       normalizar_rgb(hsv_a_rgb(*c1_hsv)), 
                                       normalizar_rgb(hsv_a_rgb(*c2_hsv)))
                
                # store start times for BL_2_COLOR
                BL_2_COLOR.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                BL_2_COLOR.tStart = globalClock.getTime(format='float')
                BL_2_COLOR.status = STARTED
                thisExp.addData('BL_2_COLOR.started', BL_2_COLOR.tStart)
                BL_2_COLOR.maxDuration = None
                # keep track of which components have finished
                BL_2_COLORComponents = BL_2_COLOR.components
                for thisComponent in BL_2_COLOR.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "BL_2_COLOR" ---
                # if trial has changed, end Routine now
                if isinstance(trials_bl_2, data.TrialHandler2) and thisTrials_bl_2.thisN != trials_bl_2.thisTrial.thisN:
                    continueRoutine = False
                BL_2_COLOR.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *dots_black_6* updates
                    
                    # if dots_black_6 is starting this frame...
                    if dots_black_6.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        dots_black_6.frameNStart = frameN  # exact frame index
                        dots_black_6.tStart = t  # local t and not account for scr refresh
                        dots_black_6.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(dots_black_6, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        dots_black_6.status = STARTED
                        dots_black_6.setAutoDraw(True)
                    
                    # if dots_black_6 is active this frame...
                    if dots_black_6.status == STARTED:
                        # update params
                        pass
                    
                    # *dots_white_6* updates
                    
                    # if dots_white_6 is starting this frame...
                    if dots_white_6.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        dots_white_6.frameNStart = frameN  # exact frame index
                        dots_white_6.tStart = t  # local t and not account for scr refresh
                        dots_white_6.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(dots_white_6, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'dots_white_6.started')
                        # update status
                        dots_white_6.status = STARTED
                        dots_white_6.setAutoDraw(True)
                    
                    # if dots_white_6 is active this frame...
                    if dots_white_6.status == STARTED:
                        # update params
                        pass
                    
                    # *key_resp_10* updates
                    
                    # if key_resp_10 is starting this frame...
                    if key_resp_10.status == NOT_STARTED and t >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_10.frameNStart = frameN  # exact frame index
                        key_resp_10.tStart = t  # local t and not account for scr refresh
                        key_resp_10.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_10, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_10.status = STARTED
                        # keyboard checking is just starting
                        key_resp_10.clock.reset()  # now t=0
                    if key_resp_10.status == STARTED:
                        theseKeys = key_resp_10.getKeys(keyList=['space', 'right', 'left'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_10_allKeys.extend(theseKeys)
                        if len(_key_resp_10_allKeys):
                            key_resp_10.keys = _key_resp_10_allKeys[-1].name  # just the last key pressed
                            key_resp_10.rt = _key_resp_10_allKeys[-1].rt
                            key_resp_10.duration = _key_resp_10_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # *logs_background_10* updates
                    
                    # if logs_background_10 is starting this frame...
                    if logs_background_10.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logs_background_10.frameNStart = frameN  # exact frame index
                        logs_background_10.tStart = t  # local t and not account for scr refresh
                        logs_background_10.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logs_background_10, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'logs_background_10.started')
                        # update status
                        logs_background_10.status = STARTED
                        logs_background_10.setAutoDraw(True)
                    
                    # if logs_background_10 is active this frame...
                    if logs_background_10.status == STARTED:
                        # update params
                        pass
                    
                    # *logs_parametros_trial_6* updates
                    
                    # if logs_parametros_trial_6 is starting this frame...
                    if logs_parametros_trial_6.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logs_parametros_trial_6.frameNStart = frameN  # exact frame index
                        logs_parametros_trial_6.tStart = t  # local t and not account for scr refresh
                        logs_parametros_trial_6.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logs_parametros_trial_6, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logs_parametros_trial_6.status = STARTED
                        logs_parametros_trial_6.setAutoDraw(True)
                    
                    # if logs_parametros_trial_6 is active this frame...
                    if logs_parametros_trial_6.status == STARTED:
                        # update params
                        pass
                    
                    # *stim_img* updates
                    
                    # if stim_img is starting this frame...
                    if stim_img.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        stim_img.frameNStart = frameN  # exact frame index
                        stim_img.tStart = t  # local t and not account for scr refresh
                        stim_img.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(stim_img, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'stim_img.started')
                        # update status
                        stim_img.status = STARTED
                        stim_img.setAutoDraw(True)
                    
                    # if stim_img is active this frame...
                    if stim_img.status == STARTED:
                        # update params
                        pass
                    
                    # *feedback_txt_2* updates
                    
                    # if feedback_txt_2 is starting this frame...
                    if feedback_txt_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        feedback_txt_2.frameNStart = frameN  # exact frame index
                        feedback_txt_2.tStart = t  # local t and not account for scr refresh
                        feedback_txt_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(feedback_txt_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'feedback_txt_2.started')
                        # update status
                        feedback_txt_2.status = STARTED
                        feedback_txt_2.setAutoDraw(True)
                    
                    # if feedback_txt_2 is active this frame...
                    if feedback_txt_2.status == STARTED:
                        # update params
                        pass
                    # Run 'Each Frame' code from code_14
                    ####################################################
                    ##############____ON SCREEN LOGS____################
                    ####################################################
                    #gaze_position = mouse.getPosition()
                    #logs_coordenadas_mirada_6.setText(f'{gaze_position[0]:.2f},{gaze_position[1]:.2f}')
                    
                    if general_config["logs"]:
                        logs_parametros_trial_6.setText(
                            f"Prueba 2 - Color/saturación\n"
                            f"Intento: {intento}\n"
                            f"Orientación: {orientacion:.2f}\n"
                            f"Excentricidad: {excentricidad}º\n"
                            f"Posicion Estimulo: ({posicion_estimulo[0]:.2f}, {posicion_estimulo[1]:.2f})\n"
                            f"Tamaño Estímulo: {grating_size[0]:.2f}\n"
                            #f"Tipo: {tipo}\n"
                            f"Offset (%): {umbral_porcentual:.2f}\n"
                            f"Umbral color {color_name}(%): {saturation_threshold:.2f}\n"
                            f"Sat. C1 (%): {color_1_s:.2f}\n"
                            f"Sat. C2 (%): {color_1_s+saturation_threshold + saturation_threshold*umbral_porcentual/100:.2f}\n"
                    )
                    
                    else:
                        logs_parametros_trial_6.setAutoDraw(False)
                        logs_background_10.setAutoDraw(False)
                    
                    ####################################################
                    ##########____GAZE VS REGION POSITION____###########
                    ####################################################
                    # Calcula la distancia del ratón al centro de foveal_region
                    #dist_from_center = ((gaze_position[0] - foveal_region_pos[0])**2 + (gaze_position[1] - foveal_region_pos[1])**2)**0.5
                    
                    # Comprueba si la distancia es menor que el radio de foveal_region
                    #if dist_from_center <= 0.25/2:#foveal_region.radius:
                    #    logs_7.setText("La mirada está dentro de la circunferencia")
                    
                    #else:
                    #    logs_7.setText("La mirada está fuera de la circunferencia")
                    
                    
                    ####################################################
                    ##############____EVENTS & STATES____###############
                    ####################################################
                    flag_skip_all           = False
                    flag_answer_registered  = False
                    undecided               = False
                    success                 = -1
                    
                    keys = event.getKeys()
                    if 'space' in keys:
                        flag_skip_all = True
                        
                    elif 'right' in keys and orientacion == 45: # Acierto:
                        flag_answer_registered  = True
                        success                 = True
                    elif 'left' in keys and orientacion == 135: # Acierto:
                        flag_answer_registered  = True
                        success                 = True
                    elif 'right' in keys or 'left' in keys: # Respuesta incorrecta
                        flag_answer_registered  = True
                        success                 = False
                    elif 'down' in keys: # NS/NC
                        flag_answer_registered  = True
                        success                 = False
                        undecided               = True
                    
                    ####################################################
                    ###############____TIME & NOISE____#################
                    ####################################################
                    
                    if first_frame: # Ejecucion unica
                        dots_white_6.setAutoDraw(False)
                        dots_black_6.setAutoDraw(False)
                        first_time = False
                    
                    if (t>stim_time) or flag_answer_registered: # time exceeded OR answer registered
                        # SHOW RESULTS IF FEEDBACK ACTIVATED
                        if FEEDBACK:
                            print(f"El resultado es: {success}")
                            show_feedback(feedback_txt_2, success)
                         # SHOW NOISE
                        stim_img.setAutoDraw(False)
                        show_noise(dots_white_6, dots_black_6, response_time, orientacion, feedback_txt_2) #only one call
                        continueRoutine = False
                    
                    if flag_skip_all:
                        trials_bl_2.finished = True
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        BL_2_COLOR.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in BL_2_COLOR.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "BL_2_COLOR" ---
                for thisComponent in BL_2_COLOR.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for BL_2_COLOR
                BL_2_COLOR.tStop = globalClock.getTime(format='float')
                BL_2_COLOR.tStopRefresh = tThisFlipGlobal
                thisExp.addData('BL_2_COLOR.stopped', BL_2_COLOR.tStop)
                # check responses
                if key_resp_10.keys in ['', [], None]:  # No response was made
                    key_resp_10.keys = None
                trials_bl_2.addData('key_resp_10.keys',key_resp_10.keys)
                if key_resp_10.keys != None:  # we had a response
                    trials_bl_2.addData('key_resp_10.rt', key_resp_10.rt)
                    trials_bl_2.addData('key_resp_10.duration', key_resp_10.duration)
                # the Routine "BL_2_COLOR" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
                thisExp.nextEntry()
                
            # completed 1.0 repeats of 'trials_bl_2'
            
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # get names of stimulus parameters
            if trials_bl_2.trialList in ([], [None], None):
                params = []
            else:
                params = trials_bl_2.trialList[0].keys()
            # save data for this loop
            trials_bl_2.saveAsExcel(filename + '.xlsx', sheetName='trials_bl_2',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            thisExp.nextEntry()
            
        # completed modules["module_1"]["tests"]["test_2"]["selected"] repeats of 'MODULE_1_TEST_2'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if MODULE_1_TEST_2.trialList in ([], [None], None):
            params = []
        else:
            params = MODULE_1_TEST_2.trialList[0].keys()
        # save data for this loop
        MODULE_1_TEST_2.saveAsExcel(filename + '.xlsx', sheetName='MODULE_1_TEST_2',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        
        # set up handler to look after randomisation of conditions etc
        MODULE_1_TEST_3 = data.TrialHandler2(
            name='MODULE_1_TEST_3',
            nReps=modules["module_1"]["tests"]["test_3"]["selected"], 
            method='random', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=[None], 
            seed=None, 
        )
        thisExp.addLoop(MODULE_1_TEST_3)  # add the loop to the experiment
        thisMODULE_1_TEST_3 = MODULE_1_TEST_3.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_1_TEST_3.rgb)
        if thisMODULE_1_TEST_3 != None:
            for paramName in thisMODULE_1_TEST_3:
                globals()[paramName] = thisMODULE_1_TEST_3[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisMODULE_1_TEST_3 in MODULE_1_TEST_3:
            currentLoop = MODULE_1_TEST_3
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisMODULE_1_TEST_3.rgb)
            if thisMODULE_1_TEST_3 != None:
                for paramName in thisMODULE_1_TEST_3:
                    globals()[paramName] = thisMODULE_1_TEST_3[paramName]
            
            # set up handler to look after randomisation of conditions etc
            BL3_instructions = data.TrialHandler2(
                name='BL3_instructions',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/BL3_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(BL3_instructions)  # add the loop to the experiment
            thisBL3_instruction = BL3_instructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisBL3_instruction.rgb)
            if thisBL3_instruction != None:
                for paramName in thisBL3_instruction:
                    globals()[paramName] = thisBL3_instruction[paramName]
            
            for thisBL3_instruction in BL3_instructions:
                currentLoop = BL3_instructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                # abbreviate parameter names if possible (e.g. rgb = thisBL3_instruction.rgb)
                if thisBL3_instruction != None:
                    for paramName in thisBL3_instruction:
                        globals()[paramName] = thisBL3_instruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(BL3_instructions, data.TrialHandler2) and thisBL3_instruction.thisN != BL3_instructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                BL3_instructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   BL3_instructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   BL3_instructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   BL3_instructions.addData('button_next_instruction_2.timesOn', "")
                   BL3_instructions.addData('button_next_instruction_2.timesOff', "")
                BL3_instructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   BL3_instructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   BL3_instructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   BL3_instructions.addData('button_previous_instruction_2.timesOn', "")
                   BL3_instructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                BL3_instructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    BL3_instructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    BL3_instructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
            # completed 1.0 repeats of 'BL3_instructions'
            
            
            # set up handler to look after randomisation of conditions etc
            trials_bl_3 = data.TrialHandler2(
                name='trials_bl_3',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('BL3.csv'), 
                seed=None, 
            )
            thisExp.addLoop(trials_bl_3)  # add the loop to the experiment
            thisTrials_bl_3 = trials_bl_3.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisTrials_bl_3.rgb)
            if thisTrials_bl_3 != None:
                for paramName in thisTrials_bl_3:
                    globals()[paramName] = thisTrials_bl_3[paramName]
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            
            for thisTrials_bl_3 in trials_bl_3:
                currentLoop = trials_bl_3
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                if thisSession is not None:
                    # if running in a Session with a Liaison client, send data up to now
                    thisSession.sendExperimentData()
                # abbreviate parameter names if possible (e.g. rgb = thisTrials_bl_3.rgb)
                if thisTrials_bl_3 != None:
                    for paramName in thisTrials_bl_3:
                        globals()[paramName] = thisTrials_bl_3[paramName]
                
                # --- Prepare to start Routine "BL_3_CONTRAST" ---
                # create an object to store info about Routine BL_3_CONTRAST
                BL_3_CONTRAST = data.Routine(
                    name='BL_3_CONTRAST',
                    components=[dots_black_7, dots_white_7, stim_5, key_resp_9, logs_background_8, logs_parametros_trial_5, feedback_txt_3],
                )
                BL_3_CONTRAST.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                dots_black_7.refreshDots()
                dots_white_7.refreshDots()
                stim_5.setColor([1,1,1], colorSpace='rgb')
                stim_5.setPos((stim_x, stim_y))
                stim_5.setSize(grating_size)
                # create starting attributes for key_resp_9
                key_resp_9.keys = []
                key_resp_9.rt = []
                _key_resp_9_allKeys = []
                # Run 'Begin Routine' code from code_8
                import math
                import random
                
                ####################################################
                ########____LOAD STAIRCASE TEST RESULTS____#########
                ####################################################
                #threshold_dict = load_thresholds_from_json()
                spatial_frequency_threshold = threshold_dict['spatial_frequency_threshold']
                contrast_threshold = threshold_dict['contrast_threshold']
                
                ####################################################
                ###############____PARAMS CONFIG____################
                ####################################################
                posicion_estimulo = stim_x, stim_y = calcular_posicion_stim(posicion_angular, excentricidad, dim_y)
                diametros_central_periferica = calculate_diameter(9, 0.65, dim_y)
                diametros_estimulo = calculate_diameter(excentricidad, 0.65, dim_y)
                
                stim_5.sf = spatial_frequency_threshold
                stim_5.contrast = contrast_threshold + contrast_threshold*offset_porcentual
                stim_5.ori = orientacion
                
                #other
                gaze_position = mouse.getPosition()
                
                logs_parametros_trial_5.alignText='left'
                logs_parametros_trial_5.anchorHoriz='left'
                event.clearEvents()
                
                first_frame             = True
                flag_skip_all           = False
                flag_answer_registered  = False
                success                 = -1
                undecided               = False
                
                logs_parametros_trial_5.setAutoDraw(False)
                logs_background_8.setAutoDraw(False)
                # store start times for BL_3_CONTRAST
                BL_3_CONTRAST.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                BL_3_CONTRAST.tStart = globalClock.getTime(format='float')
                BL_3_CONTRAST.status = STARTED
                thisExp.addData('BL_3_CONTRAST.started', BL_3_CONTRAST.tStart)
                BL_3_CONTRAST.maxDuration = None
                # keep track of which components have finished
                BL_3_CONTRASTComponents = BL_3_CONTRAST.components
                for thisComponent in BL_3_CONTRAST.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "BL_3_CONTRAST" ---
                # if trial has changed, end Routine now
                if isinstance(trials_bl_3, data.TrialHandler2) and thisTrials_bl_3.thisN != trials_bl_3.thisTrial.thisN:
                    continueRoutine = False
                BL_3_CONTRAST.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *dots_black_7* updates
                    
                    # if dots_black_7 is starting this frame...
                    if dots_black_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        dots_black_7.frameNStart = frameN  # exact frame index
                        dots_black_7.tStart = t  # local t and not account for scr refresh
                        dots_black_7.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(dots_black_7, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        dots_black_7.status = STARTED
                        dots_black_7.setAutoDraw(True)
                    
                    # if dots_black_7 is active this frame...
                    if dots_black_7.status == STARTED:
                        # update params
                        pass
                    
                    # *dots_white_7* updates
                    
                    # if dots_white_7 is starting this frame...
                    if dots_white_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        dots_white_7.frameNStart = frameN  # exact frame index
                        dots_white_7.tStart = t  # local t and not account for scr refresh
                        dots_white_7.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(dots_white_7, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'dots_white_7.started')
                        # update status
                        dots_white_7.status = STARTED
                        dots_white_7.setAutoDraw(True)
                    
                    # if dots_white_7 is active this frame...
                    if dots_white_7.status == STARTED:
                        # update params
                        pass
                    
                    # *stim_5* updates
                    
                    # if stim_5 is starting this frame...
                    if stim_5.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        stim_5.frameNStart = frameN  # exact frame index
                        stim_5.tStart = t  # local t and not account for scr refresh
                        stim_5.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(stim_5, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        stim_5.status = STARTED
                        stim_5.setAutoDraw(True)
                    
                    # if stim_5 is active this frame...
                    if stim_5.status == STARTED:
                        # update params
                        pass
                    
                    # if stim_5 is stopping this frame...
                    if stim_5.status == STARTED:
                        # is it time to stop? (based on global clock, using actual start)
                        if tThisFlipGlobal > stim_5.tStartRefresh + 2-frameTolerance:
                            # keep track of stop time/frame for later
                            stim_5.tStop = t  # not accounting for scr refresh
                            stim_5.tStopRefresh = tThisFlipGlobal  # on global time
                            stim_5.frameNStop = frameN  # exact frame index
                            # update status
                            stim_5.status = FINISHED
                            stim_5.setAutoDraw(False)
                    
                    # *key_resp_9* updates
                    
                    # if key_resp_9 is starting this frame...
                    if key_resp_9.status == NOT_STARTED and t >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_9.frameNStart = frameN  # exact frame index
                        key_resp_9.tStart = t  # local t and not account for scr refresh
                        key_resp_9.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_9, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_9.status = STARTED
                        # keyboard checking is just starting
                        key_resp_9.clock.reset()  # now t=0
                    if key_resp_9.status == STARTED:
                        theseKeys = key_resp_9.getKeys(keyList=['space', 'right', 'left'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_9_allKeys.extend(theseKeys)
                        if len(_key_resp_9_allKeys):
                            key_resp_9.keys = _key_resp_9_allKeys[-1].name  # just the last key pressed
                            key_resp_9.rt = _key_resp_9_allKeys[-1].rt
                            key_resp_9.duration = _key_resp_9_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # *logs_background_8* updates
                    
                    # if logs_background_8 is starting this frame...
                    if logs_background_8.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logs_background_8.frameNStart = frameN  # exact frame index
                        logs_background_8.tStart = t  # local t and not account for scr refresh
                        logs_background_8.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logs_background_8, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'logs_background_8.started')
                        # update status
                        logs_background_8.status = STARTED
                        logs_background_8.setAutoDraw(True)
                    
                    # if logs_background_8 is active this frame...
                    if logs_background_8.status == STARTED:
                        # update params
                        pass
                    
                    # *logs_parametros_trial_5* updates
                    
                    # if logs_parametros_trial_5 is starting this frame...
                    if logs_parametros_trial_5.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logs_parametros_trial_5.frameNStart = frameN  # exact frame index
                        logs_parametros_trial_5.tStart = t  # local t and not account for scr refresh
                        logs_parametros_trial_5.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logs_parametros_trial_5, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logs_parametros_trial_5.status = STARTED
                        logs_parametros_trial_5.setAutoDraw(True)
                    
                    # if logs_parametros_trial_5 is active this frame...
                    if logs_parametros_trial_5.status == STARTED:
                        # update params
                        pass
                    
                    # *feedback_txt_3* updates
                    
                    # if feedback_txt_3 is starting this frame...
                    if feedback_txt_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        feedback_txt_3.frameNStart = frameN  # exact frame index
                        feedback_txt_3.tStart = t  # local t and not account for scr refresh
                        feedback_txt_3.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(feedback_txt_3, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'feedback_txt_3.started')
                        # update status
                        feedback_txt_3.status = STARTED
                        feedback_txt_3.setAutoDraw(True)
                    
                    # if feedback_txt_3 is active this frame...
                    if feedback_txt_3.status == STARTED:
                        # update params
                        pass
                    # Run 'Each Frame' code from code_8
                    ####################################################
                    ##############____ON SCREEN LOGS____################
                    ####################################################
                    #gaze_position = mouse.getPosition()
                    #logs_coordenadas_mirada_5.setText(f'{gaze_position[0]:.2f},{gaze_position[1]:.2f}')
                    
                    if general_config["logs"]:
                        logs_parametros_trial_5.setText(
                            f"Prueba 3 - Contraste\n"
                            f"Intento: {intento}\n"
                            f"Orientación: {orientacion:.2f}\n"
                            f"Excentricidad: {excentricidad}º\n"
                            f"Posicion Estimulo: ({posicion_estimulo[0]:.2f}, {posicion_estimulo[1]:.2f})\n"
                            f"Tamaño Estímulo: {grating_size[0]:.2f}\n"
                            f"Tipo: {tipo}\n"
                            f"Umbral contraste cargado: {contrast_threshold:.2f}\n"
                            f"Offset aplicado: {offset_porcentual}\n"
                            f"Contraste mostrado: {contrast_threshold + contrast_threshold*offset_porcentual/100:.2f}" 
                        )
                    else:
                        logs_parametros_trial_5.setAutoDraw(False)
                        logs_background_8.setAutoDraw(False)
                    
                    
                    ####################################################
                    ##########____GAZE VS REGION POSITION____###########
                    ####################################################
                    # Calcula la distancia del ratón al centro de foveal_region
                    #dist_from_center = ((gaze_position[0] - foveal_region_pos[0])**2 + (gaze_position[1] - foveal_region_pos[1])**2)**0.5
                    
                    # Comprueba si la distancia es menor que el radio de foveal_region
                    #if dist_from_center <= 0.25/2:#foveal_region.radius:
                    #    logs_6.setText("La mirada está dentro de la región")
                    
                    #else:
                    #    logs_6.setText("La mirada está fuera de la región")
                    
                    ####################################################
                    ##############____EVENTS & STATES____###############
                    ####################################################
                    flag_skip_all           = False
                    flag_answer_registered  = False
                    undecided               = False
                    success                 = -1
                    
                    keys = event.getKeys()
                    if 'space' in keys:
                        flag_skip_all = True
                        
                    elif 'right' in keys and orientacion == 45: # Acierto:
                        flag_answer_registered  = True
                        success                 = True
                    elif 'left' in keys and orientacion == 135: # Acierto:
                        flag_answer_registered  = True
                        success                 = True
                    elif 'right' in keys or 'left' in keys: # Respuesta incorrecta
                        flag_answer_registered  = True
                        success                 = False
                    elif 'down' in keys: # NS/NC
                        flag_answer_registered  = True
                        success                 = False
                        undecided               = True
                    
                    ####################################################
                    ###############____TIME & NOISE____#################
                    ####################################################
                    
                    if first_frame: # Ejecucion unica
                        dots_white_7.setAutoDraw(False)
                        dots_black_7.setAutoDraw(False)
                        first_time = False
                    
                    if (t>stim_time) or flag_answer_registered: # time exceeded OR answer registered
                        # SHOW RESULTS IF FEEDBACK ACTIVATED
                        if FEEDBACK:
                            print(f"El resultado es: {success}")
                            show_feedback(feedback_txt_3, success)
                            
                        # SHOW NOISE
                        stim_5.setAutoDraw(False)
                        show_noise(dots_white_7, dots_black_7, response_time, orientacion, feedback_txt_3) #only one call
                        continueRoutine = False
                        
                    if flag_skip_all:
                        trials_bl_3.finished = True
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        BL_3_CONTRAST.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in BL_3_CONTRAST.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "BL_3_CONTRAST" ---
                for thisComponent in BL_3_CONTRAST.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for BL_3_CONTRAST
                BL_3_CONTRAST.tStop = globalClock.getTime(format='float')
                BL_3_CONTRAST.tStopRefresh = tThisFlipGlobal
                thisExp.addData('BL_3_CONTRAST.stopped', BL_3_CONTRAST.tStop)
                # check responses
                if key_resp_9.keys in ['', [], None]:  # No response was made
                    key_resp_9.keys = None
                trials_bl_3.addData('key_resp_9.keys',key_resp_9.keys)
                if key_resp_9.keys != None:  # we had a response
                    trials_bl_3.addData('key_resp_9.rt', key_resp_9.rt)
                    trials_bl_3.addData('key_resp_9.duration', key_resp_9.duration)
                # the Routine "BL_3_CONTRAST" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
                thisExp.nextEntry()
                
            # completed 1.0 repeats of 'trials_bl_3'
            
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # get names of stimulus parameters
            if trials_bl_3.trialList in ([], [None], None):
                params = []
            else:
                params = trials_bl_3.trialList[0].keys()
            # save data for this loop
            trials_bl_3.saveAsExcel(filename + '.xlsx', sheetName='trials_bl_3',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            thisExp.nextEntry()
            
        # completed modules["module_1"]["tests"]["test_3"]["selected"] repeats of 'MODULE_1_TEST_3'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if MODULE_1_TEST_3.trialList in ([], [None], None):
            params = []
        else:
            params = MODULE_1_TEST_3.trialList[0].keys()
        # save data for this loop
        MODULE_1_TEST_3.saveAsExcel(filename + '.xlsx', sheetName='MODULE_1_TEST_3',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        
        # set up handler to look after randomisation of conditions etc
        trials_bl_4 = data.TrialHandler2(
            name='trials_bl_4',
            nReps=1.0, 
            method='sequential', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=data.importConditions('BL4.csv'), 
            seed=None, 
        )
        thisExp.addLoop(trials_bl_4)  # add the loop to the experiment
        thisTrials_bl_4 = trials_bl_4.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisTrials_bl_4.rgb)
        if thisTrials_bl_4 != None:
            for paramName in thisTrials_bl_4:
                globals()[paramName] = thisTrials_bl_4[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisTrials_bl_4 in trials_bl_4:
            currentLoop = trials_bl_4
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisTrials_bl_4.rgb)
            if thisTrials_bl_4 != None:
                for paramName in thisTrials_bl_4:
                    globals()[paramName] = thisTrials_bl_4[paramName]
            thisExp.nextEntry()
            
        # completed 1.0 repeats of 'trials_bl_4'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if trials_bl_4.trialList in ([], [None], None):
            params = []
        else:
            params = trials_bl_4.trialList[0].keys()
        # save data for this loop
        trials_bl_4.saveAsExcel(filename + '.xlsx', sheetName='trials_bl_4',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        
        # set up handler to look after randomisation of conditions etc
        trials_bl_5 = data.TrialHandler2(
            name='trials_bl_5',
            nReps=1.0, 
            method='random', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=data.importConditions('BL5.csv'), 
            seed=None, 
        )
        thisExp.addLoop(trials_bl_5)  # add the loop to the experiment
        thisTrials_bl_5 = trials_bl_5.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisTrials_bl_5.rgb)
        if thisTrials_bl_5 != None:
            for paramName in thisTrials_bl_5:
                globals()[paramName] = thisTrials_bl_5[paramName]
        
        for thisTrials_bl_5 in trials_bl_5:
            currentLoop = trials_bl_5
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            # abbreviate parameter names if possible (e.g. rgb = thisTrials_bl_5.rgb)
            if thisTrials_bl_5 != None:
                for paramName in thisTrials_bl_5:
                    globals()[paramName] = thisTrials_bl_5[paramName]
        # completed 1.0 repeats of 'trials_bl_5'
        
        
        # set up handler to look after randomisation of conditions etc
        trials_bl_7 = data.TrialHandler2(
            name='trials_bl_7',
            nReps=1.0, 
            method='sequential', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=data.importConditions('BL7.csv'), 
            seed=None, 
        )
        thisExp.addLoop(trials_bl_7)  # add the loop to the experiment
        thisTrials_bl_7 = trials_bl_7.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisTrials_bl_7.rgb)
        if thisTrials_bl_7 != None:
            for paramName in thisTrials_bl_7:
                globals()[paramName] = thisTrials_bl_7[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisTrials_bl_7 in trials_bl_7:
            currentLoop = trials_bl_7
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisTrials_bl_7.rgb)
            if thisTrials_bl_7 != None:
                for paramName in thisTrials_bl_7:
                    globals()[paramName] = thisTrials_bl_7[paramName]
            thisExp.nextEntry()
            
        # completed 1.0 repeats of 'trials_bl_7'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if trials_bl_7.trialList in ([], [None], None):
            params = []
        else:
            params = trials_bl_7.trialList[0].keys()
        # save data for this loop
        trials_bl_7.saveAsExcel(filename + '.xlsx', sheetName='trials_bl_7',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
    # completed modules["module_1"]["selected"] repeats of 'MODULE_1'
    
    
    # set up handler to look after randomisation of conditions etc
    MODULE_2 = data.TrialHandler2(
        name='MODULE_2',
        nReps=modules["module_2"]["selected"], 
        method='sequential', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=[None], 
        seed=None, 
    )
    thisExp.addLoop(MODULE_2)  # add the loop to the experiment
    thisMODULE_2 = MODULE_2.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisMODULE_2.rgb)
    if thisMODULE_2 != None:
        for paramName in thisMODULE_2:
            globals()[paramName] = thisMODULE_2[paramName]
    
    for thisMODULE_2 in MODULE_2:
        currentLoop = MODULE_2
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_2.rgb)
        if thisMODULE_2 != None:
            for paramName in thisMODULE_2:
                globals()[paramName] = thisMODULE_2[paramName]
        
        # set up handler to look after randomisation of conditions etc
        MODULE_2_TEST_1 = data.TrialHandler2(
            name='MODULE_2_TEST_1',
            nReps=modules["module_2"]["tests"]["test_1"]["selected"], 
            method='sequential', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=[None], 
            seed=None, 
        )
        thisExp.addLoop(MODULE_2_TEST_1)  # add the loop to the experiment
        thisMODULE_2_TEST_1 = MODULE_2_TEST_1.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_2_TEST_1.rgb)
        if thisMODULE_2_TEST_1 != None:
            for paramName in thisMODULE_2_TEST_1:
                globals()[paramName] = thisMODULE_2_TEST_1[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisMODULE_2_TEST_1 in MODULE_2_TEST_1:
            currentLoop = MODULE_2_TEST_1
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisMODULE_2_TEST_1.rgb)
            if thisMODULE_2_TEST_1 != None:
                for paramName in thisMODULE_2_TEST_1:
                    globals()[paramName] = thisMODULE_2_TEST_1[paramName]
            
            # set up handler to look after randomisation of conditions etc
            et_resting_state_instructions = data.TrialHandler2(
                name='et_resting_state_instructions',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/et_resting_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(et_resting_state_instructions)  # add the loop to the experiment
            thisEt_resting_state_instruction = et_resting_state_instructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisEt_resting_state_instruction.rgb)
            if thisEt_resting_state_instruction != None:
                for paramName in thisEt_resting_state_instruction:
                    globals()[paramName] = thisEt_resting_state_instruction[paramName]
            
            for thisEt_resting_state_instruction in et_resting_state_instructions:
                currentLoop = et_resting_state_instructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                # abbreviate parameter names if possible (e.g. rgb = thisEt_resting_state_instruction.rgb)
                if thisEt_resting_state_instruction != None:
                    for paramName in thisEt_resting_state_instruction:
                        globals()[paramName] = thisEt_resting_state_instruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(et_resting_state_instructions, data.TrialHandler2) and thisEt_resting_state_instruction.thisN != et_resting_state_instructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                et_resting_state_instructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   et_resting_state_instructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   et_resting_state_instructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   et_resting_state_instructions.addData('button_next_instruction_2.timesOn', "")
                   et_resting_state_instructions.addData('button_next_instruction_2.timesOff', "")
                et_resting_state_instructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   et_resting_state_instructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   et_resting_state_instructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   et_resting_state_instructions.addData('button_previous_instruction_2.timesOn', "")
                   et_resting_state_instructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                et_resting_state_instructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    et_resting_state_instructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    et_resting_state_instructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
            # completed 1.0 repeats of 'et_resting_state_instructions'
            
            
            # --- Prepare to start Routine "ET_RESTING_STATE" ---
            # create an object to store info about Routine ET_RESTING_STATE
            ET_RESTING_STATE = data.Routine(
                name='ET_RESTING_STATE',
                components=[text_3, key_resp_8],
            )
            ET_RESTING_STATE.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            # Run 'Begin Routine' code from code_13
            win.color = eye_tracking_resting_state_background_color
            
            last_second = None
            # create starting attributes for key_resp_8
            key_resp_8.keys = []
            key_resp_8.rt = []
            _key_resp_8_allKeys = []
            # store start times for ET_RESTING_STATE
            ET_RESTING_STATE.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            ET_RESTING_STATE.tStart = globalClock.getTime(format='float')
            ET_RESTING_STATE.status = STARTED
            thisExp.addData('ET_RESTING_STATE.started', ET_RESTING_STATE.tStart)
            ET_RESTING_STATE.maxDuration = None
            # keep track of which components have finished
            ET_RESTING_STATEComponents = ET_RESTING_STATE.components
            for thisComponent in ET_RESTING_STATE.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "ET_RESTING_STATE" ---
            # if trial has changed, end Routine now
            if isinstance(MODULE_2_TEST_1, data.TrialHandler2) and thisMODULE_2_TEST_1.thisN != MODULE_2_TEST_1.thisTrial.thisN:
                continueRoutine = False
            ET_RESTING_STATE.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                # Run 'Each Frame' code from code_13
                if t>eye_tracking_resting_state_time:
                    continueRoutine = False
                
                # Solo actualizar el texto si ha cambiado el segundo
                current_second = int(t)
                if general_config["logs"] and current_second != last_second:
                    text_3.setText(str(eye_tracking_resting_state_time - current_second))
                    last_second = current_second  # Actualizar el último segundo registrado
                    
                elif general_config["logs"] == False and current_second != last_second:
                    print(str(eye_tracking_resting_state_time - current_second))
                    last_second = current_second
                
                # *text_3* updates
                
                # if text_3 is starting this frame...
                if text_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_3.frameNStart = frameN  # exact frame index
                    text_3.tStart = t  # local t and not account for scr refresh
                    text_3.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_3, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'text_3.started')
                    # update status
                    text_3.status = STARTED
                    text_3.setAutoDraw(True)
                
                # if text_3 is active this frame...
                if text_3.status == STARTED:
                    # update params
                    pass
                
                # *key_resp_8* updates
                waitOnFlip = False
                
                # if key_resp_8 is starting this frame...
                if key_resp_8.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_8.frameNStart = frameN  # exact frame index
                    key_resp_8.tStart = t  # local t and not account for scr refresh
                    key_resp_8.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_8, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp_8.started')
                    # update status
                    key_resp_8.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_8.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_8.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp_8.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_8.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                    _key_resp_8_allKeys.extend(theseKeys)
                    if len(_key_resp_8_allKeys):
                        key_resp_8.keys = _key_resp_8_allKeys[-1].name  # just the last key pressed
                        key_resp_8.rt = _key_resp_8_allKeys[-1].rt
                        key_resp_8.duration = _key_resp_8_allKeys[-1].duration
                        # a response ends the routine
                        continueRoutine = False
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer], 
                        playbackComponents=[]
                    )
                    # skip the frame we paused on
                    continue
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    ET_RESTING_STATE.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in ET_RESTING_STATE.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "ET_RESTING_STATE" ---
            for thisComponent in ET_RESTING_STATE.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for ET_RESTING_STATE
            ET_RESTING_STATE.tStop = globalClock.getTime(format='float')
            ET_RESTING_STATE.tStopRefresh = tThisFlipGlobal
            thisExp.addData('ET_RESTING_STATE.stopped', ET_RESTING_STATE.tStop)
            # check responses
            if key_resp_8.keys in ['', [], None]:  # No response was made
                key_resp_8.keys = None
            MODULE_2_TEST_1.addData('key_resp_8.keys',key_resp_8.keys)
            if key_resp_8.keys != None:  # we had a response
                MODULE_2_TEST_1.addData('key_resp_8.rt', key_resp_8.rt)
                MODULE_2_TEST_1.addData('key_resp_8.duration', key_resp_8.duration)
            # the Routine "ET_RESTING_STATE" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # set up handler to look after randomisation of conditions etc
            et_task_instructions = data.TrialHandler2(
                name='et_task_instructions',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/et_task_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(et_task_instructions)  # add the loop to the experiment
            thisEt_task_instruction = et_task_instructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisEt_task_instruction.rgb)
            if thisEt_task_instruction != None:
                for paramName in thisEt_task_instruction:
                    globals()[paramName] = thisEt_task_instruction[paramName]
            
            for thisEt_task_instruction in et_task_instructions:
                currentLoop = et_task_instructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                # abbreviate parameter names if possible (e.g. rgb = thisEt_task_instruction.rgb)
                if thisEt_task_instruction != None:
                    for paramName in thisEt_task_instruction:
                        globals()[paramName] = thisEt_task_instruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(et_task_instructions, data.TrialHandler2) and thisEt_task_instruction.thisN != et_task_instructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                et_task_instructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   et_task_instructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   et_task_instructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   et_task_instructions.addData('button_next_instruction_2.timesOn', "")
                   et_task_instructions.addData('button_next_instruction_2.timesOff', "")
                et_task_instructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   et_task_instructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   et_task_instructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   et_task_instructions.addData('button_previous_instruction_2.timesOn', "")
                   et_task_instructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                et_task_instructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    et_task_instructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    et_task_instructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
            # completed 1.0 repeats of 'et_task_instructions'
            
            
            # --- Prepare to start Routine "ET_SCREEN_POINT_TASK" ---
            # create an object to store info about Routine ET_SCREEN_POINT_TASK
            ET_SCREEN_POINT_TASK = data.Routine(
                name='ET_SCREEN_POINT_TASK',
                components=[text_5, polygon_9, key_resp_26],
            )
            ET_SCREEN_POINT_TASK.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            # Run 'Begin Routine' code from code_27
            win.color = eye_tracking_resting_state_background_color
            # create starting attributes for key_resp_26
            key_resp_26.keys = []
            key_resp_26.rt = []
            _key_resp_26_allKeys = []
            # store start times for ET_SCREEN_POINT_TASK
            ET_SCREEN_POINT_TASK.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            ET_SCREEN_POINT_TASK.tStart = globalClock.getTime(format='float')
            ET_SCREEN_POINT_TASK.status = STARTED
            thisExp.addData('ET_SCREEN_POINT_TASK.started', ET_SCREEN_POINT_TASK.tStart)
            ET_SCREEN_POINT_TASK.maxDuration = None
            # keep track of which components have finished
            ET_SCREEN_POINT_TASKComponents = ET_SCREEN_POINT_TASK.components
            for thisComponent in ET_SCREEN_POINT_TASK.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "ET_SCREEN_POINT_TASK" ---
            # if trial has changed, end Routine now
            if isinstance(MODULE_2_TEST_1, data.TrialHandler2) and thisMODULE_2_TEST_1.thisN != MODULE_2_TEST_1.thisTrial.thisN:
                continueRoutine = False
            ET_SCREEN_POINT_TASK.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                # Run 'Each Frame' code from code_27
                if t>eye_tracking_resting_state_time:
                    continueRoutine = False
                    
                    
                
                
                # Solo actualizar el texto si ha cambiado el segundo
                current_second = int(t)
                if general_config["logs"] and current_second != last_second:
                    text_5.setText(str(eye_tracking_resting_state_time - current_second))
                    last_second = current_second  # Actualizar el último segundo registrado
                    
                elif general_config["logs"] == False and current_second != last_second:
                    print(str(eye_tracking_resting_state_time - current_second))
                    last_second = current_second
                
                # *text_5* updates
                
                # if text_5 is starting this frame...
                if text_5.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_5.frameNStart = frameN  # exact frame index
                    text_5.tStart = t  # local t and not account for scr refresh
                    text_5.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_5, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'text_5.started')
                    # update status
                    text_5.status = STARTED
                    text_5.setAutoDraw(True)
                
                # if text_5 is active this frame...
                if text_5.status == STARTED:
                    # update params
                    pass
                
                # *polygon_9* updates
                
                # if polygon_9 is starting this frame...
                if polygon_9.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    polygon_9.frameNStart = frameN  # exact frame index
                    polygon_9.tStart = t  # local t and not account for scr refresh
                    polygon_9.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(polygon_9, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'polygon_9.started')
                    # update status
                    polygon_9.status = STARTED
                    polygon_9.setAutoDraw(True)
                
                # if polygon_9 is active this frame...
                if polygon_9.status == STARTED:
                    # update params
                    pass
                
                # *key_resp_26* updates
                waitOnFlip = False
                
                # if key_resp_26 is starting this frame...
                if key_resp_26.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_26.frameNStart = frameN  # exact frame index
                    key_resp_26.tStart = t  # local t and not account for scr refresh
                    key_resp_26.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_26, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp_26.started')
                    # update status
                    key_resp_26.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_26.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_26.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp_26.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_26.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                    _key_resp_26_allKeys.extend(theseKeys)
                    if len(_key_resp_26_allKeys):
                        key_resp_26.keys = _key_resp_26_allKeys[-1].name  # just the last key pressed
                        key_resp_26.rt = _key_resp_26_allKeys[-1].rt
                        key_resp_26.duration = _key_resp_26_allKeys[-1].duration
                        # a response ends the routine
                        continueRoutine = False
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer], 
                        playbackComponents=[]
                    )
                    # skip the frame we paused on
                    continue
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    ET_SCREEN_POINT_TASK.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in ET_SCREEN_POINT_TASK.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "ET_SCREEN_POINT_TASK" ---
            for thisComponent in ET_SCREEN_POINT_TASK.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for ET_SCREEN_POINT_TASK
            ET_SCREEN_POINT_TASK.tStop = globalClock.getTime(format='float')
            ET_SCREEN_POINT_TASK.tStopRefresh = tThisFlipGlobal
            thisExp.addData('ET_SCREEN_POINT_TASK.stopped', ET_SCREEN_POINT_TASK.tStop)
            # check responses
            if key_resp_26.keys in ['', [], None]:  # No response was made
                key_resp_26.keys = None
            MODULE_2_TEST_1.addData('key_resp_26.keys',key_resp_26.keys)
            if key_resp_26.keys != None:  # we had a response
                MODULE_2_TEST_1.addData('key_resp_26.rt', key_resp_26.rt)
                MODULE_2_TEST_1.addData('key_resp_26.duration', key_resp_26.duration)
            # the Routine "ET_SCREEN_POINT_TASK" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            thisExp.nextEntry()
            
        # completed modules["module_2"]["tests"]["test_1"]["selected"] repeats of 'MODULE_2_TEST_1'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if MODULE_2_TEST_1.trialList in ([], [None], None):
            params = []
        else:
            params = MODULE_2_TEST_1.trialList[0].keys()
        # save data for this loop
        MODULE_2_TEST_1.saveAsExcel(filename + '.xlsx', sheetName='MODULE_2_TEST_1',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        
        # set up handler to look after randomisation of conditions etc
        MODULE_2_TEST_2 = data.TrialHandler2(
            name='MODULE_2_TEST_2',
            nReps=modules["module_2"]["tests"]["test_2"]["selected"], 
            method='sequential', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=[None], 
            seed=None, 
        )
        thisExp.addLoop(MODULE_2_TEST_2)  # add the loop to the experiment
        thisMODULE_2_TEST_2 = MODULE_2_TEST_2.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_2_TEST_2.rgb)
        if thisMODULE_2_TEST_2 != None:
            for paramName in thisMODULE_2_TEST_2:
                globals()[paramName] = thisMODULE_2_TEST_2[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisMODULE_2_TEST_2 in MODULE_2_TEST_2:
            currentLoop = MODULE_2_TEST_2
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisMODULE_2_TEST_2.rgb)
            if thisMODULE_2_TEST_2 != None:
                for paramName in thisMODULE_2_TEST_2:
                    globals()[paramName] = thisMODULE_2_TEST_2[paramName]
            
            # set up handler to look after randomisation of conditions etc
            trials = data.TrialHandler2(
                name='trials',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/BL4_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(trials)  # add the loop to the experiment
            thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
            if thisTrial != None:
                for paramName in thisTrial:
                    globals()[paramName] = thisTrial[paramName]
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            
            for thisTrial in trials:
                currentLoop = trials
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                if thisSession is not None:
                    # if running in a Session with a Liaison client, send data up to now
                    thisSession.sendExperimentData()
                # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
                if thisTrial != None:
                    for paramName in thisTrial:
                        globals()[paramName] = thisTrial[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(trials, data.TrialHandler2) and thisTrial.thisN != trials.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                trials.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   trials.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   trials.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   trials.addData('button_next_instruction_2.timesOn', "")
                   trials.addData('button_next_instruction_2.timesOff', "")
                trials.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   trials.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   trials.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   trials.addData('button_previous_instruction_2.timesOn', "")
                   trials.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                trials.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    trials.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    trials.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
                thisExp.nextEntry()
                
            # completed 1.0 repeats of 'trials'
            
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # get names of stimulus parameters
            if trials.trialList in ([], [None], None):
                params = []
            else:
                params = trials.trialList[0].keys()
            # save data for this loop
            trials.saveAsExcel(filename + '.xlsx', sheetName='trials',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            
            # --- Prepare to start Routine "FFT_STAIRCASE_TEST" ---
            # create an object to store info about Routine FFT_STAIRCASE_TEST
            FFT_STAIRCASE_TEST = data.Routine(
                name='FFT_STAIRCASE_TEST',
                components=[key_resp_17, logs_13, dots_white_4, dots_black_4, key_resp_18, FPS_logs_2, dot],
            )
            FFT_STAIRCASE_TEST.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            # Run 'Begin Routine' code from flicker_daemon
            frecuencia_monitor = 144
            frecuencia_parpadeo = 30  # Hz, frecuencia de parpadeo deseada (valor inicial)
            frames_por_ciclo = int((frecuencia_monitor / frecuencia_parpadeo) / 2)
            opacidad = 1
            # Run 'Begin Routine' code from code_21
            import csv
            
            # Variables estaticas
            fft_starting_value = 25
            fft_step_size = 2
            staircase_test_orientation = get_random_orientation()
            
            # Inicializacion de variables que posteriormente cambian
            fft = fft_starting_value
            step = fft_step_size
            reversals = 0
            last_direction = None
            reversal_ffts = []
            correct_responses = 0
            trials = []
            
            # Para almacenar las respuestas del participante
            response = None
            
            # Cargar frecuencia espacial del test
            #threshold_dict = load_thresholds_from_json()
            #grating_8.sf = threshold_dict['spatial_frequency_threshold']
            #grating_8.ori = staircase_test_orientation
            
            #print(f"Se ha establecido la frecuencia espacial del estímulo a un valor de {threshold_dict['spatial_frequency_threshold']} unidades.")
            
            # create starting attributes for key_resp_17
            key_resp_17.keys = []
            key_resp_17.rt = []
            _key_resp_17_allKeys = []
            dots_white_4.refreshDots()
            dots_black_4.refreshDots()
            # create starting attributes for key_resp_18
            key_resp_18.keys = []
            key_resp_18.rt = []
            _key_resp_18_allKeys = []
            # Run 'Begin Routine' code from FPS_counter_2
            tiempo_anterior = 0 
            fps = 0  # Variable para almacenar el FPS
            # store start times for FFT_STAIRCASE_TEST
            FFT_STAIRCASE_TEST.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            FFT_STAIRCASE_TEST.tStart = globalClock.getTime(format='float')
            FFT_STAIRCASE_TEST.status = STARTED
            thisExp.addData('FFT_STAIRCASE_TEST.started', FFT_STAIRCASE_TEST.tStart)
            FFT_STAIRCASE_TEST.maxDuration = None
            # keep track of which components have finished
            FFT_STAIRCASE_TESTComponents = FFT_STAIRCASE_TEST.components
            for thisComponent in FFT_STAIRCASE_TEST.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "FFT_STAIRCASE_TEST" ---
            # if trial has changed, end Routine now
            if isinstance(MODULE_2_TEST_2, data.TrialHandler2) and thisMODULE_2_TEST_2.thisN != MODULE_2_TEST_2.thisTrial.thisN:
                continueRoutine = False
            FFT_STAIRCASE_TEST.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                # Run 'Each Frame' code from flicker_daemon
                if fft is not None:
                    frames_por_ciclo = int((frecuencia_monitor / fft) / 2)
                    opacidad = 1 if (frameN % (2 * frames_por_ciclo)) < frames_por_ciclo else 0
                else:
                    opacidad = 1
                
                dot.opacity = opacidad
                # Run 'Each Frame' code from code_21
                keys = event.getKeys()
                
                if 's' in keys: # El paciente ve el estimulo
                    response = True
                elif 'n' in keys: # El paciente no ve las lineas
                    response = False
                '''
                elif 'right' in keys and staircase_test_orientation == 45: # Acierto
                    response = True
                elif 'left' in keys and staircase_test_orientation == 135: # Acierto
                    response = True
                elif 'right' in keys or 'left' in keys:
                    response = False
                '''
                # Lógica del staircase
                if response is not None:
                    if response:  # Respuesta correcta: el paciente ve el parpadeo
                        correct_responses += 1
                        if correct_responses == 2:  # Después de 2 respuestas correctas consecutivas
                            correct_responses = 0
                            fft = max(0, fft + step)  # Aumentar flicker
                            last_direction = "down"
                    else:  # Respuesta incorrecta: el paciente no aprecia el parpadeo
                        fft -= step  # disminuir el parpadeo
                        correct_responses = 0
                        if last_direction == "down":
                            reversals += 1
                            reversal_ffts.append(fft)
                            # Regla para aumentar la granularidad del test
                            if (reversals % 3 == 0) and reversals != 0:
                                step = step/2
                                print(f"Reversals = {reversals}; New step = {step}")
                                last_direction = "up"
                            else:
                                print(f'Reversal detected ({reversals})')
                        last_direction = "up"
                        
                    dot.setAutoDraw(False)
                    show_noise(dots_white_4, dots_black_4, staircase_noise_duration)
                    dot.setAutoDraw(True)
                    
                    #staircase_test_orientation = get_random_orientation()
                    #grating_8.ori = staircase_test_orientation
                    
                    # Actualizar el contraste del estímulo
                    #grating.contrast = contrast
                    
                    # Registrar la información del ensayo
                    trials.append({
                        'trial': len(trials) + 1,
                        'fft': fft,
                        'response': response,
                        'reversals': reversals
                    })
                    
                    # Restablecer la respuesta para el siguiente ensayo
                    response = None
                        
                    # Regla de detencion
                    if reversals >= stop_reversals:
                        print(trials)
                        # almaceno trials en 'data' para su posterior analisis
                        staircase_data_filename = f"./data/{expInfo['participant']}/fft_staircase_data_{expInfo['participant']}.csv"
                        with open(staircase_data_filename, mode='w', newline='') as file:
                            writer = csv.DictWriter(file, fieldnames=['trial', 'fft', 'response', 'reversals'])
                            writer.writeheader()
                            writer.writerows(trials)
                        
                        # Actualizar y almacenar el diccionario de thresholds
                        test_fft = get_threshold('fft', staircase_data_filename)
                        print(f"FFT Threshold for patient: {test_fft}")
                        #threshold_dict['flicker_threshold'] = test_fft
                        #save_thresholds_to_json(threshold_dict)
                
                        continueRoutine = False
                
                #########################################################
                #############____________LOGS_________###################
                #########################################################
                
                if general_config["logs"]:
                    logs_13.text = f"Step Size = {step}\nFFT freq = {fft} Hz"
                
                
                dots_white_4.setAutoDraw(False)
                dots_black_4.setAutoDraw(False)
                
                # *key_resp_17* updates
                waitOnFlip = False
                
                # if key_resp_17 is starting this frame...
                if key_resp_17.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_17.frameNStart = frameN  # exact frame index
                    key_resp_17.tStart = t  # local t and not account for scr refresh
                    key_resp_17.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_17, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp_17.started')
                    # update status
                    key_resp_17.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_17.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_17.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp_17.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_17.getKeys(keyList=['s','n'], ignoreKeys=["escape"], waitRelease=False)
                    _key_resp_17_allKeys.extend(theseKeys)
                    if len(_key_resp_17_allKeys):
                        key_resp_17.keys = _key_resp_17_allKeys[-1].name  # just the last key pressed
                        key_resp_17.rt = _key_resp_17_allKeys[-1].rt
                        key_resp_17.duration = _key_resp_17_allKeys[-1].duration
                
                # *logs_13* updates
                
                # if logs_13 is starting this frame...
                if logs_13.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    logs_13.frameNStart = frameN  # exact frame index
                    logs_13.tStart = t  # local t and not account for scr refresh
                    logs_13.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(logs_13, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'logs_13.started')
                    # update status
                    logs_13.status = STARTED
                    logs_13.setAutoDraw(True)
                
                # if logs_13 is active this frame...
                if logs_13.status == STARTED:
                    # update params
                    pass
                
                # *dots_white_4* updates
                
                # if dots_white_4 is starting this frame...
                if dots_white_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    dots_white_4.frameNStart = frameN  # exact frame index
                    dots_white_4.tStart = t  # local t and not account for scr refresh
                    dots_white_4.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(dots_white_4, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'dots_white_4.started')
                    # update status
                    dots_white_4.status = STARTED
                    dots_white_4.setAutoDraw(True)
                
                # if dots_white_4 is active this frame...
                if dots_white_4.status == STARTED:
                    # update params
                    pass
                
                # *dots_black_4* updates
                
                # if dots_black_4 is starting this frame...
                if dots_black_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    dots_black_4.frameNStart = frameN  # exact frame index
                    dots_black_4.tStart = t  # local t and not account for scr refresh
                    dots_black_4.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(dots_black_4, 'tStartRefresh')  # time at next scr refresh
                    # update status
                    dots_black_4.status = STARTED
                    dots_black_4.setAutoDraw(True)
                
                # if dots_black_4 is active this frame...
                if dots_black_4.status == STARTED:
                    # update params
                    pass
                
                # *key_resp_18* updates
                waitOnFlip = False
                
                # if key_resp_18 is starting this frame...
                if key_resp_18.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_18.frameNStart = frameN  # exact frame index
                    key_resp_18.tStart = t  # local t and not account for scr refresh
                    key_resp_18.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_18, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp_18.started')
                    # update status
                    key_resp_18.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_18.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_18.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp_18.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_18.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                    _key_resp_18_allKeys.extend(theseKeys)
                    if len(_key_resp_18_allKeys):
                        key_resp_18.keys = _key_resp_18_allKeys[-1].name  # just the last key pressed
                        key_resp_18.rt = _key_resp_18_allKeys[-1].rt
                        key_resp_18.duration = _key_resp_18_allKeys[-1].duration
                        # a response ends the routine
                        continueRoutine = False
                # Run 'Each Frame' code from FPS_counter_2
                tiempo_actual = t
                delta_tiempo = tiempo_actual - tiempo_anterior # tiempo desde el frame anterior
                
                if delta_tiempo > 0:
                    fps = 1.0 / delta_tiempo  # Frecuencia: (1 / tiempo entre frames) (Hz)
                
                tiempo_anterior = tiempo_actual
                
                FPS_logs_2.text = f"FPS: {fps:.2f}"  # Mostrar con 2 decimales
                
                
                # *FPS_logs_2* updates
                
                # if FPS_logs_2 is starting this frame...
                if FPS_logs_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    FPS_logs_2.frameNStart = frameN  # exact frame index
                    FPS_logs_2.tStart = t  # local t and not account for scr refresh
                    FPS_logs_2.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(FPS_logs_2, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'FPS_logs_2.started')
                    # update status
                    FPS_logs_2.status = STARTED
                    FPS_logs_2.setAutoDraw(True)
                
                # if FPS_logs_2 is active this frame...
                if FPS_logs_2.status == STARTED:
                    # update params
                    pass
                
                # *dot* updates
                
                # if dot is starting this frame...
                if dot.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    dot.frameNStart = frameN  # exact frame index
                    dot.tStart = t  # local t and not account for scr refresh
                    dot.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(dot, 'tStartRefresh')  # time at next scr refresh
                    # update status
                    dot.status = STARTED
                    dot.setAutoDraw(True)
                
                # if dot is active this frame...
                if dot.status == STARTED:
                    # update params
                    pass
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer], 
                        playbackComponents=[]
                    )
                    # skip the frame we paused on
                    continue
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    FFT_STAIRCASE_TEST.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in FFT_STAIRCASE_TEST.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "FFT_STAIRCASE_TEST" ---
            for thisComponent in FFT_STAIRCASE_TEST.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for FFT_STAIRCASE_TEST
            FFT_STAIRCASE_TEST.tStop = globalClock.getTime(format='float')
            FFT_STAIRCASE_TEST.tStopRefresh = tThisFlipGlobal
            thisExp.addData('FFT_STAIRCASE_TEST.stopped', FFT_STAIRCASE_TEST.tStop)
            # check responses
            if key_resp_17.keys in ['', [], None]:  # No response was made
                key_resp_17.keys = None
            MODULE_2_TEST_2.addData('key_resp_17.keys',key_resp_17.keys)
            if key_resp_17.keys != None:  # we had a response
                MODULE_2_TEST_2.addData('key_resp_17.rt', key_resp_17.rt)
                MODULE_2_TEST_2.addData('key_resp_17.duration', key_resp_17.duration)
            # check responses
            if key_resp_18.keys in ['', [], None]:  # No response was made
                key_resp_18.keys = None
            MODULE_2_TEST_2.addData('key_resp_18.keys',key_resp_18.keys)
            if key_resp_18.keys != None:  # we had a response
                MODULE_2_TEST_2.addData('key_resp_18.rt', key_resp_18.rt)
                MODULE_2_TEST_2.addData('key_resp_18.duration', key_resp_18.duration)
            # the Routine "FFT_STAIRCASE_TEST" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            thisExp.nextEntry()
            
        # completed modules["module_2"]["tests"]["test_2"]["selected"] repeats of 'MODULE_2_TEST_2'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if MODULE_2_TEST_2.trialList in ([], [None], None):
            params = []
        else:
            params = MODULE_2_TEST_2.trialList[0].keys()
        # save data for this loop
        MODULE_2_TEST_2.saveAsExcel(filename + '.xlsx', sheetName='MODULE_2_TEST_2',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        
        # set up handler to look after randomisation of conditions etc
        MODULE_2_TEST_3 = data.TrialHandler2(
            name='MODULE_2_TEST_3',
            nReps=modules["module_2"]["tests"]["test_3"]["selected"], 
            method='random', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=[None], 
            seed=None, 
        )
        thisExp.addLoop(MODULE_2_TEST_3)  # add the loop to the experiment
        thisMODULE_2_TEST_3 = MODULE_2_TEST_3.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_2_TEST_3.rgb)
        if thisMODULE_2_TEST_3 != None:
            for paramName in thisMODULE_2_TEST_3:
                globals()[paramName] = thisMODULE_2_TEST_3[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisMODULE_2_TEST_3 in MODULE_2_TEST_3:
            currentLoop = MODULE_2_TEST_3
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisMODULE_2_TEST_3.rgb)
            if thisMODULE_2_TEST_3 != None:
                for paramName in thisMODULE_2_TEST_3:
                    globals()[paramName] = thisMODULE_2_TEST_3[paramName]
            
            # set up handler to look after randomisation of conditions etc
            et_saccade_task_instructions = data.TrialHandler2(
                name='et_saccade_task_instructions',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/et_saccade_task_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(et_saccade_task_instructions)  # add the loop to the experiment
            thisEt_saccade_task_instruction = et_saccade_task_instructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisEt_saccade_task_instruction.rgb)
            if thisEt_saccade_task_instruction != None:
                for paramName in thisEt_saccade_task_instruction:
                    globals()[paramName] = thisEt_saccade_task_instruction[paramName]
            
            for thisEt_saccade_task_instruction in et_saccade_task_instructions:
                currentLoop = et_saccade_task_instructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                # abbreviate parameter names if possible (e.g. rgb = thisEt_saccade_task_instruction.rgb)
                if thisEt_saccade_task_instruction != None:
                    for paramName in thisEt_saccade_task_instruction:
                        globals()[paramName] = thisEt_saccade_task_instruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(et_saccade_task_instructions, data.TrialHandler2) and thisEt_saccade_task_instruction.thisN != et_saccade_task_instructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                et_saccade_task_instructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   et_saccade_task_instructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   et_saccade_task_instructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   et_saccade_task_instructions.addData('button_next_instruction_2.timesOn', "")
                   et_saccade_task_instructions.addData('button_next_instruction_2.timesOff', "")
                et_saccade_task_instructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   et_saccade_task_instructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   et_saccade_task_instructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   et_saccade_task_instructions.addData('button_previous_instruction_2.timesOn', "")
                   et_saccade_task_instructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                et_saccade_task_instructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    et_saccade_task_instructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    et_saccade_task_instructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
            # completed 1.0 repeats of 'et_saccade_task_instructions'
            
            
            # set up handler to look after randomisation of conditions etc
            IPAST_LOOP = data.TrialHandler2(
                name='IPAST_LOOP',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('IPAST_loop.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(IPAST_LOOP)  # add the loop to the experiment
            thisIPAST_LOOP = IPAST_LOOP.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisIPAST_LOOP.rgb)
            if thisIPAST_LOOP != None:
                for paramName in thisIPAST_LOOP:
                    globals()[paramName] = thisIPAST_LOOP[paramName]
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            
            for thisIPAST_LOOP in IPAST_LOOP:
                currentLoop = IPAST_LOOP
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                if thisSession is not None:
                    # if running in a Session with a Liaison client, send data up to now
                    thisSession.sendExperimentData()
                # abbreviate parameter names if possible (e.g. rgb = thisIPAST_LOOP.rgb)
                if thisIPAST_LOOP != None:
                    for paramName in thisIPAST_LOOP:
                        globals()[paramName] = thisIPAST_LOOP[paramName]
                
                # --- Prepare to start Routine "SACCADE_TASK" ---
                # create an object to store info about Routine SACCADE_TASK
                SACCADE_TASK = data.Routine(
                    name='SACCADE_TASK',
                    components=[cross_1, cross_2, cross_3, polygon_5, key_resp_27],
                )
                SACCADE_TASK.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_12
                
                
                # CHANGE BACKGROUND COLOR TO BALCK
                win.color = "black"
                
                # SHOW STIMULI WITH COLOR
                if task_type == "saccade":
                    polygon_5.color = "green"
                elif task_type == "antisaccade":
                    polygon_5.color = "red"
                
                # create starting attributes for key_resp_27
                key_resp_27.keys = []
                key_resp_27.rt = []
                _key_resp_27_allKeys = []
                # store start times for SACCADE_TASK
                SACCADE_TASK.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                SACCADE_TASK.tStart = globalClock.getTime(format='float')
                SACCADE_TASK.status = STARTED
                thisExp.addData('SACCADE_TASK.started', SACCADE_TASK.tStart)
                SACCADE_TASK.maxDuration = None
                # keep track of which components have finished
                SACCADE_TASKComponents = SACCADE_TASK.components
                for thisComponent in SACCADE_TASK.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "SACCADE_TASK" ---
                # if trial has changed, end Routine now
                if isinstance(IPAST_LOOP, data.TrialHandler2) and thisIPAST_LOOP.thisN != IPAST_LOOP.thisTrial.thisN:
                    continueRoutine = False
                SACCADE_TASK.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    # Run 'Each Frame' code from code_12
                    # SEQUENCE
                    
                    # SHOW / HIDE STIMULI
                    if t> 3.5 + REST_TIME: # End of Routine
                        polygon_5.setAutoDraw(False)
                        continueRoutine = False
                        
                    elif t>1.2 + REST_TIME: # Saccade time
                        if alignment == "l":
                            IPAST_stim_position = PERIPHEREAL_POS_L
                        elif alignment == "r":
                            IPAST_stim_position = PERIPHEREAL_POS_R
                        polygon_5.color = "white"
                        polygon_5.setAutoDraw(True)
                        
                    elif t>1 + REST_TIME:
                        polygon_5.setAutoDraw(False)
                        
                    elif t>0 + REST_TIME:
                        polygon_5.setAutoDraw(True)
                        IPAST_stim_position = FIXATION_POS
                        
                    else: # wait some time between trials
                        polygon_5.setAutoDraw(False)
                    
                    #text_2.text = f"Time: {t:.2f}"
                    
                    # *cross_1* updates
                    
                    # if cross_1 is starting this frame...
                    if cross_1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        cross_1.frameNStart = frameN  # exact frame index
                        cross_1.tStart = t  # local t and not account for scr refresh
                        cross_1.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(cross_1, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'cross_1.started')
                        # update status
                        cross_1.status = STARTED
                        cross_1.setAutoDraw(True)
                    
                    # if cross_1 is active this frame...
                    if cross_1.status == STARTED:
                        # update params
                        pass
                    
                    # *cross_2* updates
                    
                    # if cross_2 is starting this frame...
                    if cross_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        cross_2.frameNStart = frameN  # exact frame index
                        cross_2.tStart = t  # local t and not account for scr refresh
                        cross_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(cross_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'cross_2.started')
                        # update status
                        cross_2.status = STARTED
                        cross_2.setAutoDraw(True)
                    
                    # if cross_2 is active this frame...
                    if cross_2.status == STARTED:
                        # update params
                        pass
                    
                    # *cross_3* updates
                    
                    # if cross_3 is starting this frame...
                    if cross_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        cross_3.frameNStart = frameN  # exact frame index
                        cross_3.tStart = t  # local t and not account for scr refresh
                        cross_3.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(cross_3, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'cross_3.started')
                        # update status
                        cross_3.status = STARTED
                        cross_3.setAutoDraw(True)
                    
                    # if cross_3 is active this frame...
                    if cross_3.status == STARTED:
                        # update params
                        pass
                    
                    # *polygon_5* updates
                    
                    # if polygon_5 is starting this frame...
                    if polygon_5.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        polygon_5.frameNStart = frameN  # exact frame index
                        polygon_5.tStart = t  # local t and not account for scr refresh
                        polygon_5.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(polygon_5, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'polygon_5.started')
                        # update status
                        polygon_5.status = STARTED
                        polygon_5.setAutoDraw(True)
                    
                    # if polygon_5 is active this frame...
                    if polygon_5.status == STARTED:
                        # update params
                        polygon_5.setPos(IPAST_stim_position, log=False)
                    
                    # *key_resp_27* updates
                    waitOnFlip = False
                    
                    # if key_resp_27 is starting this frame...
                    if key_resp_27.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_27.frameNStart = frameN  # exact frame index
                        key_resp_27.tStart = t  # local t and not account for scr refresh
                        key_resp_27.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_27, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'key_resp_27.started')
                        # update status
                        key_resp_27.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_27.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_27.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_27.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_27.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_27_allKeys.extend(theseKeys)
                        if len(_key_resp_27_allKeys):
                            key_resp_27.keys = _key_resp_27_allKeys[-1].name  # just the last key pressed
                            key_resp_27.rt = _key_resp_27_allKeys[-1].rt
                            key_resp_27.duration = _key_resp_27_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        SACCADE_TASK.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in SACCADE_TASK.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "SACCADE_TASK" ---
                for thisComponent in SACCADE_TASK.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for SACCADE_TASK
                SACCADE_TASK.tStop = globalClock.getTime(format='float')
                SACCADE_TASK.tStopRefresh = tThisFlipGlobal
                thisExp.addData('SACCADE_TASK.stopped', SACCADE_TASK.tStop)
                # check responses
                if key_resp_27.keys in ['', [], None]:  # No response was made
                    key_resp_27.keys = None
                IPAST_LOOP.addData('key_resp_27.keys',key_resp_27.keys)
                if key_resp_27.keys != None:  # we had a response
                    IPAST_LOOP.addData('key_resp_27.rt', key_resp_27.rt)
                    IPAST_LOOP.addData('key_resp_27.duration', key_resp_27.duration)
                # the Routine "SACCADE_TASK" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
                thisExp.nextEntry()
                
            # completed 1.0 repeats of 'IPAST_LOOP'
            
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # get names of stimulus parameters
            if IPAST_LOOP.trialList in ([], [None], None):
                params = []
            else:
                params = IPAST_LOOP.trialList[0].keys()
            # save data for this loop
            IPAST_LOOP.saveAsExcel(filename + '.xlsx', sheetName='IPAST_LOOP',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            thisExp.nextEntry()
            
        # completed modules["module_2"]["tests"]["test_3"]["selected"] repeats of 'MODULE_2_TEST_3'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if MODULE_2_TEST_3.trialList in ([], [None], None):
            params = []
        else:
            params = MODULE_2_TEST_3.trialList[0].keys()
        # save data for this loop
        MODULE_2_TEST_3.saveAsExcel(filename + '.xlsx', sheetName='MODULE_2_TEST_3',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        
        # set up handler to look after randomisation of conditions etc
        MODULE_2_TEST_4 = data.TrialHandler2(
            name='MODULE_2_TEST_4',
            nReps=modules["module_2"]["tests"]["test_4"]["selected"], 
            method='sequential', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=[None], 
            seed=None, 
        )
        thisExp.addLoop(MODULE_2_TEST_4)  # add the loop to the experiment
        thisMODULE_2_TEST_4 = MODULE_2_TEST_4.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_2_TEST_4.rgb)
        if thisMODULE_2_TEST_4 != None:
            for paramName in thisMODULE_2_TEST_4:
                globals()[paramName] = thisMODULE_2_TEST_4[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisMODULE_2_TEST_4 in MODULE_2_TEST_4:
            currentLoop = MODULE_2_TEST_4
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisMODULE_2_TEST_4.rgb)
            if thisMODULE_2_TEST_4 != None:
                for paramName in thisMODULE_2_TEST_4:
                    globals()[paramName] = thisMODULE_2_TEST_4[paramName]
            
            # set up handler to look after randomisation of conditions etc
            DVS_coherence_instructions = data.TrialHandler2(
                name='DVS_coherence_instructions',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/DVS_tracking_task_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(DVS_coherence_instructions)  # add the loop to the experiment
            thisDVS_coherence_instruction = DVS_coherence_instructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisDVS_coherence_instruction.rgb)
            if thisDVS_coherence_instruction != None:
                for paramName in thisDVS_coherence_instruction:
                    globals()[paramName] = thisDVS_coherence_instruction[paramName]
            
            for thisDVS_coherence_instruction in DVS_coherence_instructions:
                currentLoop = DVS_coherence_instructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                # abbreviate parameter names if possible (e.g. rgb = thisDVS_coherence_instruction.rgb)
                if thisDVS_coherence_instruction != None:
                    for paramName in thisDVS_coherence_instruction:
                        globals()[paramName] = thisDVS_coherence_instruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(DVS_coherence_instructions, data.TrialHandler2) and thisDVS_coherence_instruction.thisN != DVS_coherence_instructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                DVS_coherence_instructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   DVS_coherence_instructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   DVS_coherence_instructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   DVS_coherence_instructions.addData('button_next_instruction_2.timesOn', "")
                   DVS_coherence_instructions.addData('button_next_instruction_2.timesOff', "")
                DVS_coherence_instructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   DVS_coherence_instructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   DVS_coherence_instructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   DVS_coherence_instructions.addData('button_previous_instruction_2.timesOn', "")
                   DVS_coherence_instructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                DVS_coherence_instructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    DVS_coherence_instructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    DVS_coherence_instructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
            # completed 1.0 repeats of 'DVS_coherence_instructions'
            
            
            # --- Prepare to start Routine "DVS_COHERENCE" ---
            # create an object to store info about Routine DVS_COHERENCE
            DVS_COHERENCE = data.Routine(
                name='DVS_COHERENCE',
                components=[dots_2, dot_2, key_resp_25],
            )
            DVS_COHERENCE.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            dots_2.refreshDots()
            # Run 'Begin Routine' code from code_26
            current_angle = np.random.uniform(0, 2 * np.pi)  # Ángulo inicial aleatorio
            frame_count = 0
            frames_in_direction = 20  # Ajusta según la duración que desees para cada dirección
            direction = 1 # start value of direction to te right
            mode = 3 # behaviour of the stimuli and noise dots 1... 2... 3: Move noise with stimuli. 4:...
            # create starting attributes for key_resp_25
            key_resp_25.keys = []
            key_resp_25.rt = []
            _key_resp_25_allKeys = []
            # store start times for DVS_COHERENCE
            DVS_COHERENCE.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            DVS_COHERENCE.tStart = globalClock.getTime(format='float')
            DVS_COHERENCE.status = STARTED
            thisExp.addData('DVS_COHERENCE.started', DVS_COHERENCE.tStart)
            DVS_COHERENCE.maxDuration = None
            # keep track of which components have finished
            DVS_COHERENCEComponents = DVS_COHERENCE.components
            for thisComponent in DVS_COHERENCE.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "DVS_COHERENCE" ---
            # if trial has changed, end Routine now
            if isinstance(MODULE_2_TEST_4, data.TrialHandler2) and thisMODULE_2_TEST_4.thisN != MODULE_2_TEST_4.thisTrial.thisN:
                continueRoutine = False
            DVS_COHERENCE.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *dots_2* updates
                
                # if dots_2 is starting this frame...
                if dots_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    dots_2.frameNStart = frameN  # exact frame index
                    dots_2.tStart = t  # local t and not account for scr refresh
                    dots_2.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(dots_2, 'tStartRefresh')  # time at next scr refresh
                    # update status
                    dots_2.status = STARTED
                    dots_2.setAutoDraw(True)
                
                # if dots_2 is active this frame...
                if dots_2.status == STARTED:
                    # update params
                    dots_2.setDir(noise_dots_direction, log=False)
                
                # *dot_2* updates
                
                # if dot_2 is starting this frame...
                if dot_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    dot_2.frameNStart = frameN  # exact frame index
                    dot_2.tStart = t  # local t and not account for scr refresh
                    dot_2.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(dot_2, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'dot_2.started')
                    # update status
                    dot_2.status = STARTED
                    dot_2.setAutoDraw(True)
                
                # if dot_2 is active this frame...
                if dot_2.status == STARTED:
                    # update params
                    pass
                # Run 'Each Frame' code from code_26
                # Dentro del bucle de cada frame
                
                #if  mode == 1: # movimiento random del estimulo. Cuando cambia la coherencia del ruido el estimulo se mantiene igual
                #    current_angle, frame_count = move_dot_smooth(dot_2, dot_speed, field_size, current_angle, frames_in_direction, frame_count)
                    
                #elif mode == 2: # movimiento lateral del estimulo. Cuando cambia la coherencia del ruido el estimulo se mantiene igual
                #    direction, frame_count = move_dot_lateral(dot_2, dot_speed, field_size, direction, frame_count)
                    
                if mode == 3:
                    current_angle, frame_count = move_dot_smooth(dot_2, dot_speed, field_size, current_angle, frames_in_direction, frame_count)
                    
                    if noise_coherent_motion: # Move noise with stimuli
                        if frame_count % frames_in_direction*5 == 0: # each 100 frames change angle
                            desvio = random.uniform(-20, 20)
                        noise_dots_direction = math.degrees(current_angle) + desvio
                
                elif mode == 4:
                    if noise_coherent_motion: # True
                        direction, frame_count = move_dot_lateral(dot_2, dot_speed, field_size, direction, frame_count)
                    else:
                        current_angle, frame_count = move_dot_smooth(dot_2, dot_speed, field_size, current_angle, frames_in_direction, frame_count)
                
                # FLANCOS ASCENDENTE Y DESCENDENTE - Cambiar la coherencia del ruido segun el tiempo
                if t>10 and t<20:
                    if not noise_coherent_motion:
                        dots_2.setFieldCoherence(1)
                        noise_coherent_motion = 1
                        #noise_dots_direction = 90
                        thisExp.addData(f"DVS_noise_coherent_motion_mode_3_StartTime", time.time())
                elif t>20 and t<30:
                    if not noise_coherent_motion:
                        dots_2.setFieldCoherence(1)
                        noise_coherent_motion = 1
                        noise_dots_direction = 0
                        current_angle = 0
                        direction = 1
                        mode = 4
                        thisExp.addData(f"DVS_noise_coherent_motion_mode_4_StartTime", time.time())
                else:
                    if noise_coherent_motion:
                        dots_2.setFieldCoherence(0)
                        noise_coherent_motion = 0
                        #noise_dots_direction = 0
                    elif t>40:
                        continueRoutine = False
                
                # *key_resp_25* updates
                waitOnFlip = False
                
                # if key_resp_25 is starting this frame...
                if key_resp_25.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_25.frameNStart = frameN  # exact frame index
                    key_resp_25.tStart = t  # local t and not account for scr refresh
                    key_resp_25.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_25, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp_25.started')
                    # update status
                    key_resp_25.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_25.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_25.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp_25.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_25.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                    _key_resp_25_allKeys.extend(theseKeys)
                    if len(_key_resp_25_allKeys):
                        key_resp_25.keys = _key_resp_25_allKeys[-1].name  # just the last key pressed
                        key_resp_25.rt = _key_resp_25_allKeys[-1].rt
                        key_resp_25.duration = _key_resp_25_allKeys[-1].duration
                        # a response ends the routine
                        continueRoutine = False
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer], 
                        playbackComponents=[]
                    )
                    # skip the frame we paused on
                    continue
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    DVS_COHERENCE.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in DVS_COHERENCE.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "DVS_COHERENCE" ---
            for thisComponent in DVS_COHERENCE.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for DVS_COHERENCE
            DVS_COHERENCE.tStop = globalClock.getTime(format='float')
            DVS_COHERENCE.tStopRefresh = tThisFlipGlobal
            thisExp.addData('DVS_COHERENCE.stopped', DVS_COHERENCE.tStop)
            # check responses
            if key_resp_25.keys in ['', [], None]:  # No response was made
                key_resp_25.keys = None
            MODULE_2_TEST_4.addData('key_resp_25.keys',key_resp_25.keys)
            if key_resp_25.keys != None:  # we had a response
                MODULE_2_TEST_4.addData('key_resp_25.rt', key_resp_25.rt)
                MODULE_2_TEST_4.addData('key_resp_25.duration', key_resp_25.duration)
            # the Routine "DVS_COHERENCE" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            thisExp.nextEntry()
            
        # completed modules["module_2"]["tests"]["test_4"]["selected"] repeats of 'MODULE_2_TEST_4'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if MODULE_2_TEST_4.trialList in ([], [None], None):
            params = []
        else:
            params = MODULE_2_TEST_4.trialList[0].keys()
        # save data for this loop
        MODULE_2_TEST_4.saveAsExcel(filename + '.xlsx', sheetName='MODULE_2_TEST_4',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        
        # set up handler to look after randomisation of conditions etc
        MODULE_2_TEST_5 = data.TrialHandler2(
            name='MODULE_2_TEST_5',
            nReps=modules["module_2"]["tests"]["test_5"]["selected"], 
            method='random', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=[None], 
            seed=None, 
        )
        thisExp.addLoop(MODULE_2_TEST_5)  # add the loop to the experiment
        thisMODULE_2_TEST_5 = MODULE_2_TEST_5.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_2_TEST_5.rgb)
        if thisMODULE_2_TEST_5 != None:
            for paramName in thisMODULE_2_TEST_5:
                globals()[paramName] = thisMODULE_2_TEST_5[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisMODULE_2_TEST_5 in MODULE_2_TEST_5:
            currentLoop = MODULE_2_TEST_5
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisMODULE_2_TEST_5.rgb)
            if thisMODULE_2_TEST_5 != None:
                for paramName in thisMODULE_2_TEST_5:
                    globals()[paramName] = thisMODULE_2_TEST_5[paramName]
            
            # set up handler to look after randomisation of conditions etc
            visual_search_instructions = data.TrialHandler2(
                name='visual_search_instructions',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/visual_search_task_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(visual_search_instructions)  # add the loop to the experiment
            thisVisual_search_instruction = visual_search_instructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisVisual_search_instruction.rgb)
            if thisVisual_search_instruction != None:
                for paramName in thisVisual_search_instruction:
                    globals()[paramName] = thisVisual_search_instruction[paramName]
            
            for thisVisual_search_instruction in visual_search_instructions:
                currentLoop = visual_search_instructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                # abbreviate parameter names if possible (e.g. rgb = thisVisual_search_instruction.rgb)
                if thisVisual_search_instruction != None:
                    for paramName in thisVisual_search_instruction:
                        globals()[paramName] = thisVisual_search_instruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(visual_search_instructions, data.TrialHandler2) and thisVisual_search_instruction.thisN != visual_search_instructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                visual_search_instructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   visual_search_instructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   visual_search_instructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   visual_search_instructions.addData('button_next_instruction_2.timesOn', "")
                   visual_search_instructions.addData('button_next_instruction_2.timesOff', "")
                visual_search_instructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   visual_search_instructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   visual_search_instructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   visual_search_instructions.addData('button_previous_instruction_2.timesOn', "")
                   visual_search_instructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                visual_search_instructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    visual_search_instructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    visual_search_instructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
            # completed 1.0 repeats of 'visual_search_instructions'
            
            
            # set up handler to look after randomisation of conditions etc
            trials_2 = data.TrialHandler2(
                name='trials_2',
                nReps=1.0, 
                method='random', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('images/autogenerated_datasets/visual_search_rings/rutas_imagenes.csv'), 
                seed=None, 
            )
            thisExp.addLoop(trials_2)  # add the loop to the experiment
            thisTrial_2 = trials_2.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisTrial_2.rgb)
            if thisTrial_2 != None:
                for paramName in thisTrial_2:
                    globals()[paramName] = thisTrial_2[paramName]
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            
            for thisTrial_2 in trials_2:
                currentLoop = trials_2
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                if thisSession is not None:
                    # if running in a Session with a Liaison client, send data up to now
                    thisSession.sendExperimentData()
                # abbreviate parameter names if possible (e.g. rgb = thisTrial_2.rgb)
                if thisTrial_2 != None:
                    for paramName in thisTrial_2:
                        globals()[paramName] = thisTrial_2[paramName]
                
                # --- Prepare to start Routine "VISUAL_SEARCH_RINGS" ---
                # create an object to store info about Routine VISUAL_SEARCH_RINGS
                VISUAL_SEARCH_RINGS = data.Routine(
                    name='VISUAL_SEARCH_RINGS',
                    components=[rings_img, key_resp_28, gaze],
                )
                VISUAL_SEARCH_RINGS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_28
                import re
                
                win.color = "white"
                
                def calcular_relacion_aspecto(ruta_archivo):
                    """
                    Extrae los números del primer paréntesis en el nombre del archivo y calcula la relación de aspecto.
                    
                    :param ruta_archivo: Ruta completa o nombre del archivo (str).
                    :return: Relación de aspecto (float).
                    """
                    # Extraer solo el nombre del archivo (ignorar la ruta previa)
                    nombre_archivo = ruta_archivo.split("\\")[-1] if "\\" in ruta_archivo else ruta_archivo.split("/")[-1]
                
                    # Buscar el primer paréntesis y extraer los números
                    match = re.search(r"\((\d+),\s*(\d+)\)", nombre_archivo)
                    if match:
                        filas = int(match.group(1))
                        columnas = int(match.group(2))
                        # Calcular la relación de aspecto (filas/columnas)
                        relacion_aspecto = filas / columnas
                        return relacion_aspecto
                    else:
                        raise ValueError("No se encontraron números en el primer paréntesis del nombre del archivo.")
                
                relacion_aspecto = calcular_relacion_aspecto(ruta_relativa)
                print(f"Relación de aspecto: {relacion_aspecto:.2f}")
                
                rings_img.setSize((1.5, 1.5 / relacion_aspecto))
                rings_img.setImage(ruta_relativa)
                # create starting attributes for key_resp_28
                key_resp_28.keys = []
                key_resp_28.rt = []
                _key_resp_28_allKeys = []
                # Run 'Begin Routine' code from GP_data_adq_backend_3
                import socket
                
                # Host machine IP
                HOST = '127.0.0.1'
                PORT = 4242
                ADDRESS = (HOST, PORT)
                
                # Variable global para controlar si el gaze está disponible
                gaze_enabled = True
                gaze_position = (0, 0)  # valor por defecto
                
                try:
                    # Intentar conectar al eye tracker
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(ADDRESS)
                
                    # Enviar comandos de inicio
                    s.send(str.encode('<SET ID="ENABLE_SEND_CURSOR" STATE="1" />\r\n'))
                    s.send(str.encode('<SET ID="ENABLE_SEND_POG_FIX" STATE="1" />\r\n'))
                    s.send(str.encode('<SET ID="ENABLE_SEND_DATA" STATE="1" />\r\n'))
                
                except Exception as e:
                    gaze_enabled = False
                    print("WARNING: Eye tracker no detectado. No se visualizará el gaze en pantalla.")
                    print(f"Detalles del error: {e}")
                
                # store start times for VISUAL_SEARCH_RINGS
                VISUAL_SEARCH_RINGS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                VISUAL_SEARCH_RINGS.tStart = globalClock.getTime(format='float')
                VISUAL_SEARCH_RINGS.status = STARTED
                thisExp.addData('VISUAL_SEARCH_RINGS.started', VISUAL_SEARCH_RINGS.tStart)
                VISUAL_SEARCH_RINGS.maxDuration = None
                # keep track of which components have finished
                VISUAL_SEARCH_RINGSComponents = VISUAL_SEARCH_RINGS.components
                for thisComponent in VISUAL_SEARCH_RINGS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "VISUAL_SEARCH_RINGS" ---
                # if trial has changed, end Routine now
                if isinstance(trials_2, data.TrialHandler2) and thisTrial_2.thisN != trials_2.thisTrial.thisN:
                    continueRoutine = False
                VISUAL_SEARCH_RINGS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    # Run 'Each Frame' code from code_28
                    if t>visual_search_image_time + visual_search_wait_time:
                        continueRoutine = False
                    
                    # *rings_img* updates
                    
                    # if rings_img is starting this frame...
                    if rings_img.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        rings_img.frameNStart = frameN  # exact frame index
                        rings_img.tStart = t  # local t and not account for scr refresh
                        rings_img.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(rings_img, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'rings_img.started')
                        # update status
                        rings_img.status = STARTED
                        rings_img.setAutoDraw(True)
                    
                    # if rings_img is active this frame...
                    if rings_img.status == STARTED:
                        # update params
                        pass
                    
                    # if rings_img is stopping this frame...
                    if rings_img.status == STARTED:
                        # is it time to stop? (based on global clock, using actual start)
                        if tThisFlipGlobal > rings_img.tStartRefresh + visual_search_image_time-frameTolerance:
                            # keep track of stop time/frame for later
                            rings_img.tStop = t  # not accounting for scr refresh
                            rings_img.tStopRefresh = tThisFlipGlobal  # on global time
                            rings_img.frameNStop = frameN  # exact frame index
                            # add timestamp to datafile
                            thisExp.timestampOnFlip(win, 'rings_img.stopped')
                            # update status
                            rings_img.status = FINISHED
                            rings_img.setAutoDraw(False)
                    
                    # *key_resp_28* updates
                    waitOnFlip = False
                    
                    # if key_resp_28 is starting this frame...
                    if key_resp_28.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_28.frameNStart = frameN  # exact frame index
                        key_resp_28.tStart = t  # local t and not account for scr refresh
                        key_resp_28.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_28, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'key_resp_28.started')
                        # update status
                        key_resp_28.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_28.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_28.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_28.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_28.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_28_allKeys.extend(theseKeys)
                        if len(_key_resp_28_allKeys):
                            key_resp_28.keys = _key_resp_28_allKeys[-1].name  # just the last key pressed
                            key_resp_28.rt = _key_resp_28_allKeys[-1].rt
                            key_resp_28.duration = _key_resp_28_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    # Run 'Each Frame' code from GP_data_adq_backend_3
                    if gaze_enabled:
                        try:
                            # Recibir datos
                            rxdat = s.recv(1024)
                            data_r = bytes.decode(rxdat)
                    
                            FPOGX = -1
                            FPOGY = -1 
                    
                            datalist = data_r.split(" ")
                    
                            for el in datalist:
                                if (el.find("FPOGX") != -1):
                                    FPOGX = float(el.split("\"")[1])
                                if (el.find("FPOGY") != -1):
                                    FPOGY = float(el.split("\"")[1])
                    
                            x_psychopy, y_psychopy = convert_to_psychopy_units(FPOGX, FPOGY, screen_bounds)
                            gaze_position = (x_psychopy, y_psychopy)
                    
                        except Exception as e:
                            print("ERROR al leer datos del eye tracker:", e)
                            gaze_position = (0, 0)
                    else:
                        # Opcional: puedes definir una posición neutral si no hay eye tracker
                        gaze_position = (-1, -1)
                    
                    
                    # *gaze* updates
                    
                    # if gaze is starting this frame...
                    if gaze.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        gaze.frameNStart = frameN  # exact frame index
                        gaze.tStart = t  # local t and not account for scr refresh
                        gaze.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(gaze, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        gaze.status = STARTED
                        gaze.setAutoDraw(True)
                    
                    # if gaze is active this frame...
                    if gaze.status == STARTED:
                        # update params
                        gaze.setPos(gaze_position, log=False)
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        VISUAL_SEARCH_RINGS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in VISUAL_SEARCH_RINGS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "VISUAL_SEARCH_RINGS" ---
                for thisComponent in VISUAL_SEARCH_RINGS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for VISUAL_SEARCH_RINGS
                VISUAL_SEARCH_RINGS.tStop = globalClock.getTime(format='float')
                VISUAL_SEARCH_RINGS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('VISUAL_SEARCH_RINGS.stopped', VISUAL_SEARCH_RINGS.tStop)
                # check responses
                if key_resp_28.keys in ['', [], None]:  # No response was made
                    key_resp_28.keys = None
                trials_2.addData('key_resp_28.keys',key_resp_28.keys)
                if key_resp_28.keys != None:  # we had a response
                    trials_2.addData('key_resp_28.rt', key_resp_28.rt)
                    trials_2.addData('key_resp_28.duration', key_resp_28.duration)
                # Run 'End Routine' code from GP_data_adq_backend_3
                s.close()
                # the Routine "VISUAL_SEARCH_RINGS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
                thisExp.nextEntry()
                
            # completed 1.0 repeats of 'trials_2'
            
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # get names of stimulus parameters
            if trials_2.trialList in ([], [None], None):
                params = []
            else:
                params = trials_2.trialList[0].keys()
            # save data for this loop
            trials_2.saveAsExcel(filename + '.xlsx', sheetName='trials_2',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            
            # set up handler to look after randomisation of conditions etc
            visual_search_imgs = data.TrialHandler2(
                name='visual_search_imgs',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('visual_search_loop_images.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(visual_search_imgs)  # add the loop to the experiment
            thisVisual_search_img = visual_search_imgs.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisVisual_search_img.rgb)
            if thisVisual_search_img != None:
                for paramName in thisVisual_search_img:
                    globals()[paramName] = thisVisual_search_img[paramName]
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            
            for thisVisual_search_img in visual_search_imgs:
                currentLoop = visual_search_imgs
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                if thisSession is not None:
                    # if running in a Session with a Liaison client, send data up to now
                    thisSession.sendExperimentData()
                # abbreviate parameter names if possible (e.g. rgb = thisVisual_search_img.rgb)
                if thisVisual_search_img != None:
                    for paramName in thisVisual_search_img:
                        globals()[paramName] = thisVisual_search_img[paramName]
                thisExp.nextEntry()
                
            # completed 1.0 repeats of 'visual_search_imgs'
            
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # get names of stimulus parameters
            if visual_search_imgs.trialList in ([], [None], None):
                params = []
            else:
                params = visual_search_imgs.trialList[0].keys()
            # save data for this loop
            visual_search_imgs.saveAsExcel(filename + '.xlsx', sheetName='visual_search_imgs',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            thisExp.nextEntry()
            
        # completed modules["module_2"]["tests"]["test_5"]["selected"] repeats of 'MODULE_2_TEST_5'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if MODULE_2_TEST_5.trialList in ([], [None], None):
            params = []
        else:
            params = MODULE_2_TEST_5.trialList[0].keys()
        # save data for this loop
        MODULE_2_TEST_5.saveAsExcel(filename + '.xlsx', sheetName='MODULE_2_TEST_5',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
    # completed modules["module_2"]["selected"] repeats of 'MODULE_2'
    
    
    # set up handler to look after randomisation of conditions etc
    MODULE_3 = data.TrialHandler2(
        name='MODULE_3',
        nReps=modules["module_3"]["selected"], 
        method='sequential', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=[None], 
        seed=None, 
    )
    thisExp.addLoop(MODULE_3)  # add the loop to the experiment
    thisMODULE_3 = MODULE_3.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisMODULE_3.rgb)
    if thisMODULE_3 != None:
        for paramName in thisMODULE_3:
            globals()[paramName] = thisMODULE_3[paramName]
    
    for thisMODULE_3 in MODULE_3:
        currentLoop = MODULE_3
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_3.rgb)
        if thisMODULE_3 != None:
            for paramName in thisMODULE_3:
                globals()[paramName] = thisMODULE_3[paramName]
        
        # set up handler to look after randomisation of conditions etc
        MODULE_3_TEST_1 = data.TrialHandler2(
            name='MODULE_3_TEST_1',
            nReps=modules["module_3"]["tests"]["test_1"]["selected"], 
            method='sequential', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=[None], 
            seed=None, 
        )
        thisExp.addLoop(MODULE_3_TEST_1)  # add the loop to the experiment
        thisMODULE_3_TEST_1 = MODULE_3_TEST_1.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_3_TEST_1.rgb)
        if thisMODULE_3_TEST_1 != None:
            for paramName in thisMODULE_3_TEST_1:
                globals()[paramName] = thisMODULE_3_TEST_1[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisMODULE_3_TEST_1 in MODULE_3_TEST_1:
            currentLoop = MODULE_3_TEST_1
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisMODULE_3_TEST_1.rgb)
            if thisMODULE_3_TEST_1 != None:
                for paramName in thisMODULE_3_TEST_1:
                    globals()[paramName] = thisMODULE_3_TEST_1[paramName]
            
            # set up handler to look after randomisation of conditions etc
            pupilometry_instructions = data.TrialHandler2(
                name='pupilometry_instructions',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/pupilometry_task_instructions.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(pupilometry_instructions)  # add the loop to the experiment
            thisPupilometry_instruction = pupilometry_instructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisPupilometry_instruction.rgb)
            if thisPupilometry_instruction != None:
                for paramName in thisPupilometry_instruction:
                    globals()[paramName] = thisPupilometry_instruction[paramName]
            
            for thisPupilometry_instruction in pupilometry_instructions:
                currentLoop = pupilometry_instructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                # abbreviate parameter names if possible (e.g. rgb = thisPupilometry_instruction.rgb)
                if thisPupilometry_instruction != None:
                    for paramName in thisPupilometry_instruction:
                        globals()[paramName] = thisPupilometry_instruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(pupilometry_instructions, data.TrialHandler2) and thisPupilometry_instruction.thisN != pupilometry_instructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                pupilometry_instructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   pupilometry_instructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   pupilometry_instructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   pupilometry_instructions.addData('button_next_instruction_2.timesOn', "")
                   pupilometry_instructions.addData('button_next_instruction_2.timesOff', "")
                pupilometry_instructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   pupilometry_instructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   pupilometry_instructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   pupilometry_instructions.addData('button_previous_instruction_2.timesOn', "")
                   pupilometry_instructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                pupilometry_instructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    pupilometry_instructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    pupilometry_instructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
            # completed 1.0 repeats of 'pupilometry_instructions'
            
            
            # set up handler to look after randomisation of conditions etc
            pupilometry_config = data.TrialHandler2(
                name='pupilometry_config',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('pupilometry_colors_and_sequence.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(pupilometry_config)  # add the loop to the experiment
            thisPupilometry_config = pupilometry_config.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisPupilometry_config.rgb)
            if thisPupilometry_config != None:
                for paramName in thisPupilometry_config:
                    globals()[paramName] = thisPupilometry_config[paramName]
            
            for thisPupilometry_config in pupilometry_config:
                currentLoop = pupilometry_config
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                # abbreviate parameter names if possible (e.g. rgb = thisPupilometry_config.rgb)
                if thisPupilometry_config != None:
                    for paramName in thisPupilometry_config:
                        globals()[paramName] = thisPupilometry_config[paramName]
                
                # --- Prepare to start Routine "PUPILOMETRY_TASK_adaptation_period" ---
                # create an object to store info about Routine PUPILOMETRY_TASK_adaptation_period
                PUPILOMETRY_TASK_adaptation_period = data.Routine(
                    name='PUPILOMETRY_TASK_adaptation_period',
                    components=[key_resp_23],
                )
                PUPILOMETRY_TASK_adaptation_period.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_25
                win.color = "black"
                # create starting attributes for key_resp_23
                key_resp_23.keys = []
                key_resp_23.rt = []
                _key_resp_23_allKeys = []
                # store start times for PUPILOMETRY_TASK_adaptation_period
                PUPILOMETRY_TASK_adaptation_period.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                PUPILOMETRY_TASK_adaptation_period.tStart = globalClock.getTime(format='float')
                PUPILOMETRY_TASK_adaptation_period.status = STARTED
                thisExp.addData('PUPILOMETRY_TASK_adaptation_period.started', PUPILOMETRY_TASK_adaptation_period.tStart)
                PUPILOMETRY_TASK_adaptation_period.maxDuration = None
                # keep track of which components have finished
                PUPILOMETRY_TASK_adaptation_periodComponents = PUPILOMETRY_TASK_adaptation_period.components
                for thisComponent in PUPILOMETRY_TASK_adaptation_period.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "PUPILOMETRY_TASK_adaptation_period" ---
                # if trial has changed, end Routine now
                if isinstance(pupilometry_config, data.TrialHandler2) and thisPupilometry_config.thisN != pupilometry_config.thisTrial.thisN:
                    continueRoutine = False
                PUPILOMETRY_TASK_adaptation_period.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    # Run 'Each Frame' code from code_25
                    if not hasattr(thisExp, 'last_print_time'):
                        thisExp.last_print_time = 0  # Inicializa la variable de tiempo
                    
                    if t - thisExp.last_print_time >= 1:  # Se ejecuta cada 10 segundos
                        print(adaptation_time - int(t))
                        thisExp.last_print_time = t  # Actualiza el último tiempo de impresión
                    
                    if t>adaptation_time:
                        continueRoutine = False
                    
                    # *key_resp_23* updates
                    waitOnFlip = False
                    
                    # if key_resp_23 is starting this frame...
                    if key_resp_23.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_23.frameNStart = frameN  # exact frame index
                        key_resp_23.tStart = t  # local t and not account for scr refresh
                        key_resp_23.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_23, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'key_resp_23.started')
                        # update status
                        key_resp_23.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_23.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_23.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_23.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_23.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_23_allKeys.extend(theseKeys)
                        if len(_key_resp_23_allKeys):
                            key_resp_23.keys = _key_resp_23_allKeys[-1].name  # just the last key pressed
                            key_resp_23.rt = _key_resp_23_allKeys[-1].rt
                            key_resp_23.duration = _key_resp_23_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        PUPILOMETRY_TASK_adaptation_period.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in PUPILOMETRY_TASK_adaptation_period.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "PUPILOMETRY_TASK_adaptation_period" ---
                for thisComponent in PUPILOMETRY_TASK_adaptation_period.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for PUPILOMETRY_TASK_adaptation_period
                PUPILOMETRY_TASK_adaptation_period.tStop = globalClock.getTime(format='float')
                PUPILOMETRY_TASK_adaptation_period.tStopRefresh = tThisFlipGlobal
                thisExp.addData('PUPILOMETRY_TASK_adaptation_period.stopped', PUPILOMETRY_TASK_adaptation_period.tStop)
                # check responses
                if key_resp_23.keys in ['', [], None]:  # No response was made
                    key_resp_23.keys = None
                pupilometry_config.addData('key_resp_23.keys',key_resp_23.keys)
                if key_resp_23.keys != None:  # we had a response
                    pupilometry_config.addData('key_resp_23.rt', key_resp_23.rt)
                    pupilometry_config.addData('key_resp_23.duration', key_resp_23.duration)
                # the Routine "PUPILOMETRY_TASK_adaptation_period" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
                
                # --- Prepare to start Routine "PUPILOMETRY_TASK_flash" ---
                # create an object to store info about Routine PUPILOMETRY_TASK_flash
                PUPILOMETRY_TASK_flash = data.Routine(
                    name='PUPILOMETRY_TASK_flash',
                    components=[text_4, key_resp_24],
                )
                PUPILOMETRY_TASK_flash.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_24
                win.color = color
                thisExp.addData(f"{color}StartTime", time.time())
                # create starting attributes for key_resp_24
                key_resp_24.keys = []
                key_resp_24.rt = []
                _key_resp_24_allKeys = []
                # store start times for PUPILOMETRY_TASK_flash
                PUPILOMETRY_TASK_flash.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                PUPILOMETRY_TASK_flash.tStart = globalClock.getTime(format='float')
                PUPILOMETRY_TASK_flash.status = STARTED
                thisExp.addData('PUPILOMETRY_TASK_flash.started', PUPILOMETRY_TASK_flash.tStart)
                PUPILOMETRY_TASK_flash.maxDuration = None
                # keep track of which components have finished
                PUPILOMETRY_TASK_flashComponents = PUPILOMETRY_TASK_flash.components
                for thisComponent in PUPILOMETRY_TASK_flash.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "PUPILOMETRY_TASK_flash" ---
                # if trial has changed, end Routine now
                if isinstance(pupilometry_config, data.TrialHandler2) and thisPupilometry_config.thisN != pupilometry_config.thisTrial.thisN:
                    continueRoutine = False
                PUPILOMETRY_TASK_flash.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    # Run 'Each Frame' code from code_24
                    if t>flash_time:
                        continueRoutine = False
                    
                    # *text_4* updates
                    
                    # if text_4 is starting this frame...
                    if text_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_4.frameNStart = frameN  # exact frame index
                        text_4.tStart = t  # local t and not account for scr refresh
                        text_4.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_4, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'text_4.started')
                        # update status
                        text_4.status = STARTED
                        text_4.setAutoDraw(True)
                    
                    # if text_4 is active this frame...
                    if text_4.status == STARTED:
                        # update params
                        text_4.setText('', log=False)
                    
                    # if text_4 is stopping this frame...
                    if text_4.status == STARTED:
                        # is it time to stop? (based on global clock, using actual start)
                        if tThisFlipGlobal > text_4.tStartRefresh + flash_time-frameTolerance:
                            # keep track of stop time/frame for later
                            text_4.tStop = t  # not accounting for scr refresh
                            text_4.tStopRefresh = tThisFlipGlobal  # on global time
                            text_4.frameNStop = frameN  # exact frame index
                            # add timestamp to datafile
                            thisExp.timestampOnFlip(win, 'text_4.stopped')
                            # update status
                            text_4.status = FINISHED
                            text_4.setAutoDraw(False)
                    
                    # *key_resp_24* updates
                    waitOnFlip = False
                    
                    # if key_resp_24 is starting this frame...
                    if key_resp_24.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_24.frameNStart = frameN  # exact frame index
                        key_resp_24.tStart = t  # local t and not account for scr refresh
                        key_resp_24.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_24, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'key_resp_24.started')
                        # update status
                        key_resp_24.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_24.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_24.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_24.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_24.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_24_allKeys.extend(theseKeys)
                        if len(_key_resp_24_allKeys):
                            key_resp_24.keys = _key_resp_24_allKeys[-1].name  # just the last key pressed
                            key_resp_24.rt = _key_resp_24_allKeys[-1].rt
                            key_resp_24.duration = _key_resp_24_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        PUPILOMETRY_TASK_flash.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in PUPILOMETRY_TASK_flash.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "PUPILOMETRY_TASK_flash" ---
                for thisComponent in PUPILOMETRY_TASK_flash.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for PUPILOMETRY_TASK_flash
                PUPILOMETRY_TASK_flash.tStop = globalClock.getTime(format='float')
                PUPILOMETRY_TASK_flash.tStopRefresh = tThisFlipGlobal
                thisExp.addData('PUPILOMETRY_TASK_flash.stopped', PUPILOMETRY_TASK_flash.tStop)
                # Run 'End Routine' code from code_24
                win.color = "grey"
                # check responses
                if key_resp_24.keys in ['', [], None]:  # No response was made
                    key_resp_24.keys = None
                pupilometry_config.addData('key_resp_24.keys',key_resp_24.keys)
                if key_resp_24.keys != None:  # we had a response
                    pupilometry_config.addData('key_resp_24.rt', key_resp_24.rt)
                    pupilometry_config.addData('key_resp_24.duration', key_resp_24.duration)
                # the Routine "PUPILOMETRY_TASK_flash" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
            # completed 1.0 repeats of 'pupilometry_config'
            
            thisExp.nextEntry()
            
        # completed modules["module_3"]["tests"]["test_1"]["selected"] repeats of 'MODULE_3_TEST_1'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if MODULE_3_TEST_1.trialList in ([], [None], None):
            params = []
        else:
            params = MODULE_3_TEST_1.trialList[0].keys()
        # save data for this loop
        MODULE_3_TEST_1.saveAsExcel(filename + '.xlsx', sheetName='MODULE_3_TEST_1',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
        
        # set up handler to look after randomisation of conditions etc
        MODULE_3_TEST_2 = data.TrialHandler2(
            name='MODULE_3_TEST_2',
            nReps=modules["module_3"]["tests"]["test_2"]["selected"], 
            method='sequential', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=[None], 
            seed=None, 
        )
        thisExp.addLoop(MODULE_3_TEST_2)  # add the loop to the experiment
        thisMODULE_3_TEST_2 = MODULE_3_TEST_2.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisMODULE_3_TEST_2.rgb)
        if thisMODULE_3_TEST_2 != None:
            for paramName in thisMODULE_3_TEST_2:
                globals()[paramName] = thisMODULE_3_TEST_2[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisMODULE_3_TEST_2 in MODULE_3_TEST_2:
            currentLoop = MODULE_3_TEST_2
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisMODULE_3_TEST_2.rgb)
            if thisMODULE_3_TEST_2 != None:
                for paramName in thisMODULE_3_TEST_2:
                    globals()[paramName] = thisMODULE_3_TEST_2[paramName]
            
            # set up handler to look after randomisation of conditions etc
            fearful_and_affective_images_insructions = data.TrialHandler2(
                name='fearful_and_affective_images_insructions',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('instructions/fearful_and_affective_images_instrucitons.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(fearful_and_affective_images_insructions)  # add the loop to the experiment
            thisFearful_and_affective_images_insruction = fearful_and_affective_images_insructions.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisFearful_and_affective_images_insruction.rgb)
            if thisFearful_and_affective_images_insruction != None:
                for paramName in thisFearful_and_affective_images_insruction:
                    globals()[paramName] = thisFearful_and_affective_images_insruction[paramName]
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            
            for thisFearful_and_affective_images_insruction in fearful_and_affective_images_insructions:
                currentLoop = fearful_and_affective_images_insructions
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                if thisSession is not None:
                    # if running in a Session with a Liaison client, send data up to now
                    thisSession.sendExperimentData()
                # abbreviate parameter names if possible (e.g. rgb = thisFearful_and_affective_images_insruction.rgb)
                if thisFearful_and_affective_images_insruction != None:
                    for paramName in thisFearful_and_affective_images_insruction:
                        globals()[paramName] = thisFearful_and_affective_images_insruction[paramName]
                
                # --- Prepare to start Routine "INSTRUCTIONS" ---
                # create an object to store info about Routine INSTRUCTIONS
                INSTRUCTIONS = data.Routine(
                    name='INSTRUCTIONS',
                    components=[logo_bio_2, logo_compneurolab_2, text_title_2, text_instructions_2, button_next_instruction_2, button_previous_instruction_2, key_resp_skip_instructions_2],
                )
                INSTRUCTIONS.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_9
                win.color = "grey"
                
                
                instruction_no = 0
                messages_instructions = [title]
                for i in range(1, 6):
                    var_name = f"instruction_{i}"
                    if var_name in globals():
                        instruction = globals()[var_name]
                        if instruction: # Si la instrucción no esta vacía se añade a la lista que aparecera por pantalla
                            messages_instructions.append(instruction)
                print(f'Lista de instrucciones cargada: {messages_instructions}')
                # reset button_next_instruction_2 to account for continued clicks & clear times on/off
                button_next_instruction_2.reset()
                # reset button_previous_instruction_2 to account for continued clicks & clear times on/off
                button_previous_instruction_2.reset()
                # create starting attributes for key_resp_skip_instructions_2
                key_resp_skip_instructions_2.keys = []
                key_resp_skip_instructions_2.rt = []
                _key_resp_skip_instructions_2_allKeys = []
                # store start times for INSTRUCTIONS
                INSTRUCTIONS.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                INSTRUCTIONS.tStart = globalClock.getTime(format='float')
                INSTRUCTIONS.status = STARTED
                thisExp.addData('INSTRUCTIONS.started', INSTRUCTIONS.tStart)
                INSTRUCTIONS.maxDuration = None
                # keep track of which components have finished
                INSTRUCTIONSComponents = INSTRUCTIONS.components
                for thisComponent in INSTRUCTIONS.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "INSTRUCTIONS" ---
                # if trial has changed, end Routine now
                if isinstance(fearful_and_affective_images_insructions, data.TrialHandler2) and thisFearful_and_affective_images_insruction.thisN != fearful_and_affective_images_insructions.thisTrial.thisN:
                    continueRoutine = False
                INSTRUCTIONS.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    
                    # *logo_bio_2* updates
                    
                    # if logo_bio_2 is starting this frame...
                    if logo_bio_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_bio_2.frameNStart = frameN  # exact frame index
                        logo_bio_2.tStart = t  # local t and not account for scr refresh
                        logo_bio_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_bio_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_bio_2.status = STARTED
                        logo_bio_2.setAutoDraw(True)
                    
                    # if logo_bio_2 is active this frame...
                    if logo_bio_2.status == STARTED:
                        # update params
                        pass
                    
                    # *logo_compneurolab_2* updates
                    
                    # if logo_compneurolab_2 is starting this frame...
                    if logo_compneurolab_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logo_compneurolab_2.frameNStart = frameN  # exact frame index
                        logo_compneurolab_2.tStart = t  # local t and not account for scr refresh
                        logo_compneurolab_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logo_compneurolab_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logo_compneurolab_2.status = STARTED
                        logo_compneurolab_2.setAutoDraw(True)
                    
                    # if logo_compneurolab_2 is active this frame...
                    if logo_compneurolab_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_title_2* updates
                    
                    # if text_title_2 is starting this frame...
                    if text_title_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_title_2.frameNStart = frameN  # exact frame index
                        text_title_2.tStart = t  # local t and not account for scr refresh
                        text_title_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_title_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_title_2.status = STARTED
                        text_title_2.setAutoDraw(True)
                    
                    # if text_title_2 is active this frame...
                    if text_title_2.status == STARTED:
                        # update params
                        pass
                    
                    # *text_instructions_2* updates
                    
                    # if text_instructions_2 is starting this frame...
                    if text_instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        text_instructions_2.frameNStart = frameN  # exact frame index
                        text_instructions_2.tStart = t  # local t and not account for scr refresh
                        text_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(text_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        text_instructions_2.status = STARTED
                        text_instructions_2.setAutoDraw(True)
                    
                    # if text_instructions_2 is active this frame...
                    if text_instructions_2.status == STARTED:
                        # update params
                        text_instructions_2.setText('', log=False)
                    # Run 'Each Frame' code from code_9
                    text_instructions_2.text = messages_instructions[instruction_no]
                        
                    if instruction_no == (len(messages_instructions) - 1):
                        button_next_instruction_2.opacity = 0
                        #button_next_instruction.status = PAUSED
                    else:
                        button_next_instruction_2.opacity = 1.0
                        #button_next_instruction.status = STARTED
                    
                    if instruction_no == 0:
                        button_previous_instruction_2.opacity = 0
                        #button_previous_instruction.status = PAUSED
                    else:
                        button_previous_instruction_2.opacity = 1.0
                        #button_previous_instruction.status = STARTED
                    
                    ###################################################
                    ####________________EVENTS_____________________####
                    ###################################################
                    
                    keys = event.getKeys()  # Cada llamada al buffer lo vacía
                    
                    if 'right' in keys:
                        if instruction_no < len(messages_instructions)-1:
                            instruction_no+=1
                    elif 'left' in keys:
                        if 0 < instruction_no:
                            instruction_no-=1
                    
                    # *button_next_instruction_2* updates
                    
                    # if button_next_instruction_2 is starting this frame...
                    if button_next_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_next_instruction_2.frameNStart = frameN  # exact frame index
                        button_next_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_next_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_next_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        button_next_instruction_2.status = STARTED
                        win.callOnFlip(button_next_instruction_2.buttonClock.reset)
                        button_next_instruction_2.setAutoDraw(True)
                    
                    # if button_next_instruction_2 is active this frame...
                    if button_next_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_next_instruction_2 has been pressed
                        if button_next_instruction_2.isClicked:
                            if not button_next_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_next_instruction_2.timesOn.append(button_next_instruction_2.buttonClock.getTime())
                                button_next_instruction_2.timesOff.append(button_next_instruction_2.buttonClock.getTime())
                            elif len(button_next_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_next_instruction_2.timesOff[-1] = button_next_instruction_2.buttonClock.getTime()
                            if not button_next_instruction_2.wasClicked:
                                # run callback code when button_next_instruction_2 is clicked
                                if instruction_no < len(messages_instructions)-1:
                                    instruction_no+=1
                    # take note of whether button_next_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_next_instruction_2.wasClicked = button_next_instruction_2.isClicked and button_next_instruction_2.status == STARTED
                    # *button_previous_instruction_2* updates
                    
                    # if button_previous_instruction_2 is starting this frame...
                    if button_previous_instruction_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                        # keep track of start time/frame for later
                        button_previous_instruction_2.frameNStart = frameN  # exact frame index
                        button_previous_instruction_2.tStart = t  # local t and not account for scr refresh
                        button_previous_instruction_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(button_previous_instruction_2, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'button_previous_instruction_2.started')
                        # update status
                        button_previous_instruction_2.status = STARTED
                        win.callOnFlip(button_previous_instruction_2.buttonClock.reset)
                        button_previous_instruction_2.setAutoDraw(True)
                    
                    # if button_previous_instruction_2 is active this frame...
                    if button_previous_instruction_2.status == STARTED:
                        # update params
                        pass
                        # check whether button_previous_instruction_2 has been pressed
                        if button_previous_instruction_2.isClicked:
                            if not button_previous_instruction_2.wasClicked:
                                # if this is a new click, store time of first click and clicked until
                                button_previous_instruction_2.timesOn.append(button_previous_instruction_2.buttonClock.getTime())
                                button_previous_instruction_2.timesOff.append(button_previous_instruction_2.buttonClock.getTime())
                            elif len(button_previous_instruction_2.timesOff):
                                # if click is continuing from last frame, update time of clicked until
                                button_previous_instruction_2.timesOff[-1] = button_previous_instruction_2.buttonClock.getTime()
                            if not button_previous_instruction_2.wasClicked:
                                # run callback code when button_previous_instruction_2 is clicked
                                if 0 < instruction_no:
                                    instruction_no-=1
                    # take note of whether button_previous_instruction_2 was clicked, so that next frame we know if clicks are new
                    button_previous_instruction_2.wasClicked = button_previous_instruction_2.isClicked and button_previous_instruction_2.status == STARTED
                    
                    # *key_resp_skip_instructions_2* updates
                    waitOnFlip = False
                    
                    # if key_resp_skip_instructions_2 is starting this frame...
                    if key_resp_skip_instructions_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_skip_instructions_2.frameNStart = frameN  # exact frame index
                        key_resp_skip_instructions_2.tStart = t  # local t and not account for scr refresh
                        key_resp_skip_instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_skip_instructions_2, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        key_resp_skip_instructions_2.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_skip_instructions_2.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_skip_instructions_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_skip_instructions_2.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_skip_instructions_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_skip_instructions_2_allKeys.extend(theseKeys)
                        if len(_key_resp_skip_instructions_2_allKeys):
                            key_resp_skip_instructions_2.keys = _key_resp_skip_instructions_2_allKeys[-1].name  # just the last key pressed
                            key_resp_skip_instructions_2.rt = _key_resp_skip_instructions_2_allKeys[-1].rt
                            key_resp_skip_instructions_2.duration = _key_resp_skip_instructions_2_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        INSTRUCTIONS.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in INSTRUCTIONS.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "INSTRUCTIONS" ---
                for thisComponent in INSTRUCTIONS.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for INSTRUCTIONS
                INSTRUCTIONS.tStop = globalClock.getTime(format='float')
                INSTRUCTIONS.tStopRefresh = tThisFlipGlobal
                thisExp.addData('INSTRUCTIONS.stopped', INSTRUCTIONS.tStop)
                fearful_and_affective_images_insructions.addData('button_next_instruction_2.numClicks', button_next_instruction_2.numClicks)
                if button_next_instruction_2.numClicks:
                   fearful_and_affective_images_insructions.addData('button_next_instruction_2.timesOn', button_next_instruction_2.timesOn)
                   fearful_and_affective_images_insructions.addData('button_next_instruction_2.timesOff', button_next_instruction_2.timesOff)
                else:
                   fearful_and_affective_images_insructions.addData('button_next_instruction_2.timesOn', "")
                   fearful_and_affective_images_insructions.addData('button_next_instruction_2.timesOff', "")
                fearful_and_affective_images_insructions.addData('button_previous_instruction_2.numClicks', button_previous_instruction_2.numClicks)
                if button_previous_instruction_2.numClicks:
                   fearful_and_affective_images_insructions.addData('button_previous_instruction_2.timesOn', button_previous_instruction_2.timesOn)
                   fearful_and_affective_images_insructions.addData('button_previous_instruction_2.timesOff', button_previous_instruction_2.timesOff)
                else:
                   fearful_and_affective_images_insructions.addData('button_previous_instruction_2.timesOn', "")
                   fearful_and_affective_images_insructions.addData('button_previous_instruction_2.timesOff', "")
                # check responses
                if key_resp_skip_instructions_2.keys in ['', [], None]:  # No response was made
                    key_resp_skip_instructions_2.keys = None
                fearful_and_affective_images_insructions.addData('key_resp_skip_instructions_2.keys',key_resp_skip_instructions_2.keys)
                if key_resp_skip_instructions_2.keys != None:  # we had a response
                    fearful_and_affective_images_insructions.addData('key_resp_skip_instructions_2.rt', key_resp_skip_instructions_2.rt)
                    fearful_and_affective_images_insructions.addData('key_resp_skip_instructions_2.duration', key_resp_skip_instructions_2.duration)
                # the Routine "INSTRUCTIONS" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
                thisExp.nextEntry()
                
            # completed 1.0 repeats of 'fearful_and_affective_images_insructions'
            
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # get names of stimulus parameters
            if fearful_and_affective_images_insructions.trialList in ([], [None], None):
                params = []
            else:
                params = fearful_and_affective_images_insructions.trialList[0].keys()
            # save data for this loop
            fearful_and_affective_images_insructions.saveAsExcel(filename + '.xlsx', sheetName='fearful_and_affective_images_insructions',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            
            # set up handler to look after randomisation of conditions etc
            imgs_loop = data.TrialHandler2(
                name='imgs_loop',
                nReps=1.0, 
                method='sequential', 
                extraInfo=expInfo, 
                originPath=-1, 
                trialList=data.importConditions('CEACO_image_selection.xlsx'), 
                seed=None, 
            )
            thisExp.addLoop(imgs_loop)  # add the loop to the experiment
            thisImgs_loop = imgs_loop.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisImgs_loop.rgb)
            if thisImgs_loop != None:
                for paramName in thisImgs_loop:
                    globals()[paramName] = thisImgs_loop[paramName]
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            
            for thisImgs_loop in imgs_loop:
                currentLoop = imgs_loop
                thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
                if thisSession is not None:
                    # if running in a Session with a Liaison client, send data up to now
                    thisSession.sendExperimentData()
                # abbreviate parameter names if possible (e.g. rgb = thisImgs_loop.rgb)
                if thisImgs_loop != None:
                    for paramName in thisImgs_loop:
                        globals()[paramName] = thisImgs_loop[paramName]
                
                # --- Prepare to start Routine "FEARFUL_AND_AFFECTIVE_IMAGES_TASK" ---
                # create an object to store info about Routine FEARFUL_AND_AFFECTIVE_IMAGES_TASK
                FEARFUL_AND_AFFECTIVE_IMAGES_TASK = data.Routine(
                    name='FEARFUL_AND_AFFECTIVE_IMAGES_TASK',
                    components=[img, key_resp_29, logs_29],
                )
                FEARFUL_AND_AFFECTIVE_IMAGES_TASK.status = NOT_STARTED
                continueRoutine = True
                # update component parameters for each repeat
                # Run 'Begin Routine' code from code_29
                
                def calcular_relacion_aspecto(ruta_archivo):
                    """
                    Calcula la relación de aspecto de una imagen a partir de su anchura y altura.
                    
                    :param ruta_archivo: Ruta completa de la imagen (str).
                    :return: Relación de aspecto (float).
                    """
                    try:
                        with Image.open(ruta_archivo) as img:
                            anchura, altura = img.size
                            return anchura / altura
                    except Exception as e:
                        raise ValueError(f"Error al abrir la imagen: {e}")
                
                relacion_aspecto = calcular_relacion_aspecto(ceaco_relative_path)
                
                if general_config["logs"]:
                    logs_29.text = f"Img path: {ceaco_relative_path}"
                img.setSize((relacion_aspecto,1))
                img.setImage(ceaco_relative_path)
                # create starting attributes for key_resp_29
                key_resp_29.keys = []
                key_resp_29.rt = []
                _key_resp_29_allKeys = []
                # store start times for FEARFUL_AND_AFFECTIVE_IMAGES_TASK
                FEARFUL_AND_AFFECTIVE_IMAGES_TASK.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
                FEARFUL_AND_AFFECTIVE_IMAGES_TASK.tStart = globalClock.getTime(format='float')
                FEARFUL_AND_AFFECTIVE_IMAGES_TASK.status = STARTED
                thisExp.addData('FEARFUL_AND_AFFECTIVE_IMAGES_TASK.started', FEARFUL_AND_AFFECTIVE_IMAGES_TASK.tStart)
                FEARFUL_AND_AFFECTIVE_IMAGES_TASK.maxDuration = None
                # keep track of which components have finished
                FEARFUL_AND_AFFECTIVE_IMAGES_TASKComponents = FEARFUL_AND_AFFECTIVE_IMAGES_TASK.components
                for thisComponent in FEARFUL_AND_AFFECTIVE_IMAGES_TASK.components:
                    thisComponent.tStart = None
                    thisComponent.tStop = None
                    thisComponent.tStartRefresh = None
                    thisComponent.tStopRefresh = None
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED
                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")
                frameN = -1
                
                # --- Run Routine "FEARFUL_AND_AFFECTIVE_IMAGES_TASK" ---
                # if trial has changed, end Routine now
                if isinstance(imgs_loop, data.TrialHandler2) and thisImgs_loop.thisN != imgs_loop.thisTrial.thisN:
                    continueRoutine = False
                FEARFUL_AND_AFFECTIVE_IMAGES_TASK.forceEnded = routineForceEnded = not continueRoutine
                while continueRoutine:
                    # get current time
                    t = routineTimer.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                    # update/draw components on each frame
                    # Run 'Each Frame' code from code_29
                    if t>autonomic_response_basal_time + autonomic_response_image_time + autonomic_response_recovery_time:
                        continueRoutine = False
                    
                    # *img* updates
                    
                    # if img is starting this frame...
                    if img.status == NOT_STARTED and tThisFlip >= autonomic_response_basal_time-frameTolerance:
                        # keep track of start time/frame for later
                        img.frameNStart = frameN  # exact frame index
                        img.tStart = t  # local t and not account for scr refresh
                        img.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(img, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'img.started')
                        # update status
                        img.status = STARTED
                        img.setAutoDraw(True)
                    
                    # if img is active this frame...
                    if img.status == STARTED:
                        # update params
                        pass
                    
                    # if img is stopping this frame...
                    if img.status == STARTED:
                        # is it time to stop? (based on global clock, using actual start)
                        if tThisFlipGlobal > img.tStartRefresh + autonomic_response_image_time-frameTolerance:
                            # keep track of stop time/frame for later
                            img.tStop = t  # not accounting for scr refresh
                            img.tStopRefresh = tThisFlipGlobal  # on global time
                            img.frameNStop = frameN  # exact frame index
                            # add timestamp to datafile
                            thisExp.timestampOnFlip(win, 'img.stopped')
                            # update status
                            img.status = FINISHED
                            img.setAutoDraw(False)
                    
                    # *key_resp_29* updates
                    waitOnFlip = False
                    
                    # if key_resp_29 is starting this frame...
                    if key_resp_29.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        key_resp_29.frameNStart = frameN  # exact frame index
                        key_resp_29.tStart = t  # local t and not account for scr refresh
                        key_resp_29.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(key_resp_29, 'tStartRefresh')  # time at next scr refresh
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'key_resp_29.started')
                        # update status
                        key_resp_29.status = STARTED
                        # keyboard checking is just starting
                        waitOnFlip = True
                        win.callOnFlip(key_resp_29.clock.reset)  # t=0 on next screen flip
                        win.callOnFlip(key_resp_29.clearEvents, eventType='keyboard')  # clear events on next screen flip
                    if key_resp_29.status == STARTED and not waitOnFlip:
                        theseKeys = key_resp_29.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                        _key_resp_29_allKeys.extend(theseKeys)
                        if len(_key_resp_29_allKeys):
                            key_resp_29.keys = _key_resp_29_allKeys[-1].name  # just the last key pressed
                            key_resp_29.rt = _key_resp_29_allKeys[-1].rt
                            key_resp_29.duration = _key_resp_29_allKeys[-1].duration
                            # a response ends the routine
                            continueRoutine = False
                    
                    # *logs_29* updates
                    
                    # if logs_29 is starting this frame...
                    if logs_29.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        logs_29.frameNStart = frameN  # exact frame index
                        logs_29.tStart = t  # local t and not account for scr refresh
                        logs_29.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(logs_29, 'tStartRefresh')  # time at next scr refresh
                        # update status
                        logs_29.status = STARTED
                        logs_29.setAutoDraw(True)
                    
                    # if logs_29 is active this frame...
                    if logs_29.status == STARTED:
                        # update params
                        pass
                    
                    # check for quit (typically the Esc key)
                    if defaultKeyboard.getKeys(keyList=["escape"]):
                        thisExp.status = FINISHED
                    if thisExp.status == FINISHED or endExpNow:
                        endExperiment(thisExp, win=win)
                        return
                    # pause experiment here if requested
                    if thisExp.status == PAUSED:
                        pauseExperiment(
                            thisExp=thisExp, 
                            win=win, 
                            timers=[routineTimer], 
                            playbackComponents=[]
                        )
                        # skip the frame we paused on
                        continue
                    
                    # check if all components have finished
                    if not continueRoutine:  # a component has requested a forced-end of Routine
                        FEARFUL_AND_AFFECTIVE_IMAGES_TASK.forceEnded = routineForceEnded = True
                        break
                    continueRoutine = False  # will revert to True if at least one component still running
                    for thisComponent in FEARFUL_AND_AFFECTIVE_IMAGES_TASK.components:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished
                    
                    # refresh the screen
                    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                        win.flip()
                
                # --- Ending Routine "FEARFUL_AND_AFFECTIVE_IMAGES_TASK" ---
                for thisComponent in FEARFUL_AND_AFFECTIVE_IMAGES_TASK.components:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store stop times for FEARFUL_AND_AFFECTIVE_IMAGES_TASK
                FEARFUL_AND_AFFECTIVE_IMAGES_TASK.tStop = globalClock.getTime(format='float')
                FEARFUL_AND_AFFECTIVE_IMAGES_TASK.tStopRefresh = tThisFlipGlobal
                thisExp.addData('FEARFUL_AND_AFFECTIVE_IMAGES_TASK.stopped', FEARFUL_AND_AFFECTIVE_IMAGES_TASK.tStop)
                # check responses
                if key_resp_29.keys in ['', [], None]:  # No response was made
                    key_resp_29.keys = None
                imgs_loop.addData('key_resp_29.keys',key_resp_29.keys)
                if key_resp_29.keys != None:  # we had a response
                    imgs_loop.addData('key_resp_29.rt', key_resp_29.rt)
                    imgs_loop.addData('key_resp_29.duration', key_resp_29.duration)
                # the Routine "FEARFUL_AND_AFFECTIVE_IMAGES_TASK" was not non-slip safe, so reset the non-slip timer
                routineTimer.reset()
                thisExp.nextEntry()
                
            # completed 1.0 repeats of 'imgs_loop'
            
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # get names of stimulus parameters
            if imgs_loop.trialList in ([], [None], None):
                params = []
            else:
                params = imgs_loop.trialList[0].keys()
            # save data for this loop
            imgs_loop.saveAsExcel(filename + '.xlsx', sheetName='imgs_loop',
                stimOut=params,
                dataOut=['n','all_mean','all_std', 'all_raw'])
            thisExp.nextEntry()
            
        # completed modules["module_3"]["tests"]["test_2"]["selected"] repeats of 'MODULE_3_TEST_2'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # get names of stimulus parameters
        if MODULE_3_TEST_2.trialList in ([], [None], None):
            params = []
        else:
            params = MODULE_3_TEST_2.trialList[0].keys()
        # save data for this loop
        MODULE_3_TEST_2.saveAsExcel(filename + '.xlsx', sheetName='MODULE_3_TEST_2',
            stimOut=params,
            dataOut=['n','all_mean','all_std', 'all_raw'])
    # completed modules["module_3"]["selected"] repeats of 'MODULE_3'
    
    # Run 'End Experiment' code from GLOBAL_VARIABLES_AND_FUNCTIONS
    staircase_data_filename = f"./data/{expInfo['participant']}/sf_staircase_data_{expInfo['participant']}.csv"
    generate_staircase_test_graph(results_csv_path=staircase_data_filename, test_var_name='spatial_frequency')
    staircase_data_filename = f"./data/{expInfo['participant']}/contrast_staircase_data_{expInfo['participant']}.csv"
    generate_staircase_test_graph(results_csv_path=staircase_data_filename, test_var_name='contrast')
    staircase_data_filename = f"./data/{expInfo['participant']}/saturation_staircase_data_{expInfo['participant']}_green.csv"
    generate_staircase_test_graph(results_csv_path=staircase_data_filename, test_var_name='saturation')
    staircase_data_filename = f"./data/{expInfo['participant']}/saturation_staircase_data_{expInfo['participant']}_red.csv"
    generate_staircase_test_graph(results_csv_path=staircase_data_filename, test_var_name='saturation')
    
    
    # mark experiment as finished
    endExperiment(thisExp, win=win)


def saveData(thisExp):
    """
    Save data from this experiment
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    filename = thisExp.dataFileName
    # these shouldn't be strictly necessary (should auto-save)
    thisExp.saveAsWideText(filename + '.csv', delim='auto')
    thisExp.saveAsPickle(filename)


def endExperiment(thisExp, win=None):
    """
    End this experiment, performing final shut down operations.
    
    This function does NOT close the window or end the Python process - use `quit` for this.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    """
    if win is not None:
        # remove autodraw from all current components
        win.clearAutoDraw()
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed
        win.flip()
    # return console logger level to WARNING
    logging.console.setLevel(logging.WARNING)
    # mark experiment handler as finished
    thisExp.status = FINISHED
    logging.flush()


def quit(thisExp, win=None, thisSession=None):
    """
    Fully quit, closing the window and ending the Python process.
    
    Parameters
    ==========
    win : psychopy.visual.Window
        Window to close.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    thisExp.abort()  # or data files will save again on exit
    # make sure everything is closed down
    if win is not None:
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed before quitting
        win.flip()
        win.close()
    logging.flush()
    if thisSession is not None:
        thisSession.stop()
    # terminate Python process
    core.quit()


# if running this experiment as a script...
if __name__ == '__main__':
    # call all functions in order
    expInfo = showExpInfoDlg(expInfo=expInfo)
    thisExp = setupData(expInfo=expInfo)
    logFile = setupLogging(filename=thisExp.dataFileName)
    win = setupWindow(expInfo=expInfo)
    setupDevices(expInfo=expInfo, thisExp=thisExp, win=win)
    run(
        expInfo=expInfo, 
        thisExp=thisExp, 
        win=win,
        globalClock='float'
    )
    saveData(thisExp=thisExp)
    quit(thisExp=thisExp, win=win)
