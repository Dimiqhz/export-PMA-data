#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from colorama import init, Fore, Style
import pandas as pd

try:
    from docx import Document
except ImportError:
    Document = None
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from reportlab.lib import colors
except ImportError:
    SimpleDocTemplate = None

init(autoreset=True)

def prompt(msg, color=Fore.CYAN):
    return input(color + msg + Style.RESET_ALL + ' ').strip()

def error(msg):
    print(Fore.RED + '❌ ERROR: ' + msg + Style.RESET_ALL, file=sys.stderr)

def info(msg):
    print(Fore.GREEN + 'ℹ️  ' + msg + Style.RESET_ALL)

def get_token(html):
    soup = BeautifulSoup(html, 'html.parser')
    inp = soup.find('input', {'name': 'token'})
    if not inp:
        raise RuntimeError('Failed to retrieve CSRF token')
    return inp['value']

def login(sess, base_url, username, password):
    login_url = urljoin(base_url, 'index.php?route=/')
    info('Logging in… 🔐')
    r = sess.get(login_url); r.raise_for_status()
    sess.headers.update({'Referer': login_url})
    token = get_token(r.text)
    payload = {
        'pma_username': username,
        'pma_password': password,
        'server': '1',
        'set_session': '1',
        'token': token,
        'route': '/'
    }
    r = sess.post(login_url, data=payload); r.raise_for_status()
    if 'loginform' in r.text.lower():
        raise RuntimeError('Invalid username or password')
    info('Logged in successfully ✅')

def fetch_all_rows(sess, base_url, db, cols, total_limit):
    info(f'Fetching up to {total_limit} rows from `{db}`.users… 📋')
    all_rows, pos = [], 0
    page_size = total_limit if total_limit < 250 else 250
    headers = None
    while len(all_rows) < total_limit:
        url = base_url + f"index.php?route=/sql&server=1&db={db}&table=users&pos={pos}&session_max_rows={page_size}"
        info(f'GET page @ pos={pos}')
        r = sess.get(url); r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        tbl = soup.find('table', class_='table_results')
        if not tbl:
            break
        if headers is None:
            headers = [th.get_text(strip=True) for th in tbl.find_all('th', attrs={'data-column': True})]
            if cols: headers = [h for h in headers if h in cols]
        orig_cols = [th['data-column'] for th in tbl.find_all('th', attrs={'data-column': True})]
        page_rows = []
        for tr in tbl.tbody.find_all('tr'):
            tds = [td for td in tr.find_all('td') if 'print_ignore' not in td.get('class', [])]
            cells = [td.get_text(strip=True) for td in tds]
            if cols:
                cells = [val for col, val in zip(orig_cols, cells) if col in cols]
            if cells:
                page_rows.append(cells)
        if not page_rows:
            break
        all_rows.extend(page_rows)
        pos += page_size
    all_rows = all_rows[:total_limit]
    if not headers or not all_rows:
        raise RuntimeError('No data found')
    info(f'Total rows fetched: {len(all_rows)}')
    return pd.DataFrame(all_rows, columns=headers)

def export_data(df):
    choice = prompt('Export format? [excel/pdf/word/none]:', Fore.YELLOW).lower()
    if choice == 'excel':
        fname = 'output.xlsx'; df.to_excel(fname, index=False); info(f'Excel saved to {fname}')
    elif choice == 'word':
        if not Document: error('python-docx not installed'); return
        doc = Document(); table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns): hdr_cells[i].text = col
        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, val in enumerate(row): row_cells[i].text = str(val)
        fname = 'output.docx'; doc.save(fname); info(f'Word document saved to {fname}')
    elif choice == 'pdf':
        if not SimpleDocTemplate: error('reportlab not installed'); return
        data = [df.columns.to_list()] + df.values.tolist()
        fname = 'output.pdf'; pdf = SimpleDocTemplate(fname, pagesize=letter)
        tbl = Table(data); tbl.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.black),('BACKGROUND',(0,0),(-1,0),colors.lightgrey)]))
        pdf.build([tbl]); info(f'PDF saved to {fname}')
    else:
        info('No export selected, done.')

def main():
    try:
        use_https = prompt('Use HTTPS? [y/n]:').lower() == 'y'
        domain = prompt('Enter phpMyAdmin domain or IP:')
        username = prompt('Enter phpMyAdmin username:')
        password = prompt('Enter phpMyAdmin password:')
        scheme = 'https://' if use_https else 'http://'
        base = scheme + domain.rstrip('/') + '/phpmyadmin/'
        db = prompt('Enter database name:')
        total_limit = int(prompt('Enter total number of rows to fetch:')) if prompt('Limit total number of rows? [y/n]:').lower()=='y' else 250
        cols = [c.strip() for c in prompt('Enter columns comma-separated (exact names):').split(',')] if prompt('Select specific columns? [y/n]:').lower()=='y' else None
        sess = requests.Session()
        login(sess, base, username, password)
        df = fetch_all_rows(sess, base, db, cols, total_limit)
        print('\n' + Fore.MAGENTA + 'Preview of data:' + Style.RESET_ALL)
        print(df.head().to_string(index=False))
        export_data(df)
    except Exception as e:
        error(str(e)); sys.exit(1)

if __name__ == '__main__':
    main()
