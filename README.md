# Taiwan Industry Census Data (1981–2021)

Parses the Taiwan **Census of Industry and Commerce** (工商及服務業普查) published by the Directorate-General of Budget, Accounting and Statistics (DGBAS) into a clean, analysis-ready CSV.

## Coverage

- **17 industries** (TSIC sections B–S, excluding A and O)
- **9 census years**: 1981, 1986, 1991, 1996, 2001, 2006, 2011, 2016, 2021
- **19 economic indicators** per industry per year

## Output: `tw_industry_census.csv`

| Column | Description |
|---|---|
| `industry_code` | TSIC section letter (B–S) |
| `industry_name` | Industry name (English) |
| `indicator_id` | Indicator number (1–15) |
| `indicator_name` | Indicator description (English) |
| `unit` | Unit of measurement |
| `1981` … `2021` | Value for that census year (`None` if not surveyed) |
| `change_2016_to_2021_pct` | % change from 2016 to 2021 |

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

## Data Source

Original PDFs are published by the DGBAS, Executive Yuan, Taiwan:
https://www.dgbas.gov.tw/np.asp?ctNode=2373

Download the ROC year 110 (2021) census report PDFs and place them in a `raw data/` folder to reproduce the output.

## Usage

```bash
pip install pdfplumber
python parse_pdfs.py
```

Outputs `tw_industry_census.csv` in the project root.
