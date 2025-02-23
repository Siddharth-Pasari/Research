# **`Braunschweig Lab Research`**

## **`Overview`**

This project is a pip-installable python package with subpackages for Fluorescence and Profilometry analysis.

Fluorescence analysis is based off of an image file of a surface with some degree of fluorescence, and all data (max, min, mean, stdev, etc.) goes into an Excel spreadsheet for easy graphing.

Profilometry analysis isbased off of a .OPDx file (from the DektakXT stylus profiler), and all height data (bottom, top, difference) goes into an Excel spreadsheet for easy graphing.

The Profilometry package also includes a subpackage of its own, the grapher, which uses the Excel output as an input and users can choose to select files to generate graphs (in the form of Excel sheets in the same file) of height vs. feature number.

## **`Directory Structure`**

```
.
├── braunschweig_lab_research
│   ├── fluorescence
│   │   ├── __init__.py
│   │   ├── autofluorescence.py
│   │   ├── fluorescence.py
│   ├── profilometry
│   │   ├── __init__.py
│   │   ├── dragrectangle.py
│   │   ├── opdx_plotter.py
│   │   ├── opdx_reader.py
│   │   ├── colormap.png
│   │   ├── grapher
│   │   │   ├── __init__.py
│   │   │   ├── plotter.py
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── setup.cfg
├── setup.py
├── .gitignore
└── .github
    └── workflows
        └── python-ci.yml             
```

## **`Setup Instructions`**

### 1. Install the Package

**`Option 1: Install via PyPI`**

Ensure you have Python installed, then run:

    pip install braunschweig-lab-research

**`Option 2: Clone the Repository`**

To install the package from the source, first clone the repository:

    git clone https://github.com/Siddharth-Pasari/Research.git
    cd Research

Then, create a virtual environment and install dependencies:

    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate     # On Windows
    pip install -e .

### 2. Running Fluorescence Code

To run the fluorescence module, use:

    fluorescence-cli

Or run it manually:

    python -m braunschweig_lab_research.fluorescence.fluorescence

### 3. Running Profilometry Code

To run the profilometry module, use:

    profilometry-cli

Or run it manually:

    python -m braunschweig_lab_research.profilometry.opdx_plotter