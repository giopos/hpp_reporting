# Swimmer Performance Dashboard

A comprehensive Streamlit-based dashboard for analyzing 12x25m swimmer test data. This tool allows coaches and athletes to upload performance data, visualize metrics like Critical Velocity (CV) and D', evaluate performance against cohort percentiles, and generate customized PDF reports.

## Features

- **Data Upload & Validation**: Upload `.xlsx` or `.xls` files containing split times for 12x25m swimming tests. Provides a downloadable template for ease of use.
- **Key Metrics Calculation**: Automatically calculates Critical Velocity (CV), D' (Anaerobic Capacity), Peak Speed, Drop-off %, and projected paces for SCM/LCM based on test splits.
- **Interactive Visualizations**: View velocity curves, split times, stroke rates, and stroke counts using Plotly.
- **Percentile Analysis**: Compare athlete performance (Peak Speed, CV, D') against a built-in cohort database using reference percentile data.
- **Historical Tracking**: Track a swimmer's progress over multiple test dates and identify trends in performance.
- **PDF Reporting**: Generate detailed individual or bulk PDF reports with velocity curves, percentile rankings, and historical comparisons. Supports custom logo uploads.
- **Usage Tracking**: Built-in silent activity logging for dashboard usage statistics, accessible via an admin panel.

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

4. **Run the application:**
   ```bash
   streamlit run main.py
   ```

## How to Use

1. Launch the app using `streamlit run main.py`.
2. Download the Excel template from the upload page.
3. Fill in the template with your athletes' 12x25m test data. Required columns include:
   - `Swimmer` (Name)
   - `Gender` (M/F)
   - `Stroke` (Freestyle, Backstroke, Breaststroke, Butterfly)
   - `Date` (Test date)
   - `Time 1` to `Time 12` (Split times in seconds for each 25m rep)
4. Upload the completed Excel file to the dashboard.
5. Select a swimmer from the sidebar to view their performance metrics, velocity curve, percentile rankings, and historical trends.
6. Use the **Export Report** or **Bulk Export** buttons in the sidebar to generate PDF reports.

## Project Structure

- `main.py`: The core Streamlit application containing the UI, data processing, and PDF generation logic.
- `tracker.py`: Utility script for logging app usage and exporting logs to GitHub.
- `requirements.txt`: Python package dependencies.
- `percentile_data.json`: Reference database for the cohort percentile rankings.
- `logo.jpg`: Default logo used in PDF report exports.
- `.gitignore`: Files to be ignored by Git.

## Tech Stack

- **Framework**: [Streamlit](https://streamlit.io/)
- **Data Manipulation**: Pandas, NumPy, SciPy
- **Data Visualization**: Plotly, Matplotlib
- **Reporting**: Matplotlib (PDF Generation)

## Admin Configuration

To access the "Usage Logs" panel in the sidebar, you can configure an admin password in your Streamlit secrets (`.streamlit/secrets.toml`):

```toml
[admin]
password = "your_secure_password"
```

If not configured, the default password is `admin12x25`.

To enable automatic GitHub log pushing, configure the following secrets:
```toml
[github]
token = "your_github_personal_access_token"
repo = "username/repo-name"
```
