import json
import os
from tkinter import ttk, filedialog

CONFIG_FILE = "config_data/last_protocol_selection.json"

# Diccionario de configuración general
global general_config

general_config = { # Se sobreescribe si se encuentra fichero de configuracion anterior
    "feedback": False,
    "logs": False,
    "full_screen_noise": False,
    "gabor_texture": None,
    "pretest_standard_values": True,
    "remember_protocol": False,
    "tutorial":True
}

# Diccionario de módulos y tests
modules = {
    "module_1": {
        "name": "SPATIAL VISION",
        "selected": False,
        "tests": {
            "pretest": {"name": "Threshold estimation", "selected": False, "enabled": True},
            "test_1": {"name": "Spatial Frequency (SF)", "selected": False, "enabled": True},
            "test_2": {"name": "Color Vision (CV)", "selected": False, "enabled": True},
            "test_3": {"name": "Contrast Sensitivity (CS)", "selected": False, "enabled": True},
            "test_4": {"name": "Semantic SF", "selected": False, "enabled": True,
                "config": {
                    "screen_width_cm": None,
                    "distance_to_screen_cm": None,
                    "screen_resolution_dpi": None,
                    "magno_low_sf": None,
                    "magno_high_sf": None,
                    "parvo_low_sf": None,
                    "parvo_high_sf": None,
                    "neutro_low_sf": None,
                    "neutro_high_sf": None}
            },
            "test_5": {"name": "Semantic CS", "selected": False, "enabled": True},
            "test_6": {"name": "Semantic CV", "selected": False, "enabled": True}
        }
    },
    "module_2": {
        "name": "DYNAMIC VISION + EYE-TRACKING",
        "selected": False,
        "tests": {
            "test_1": {"name": "Fixation stability", "selected": False, "enabled": True},
            "test_2": {"name": "Flicker fusion threshold", "selected": False, "enabled": True},
            "test_3": {"name": "Saccadic & antisaccadic (eye-tracking)", "selected": False, "enabled": True},
            "test_4": {"name": "Smooth pursuit (eye-tracking)", "selected": False, "enabled": True},
            "test_5": {"name": "Visual search (eye-tracking)", "selected": False, "enabled": True}
        }
    },
    "module_3": {
        "name": "PUPILOMETRY + AUTONOMIC RESPONSE",
        "selected": False,
        "tests": {
            "test_1": {"name": "Elementary full-field stimuli", "selected": False, "enabled": True},
            "test_2": {"name": "Semantic (fearful & affective) stimuli", "selected": False, "enabled": True}
        }
    }
}


def load_saved_configuration():
    if os.path.exists(CONFIG_FILE):
        print("Previously used config file was found")
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("general_config", {}), data.get("modules", {})
    else:
        print("No config file was found. Showing default selection menu.")
    return None, None

def save_configuration(general_config, modules):
    with open(CONFIG_FILE, "w") as f:
            json.dump({
                "general_config": general_config,
                "modules": modules
            }, f, indent=4)

def reset_configuration():
    '''
    Resets the configuration by deleting the config file if it exists.
    '''
    
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)

def save_config_to_file():
    # Elegir archivo .json para guardar
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        title="Guardar configuración/protocolo"
    )
    