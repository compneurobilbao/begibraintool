# BegiBrainTool: An Innovative Toolbox for Visual Assessment in Neurodegenerative Diseases

📌 Early detection of Alzheimer’s and Parkinson’s could start with vision.

## 🧠 What is BegiBrainTool?

BegiBrainTool is an innovative battery of visual tests designed to assess spatial and dynamic vision processing, autonomous visual responses, and learning and decision-making behavior in patients with neurodegenerative diseases. Its goal is to provide a standardized and adaptable tool for both research and clinical practice, facilitating early detection and monitoring of conditions such as Alzheimer’s and Parkinson’s.

### 🎯 Key Features:
✔ **Modular and customizable test battery**  
✔ **PsychoPy-based, open-source platform**  
✔ **Compatible with eye-tracking, biometric sensors (e.g., GazePoint GP3 HD) and EEG**  
✔ **Designed for both research and clinical use**  
✔ **JSON/XLSX parameter configuration**  
→ **Automated preprocessing & feature extraction pipelines (in development)**  

> 🏥 *A solution for a growing need in neurology: vision assessment as an early biomarker for neurodegenerative diseases.*

---

## 🧰 System Architecture

**Hardware setup tested in lab conditions:**

- 🖥️ Control computer with PsychoPy  
- 👁️ Eye-tracker (GazePoint GP3 HD)  
- 💓 Biometric sensors (PPG, GSR)  
- ⚡ EEG system (required for Module 4)  
- 🎮 Response pad  
- 🧠 Head-mounted display (optional)  
- To be implemented: DVS Camera

**Software overview:**

- User-friendly GUI for clinicians and researchers  
- Synchronized acquisition of gaze, pupil, HRV, GSR, and responses
- Modular execution: run only the tests you need  
- Optimized for scalability and multicenter/longitudinal studies  

---

## 🔬 How does it work?

BegiBrainTool consists of four interactive modules. The first three assess different aspects of visual perception; the fourth studies how participants learn and make decisions:

![Modules diagram](https://drive.google.com/file/d/1Q-J0TSwghCw6-cyTywi1BrUpAKS_ylJY/view?usp=sharing)


### 👁 1. Spatial Vision Module

🟢 Evaluates basic and semantic visual processing through stimuli that vary in:  
✅ **Spatial frequency**  
✅ **Contrast**  
✅ **Color saturation**  
Each visual parameter (spatial frequency, contrast, saturation) is first calibrated individually using a threshold detection test.

### 🎯 2. Dynamic Vision and Eye-Tracking Module

🟢 Analyzes visual attention and tracking ability through moving stimuli tasks, including:  
✅ **Fixation Stability Test (with and without fixation point)**  
✅ **Visual search test**  
✅ **Background noise tasks - Smooth Pursuit test**  
✅ **Flicker Fusion Threshold test**  
✅ **Saccade and antisaccade test**  

🎥 [Example Video](https://drive.google.com/file/d/135xDY6b7f480qEJCvrBDCASXKUBnwraL/view)

### 💓 3. Autonomous Response Module

🟢 Measures unconscious reactions to basic and emotional visual stimuli (e.g., fear-related images) through:  
✅ **Pupillary response analysis**  
✅ **Heart rate variability (HRV)**  
✅ **Galvanic skin response (GSR)**  

### 🧩 4. Learning and Decision-Making Module

🟢 Studies participants' behavior while they learn from rewards, combining choices, gaze and brain activity through:  
✅ **Probabilistic reversal learning task**: on each trial the participant opens one of two treasure chests; one is rewarded more often than the other until the rule reverses without warning  
✅ **Eye-tracking during choice**: which chest is looked at, and for how long, before deciding  
✅ **EEG over the medial frontal cortex (required)**: brain response to wins and losses  
✅ **Computational modeling**: reinforcement-learning and decision models fitted to each participant (learning from gains and losses, choice consistency, perseveration, influence of attention on choice)  

![Module 4 - Learning and Decision-Making]

🤝 Developed in collaboration with Dr. Javier Rasero (School of Data Science, University of Virginia) as part of Unai Sainz-Lugarezaresti's PhD thesis. The task builds on Bond, Rasero et al. (2023), *Competing neural representations of choice shape evidence accumulation in humans*, eLife 12:e85223 ([doi:10.7554/eLife.85223](https://doi.org/10.7554/eLife.85223)).

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
✅ **Computational modeling of Module 4 data, in collaboration with the UVA School of Data Science.**  
✅ **Release as an open-source tool for the scientific community.**  

📢 **You can contribute!** If you are a researcher, clinician, or developer, join our community and help us improve BegiBrainTool.  

---

## 📥 Download and Installation

> 🔹 **Requirements:** PsychoPy 2024+, Python 3.8+  
🔹 **Compatible devices:** GazePoint GP3 HD eye-tracking system and compatible biometric sensors. Other eye-trackers may be used. Module 4 also requires an EEG system.  

### 1️⃣ Clone the repository

```bash
git clone https://github.com/user/BegiBrainTool.git
cd BegiBrainTool
```

### 2️⃣ Install dependencies


```bash
C:\Program Files\PsychoPy> python.exe -m pip install requirements.txt
```

OR:

Open PsychoPy's PIP terminal: Tools --> 'Plugion/Packages manager' --> 'Packages' --> 'Open PIP terminal':
```bash
pip install requirements.txt
```
This terminal may crash during installation. Please, be patient.
If PsychoPy crashes while trying to open the Package manager make sure to run PsychoPy with admin rigths.

### 3️⃣ Run the toolbox

```bash
python begibraintool_main.py
```

## 📩 Contact and Contributions

unai.sainz.bc@gmail.com
