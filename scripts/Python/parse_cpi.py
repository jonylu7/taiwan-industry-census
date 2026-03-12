"""
Parse Taiwan CPI CSV (消費者物價基本分類指數) into clean English CSV.

Input:  data/raw/A030101015_0533012602.csv  (Big5 encoding, ROC years)
Output: data/clean/tw_cpi.csv

Transformations:
- Encoding: Big5 → UTF-8
- Year: ROC year (e.g. 70) → Gregorian year (e.g. 1981, +1911)
- Column names: Chinese → English
- Strips header metadata rows and footnotes
"""

import os
import re
import csv

RAW_PATH   = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw',   'A030101015_0533012602.csv')
OUT_PATH   = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'clean', 'tw_cpi.csv')

_ROC_YEAR  = re.compile(r'^(\d+)年$')

def main():
    rows = []
    with open(RAW_PATH, encoding='big5', errors='replace') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            m = _ROC_YEAR.match(row[0].strip().strip('"'))
            if not m:
                continue
            greg_year = int(m.group(1)) + 1911
            cpi_value = float(row[1].strip().strip('"'))
            rows.append((greg_year, cpi_value))

    with open(OUT_PATH, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['year', 'cpi_index'])
        writer.writerows(rows)

    print(f"Done. {len(rows)} rows → {OUT_PATH}")

if __name__ == '__main__':
    main()
