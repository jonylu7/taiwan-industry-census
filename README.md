# Taiwan Industry Census Analysis (1981–2021)

Parses the Taiwan **Census of Industry and Commerce** (工商及服務業普查) published by the Directorate-General of Budget, Accounting and Statistics (DGBAS) into a clean, analysis-ready dataset, then analyses labour compensation, productivity, and profit trends across 17 industries using visualisation and regression.

---

## Project Structure

```
taiwan-industry-census/
├── data/
│   ├── raw/                         # Raw source files (not tracked by git)
│   │   ├── *.pdf                    # DGBAS census PDFs (ROC year 110)
│   │   └── A030101015_*.csv         # DGBAS CPI CSV (Big5 encoded)
│   └── clean/
│       ├── tw_industry_census.csv   # Parsed census data (long format)
│       ├── census_clean.csv         # Reshaped data for analysis
│       └── tw_cpi.csv               # CPI index (1981–2021)
├── scripts/
│   ├── Python/
│   │   ├── parse_pdfs.py            # PDF → tw_industry_census.csv
│   │   └── parse_cpi.py             # CPI CSV → tw_cpi.csv
│   └── R/
│       ├── 01_clean_data.R          # Load and inspect census data
│       ├── 02_visualization.R       # Generate figures
│       └── 03_regression.R          # Regression analysis
├── output/
│   └── figures/                     # PNG charts
├── report.Rmd                       # Full analysis report (R Markdown)
├── report.pdf                       # Compiled report
└── README.md
```

---

## Data

### `data/clean/tw_industry_census.csv`

Parsed from DGBAS census PDFs. Long format: one row per industry × indicator × year.

| Column | Description |
|---|---|
| `industry_code` | TSIC section letter (B–S) |
| `industry_name` | Industry name (English) |
| `indicator_id` | Indicator number (1–15) |
| `indicator_name` | Indicator description (English) |
| `unit` | Unit of measurement |
| `1981` … `2021` | Value for that census year (`None` if not surveyed) |
| `change_2016_to_2021_pct` | % change from 2016 to 2021 |

Coverage: 17 industries, 9 census years (1981–2021), 19 indicators each.

### `data/clean/tw_cpi.csv`

Annual CPI for Taiwan, base year 2021 (= 100).

| Column | Description |
|---|---|
| `year` | Gregorian year (ROC year + 1911) |
| `cpi_index` | CPI index value (base: 2021 = 100) |

Coverage: 1981–2021 (41 years).

---

## Analysis

### Visualisation (`02_visualization.R`)

Generates industry-level time series charts for:
- Labour compensation (nominal and CPI-deflated)
- Labour productivity (nominal and CPI-deflated)
- Capital–labour ratio
- Value added and value-added rate
- Labour cost ratio and profit rate
- Labour share of gross value added

### Regression (`03_regression.R`)

Investigates the productivity–wage relationship across Taiwan's industries:

- **Model 1**: Does productivity growth translate to wage growth?
  - OLS and employment-weighted regressions on `log(real_compensation) ~ log(real_labor_productivity)`
  - Split by early period (≤ 1996) and late period (≥ 2001) to test for a structural break around 2001
  - Structural break test using `strucchange`
- Real variables deflated by CPI (base 2021 = 100)

---

## Indicators

| ID | Indicator | Unit |
|---|---|---|
| 1 | Number of enterprises (year-end) | establishments |
| 2 | Number of employees (year-end) | persons |
| 3 | Average annual labour compensation per employed worker | NTD |
| 4 | Total annual receipts | million NTD |
| 5 | Total annual expenditures | million NTD |
| 6 | Total annual output | million NTD |
| 7 | Gross value added | million NTD |
| 8 | Net assets in actual use (year-end) | million NTD |
| 9 | Net fixed assets in actual use (year-end) | million NTD |
| 10(1) | Average employees per enterprise | persons |
| 10(2) | Average assets per enterprise | thousand NTD |
| 11 | Labour equipment ratio | thousand NTD |
| 12 | Labour productivity | thousand NTD |
| 13(1) | Gross value added per NTD of assets | NTD |
| 13(2) | Gross value added per NTD of fixed assets | NTD |
| 14 | Labour compensation as % of total expenditures | % |
| 15(1) | Value-added ratio | % |
| 15(2) | Profit ratio | % |
| 15(3) | Asset turnover ratio | % |

---

## Data Sources

- **Census PDFs**: DGBAS Census of Industry and Commerce — https://www.dgbas.gov.tw/np.asp?ctNode=2373
- **CPI**: DGBAS Consumer Price Basic Classification Index (消費者物價基本分類指數)

Place raw files in `data/raw/` to reproduce the cleaned datasets.

## Reproducing the Data

```bash
pip install pdfplumber
python scripts/Python/parse_pdfs.py   # → data/clean/tw_industry_census.csv
python scripts/Python/parse_cpi.py    # → data/clean/tw_cpi.csv
```

Then run the R scripts in order (`01` → `02` → `03`) in RStudio.
