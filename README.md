# 🎥 Hercules Video Analysis Agent

## 📋 Project Overview

This project implements an automated Video Analysis Agent for Hercules test runs.

The agent evaluates whether the test run was executed as planned by comparing:

✅ The agent's Planning Log (thoughts/steps)  
✅ Video recording(s) of the run  
✅ The final test output  

**Deviation reports** are generated indicating if any claimed action was skipped, altered, or missing in the video evidence.

---

## ⚙️ Features

- Modular, scalable Python codebase  
- Step-by-step video inspection with YOLOv8-based action detection  
- Final test output validation  
- Lightweight AI assistance using `flan-t5-small` (runs on low-resource machines)  
- Generates `.txt` and `.html` deviation reports  
- Fully configurable via `configs/settings.py`  

---

## 🗂️ Project Structure

video_analysis_agent/

├── agent\
│   └── base_agent.py\
├── config\
│   ├── __init__.py\
│   └── settings.py\
├── data\
│   ├── planning_logs\
│   │   └── run1.txt\
│   ├── test_outputs\
│   │   └── run1_output.txt\
│   └── videos\
│       └── run1.mp4\
├── models\
│   └── yolov8s.pt\
├── reports\
├── requirements.txt\
├── run_agent.py\
├── src\
│   ├── deviation_engine.py\
│   ├── __init__.py\
│   ├── input_handler.py\
│   ├── output_checker.py\
│   ├── planning_parser.py\
│   ├── report_generator.py\
│   └── video_analyzer.py\
└── tools\
│   ├── ai_tools.py\
│    ├── __init__.py

---
## 🚀 How to Run the Agent

### 1️⃣ Setup

Install requirements:

```bash
pip install -r requirements.txt
```

### 2️⃣ Place Input Files
Videos → `data/videos/`

Planning Logs (`.txt`) → `data/planning_logs/`

Final Output Files → `data/test_outputs/`

Ensure filenames align (e.g., `run1.mp4`, `run1.txt`, `run1_output.txt`).


### 3️⃣ Run the Agent

```bash
python run_agent.py
```

Reports are generated in `reports/` with timestamps.

Example:

`reports/run1_detailed_report_20240628_153020.txt` \
`reports/run1_detailed_report_20240628_153020.html`

### 📊 Sample Output

```bash
Test Report Details
Test Suite: run1
==================================================
Total Duration: 87.63 sec
Total Token Used: 43
Total Cost Estimate: 9e-05 USD

Test Result Summary
--------------------------------------------------
Steps Passed: 0
Steps Failed: 3

Detailed Steps:
--------------------------------------------------
Step 1: ﻿Click "Login"
  Result: ❌ Deviation
  Notes: Action not found in video

Step 2: Enter Password
  Result: ❌ Deviation
  Notes: Action not found in video

Step 3: Submit Form
  Result: ❌ Deviation
  Notes: Action not found in video

Output File: data/test_outputs/run1_output.txt
Proofs Video: data/videos/run1.mp4
Planner Thoughts Log: ./log_files/run1_planner_thoughts.log
Chat Messages Log: ./log_files/run1_chat_messages.log
```

### 🛠 Requirements
- Python 3.8+
- Tested with flan-t5-small for AI tasks
- Uses YOLOv8 for action detection
- Low hardware requirements (8GB RAM compatible)

### 📚 References
- [Hercules GitHub](https://github.com/test-zeus-ai/testzeus-hercules)



