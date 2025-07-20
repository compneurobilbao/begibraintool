# BegiBrainTool: An Innovative Toolbox for Visual Assessment in Neurodegenerative Diseases

📌 Early detection of Alzheimer’s and Parkinson’s could start with vision.

## 🧠 What is BegiBrainTool?

BegiBrainTool is an innovative battery of visual tests designed to assess spatial and dynamic vision processing, as well as autonomous visual responses in patients with neurodegenerative diseases. Its goal is to provide a standardized and adaptable tool for both research and clinical practice, facilitating early detection and monitoring of conditions such as Alzheimer’s and Parkinson’s.

### 🎯 Key Features:
✔ **Modular and customizable test battery**  
✔ **PsychoPy-based, open-source platform**  
✔ **Compatible with eye-tracking and biometric sensors (e.g., GazePoint GP3 HD)**  
✔ **Designed for both research and clinical use**  
✔ **JSON/XLSX parameter configuration**  
- **Automated preprocessing & feature extraction pipelines (in development)**  

> 🏥 *A solution for a growing need in neurology: vision assessment as an early biomarker for neurodegenerative diseases.*

---

## 🧰 System Architecture

**Hardware setup tested in lab conditions:**

- 🖥️ Control computer with PsychoPy  
- 👁️ Eye-tracker (GazePoint GP3 HD)  
- 💓 Biometric sensors (PPG, GSR)  
- 🎮 Response pad  
- 🧠 Head-mounted display (optional)  
- 🔄 Centralized data acquisition  

**Software overview:**

- User-friendly GUI for clinicians and researchers  
- Synchronized acquisition of gaze, pupil, HRV, GSR, and RT  
- Modular execution: run only the tests you need  
- Optimized for scalability and multicenter/longitudinal studies  

---

## 🔬 How does it work?

BegiBrainTool consists of three interactive modules, each designed to assess different aspects of visual perception:

![Modules diagram](https://drive.google.com/uc?export=view&id=1VCpIMSZqYYqGqmp2fy_Fq6NnNz6HDQoV)


### 👁 1. Spatial Vision Module

🟢 Evaluates basic and semantic visual processing through stimuli that vary in:  
✅ **Spatial frequency**  
✅ **Contrast and brightness**  
✅ **Color perception**  


### 🎯 2. Dynamic Vision and Eye-Tracking Module

🟢 Analyzes visual attention and tracking ability through moving stimuli tasks, including:  
✅ **Visual search**  
✅ **Background noise tasks**  
✅ **Flicker Fusion Threshold tests**  
✅ **Eye-tracking integration for precise measurement of visual behavior**  

🎥 [Example Video](https://drive.google.com/file/d/135xDY6b7f480qEJCvrBDCASXKUBnwraL/view)

### 💓 3. Autonomous Response Module

🟢 Measures unconscious reactions to basic and emotional visual stimuli (e.g., fear-related images) through:  
✅ **Pupillary response analysis**  
✅ **Heart rate variability (HRV)**  
✅ **Galvanic skin response (GSR)**  

---

## 🚀 Why BegiBrainTool?

📢 **A growing problem:** The aging population in Spain has led to an increase in neurodegenerative diseases. Neurologists need fast, non-invasive, and personalized tools to tackle this challenge.  

🔍 **A gap in clinical neuroscience:** Currently, there is no comprehensive toolbox that evaluates vision in relation to early detection of Alzheimer’s and Parkinson’s.  

🖥 **A modular and open-source solution:** BegiBrainTool is a flexible platform, tailored for both clinical and research applications, integrating cutting-edge technology for visual assessment and computational neuroscience.  

---

## 📊 Project Status

🔬 BegiBrainTool is under active development. We are currently working on validating the toolbox components and establishing solid data collection protocols.

### 🛠 Next Steps:
✅ **Optimization of modules and integration with databases.**  
✅ **Clinical validation with patients of different neurodegenerative profiles.**  
✅ **Release as an open-source tool for the scientific community.**  

📢 **You can contribute!** If you are a researcher, clinician, or developer, join our community and help us improve BegiBrainTool.  

---

## 📥 Download and Installation

> 🔹 **Requirements:** PsychoPy 2024+, Python 3.8+  
🔹 **Compatible devices:** GazePoint GP3 HD eye-tracking system and compatible biometric sensors.  

### 1️⃣ Clone the repository

```bash
git clone https://github.com/user/BegiBrainTool.git
cd BegiBrainTool
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the toolbox

```bash
python begibraintool_main.py
```

## 📩 Contact and Contributions

unai.sainz.bc@gmail.com


<!---
# BegiBrainTool: Un toolbox innovador para la evaluación visual en enfermedades neurodegenerativas

📌 La detección temprana del Alzheimer y Parkinson podría empezar por la vista.

## 🧠 ¿Qué es BegiBrainTool?

BegiBrainTool es una innovadora batería de tests visuales diseñada para evaluar el procesamiento espacial y dinámico de la visión, así como respuestas visuales autónomas en pacientes con enfermedades neurodegenerativas. Su objetivo es proporcionar una herramienta estandarizada y adaptable tanto para la investigación como para la práctica clínica, facilitando la detección temprana y el seguimiento de enfermedades como el Alzheimer y el Parkinson.

### 🎯 Características principales:
✔ **Modular y personalizable**  
✔ **Implementado en PsychoPy**  
✔ **Compatible con eye-tracking y sensores biométricos**  
✔ **Orientado a la evaluación clínica e investigación**  

> 🏥 *Una solución para una necesidad creciente en neurología: la evaluación de la visión como biomarcador temprano de enfermedades neurodegenerativas.*

---

## 🔬 ¿Cómo funciona?

BegiBrainTool está compuesto por tres módulos interactivos, cada uno diseñado para evaluar diferentes aspectos de la percepción visual:

### 👁 1. Módulo de Visión Espacial

🟢 Evalúa el procesamiento visual elemental y semántico a través de estímulos que varían en:  
✅ **Frecuencia espacial**  
✅ **Contraste y luminosidad**  
✅ **Percepción del color**  

🎥 *(GIF de ejemplo: test de percepción del contraste y color)*

### 🎯 2. Módulo de Visión Dinámica y Eye Tracking

🟢 Analiza la atención visual y la capacidad de seguimiento a través de tareas con estímulos en movimiento, incluyendo:  
✅ **Búsqueda visual**  
✅ **Tareas con ruido de fondo**  
✅ **Pruebas de fusión de parpadeo (Flicker Fusion Threshold)**  
✅ **Integración con eye-tracking para medición precisa del comportamiento visual**  

🎥 *(GIF de ejemplo: prueba de seguimiento de punto camuflado en ruido)*

### 💓 3. Módulo de Respuesta Autónoma

🟢 Mide reacciones inconscientes a estímulos visuales elementales y emocionales (p.ej., imágenes de miedo) mediante:  
✅ **Análisis de la respuesta pupilar**  
✅ **Variabilidad de la frecuencia cardíaca (HRV)**  
✅ **Respuesta galvánica de la piel (GSR)**  

🎥 *(GIF de ejemplo: test de respuesta pupilar a estímulos emocionales)*

---

## 🚀 ¿Por qué BegiBrainTool?

📢 **Un problema creciente:** El envejecimiento de la población en España ha generado un aumento en enfermedades neurodegenerativas. Los neurólogos necesitan herramientas personalizadas, rápidas y no invasivas para abordar este desafío.  

🔍 **Un vacío en la neurociencia clínica:** Actualmente, no existe una toolbox integral que evalúe la visión en relación con la detección temprana del Alzheimer y el Parkinson.  

🖥 **Una solución modular y de código abierto:** BegiBrainTool es una plataforma flexible, adaptada tanto a la clínica como a la investigación, que integra las tecnologías más avanzadas para la evaluación visual y la neurociencia computacional.  

---

## 📊 Estado del proyecto

🔬 BegiBrainTool está en desarrollo activo. En la actualidad, estamos trabajando en la validación de los componentes de la toolbox y en la creación de protocolos sólidos de recolección de datos.

### 🛠 Próximos pasos:
✅ **Optimización de los módulos y su integración con bases de datos.**  
✅ **Validación clínica con pacientes de diferentes perfiles neurodegenerativos.**  
✅ **Publicación del software como herramienta de código abierto para la comunidad científica.**  

📢 **¡Tú puedes contribuir!** Si eres investigador, clínico o desarrollador, únete a nuestra comunidad y ayúdanos a mejorar BegiBrainTool.  

---

## 📥 Descarga e instalación

> 🔹 **Requisitos:** PsychoPy 2024+, Python 3.8+  
🔹 **Dispositivos compatibles:** Sistema de eye-tracking GazePoint GP3 HD y sensores biométricos compatibles.  

### 1️⃣ Clona el repositorio

```bash
git clone https://github.com/usuario/BegiBrainTool.git
cd BegiBrainTool
```

### 2️⃣ Instala las dependencias

```bash
pip install -r requirements.txt
```

### 3️⃣ Ejecuta la toolbox

```bash
python begibraintool_main.py
```

---

## 📩 Contacto y contribuciones

unai.sainz.bc@gmail.com
-->
