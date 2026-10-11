# Bemi - BMI Monitor & Health Analyzer

Bemi is a sleek, modern desktop application written in Python to calculate, track, and analyze Body Mass Index (BMI). Built using Python's standard library (**Tkinter** and **SQLite3**), this application has **zero external dependencies** and is ready to run on any computer instantly.

---

## Key Features

*   **👥 Multi-User Profiles**: Create, select, edit, and delete profiles from a persistent database (SQLite3). Perfect for families or tracking multiple users.
*   **⚖️ Unit Switcher**: Toggle dynamically between **Metric (kg/cm)** and **Imperial (lbs/in)**.
*   **⚡ Real-Time Calculations**: Needle dial rotations, BMI values, health classifications, and wellness recommendations update dynamically as you type.
*   **📊 Custom Interactive Trend Graph**: Built directly on a Tkinter Canvas (no Matplotlib needed). Supports:
    *   Dynamic axis scaling
    *   Interactive mouse hover tooltips displaying date, weight, BMI, and logs details
*   **📈 Dashboard Metrics**: Displays weight changes (loss/gain progress highlighted), average BMI, and min/max limits.
*   **📝 Log History Table**: View a list of measurements with dates and optional notes, with support for individual log deletions.
*   **🎨 Premium Dark Theme**: Custom dark styling (`#11111b` dark theme) with smooth micro-animations.

---

## Project Structure

*   `main.py` - Application launcher and DB initializer.
*   `gui.py` - Main layout views, forms, tab navigation, and validation.
*   `custom_widgets.py` - Custom Tkinter Canvas classes for `BMIGauge` and `TrendGraph`.
*   `database.py` - SQLite query executions, statistics, and profile management.
*   `test_bmi.py` - Automated unit tests to verify CRUD and math calculations.
*   `.gitignore` - Prevents committing cache and local database files.

---

## How to Setup and Run

### Prerequisites
Make sure you have Python installed on your computer.

### Run the Application
1. Clone or download this repository.
2. Open your terminal in the directory and run:
   ```bash
   python main.py
   ```

### Running Automated Tests
Verify code logic by running the test suite:
```bash
python -m unittest test_bmi.py
```
