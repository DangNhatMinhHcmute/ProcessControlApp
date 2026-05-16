# Process Control Application

## Overview
Process Control Application is a Python-based desktop application for process analysis and process improvement from event log data.

The application supports:
- creating a new analysis from a log file,
- configuring required process attributes,
- visualizing a Petri Net model,
- reviewing key process statistics and charts,
- comparing process models in the Improvement tab.

This repository contains the application source code, sample model files, sample data, and supporting documentation required to run the software on Windows.

## Main Features
- Load process log files
- Configure process attributes:
  - Case ID
  - Activity
  - Timestamp
  - Time type
  - Time unit
- Display summary KPIs
- Display throughput time histogram
- Display activity frequency chart
- Display cycle time chart
- Generate and render a Petri Net model
- Compare two process models from `.pnml` files
- Save process configuration to `.json`

## Repository Structure
```text
ProcessControlApp/
├── README.md
├── LICENSE.txt
├── requirements.txt
├── src/
│   ├── main.py
│   ├── analysis_tab.py
│   ├── build_petri_net.py
│   ├── improvement_tab.py
│   ├── main_screens.py
│   ├── other_frames.py
│   ├── plot_and_dataframe.py
│   ├── install_required_libraries.bat
│   ├── run_app.bat
│   ├── required_libraries.txt
│   ├── README.txt
│   ├── app_data/
│   └── __pycache__/
├── images/
└── docs/
```

## System Requirements
- Windows 10 or later
- Python installed and available in Command Prompt
- Internet connection for installing Python packages
- Graphviz installed and available in system PATH

## Required Components
The following components are required:
- Python
- pandas
- matplotlib
- numpy
- Pillow
- pm4py
- graphviz (Python package)
- Graphviz desktop package with `dot` command available

Check the environment in Command Prompt:

```cmd
python --version
pip --version
dot -V
```

## Installation
Install the required Python packages with:

```cmd
python -m pip install -r requirements.txt
```

If Graphviz is installed correctly, the following command should return the Graphviz version:

```cmd
dot -V
```

## Run the Application
Open Command Prompt in the `src` folder and run:

```cmd
py main.py
```

Alternative helper files are also included in the `src` folder:
- `install_required_libraries.bat`
- `run_app.bat`

In the tested environment, the most stable way to start the application is:

```cmd
py main.py
```

> Important: keep the Command Prompt window open while the application is running.

## Input Configuration
The following mapping was tested successfully:

| Field | Value |
|---|---|
| Case ID | `case:concept:name` |
| Activity | `concept:name` |
| Timestamp | `time:timestamp` |
| Time type | `end` |
| Time unit | `Ngày` |

## Tested Workflow
1. Open the application with `py main.py`
2. Select **New**
3. Choose the event log file
4. Map the required fields
5. Enter a process name and continue
6. Review the **Analysis** tab
7. Open the **Improvement** tab
8. Add model files from `.pnml`
9. Review comparison metrics and missing-flow tables
10. Save the configuration to `.json`

## Verified Results
The following functions were tested successfully in the current environment:
- application startup from Command Prompt
- loading data with **New**
- successful field mapping
- summary KPI display
- throughput time histogram display
- activity frequency chart display
- cycle time chart display
- Petri Net rendering
- loading two `.pnml` files in the Improvement tab
- comparison metrics display
- configuration save to `.json`

## Included Data and Models
This public package includes:
- `src/app_data/3_way_before_log_sample_5000_cases.csv`
- `src/app_data/3-way_match_invoice_before_GR_model.pnml`
- `src/app_data/3-way_match_invoice_before_GR_model_improved.pnml`

The full original event log is not included in the public package because of file size and public repository limitations.

## Known Issues
- The **New** workflow is stable in the tested environment.
- Petri Net rendering is stable after Graphviz is installed correctly.
- Model comparison from `.pnml` files is available in the Improvement tab.
- The **Open** function from a saved `.json` file was not stable in the tested environment and may open a blank window.

## Documentation
The `docs` folder contains the detailed user guide in Word format.

## Status
**Prototype / Initial Working Version**

## Citation

If you use this software in your research, please cite:

Dang, N. M. (2026). Process Control Application (Version 1.0.1) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.20243051
