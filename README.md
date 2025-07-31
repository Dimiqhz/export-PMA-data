# Export phpMyAdmin Data Script

A Python script to automate logging into phpMyAdmin, fetching data from a specified table, and exporting results to Excel, PDF, or Word.

## Features
- HTTP-based login to phpMyAdmin (no browser automation)
- Configurable database, row limits, and column selection
- Pagination support to fetch all rows
- Colored console output for better readability
- Export options: Excel, PDF (with DejaVuSans for Cyrillic), and Word

## Requirements
- Python 3.x
- `requests`
- `beautifulsoup4`
- `pandas`
- `colorama`
- Optional for export:
  - `openpyxl` (for Excel)
  - `python-docx` (for Word)
  - `reportlab` (for PDF)

## Installation

### 1. Install Python
Make sure you have **Python 3.6+** installed.  
- Download & install from https://www.python.org/downloads/

### 2. Clone the repository
```bash
git clone https://github.com/Dimiqhz/export-PMA-data.git
cd export-PMA-data
```

### 3. Create & activate a virtual environment
```
# Create a venv folder
python3 -m venv venv

# Activate on Linux / macOS:
source venv/bin/activate

# Activate on Windows (PowerShell):
venv\Scripts\Activate.ps1

# Activate on Windows (cmd.exe):
venv\Scripts\activate.bat
```

### 4. Install dependencies
```bash
pip install requests beautifulsoup4 pandas colorama openpyxl python-docx reportlab
```
or
```
pip install requirements.txt
```

Ensure DejaVuSans font is available at `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` for PDF exports.

## Usage
```bash
python script.py
```
1. Choose HTTP or HTTPS.
2. Enter phpMyAdmin domain or IP.
3. Provide database name.
4. Decide on total number of rows to fetch.
5. (Optional) Select specific columns.
6. View colored console output.
7. (Optional) Export to Excel, PDF, or Word.

## Functions
- **prompt(msg, color)**: Colored input prompt.
- **error(msg)**: Red error output.
- **info(msg)**: Green informational output.
- **get_token(html)**: Extract CSRF token from HTML.
- **login(session, base_url)**: Perform HTTP login to phpMyAdmin.
- **fetch_all_rows(session, base_url, db, cols, total_limit)**: Fetch and parse table rows into a DataFrame.
- **export_data(df)**: Export DataFrame to Excel, PDF, or Word.

## Example
```
$ python script.py
Use HTTPS? [y/n]: n
Enter phpMyAdmin domain or IP: 127.0.0.1
Enter database name: testDB
Limit total number of rows? [y/n]: y
Enter total number of rows to fetch: 3
Select specific columns? [y/n]: y
Enter columns comma-separated (exact names): id,name

ℹ️  Logging in… 🔐
ℹ️  Logged in successfully ✅
ℹ️  Fetching up to 3 rows from `testDB`.users… 📋
ℹ️  GET page @ pos=0
────────────────────────────────────────
id    name
1     Ivan
2     Petr
3     Vasilii
────────────────────────────────────────

Preview of data:
 id    name
 1     Ivan
 2     Petr
 3     Vasilii

Export format? [excel/pdf/word/none]: none
ℹ️  No export selected, done.
```

## License
MIT License
