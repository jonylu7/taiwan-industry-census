"""
Parse Taiwan Industry Census PDFs (工商及服務業普查) into CSV.

Each PDF page contains a summary table for one industry with 19 economic
indicators (rows) × 9 census years (columns) + a % change column.

Strategy: use pdfplumber word-position analysis to handle PDFs where large
numbers are split across multiple tokens by thousands-separator spaces
(e.g. "1 442 256" → tokens "1", "442", "256" all in the same column cell).

Output: tw_industry_census.csv (long format, years converted to Gregorian)
"""

import re
import os
import csv
from collections import defaultdict

import pdfplumber

# ── Constants ────────────────────────────────────────────────────────────────

ROC_YEARS   = [70, 75, 80, 85, 90, 95, 100, 105, 110]
# ROC year + 1911 = Gregorian year
GREG_YEARS  = [y + 1911 for y in ROC_YEARS]   # [1981, 1986, …, 2021]

INDICATORS = [
    ('1',     'Number of enterprises (year-end)',                              'establishments'),
    ('2',     'Number of employees (year-end)',                                'persons'),
    ('3',     'Average annual labour compensation per employed worker',        'NTD'),
    ('4',     'Total annual receipts of enterprises',                          'million NTD'),
    ('5',     'Total annual expenditures of enterprises',                      'million NTD'),
    ('6',     'Total annual output of enterprises',                            'million NTD'),
    ('7',     'Gross value added of enterprises',                              'million NTD'),
    ('8',     'Net assets in actual use (year-end)',                           'million NTD'),
    ('9',     'Net fixed assets in actual use (year-end)',                     'million NTD'),
    ('10(1)', 'Average number of employees per enterprise',                    'persons'),
    ('10(2)', 'Average assets in actual use per enterprise',                   'thousand NTD'),
    ('11',    'Labour equipment ratio',                                        'thousand NTD'),
    ('12',    'Labour productivity',                                           'thousand NTD'),
    ('13(1)', 'Gross value added per NTD of assets in actual use',             'NTD'),
    ('13(2)', 'Gross value added per NTD of fixed assets in actual use',       'NTD'),
    ('14',    'Labour compensation as % of total expenditures',                '%'),
    ('15(1)', 'Value-added ratio',                                             '%'),
    ('15(2)', 'Profit ratio',                                                  '%'),
    ('15(3)', 'Asset turnover ratio',                                          '%'),
]

INDUSTRY_CODE_MAP = {
    '礦業及土石採取業':         'B',
    '製造業':                   'C',
    '電力及燃氣供應業':         'D',
    '用水供應及污染整治業':     'E',
    '營建工程業':               'F',
    '批發及零售業':             'G',
    '運輸及倉儲業':             'H',
    '住宿及餐飲業':             'I',
    '出版影音及資通訊業':       'J',
    '金融及保險業':             'K',
    '不動產業':                 'L',
    '專業、科學及技術服務業':   'M',
    '支援服務業':               'N',
    '教育業':                   'P',
    '醫療保健及社會工作服務業': 'Q',
    '藝術、娛樂及休閒服務業':   'R',
    '其他服務業':               'S',
}

INDUSTRY_NAME_EN = {
    '礦業及土石採取業':         'Mining and Quarrying',
    '製造業':                   'Manufacturing',
    '電力及燃氣供應業':         'Electricity and Gas Supply',
    '用水供應及污染整治業':     'Water Supply and Remediation',
    '營建工程業':               'Construction',
    '批發及零售業':             'Wholesale and Retail Trade',
    '運輸及倉儲業':             'Transportation and Storage',
    '住宿及餐飲業':             'Accommodation and Food Service',
    '出版影音及資通訊業':       'Publishing, Audio-Visual and Information',
    '金融及保險業':             'Finance and Insurance',
    '不動產業':                 'Real Estate',
    '專業、科學及技術服務業':   'Professional, Scientific and Technical Services',
    '支援服務業':               'Support Services',
    '教育業':                   'Education',
    '醫療保健及社會工作服務業': 'Health and Social Work',
    '藝術、娛樂及休閒服務業':   'Arts, Entertainment and Recreation',
    '其他服務業':               'Other Services',
}

_YEAR_SET   = set(ROC_YEARS)
_NUM_RE     = re.compile(r'^-?\d+\.?\d*$')
_YEAR_TOK   = re.compile(r'^(\d{2,3})年?$')   # matches "70", "75年", "100年" …


# ── Column anchor detection ───────────────────────────────────────────────────

def find_column_anchors(words, page_height=842):
    """
    Detect data columns from the table header row.

    Returns (found_years, anchors) where:
      - found_years: sorted list of ROC year ints present in this table
                     (may be fewer than 9 for industries like 教育業)
      - anchors:     list of x-coordinates, length = len(found_years) + 1
                     (one per year column plus one for the change column)
    Returns (None, None) if no year headers were found.

    Searches the top 60% of the page.  Spurious year numbers in title text
    are filtered by selecting the y-band that contains the most distinct
    year tokens (the real column-header row).
    """
    cutoff = page_height * 0.60
    header_words = [w for w in words if w['top'] < cutoff]

    # Collect all year-token candidates with their positions
    year_candidates = []    # (roc_year, x0, top)
    change_candidates = []  # (x0, top)

    for w in header_words:
        t = w['text'].strip()
        m = _YEAR_TOK.match(t)
        if m:
            yr = int(m.group(1))
            if yr in _YEAR_SET:
                year_candidates.append((yr, w['x0'], w['top']))
        if '減率' in t:
            change_candidates.append((w['x0'], w['top']))

    if not year_candidates:
        return None, None

    # Group candidates by y-band (20 pt tolerance) and pick the band
    # with the most distinct years — that is the real column-header row.
    y_groups = defaultdict(dict)
    for yr, x0, top in year_candidates:
        y_key = round(top / 20) * 20
        y_groups[y_key][yr] = x0   # last token in band wins (fine for headers)

    best_y_key = max(y_groups, key=lambda k: len(y_groups[k]))
    year_anchors = y_groups[best_y_key]

    # Change-column anchor: use the one closest in y to the header band
    change_anchor = None
    if change_candidates:
        change_anchor = min(change_candidates,
                            key=lambda c: abs(c[1] - best_y_key))[0]

    found_years = sorted(year_anchors)          # e.g. [95,100,105,110] for 教育業
    anchors = [year_anchors[y] for y in found_years]
    if change_anchor is None:
        gap = (anchors[-1] - anchors[-2]) if len(anchors) > 1 else 40
        change_anchor = anchors[-1] + gap
    anchors.append(change_anchor)               # len = len(found_years) + 1
    return found_years, anchors


def column_boundaries(anchors):
    """
    Build 10 (left, right) boundary intervals from column anchor x-positions.

    Uses a 75 % ratio rather than a 50 % midpoint so that small right-aligned
    numbers (whose left edge sits near the column's right margin) are still
    assigned to the correct column, not the next one.

        left_i  = anchor[i-1] + 0.75 * gap[i-1]   (i > 0)
        right_i = anchor[i]   + 0.75 * gap[i]      (i < n-1)
    """
    n = len(anchors)
    bounds = []
    for i in range(n):
        if i == 0:
            left = anchors[0] - 50
        else:
            left = anchors[i-1] + 0.75 * (anchors[i] - anchors[i-1])

        if i == n - 1:
            right = anchors[i] + 100
        else:
            right = anchors[i] + 0.75 * (anchors[i+1] - anchors[i])

        bounds.append((left, right))
    return bounds


def token_column(x, bounds):
    """Return column index (0-9) for a token at x-position, or None."""
    for i, (lo, hi) in enumerate(bounds):
        if lo <= x < hi:
            return i
    return None


# ── Industry title extraction ─────────────────────────────────────────────────

def extract_industry_name(text):
    for line in text.split('\n'):
        if '歷次普查結果摘要' in line:
            m = re.search(r'(.+?)歷次普查結果摘要', line)
            if m:
                name = m.group(1).strip()
                name = re.sub(r'^表[一二三四五六七八九十]+\s*', '', name)
                return name
    return None


# ── Page parsing ─────────────────────────────────────────────────────────────

def parse_page(page):
    """
    Parse one PDF page.  Returns (industry_name, list_of_19_value_lists).
    Each value list has 10 floats: [yr70, yr75, …, yr110, change].
    """
    words = page.extract_words()
    text  = page.extract_text() or ''

    industry_name = extract_industry_name(text)
    if not industry_name:
        return None, []

    page_h = float(page.height)
    found_years, anchors = find_column_anchors(words, page_height=page_h)
    if not found_years:
        print(f"    [skip] could not detect columns for: {industry_name}")
        return industry_name, []

    n_year_cols = len(found_years)              # 9 normally, 4 for 教育業, etc.
    n_cols      = n_year_cols + 1               # +1 change column
    bounds      = column_boundaries(anchors)

    # Determine y below which data rows begin (just below the year header)
    header_y = min(
        (w['top'] for w in words
         if _YEAR_TOK.match(w['text'].strip())
         and int(_YEAR_TOK.match(w['text'].strip()).group(1)) in _YEAR_SET),
        default=170
    )
    data_start_y = header_y + 5

    # Group all words below the header by rounded y (6-pt rows)
    rows_by_y = defaultdict(list)
    for w in words:
        if w['top'] < data_start_y:
            continue
        y_key = round(w['top'] / 6) * 6
        rows_by_y[y_key].append(w)

    data_rows = []
    for y_key in sorted(rows_by_y):
        row_words = rows_by_y[y_key]

        # Collect numeric tokens and assign to columns
        col_tokens = defaultdict(list)
        for w in row_words:
            if not _NUM_RE.match(w['text']):
                continue
            col_idx = token_column(w['x0'], bounds)
            if col_idx is not None:
                col_tokens[col_idx].append(w['text'])

        if len(col_tokens) != n_cols:
            continue  # not a complete data row

        # Merge tokens within each column (handles split thousands: "354"+"460" → 354460)
        try:
            col_values = [float(''.join(col_tokens[i])) for i in range(n_cols)]
        except ValueError:
            continue

        # Map found years to full 9-year slot; missing years → None
        year_map = {yr: col_values[i] for i, yr in enumerate(found_years)}
        change   = col_values[n_year_cols]
        full_row = [year_map.get(yr) for yr in ROC_YEARS] + [change]
        data_rows.append(full_row)

    return industry_name, data_rows


# ── PDF parsing ───────────────────────────────────────────────────────────────

def parse_pdf(pdf_path):
    """Return list of (industry_name, code, data_rows) for every page."""
    results = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            industry_name, data_rows = parse_page(page)
            if not industry_name:
                continue
            code = INDUSTRY_CODE_MAP.get(industry_name, '?')
            if len(data_rows) != 19:
                print(f"  WARNING {code} {industry_name}: "
                      f"expected 19 rows, got {len(data_rows)}")
                print(data_rows)
                exit()
            results.append((industry_name, code, data_rows))
    return results


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    raw_dir     = os.path.join(os.path.dirname(__file__), 'raw data')
    output_path = os.path.join(os.path.dirname(__file__), 'tw_industry_census.csv')
    pdf_files   = sorted(f for f in os.listdir(raw_dir) if f.endswith('.pdf'))

    # Column headers use Gregorian years (ROC + 1911)
    year_cols = [f'{g}' for g in GREG_YEARS]
    columns   = (['industry_code', 'industry_name',
                  'indicator_id', 'indicator_name', 'unit']
                 + year_cols
                 + ['change_2016_to_2021_pct'])

    total_rows = 0
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(columns)

        for filename in pdf_files:
            pdf_path = os.path.join(raw_dir, filename)
            print(f"Processing {filename}...")
            pages = parse_pdf(pdf_path)

            for industry_name, code, data_rows in pages:
                print(f"  → {code}: {industry_name}  ({len(data_rows)} indicators)")
                for i, (ind_id, ind_name, unit) in enumerate(INDICATORS):
                    values = data_rows[i] if i < len(data_rows) else [None] * 10
                    writer.writerow(
                        [code, INDUSTRY_NAME_EN.get(industry_name, industry_name),
                         ind_id, ind_name, unit] + values
                    )
                    total_rows += 1

    print(f"\nDone. {total_rows} rows → {output_path}")


if __name__ == '__main__':
    main()
