import json
from tkinter import filedialog, messagebox

CONFIG_FILE = "config_data/last_protocol_selection.json"


general_config = {
    "language": {
        "value": "en",
        "default": "en",
        "type": str,
        "options": ["en", "es", "eu"],
        "tooltip": {
            "es": "español",
            "en": "English",
            "eu": "Euskara"
        },
        "variable_display_name": {
            "es": "Idioma",
            "en": "Language",
            "eu": "Hizkuntza"
        }
    },
    "difficulty": {
        "value": None,
        "default": "medium",
        "type": "radio_button",
        "options": ["easy", "medium", "hard", "custom"],
        "variable_display_name": {
            "es": "Dificultad",
            "en": "Difficulty",
            "eu": "Zailtasuna"
        },
        "tooltip": {
            "es": "Dificultad del experimento",
            "en": "Experiment difficulty",
            "eu": "Esperimentuen zailtasuna"
        }
    },
    "start_tutorial": {
        "value": None,
        "default": True,
        "type": bool,
        "variable_display_name": {
            "es": "Tutorial general",
            "en": "General use tutorial",
            "eu": "Tutorial orokorra"
        },
        "tooltip": {
            "es": "Tutorial del experimento genérico. Enseña a usar la botonera y a navegar por la interfaz al principio del experimento.",
            "en": "General experiment tutorial. Teaches how to use the buttons and navigate the interface at the beginning of the experiment.",
            "eu": "Esperimentu orokorreko tutoriala. Nola erabili botoiak eta nola nabigatu interfazea erakusten du esperimentua hasi aurretik."
        }
    },
    "test_tutorial": {
        "value": None,
        "default": True,
        "type": bool,
        "variable_display_name": {
            "es": "Tutorial específico",
            "en": "Specific tutorial",
            "eu": "Tutorial zehatza"
        },
        "tooltip": {
            "es": "Tutorial de los experimentos específicos (únicamente para los que tengan tutorial disponible).",
            "en": "Specific experiment tutorial (only for those with available tutorial).",
            "eu": "Esperimentu zehatzaren tutoriala (eskuragarri dagoen tutoriala dutenentzat bakarrik)."
        }
    },
    # "modules": {
    #     "value": None,
    #     "default": "run all modules",
    #     "type": "radio_button",
    #     "options": ["run all modules", "select modules"],
    #     "variable_display_name": {
    #         "es": "Módulos",
    #         "en": "Modules",
    #         "eu": "Moduluak"
    #     },
    #     "tooltip": {
    #         "es": "",
    #         "en": "",
    #         "eu": ""
    #     }
    # },
 
}

advanced_config = {
    "feedback": {
        "value": False,
        "default": False,
        "type": bool,
        "options": [True, False],
        "tooltip": {
            "es": "Mostrar retroalimentación tras cada prueba",
            "en": "Show feedback after each test",
            "eu": "Eman atzeraelikadura proba bakoitzaren ondoren"
        },
        "variable_display_name": {
            "es": "Retroalimentación",
            "en": "Feedback",
            "eu": "Atzeraelikadura"
        }
    },
    "logs": {
        "value": False,
        "default": False,
        "type": bool,
        "options": [True, False],
        "tooltip": {
            "es": "Mostrar logs durante el experimento (para depuración)",
            "en": "Show logs during the experiment (for debugging)",
            "eu": "Erakutsi logak esperimentuan (debugging-erako)"
        },
        "variable_display_name": {
            "es": "Mostrar logs",
            "en": "Show logs",
            "eu": "Log-ak erakutsi"
        }
    },
    "full_screen_noise": {
        "value": False,
        "default": False,
        "type": bool,
        "options": [True, False],
        "tooltip": {
            "es": "Activar ruido a pantalla completa",
            "en": "Enable full screen noise",
            "eu": "Aktibatu pantaila osoko zarata"
        },
        "variable_display_name": {
            "es": "Ruido pantalla completa",
            "en": "Full screen noise",
            "eu": "Pantaila osoko zarata"
        }
    },
    # "gabor_texture": {
    #     "value": None,
    #     "default": "circle",
    #     "type": str,
    #     "options": ["circle", "gauss"],
    #     "tooltip": {
    #         "es": "Tipo de textura del estímulo Gabor",
    #         "en": "Type of Gabor stimulus texture",
    #         "eu": "Gabor estimuluaren testura mota"
    #     },
    #     "variable_display_name": {
    #         "es": "Textura Gabor",
    #         "en": "Gabor texture",
    #         "eu": "Gabor testura"
    #     }
    # },
    "pretest_standard_values": {
        "value": True,
        "default": True,
        "type": bool,
        "options": [True, False],
        "tooltip": {
            "es": "Usar valores estándar en el pretest",
            "en": "Use standard values in pretest",
            "eu": "Erabili balio estandarrak aurreprobako"
        },
        "variable_display_name": {
            "es": "Valores estándar en pretest",
            "en": "Standard pretest values",
            "eu": "Aurreprobaren balio estandarrak"
        }
    },
    "remember_protocol": {
        "value": False,
        "default": False,
        "type": bool,
        "options": [True, False],
        "tooltip": {
            "es": "Recordar protocolo entre sesiones",
            "en": "Remember protocol between sessions",
            "eu": "Gogoratu protokoloa saioen artean"
        },
        "variable_display_name": {
            "es": "Recordar protocolo",
            "en": "Remember protocol",
            "eu": "Protokoloa gogoratu"
        }
    },
    # "tutorial": {
    #     "value": False,
    #     "default": False,
    #     "type": bool,
    #     "options": [True, False],
    #     "tooltip": {
    #         "es": "Mostrar tutorial inicial",
    #         "en": "Show initial tutorial",
    #         "eu": "Erakutsi hasierako tutoriala"
    #     },
    #     "variable_display_name": {
    #         "es": "Tutorial inicial",
    #         "en": "Initial tutorial",
    #         "eu": "Hasierako tutoriala"
    #     }
    # },
    "screen_width_cm": {
        "value": None,
        "default": 50.0,
        "type": float,
        "options": None,
        "tooltip": {
            "es": "Anchura util de la pantalla en cm - se debe medir la anchura de la imgen durante las pruebas de sf",
            "en": "Screen width in cm - should measure the width of the image during sf tests",
            "eu": "Pantailaren zabalera cm-tan - sf probetan irudiaren zabalera neurtu behar da"
        },
        "variable_display_name": {
            "es": "Ancho pantalla (cm)",
            "en": "Screen width (cm)",
            "eu": "Pantaila zabala (cm)"
        }
    },
    "distance_to_screen_cm": {
        "value": None,
        "default": 96.0,
        "type": float,
        "options": None,
        "tooltip": {
            "es": "Distancia del participante a la pantalla en cm",
            "en": "Participant distance to screen in cm",
            "eu": "Parte-hartzailearen distantzia pantailara cm-tan"
        },
        "variable_display_name": {
            "es": "Distancia a pantalla (cm)",
            "en": "Distance to screen (cm)",
            "eu": "Pantailarako distantzia (cm)"
        }
    },
    "screen_resolution_dpi": {
        "value": None,
        "default": 96,
        "type": int,
        "options": None,
        "tooltip": {
            "es": "Resolución de la pantalla en DPI",
            "en": "Screen resolution in DPI",
            "eu": "Pantailaren bereizmena DPI-tan"
        },
        "variable_display_name": {
            "es": "Resolución pantalla (DPI)",
            "en": "Screen resolution (DPI)",
            "eu": "Pantailaren bereizmena (DPI)"
        }
    },
}

modules = {
    "module_1": {
        "name": {
            "es": "VISIÓN ESPACIAL",
            "en": "SPATIAL VISION",
            "eu": "IKUSMEN ESPAZIALA"
        },
        "selected": False,
        "tests": {
            "pretest": {
                "name": {
                    "es": "Pre-estimar umbral individual",
                    "en": "Pre-estimate individual thresholds (SF,CV,CS)",
                    "eu": "Atalasearen pre-estimazioa"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 3,
                "tooltip": {
                    "es": "Estimación del umbral inicial",
                    "en": "Initial threshold estimation",
                    "eu": "Hasierako atalasearen estimazioa"
                },
                "config": {
                    "n_reversals_to_average": {
                        "value": 4,
                        "default": 4,
                        "type": int,
                        "variable_display_name": {
                            "es": "Reversiones para promediar",
                            "en": "Reversals to average",
                            "eu": "Batezbesteko itzulketak"
                        },
                    },
                    "stop_reversals": {
                        "value": 5,
                        "default": 5,
                        "type": int,
                        "variable_display_name": {
                            "es": "Reversiones para detener",
                            "en": "Stop after reversals",
                            "eu": "Gehienezko itzulketak"
                        },
                        "tooltip": {
                            "es": "Número de reversiones tras las cuales termina el test",
                            "en": "Number of reversals before stopping the test",
                            "eu": "Proba amaitzeko itzulketak"
                        }
                    },
                    "staircase_noise_duration": {
                        "value": 0.5,
                        "default": 0.5,
                        "type": float,
                        "variable_display_name": {
                            "es": "Duración del ruido",
                            "en": "Noise duration",
                            "eu": "Zarata iraupena"
                        },
                        "tooltip": {
                            "es": "Duración del ruido en segundos en el test de umbral",
                            "en": "Noise duration in seconds in the staircase test",
                            "eu": "Zarata iraupena atalase-proban"
                        }
                    }
                }
            },
            "test_1": {
                "name": {
                    "es": "Frecuencia espacial (SF)",
                    "en": "Spatial Frequency (SF)",
                    "eu": "Maiztasun espaziala (SF)"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 2,
                "tooltip": {
                    "es": "Medición de frecuencia espacial",
                    "en": "Spatial frequency measurement",
                    "eu": "Maiztasun espazialaren neurketa"
                }
            },
            "test_2": {
                "name": {
                    "es": "Visión cromática (CV)",
                    "en": "Color Vision (CV)",
                    "eu": "Kolore ikusmena (CV)"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 2,
                "tooltip": {
                    "es": "Evaluación de visión cromática",
                    "en": "Color vision evaluation",
                    "eu": "Kolore ikusmenaren ebaluazioa"
                },
                "config": {
                    "default_sf": {
                        "value": True,
                        "default": True,
                        "type": bool,
                        "options": [True, False],
                        "variable_display_name": {
                            "es": "Usar SF estándar",
                            "en": "Use standard SF",
                            "eu": "Erabili SF estandarra"
                        },
                        "tooltip": {
                            "es": "Si se habilita la opción la SF durante la prueba de color será la definida en el campo inferior. Si se deshabilita, se usará la SF obtenida en el pretest para la prueba de color.",
                            "en": "If enabled, the SF during the color test will be the one defined in the field below. If disabled, the SF obtained in the pretest will be used.",
                            "eu": "Aukera gaituta badago, kolore-proban erabiliko den SF beheko eremuan definitutako izango da. Desgaituta badago, aurreproban lortutako SF erabiliko da."
                        }
                    },

                    "gabor_sf": {
                        "value": 100,
                        "default": 100,
                        "type": int,
                        "variable_display_name": {
                            "es": "Frecuencia espacial",
                            "en": "Spatial frequency",
                            "eu": "Maiztasun espaziala"
                        },
                        "tooltip": {
                            "es": "Frecuencia espacial del parche para la prueba de contraste",
                            "en": "Spatial frequency of the patch for the contrast test",
                            "eu": "Kontraste-probarako txertaketaren maiztasun espaziala"
                        },
                    },
            },
            },
            "test_3": {
                "name": {
                    "es": "Sensibilidad al contraste (CS)",
                    "en": "Contrast Sensitivity (CS)",
                    "eu": "Kontrastearekiko sentikortasuna (CS)"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 2,
                "tooltip": {
                    "es": "Evaluación de sensibilidad al contraste",
                    "en": "Contrast sensitivity evaluation",
                    "eu": "Kontrastearekiko sentikortasunaren ebaluazioa"
                },
                "config": {
                    "default_sf": {
                        "value": True,
                        "default": True,
                        "type": bool,
                        "options": [True, False],
                        "variable_display_name": {
                            "es": "Usar SF estándar",
                            "en": "Use standard SF",
                            "eu": "Erabili SF estandarra"
                        },
                        "tooltip": {
                            "es": "Si se habilita la opción la SF durante la prueba de contraste será la definida en el campo inferior. Si se deshabilita, se usará la SF obtenida en el pretest.",
                            "en": "If enabled, the SF during the contrast test will be the one defined in the field below. If disabled, the SF obtained in the pretest will be used.",
                            "eu": "Aukera gaituta badago, kontraste-proban erabiliko den SF beheko eremuan definitutako izango da. Desgaituta badago, aurreproban lortutako SF erabiliko da."
                        }
                    },

                    "gabor_sf": {
                        "value": 100,
                        "default": 100,
                        "type": int,
                        "variable_display_name": {
                            "es": "Frecuencia espacial",
                            "en": "Spatial frequency",
                            "eu": "Maiztasun espaziala"
                        },
                        "tooltip": {
                            "es": "Frecuencia espacial del parche para la prueba de contraste",
                            "en": "Spatial frequency of the patch for the contrast test",
                            "eu": "Kontraste-probarako txertaketaren maiztasun espaziala"
                        },
                    },
            },
            },
            "test_4": {
                "name": {
                    "es": "Frecuencia espacial semántica",
                    "en": "Semantic SF",
                    "eu": "Maiztasun espazial semantikoa"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 3,
                "tooltip": {
                    "es": "Evaluación semántica de la frecuencia espacial",
                    "en": "Semantic spatial frequency evaluation",
                    "eu": "Maiztasun espazialaren ebaluazio semantikoa"
                }
            },
            "test_5": {
                "name": {
                    "es": "Sensibilidad al contraste semántica",
                    "en": "Semantic CS",
                    "eu": "Kontraste sentikortasun semantikoa"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 3,
                "tooltip": {
                    "es": "Evaluación semántica de la sensibilidad al contraste",
                    "en": "Semantic contrast sensitivity evaluation",
                    "eu": "Kontraste sentikortasunaren ebaluazio semantikoa"
                }
            },
            "test_6": {
                "name": {
                    "es": "Visión cromática semántica",
                    "en": "Semantic CV",
                    "eu": "Kolore ikusmen semantikoa"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 3,
                "tooltip": {
                    "es": "Evaluación semántica de la visión cromática",
                    "en": "Semantic color vision evaluation",
                    "eu": "Kolore ikusmenaren ebaluazio semantikoa"
                }
            }
        },
        "config":{
            "grating": {
                "grating_mask": {
                    "value": "gauss",
                    "default": "gauss",
                    "type": str,
                    "options": ["gauss", "circle"],
                    "variable_display_name": {
                        "es": "Máscara Gabor",
                        "en": "Gabor Mask",
                        "eu": "Gabor maskara"
                    },
                    "tooltip": {
                        "es": "Tipo de máscara para el estímulo Gabor",
                        "en": "Type of mask used for Gabor stimulus",
                        "eu": "Gabor estimuluaren maskara mota"
                    }
                },
                "grating_size": {
                    "value": [0.5, 0.5],
                    "default": [0.5, 0.5],
                    "type": list,
                    "variable_display_name": {
                        "es": "Tamaño del estímulo Gabor",
                        "en": "Gabor stimulus size",
                        "eu": "Gabor estimuluaren tamaina"
                    },
                    "tooltip": {
                        "es": "Tamaño (ancho, alto) del estímulo Gabor",
                        "en": "Size (width, height) of the Gabor stimulus",
                        "eu": "Gabor estimuluaren tamaina (zabalera, altuera)"
                    }
                }
            },
            "general_settings": {
                "stim_time": {
                    "value": 2.0,
                    "default": 2.0,
                    "type": float,
                    "variable_display_name": {
                        "es": "Duración del estímulo",
                        "en": "Stimulus duration",
                        "eu": "Estimuluaren iraupena"
                    },
                    "tooltip": {
                        "es": "Tiempo durante el cual se muestra el estímulo (segundos)",
                        "en": "Time the stimulus is shown (in seconds)",
                        "eu": "Estimuluaren bistaratze-denbora (segundotan)"
                    }
                },
                "response_time": {
                    "value": 0.5,
                    "default": 0.5,
                    "type": float,
                    "variable_display_name": {
                        "es": "Tiempo de respuesta",
                        "en": "Response time",
                        "eu": "Erantzun denbora"
                    },
                    "tooltip": {
                        "es": "Tiempo que tiene el usuario para responder tras desaparecer el estímulo",
                        "en": "Time the user has to respond after the stimulus disappears",
                        "eu": "Estimuluaren desagerpenaren ondoren erabiltzaileak erantzuteko duen denbora"
                    }
                },
                "noise_type": {
                    "value": 2,
                    "default": 2,
                    "type": int,
                    "options": [1, 2],
                    "variable_display_name": {
                        "es": "Tipo de ruido",
                        "en": "Noise type",
                        "eu": "Zarata mota"
                    },
                    "tooltip": {
                        "es": "1: ruido en toda la pantalla, 2: solo sobre el estímulo",
                        "en": "1: full screen noise, 2: only over the stimulus",
                        "eu": "1: pantaila osoan, 2: estimuluaren gainean soilik"
                    }
                },
                "noise_field_size": {
                    "value": [1.75, 1.0],
                    "default": [1.75, 1.0],
                    "type": list,
                    "variable_display_name": {
                        "es": "Tamaño del campo de ruido",
                        "en": "Noise field size",
                        "eu": "Zarata eremuaren tamaina"
                    },
                    "tooltip": {
                        "es": "Área (ancho, alto) en la que se genera el ruido visual",
                        "en": "Area (width, height) where visual noise is generated",
                        "eu": "Zarata bisuala sortzen den eremua (zabalera, altuera)"
                    }
                },
                "noise_dots": {
                    "value": 25000,
                    "default": 25000,
                    "type": int,
                    "variable_display_name": {
                        "es": "Cantidad de puntos de ruido",
                        "en": "Noise dot count",
                        "eu": "Zarata puntu kopurua"
                    },
                    "tooltip": {
                        "es": "Cantidad total de puntos de ruido generados en pantalla",
                        "en": "Total number of noise dots generated on screen",
                        "eu": "Pantailan sortutako zarata puntu kopurua"
                    }
                },
                "sf_images_cpd_ranges": {
                    "value": [(1, 3), (4, 6), (10, 18)],
                    "default": [(1, 3), (4, 6), (10, 18)],
                    "type": list,
                    "variable_display_name": {
                        "es": "Rangos de CPD (frecuencia espacial)",
                        "en": "CPD ranges (spatial frequency)",
                        "eu": "CPD barrutiak (maiztasun espaziala)"
                    },
                    "tooltip": {
                        "es": "Lista de tuplas con rangos de frecuencias espaciales (ciclos por grado) para las imágenes",
                        "en": "List of tuples with spatial frequency ranges (cycles per degree) for image filtering",
                        "eu": "Maiztasun espazialeko barrutiak (graduko zikloak) irudien iragazketarako"
                    }
                }
            }
        }
    },
    "module_2": {
        "name": {
            "es": "VISIÓN DINÁMICA + SEGUIMIENTO OCULAR",
            "en": "DYNAMIC VISION + EYE-TRACKING",
            "eu": "IKUSMEN DINAMIKOA + BEGIAREN JARRAIPENA"
        },
        "selected": False,
        "tests": {
            "test_1": {
                "name": {
                    "es": "Estabilidad de la fijación",
                    "en": "Fixation stability",
                    "eu": "Finkapenaren egonkortasuna"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 1,
                "tooltip": {
                    "es": "Estabilidad de la fijación",
                    "en": "Fixation stability",
                    "eu": "Finkapenaren egonkortasuna"
                },
                "config": {
                    "eye_tracking_resting_state_time": {
                        "value": 30,
                        "default": 30,
                        "type": int,
                        "variable_display_name": {
                            "es": "Duración del estado en reposo",
                            "en": "Resting state duration",
                            "eu": "Atseden-egoeraren iraupena"
                        },
                        "tooltip": {
                            "es": "Tiempo (en segundos) durante el cual el participante permanece en reposo observando un punto fijo",
                            "en": "Time (in seconds) the participant stays at rest watching a fixation point",
                            "eu": "Parte-hartzailea puntu bati begira atseden-egoeran dagoen denbora (segundotan)"
                        }
                    },
                    "eye_tracking_resting_state_background_color": {
                        "value": "black",
                        "default": "black",
                        "type": 'color',
                        "variable_display_name": {
                            "es": "Color de fondo",
                            "en": "Background color",
                            "eu": "Atzeko planoaren kolorea"
                        },
                        "tooltip": {
                            "es": "Color de fondo de la pantalla durante el estado de reposo",
                            "en": "Background color of the screen during resting state",
                            "eu": "Atseden-egoerako pantailaren atzeko planoaren kolorea"
                        }
                    }
                }

            },
            "test_2": {
                "name": {
                    "es": "Umbral de fusión de parpadeo",
                    "en": "Flicker fusion threshold",
                    "eu": "Keinu-fusio atalasea"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 2,
                "tooltip": {
                    "es": "Umbral de fusión de parpadeo",
                    "en": "Flicker fusion threshold",
                    "eu": "Keinu-fusio atalasea"
                }
            },
            "test_3": {
                "name": {
                    "es": "Sacádicos y antisacádicos (eye-tracking)",
                    "en": "Saccadic & antisaccadic (eye-tracking)",
                    "eu": "Mugimendu sakadiko eta antisakadikoak (eye-tracking)"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 3,
                "tooltip": {
                    "es": "Movimientos sacádicos y antisacádicos (eye-tracking)",
                    "en": "Saccadic & antisaccadic movements (eye-tracking)",
                    "eu": "Mugimendu sakadiko eta antisakadikoak (eye-tracking)"
                },
                "config": {
                    
                }
            },
            "test_4": {
                "name": {
                    "es": "Seguimiento suave (eye-tracking)",
                    "en": "Smooth pursuit (eye-tracking)",
                    "eu": "Jarraipen leuna (eye-tracking)"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 1.5,
                "tooltip": {
                    "es": "Seguimiento suave (eye-tracking)",
                    "en": "Smooth pursuit (eye-tracking)",
                    "eu": "Jarraipen leuna (eye-tracking)"
                },
                "gif_source":"C:\\Users\\akoun\\Desktop\\Biocruces\\begibraintool\\src\\images\\gui_images\\module_1_example_2_compressed.gif",
                "config": {
                    "dot_size": {
                        "value": 0.01,
                        "default": 0.01,
                        "type": float,
                        "variable_display_name": {
                            "es": "Tamaño del punto principal (u)",
                            "en": "Main dot size (u)",
                            "eu": "Puntu nagusiaren tamaina (u)"
                        },
                        "tooltip": {
                            "es": "Tamaño del punto objetivo principal (en unidades de ventana)",
                            "en": "Size of the main target dot (in window units)",
                            "eu": "Helburuko puntu nagusiaren tamaina (leiho unitateetan)"
                        }
                    },
                    "enable_noise_dots": {
                        "value": True,
                        "default": True,
                        "type": bool,
                        "options": [True, False],
                        "variable_display_name": {
                            "es": "Activar puntos de ruido",
                            "en": "Enable noise dots",
                            "eu": "Aktibatu zarata puntuak"
                        },
                        "tooltip": {
                            "es": "Activar/desactivar los puntos de ruido que rodean al punto principal",
                            "en": "Enable/disable the noise dots surrounding the main dot",
                            "eu": "Aktibatu/desaktibatu puntu nagusiaren inguruko zarata puntuak"
                        }
                    },
                    "noise_dots_size": {
                        "value": 15,
                        "default": 15,
                        "type": float,
                        "variable_display_name": {
                            "es": "Tamaño de puntos de ruido (px)",
                            "en": "Noise dots size (px)",
                            "eu": "Zarata puntuen tamaina (px)"
                        },
                        "tooltip": {
                            "es": "Tamaño de los puntos de ruido (en píxeles) que rodean al punto principal",
                            "en": "Size of the noise dots (in pixel units) surrounding the main dot",
                            "eu": "Puntu nagusiaren inguruko zarata puntuen tamaina (px)"
                        }
                    },
                    "noise_dots_no": {
                        "value": 700,
                        "default": 700,
                        "type": int,
                        "variable_display_name": {
                            "es": "Número de puntos de ruido",
                            "en": "Noise dot count",
                            "eu": "Zarata puntu kopurua"
                        },
                        "tooltip": {
                            "es": "Número total de puntos de ruido en pantalla",
                            "en": "Total number of noise dots on screen",
                            "eu": "Pantailan dauden zarata puntu guztien kopurua"
                        }
                    },
                    "dot_speed": {
                        "value": 0.003,
                        "default": 0.003,
                        "type": float,
                        "variable_display_name": {
                            "es": "Velocidad del punto principal",
                            "en": "Main dot speed",
                            "eu": "Puntu nagusiaren abiadura"
                        },
                        "tooltip": {
                            "es": "Velocidad de desplazamiento del punto principal",
                            "en": "Movement speed of the main dot",
                            "eu": "Puntu nagusiaren mugimenduaren abiadura"
                        }
                    },
                    "noise_dots_speed": {
                        "value": 0.003,
                        "default": 0.003,
                        "type": float,
                        "variable_display_name": {
                            "es": "Velocidad de puntos de ruido",
                            "en": "Noise dots speed",
                            "eu": "Zarata puntuen abiadura"
                        },
                        "tooltip": {
                            "es": "Velocidad de desplazamiento de los puntos de ruido",
                            "en": "Movement speed of the noise dots",
                            "eu": "Zarata puntuen mugimenduaren abiadura"
                        }
                    },
                    "dot_color": {
                        "value": "white",
                        "default": "white",
                        "type": "color",
                        "variable_display_name": {
                            "es": "Color del punto principal",
                            "en": "Main dot color",
                            "eu": "Puntu nagusiaren kolorea"
                        },
                        "tooltip": {
                            "es": "Color del punto objetivo principal",
                            "en": "Color of the main target dot",
                            "eu": "Helburuko puntu nagusiaren kolorea"
                        }
                    },
                    "dot_border_color": {
                        "value": "red",
                        "default": "red",
                        "type": "color",
                        "variable_display_name": {
                            "es": "Color del borde del punto",
                            "en": "Dot border color",
                            "eu": "Puntuaren ertzaren kolorea"
                        },
                        "tooltip": {
                            "es": "Color del borde del punto principal",
                            "en": "Color of the border of the main dot",
                            "eu": "Puntu nagusiaren ertzaren kolorea"
                        }
                    },
                    "noise_dots_color": {
                        "value": "white",
                        "default": "white",
                        "type": "color",
                        "variable_display_name": {
                            "es": "Color de los puntos de ruido",
                            "en": "Noise dots color",
                            "eu": "Zarata puntuen kolorea"
                        },
                        "tooltip": {
                            "es": "Color de los puntos de ruido en la tarea",
                            "en": "Color of the noise dots in the task",
                            "eu": "Zarata puntuen kolorea atazan"
                        }
                    },
                    "noise_dots_lifetime": {
                        "value": 200,
                        "default": 200,
                        "type": int,
                        "variable_display_name": {
                            "es": "Vida útil de puntos de ruido",
                            "en": "Noise dots lifetime",
                            "eu": "Zarata puntuen iraupena"
                        },
                        "tooltip": {
                            "es": "Cuántos fotogramas vive cada punto de ruido antes de regenerarse",
                            "en": "How many frames each noise dot lives before being regenerated",
                            "eu": "Zarata puntu bakoitzak birsortu aurretik bizi dituen frame kopurua"
                        }
                    },
                    "background_color": {
                        "value": "white",
                        "default": "white",
                        "type": "color",
                        "variable_display_name": {
                            "es": "Color de fondo",
                            "en": "Background color",
                            "eu": "Atzeko planoaren kolorea"
                        },
                        "tooltip": {
                            "es": "Color de fondo de la pantalla durante la tarea",
                            "en": "Background color of the screen during the task",
                            "eu": "Ataza denbora pantailaren atzeko planoaren kolorea"
                        }
                    },
                    "field_size": {
                        "value": [1.4, 0.9],
                        "default": [1.4, 0.9],
                        "type": list,
                        "variable_display_name": {
                            "es": "Tamaño del campo visual",
                            "en": "Field size",
                            "eu": "Eremu ikusgaiaren tamaina"
                        },
                        "tooltip": {
                            "es": "Área visible donde se mueven los puntos",
                            "en": "Visible area where the dots move",
                            "eu": "Puntuak mugitzen diren ikus-eremua"
                        }
                    }
                }


            },
            "test_5": {
                "name": {
                    "es": "Búsqueda visual (eye-tracking)",
                    "en": "Visual search (eye-tracking)",
                    "eu": "Bilaketa bisuala (eye-tracking)"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 1,
                "tooltip": {
                    "es": "Búsqueda visual (eye-tracking)",
                    "en": "Visual search (eye-tracking)",
                    "eu": "Bilaketa bisuala (eye-tracking)"
                },
                "config": {
                    "visual_search_image_time": {
                        "value": 5.5,
                        "default": 5.5,
                        "type": float,
                        "variable_display_name": {
                            "es": "Duración de la imagen",
                            "en": "Image duration",
                            "eu": "Irudiaren iraupena"
                        },
                        "tooltip": {
                            "es": "Tiempo que la imagen de búsqueda visual permanece en pantalla (segundos)",
                            "en": "Time the visual search image remains on screen (seconds)",
                            "eu": "Bilaketa bisualaren irudia pantailan dagoen denbora (segundotan)"
                        }
                    },
                    "visual_search_wait_time": {
                        "value": 1.0,
                        "default": 1.0,
                        "type": float,
                        "variable_display_name": {
                            "es": "Tiempo de espera entre imágenes",
                            "en": "Wait time between images",
                            "eu": "Irudien arteko itxaron denbora"
                        },
                        "tooltip": {
                            "es": "Tiempo de espera entre la presentación de imágenes (segundos)",
                            "en": "Waiting time between image presentations (seconds)",
                            "eu": "Irudiak erakustearen arteko itxaron denbora (segundotan)"
                        }
                    }
                }

            },
            "test_6": {
                "name": {
                    "es": "Búsqueda visual dinámica(eye-tracking)",
                    "en": "Dynamic visual search (eye-tracking)",
                    "eu": "Bilaketa bisuala dinamikoa (eye-tracking)"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 1,
                "tooltip": {
                    "es": "Búsqueda visual con los discos rotando sobre sí mismos. Hay que encontrar el disco que rota en sentido contrario.",
                    "en": "Dynamic visual search with discs rotating on themselves. You have to find the disc that rotates in the opposite direction.",
                    "eu": "Bilaketa bisuala dinamikoa diskoak euren buruen inguruan biratzen. Aurkitu behar duzu norabide kontrakoan biratzen den diskoa."
                },
                "config": {
                    "visual_search_image_time": {
                        "value": 5.5,
                        "default": 5.5,
                        "type": float,
                        "variable_display_name": {
                            "es": "Duración de cada intento",
                            "en": "Trial duration",
                            "eu": "Iraupena"
                        },
                        "tooltip": {
                            "es": "Tiempo que los discos permanecen en pantalla (segundos)",
                            "en": "Time the visual search discs remain on screen (seconds)",
                            "eu": "Bilaketa bisualaren diskoak pantailan dagoen denbora (segundotan)"
                        }
                    },
                    "visual_search_wait_time": {
                        "value": 1.0,
                        "default": 1.0,
                        "type": float,
                        "variable_display_name": {
                            "es": "Tiempo de espera entre imágenes",
                            "en": "Wait time between images",
                            "eu": "Irudien arteko itxaron denbora"
                        },
                        "tooltip": {
                            "es": "Tiempo de espera entre la presentación de imágenes (segundos)",
                            "en": "Waiting time between image presentations (seconds)",
                            "eu": "Irudiak erakustearen arteko itxaron denbora (segundotan)"
                        }
                    },
                    "visual_search_rotation_speed": {
                        "value": 90,
                        "default": 90,
                        "type": int,
                        "variable_display_name": {
                            "es": "Velocidad de rotación (grados/segundos)",
                            "en": "Rotation speed (degrees/second)",
                            "eu": "Biraketa abiadura (gradu/segundo)"
                        },
                        "tooltip": {
                            "es": "Velocidad de rotación de los discos (grados por segundo)",
                            "en": "Rotation speed of the discs (degrees per second)",
                            "eu": "Diskoen biraketa abiadura (gradu segunduko)"
                        }
                    },
                    "visual_search_matrix_size": {
                        "value": [3, 3],
                        "default": [3, 3],
                        "type": list,
                        "variable_display_name": {
                            "es": "Tamaño de la matriz (filas, columnas)",
                            "en": "Matrix size (rows, columns)",
                            "eu": "Matrizearen tamaina (ilara, zutabe)"
                        },
                        "tooltip": {
                            "es": "Tamaño de la matriz de discos (número de filas y columnas)",
                            "en": "Matrix size (number of rows and columns)",
                            "eu": "Matrizearen tamaina (ilara eta zutabe kopurua)"
                        }
                    },
                    "disks_in_phase": {
                        "value": True,
                        "default": True,
                        "type": bool,
                        "variable_display_name": {
                            "es": "Discos en fase",
                            "en": "Disks in phase",
                            "eu": "Diskoak fasean"
                        },
                        "tooltip": {
                            "es": "Marcar la celda para que los discos giren todos en la misma fase. Lo contrario es que giren en fases aleatorias.",
                            "en": "Mark the cell for all disks to rotate in the same phase. The opposite is for them to rotate in random phases.",
                            "eu": "Markatu zelula disko guztiak fase berean biratzeko. Aurkakoa da fase aleatorioetan biratzea."
                        }
                    }
                }

            }
        }
    },
    "module_3": {
        "name": {
            "es": "PUPILOMETRÍA + RESPUESTA AUTONÓMICA",
            "en": "PUPILOMETRY + AUTONOMIC RESPONSE",
            "eu": "IKASLEOMETRIA + ERANTZUN AUTONOMOA"
        },
        "selected": False,
        "tests": {
            "test_1": {
                "name": {
                    "es": "Estímulos elementales a campo completo",
                    "en": "Elementary full-field stimuli",
                    "eu": "Eremu osoko estimulu elementalak"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 20,
                "tooltip": {
                    "es": "Estímulos elementales a campo completo",
                    "en": "Elementary full-field stimuli",
                    "eu": "Eremu osoko estimulu elementalak"
                }
            },
            "test_2": {
                "name": {
                    "es": "Estímulos semánticos (emocionales y de miedo)",
                    "en": "Semantic (fearful & affective) stimuli",
                    "eu": "Estimulu semantikoak (beldurrezkoak eta afektiboak)"
                },
                "selected": False,
                "enabled": True,
                "estimated_time": 4,
                "tooltip": {
                    "es": "Estímulos semánticos (emocionales y de miedo)",
                    "en": "Semantic (fearful & affective) stimuli",
                    "eu": "Estimulu semantikoak (beldurrezkoak eta afektiboak)"
                },
                "config": {
                    "autonomic_response_basal_time": {
                        "value": 1.0,
                        "default": 1.0,
                        "type": float,
                        "variable_display_name": {
                            "es": "Tiempo basal (reposo)",
                            "en": "Basal time (rest)",
                            "eu": "Oinarrizko denbora (atsedena)"
                        },
                        "tooltip": {
                            "es": "Duración del periodo basal antes de mostrar la imagen (en segundos)",
                            "en": "Duration of the baseline period before the image is shown (in seconds)",
                            "eu": "Irudia erakutsi aurreko oinarrizko denboraren iraupena (segundotan)"
                        }
                    },
                    "autonomic_response_image_time": {
                        "value": 5.0,
                        "default": 5.0,
                        "type": float,
                        "variable_display_name": {
                            "es": "Tiempo de exposición de la imagen",
                            "en": "Image exposure time",
                            "eu": "Irudiaren bistaratze-denbora"
                        },
                        "tooltip": {
                            "es": "Tiempo que la imagen permanece en pantalla (en segundos)",
                            "en": "Time the image is shown on screen (in seconds)",
                            "eu": "Irudia pantailan bistaratzen den denbora (segundotan)"
                        }
                    },
                    "autonomic_response_recovery_time": {
                        "value": 1.0,
                        "default": 1.0,
                        "type": float,
                        "variable_display_name": {
                            "es": "Tiempo de recuperación",
                            "en": "Recovery time",
                            "eu": "Berreskuratze denbora"
                        },
                        "tooltip": {
                            "es": "Duración del periodo de recuperación tras la imagen (en segundos)",
                            "en": "Duration of the recovery period after the image (in seconds)",
                            "eu": "Irudiaren ondorengo berreskuratze-denboraren iraupena (segundotan)"
                        }
                    }
                }

            }
        }
    }
}

def extract_values(config_dict):
    """
    Recursively extract only 'value' fields from the nested config dictionaries.
    """
    if not isinstance(config_dict, dict):
        return config_dict
    result = {}
    for key, cfg in config_dict.items():
        if isinstance(cfg, dict):
            if "value" in cfg:
                result[key] = cfg["value"]
            else:
                result[key] = extract_values(cfg)
        else:
            result[key] = cfg
    return result

def save_configuration_to_file():
    data_to_save = {
        "general_config": extract_values(general_config),
        "advanced_config": extract_values(advanced_config),
        "modules": extract_values(modules)
    }

    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        title="Guardar configuración"
    )

    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

def update_config_values(config_dict, loaded_values):
    """
    Actualiza los valores 'value' de config_dict con los valores correspondientes de loaded_values.
    """
    for key, cfg in config_dict.items():
        if key in loaded_values:
            if isinstance(cfg, dict) and "value" in cfg:
                cfg["value"] = loaded_values[key]
            elif isinstance(cfg, dict):
                update_config_values(cfg, loaded_values[key])