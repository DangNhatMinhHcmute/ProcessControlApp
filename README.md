# Process Management Application

A Python-based application for process analysis and process configuration management from log files.  
This software allows users to create a new analysis from `.csv` or `.xlsx` log files, or reopen a previously saved process configuration from a `.json` file.

---

## Overview

The Process Management Application is developed to support users in analyzing process data and managing process configurations in a simple and structured way.

The application provides two main functions:
- **New**: Create a new analysis from log files (`.csv` / `.xlsx`)
- **Open**: Reopen a previously saved process configuration (`.json`)

This repository contains the application files and the installation instructions required to run the software on Windows.

---

## Features

- Load log files in `.csv` and `.xlsx` formats
- Open saved configuration files in `.json` format
- Simple startup interface with **New** and **Open** options
- Automated installation of required Python libraries
- Support for Graphviz and pm4py-related process analysis tasks

---

## System Requirements

- **Operating System:** Windows 10 or later
- **Internet connection:** Required for installing libraries
- **Administrator privileges:** May be required during software installation
- **Python version:** Python 3.10 or later

---

## Project Structure

```text
project_folder/
├─ install_required_libraries.bat
├─ run_app.bat
├─ required_libraries.txt
├─ README.md
├─ [application source files]
└─ [other supporting files]
