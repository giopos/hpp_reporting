# HPP Physiology Testing

Streamlit dashboard for analysing 12x25m swimming physiology test data. The app supports upload/validation of session files, automatic metric calculation (e.g. CV and D'), percentile benchmarking, historical tracking, and PDF report export.

## Features

- **Data Upload & Validation**: Upload `.xlsx` or `.xls` files containing split times for 12x25m swimming tests. Provides a downloadable template for ease of use.
- **Key Metrics Calculation**: Automatically calculates Critical Velocity (CV), D' (Anaerobic Capacity), Peak Speed, Drop-off %, and projected paces for SCM/LCM based on test splits.
- **Interactive Visualizations**: View velocity curves, split times, stroke rates, and stroke counts using Plotly.
- **Percentile Analysis**: Compare athlete performance (Peak Speed, CV, D') against a built-in cohort database using reference percentile data.
- **Historical Tracking**: Track a swimmer's progress over multiple test dates and identify trends in performance.
- **PDF Reporting**: Generate detailed individual or bulk PDF reports with velocity curves, percentile rankings, and historical comparisons. Supports custom logo uploads.

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/giopos/hpp_reporting.git
   cd hpp_reporting
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Configure usage-log access:**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit .streamlit/secrets.toml with your own password
   ```

5. **Run the application:**
   ```bash
   streamlit run main.py
   ```

## How to Use

1. Launch the app using `streamlit run main.py`.
2. Download the Excel template from the upload page.
3. Fill in the template with your athletes' 12x25m test data.
   - **Required:** `Swimmer`, `Gender` (M/F), `Stroke` (Freestyle/Backstroke/Breaststroke/Butterfly), `Date`, `Time 1`–`Time 12` (split times in seconds)
   - **Optional profile:** `Age`, `Para`, `Club`, `100 m PB`
   - **Optional performance:** `Stroke Rate 1`–`12` (needed for efficiency calculations), `Stroke Count 1`–`12`, `Velocity 1`–`12`
   - **Auto-calculated:** Stroke Efficiency Index (from Time + Stroke Rate), CV, Dprime, Peak Speed
4. Upload the completed Excel file to the dashboard.
5. Select a swimmer from the sidebar to view their performance metrics, velocity curve, percentile rankings, and historical trends.
6. Use the **Export Report** or **Bulk Export** buttons in the sidebar to generate PDF reports.

## Project Structure

- `main.py`: The core Streamlit application containing the UI, data processing, and PDF generation logic.
- `requirements.txt`: Python package dependencies.
- `percentile_data.json`: Reference database for the cohort percentile rankings.
- `logo.jpg`: Default logo used in PDF report exports.
- `.gitignore`: Files to be ignored by Git.

## Tech Stack

- **Framework**: [Streamlit](https://streamlit.io/)
- **Data Manipulation**: Pandas, NumPy, SciPy
- **Data Visualization**: Plotly, Matplotlib
- **Reporting**: Matplotlib (PDF Generation)
