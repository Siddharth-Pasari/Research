# **`Braunschweig Lab Research`**

## **`Overview`**

This project is a pip-installable python package with subpackages for Fluorescence and Profilometry analysis.

Fluorescence analysis is based off of an image file of a surface with some degree of fluorescence, and all data (max, min, mean, stdev, etc.) goes into an Excel spreadsheet for easy graphing.

Profilometry analysis isbased off of a .OPDx file (from the DektakXT stylus profiler), and all height data (bottom, top, difference) goes into an Excel spreadsheet for easy graphing.

The Profilometry package also includes a subpackage of its own, the grapher, which uses the Excel output as an input and users can choose to select files to generate graphs (in the form of Excel sheets in the same file) of height vs. feature number.

## **`How To Use`**

Profilometry:
- Click and drag to form a rectangle around a region
- The highest point of the region is automatically chosen
- Click the point on the 2D representation where you would like to log the lowest point
- Right click the heatmap to create a 'NoVal' row
- Backspace the heatmap to delete the last row (close 2D graph if open)
- Keep track of rows via the terminal if you'd like (close 2D graph if open)
- To go to a new file, close the current running heatmap

Fluorescence:
- Click where you want to center the rectangle
- Right click to log the currently surrounded area

## **`Setup Instructions`**

### 1. Install the Package

**`Option 1: Install via PyPI`**

PyPI support not implemented yet.

**`Option 2: Clone the Repository`**

To install the package from the source, first clone the repository:

    git clone https://github.com/Siddharth-Pasari/Research.git
    cd Research

Then, create a virtual environment and install dependencies:

    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate     # On Windows
    pip install -e .

### 2. Running Fluorescence Code (make sure you are still in venv)

To run the fluorescence module, use:

    fluorescence-cli

Or run it manually:

    python -m braunschweig_lab_research.fluorescence.fluorescence

### 3. Running Profilometry Code (make sure you are still in venv)

To run the profilometry module, use:

    profilometry-cli

Or run it manually:

    python -m braunschweig_lab_research.profilometry.opdx_plotter

## **Updating the Package**

    If you've already cloned the repository and installed the package using `pip install -e .`, you can update it easily by pulling the latest changes:

    cd path/to/Research
    git pull origin main
