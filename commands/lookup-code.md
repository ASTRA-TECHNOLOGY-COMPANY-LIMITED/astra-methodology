---
description: Looks up country codes, region codes, and international calling codes
argument-hint: "<country name|code|calling code> (e.g., 대한민국, KR, +82, KR-11)"
allowed-tools: Read
---

# International Standard Code Lookup

Look up the international standard code corresponding to "$ARGUMENTS".

## Reference Data

| Lookup Target | Data File | Search Fields |
|---|---|---|
| Country | `${CLAUDE_PLUGIN_ROOT}/data/iso_3166_1_countries.json` | `koreanName`, `englishName`, `alpha2`, `alpha3` |
| Region | `${CLAUDE_PLUGIN_ROOT}/data/iso_3166_2_regions.json` | `code`, `nameEn`, `nameLocal` |
| Calling code | `${CLAUDE_PLUGIN_ROOT}/data/country_calling_codes.json` | `countryNameKo`, `countryNameEn`, `alpha2`, `callingCode` |

## Lookup Procedure

### Step 1: Input Analysis

Analyze the input to determine the lookup type:

- **Country lookup**: Country name (Korean/English) or alpha-2/alpha-3 code input
  - e.g., `대한민국`, `South Korea`, `KR`, `KOR`
- **Region lookup**: ISO 3166-2 code or `country:region name` format input
  - e.g., `KR-11`, `대한민국:서울`, `US:California`
- **Calling code lookup**: Country name or `+calling code` format input
  - e.g., `+82`, `+1`, `대한민국 국번`

If only a country name is entered, output all information for that country (country code + region list + calling code) together.

### Step 2: Data Search

Search the corresponding data file. If no exact match is found, show up to 10 partial match results.

### Step 3: Result Output

## Output Format

### Country Lookup Result

| Item | Value |
|---|---|
| **Korean Country Name** | (Korean name) |
| **English Country Name** | (ISO official English name) |
| **Alpha-2 Code** | (2 digits) |
| **Alpha-3 Code** | (3 digits) |
| **Numeric Code** | (3 digits) |
| **Independent Country** | Yes/No |
| **International Calling Code** | (calling code) |
| **ITU Zone** | (zone number) |

### Region List (if data available)

| # | ISO 3166-2 Code | English Name | Local Name | Subdivision Type |
|---|---|---|---|---|
| 1 | KR-11 | Seoul | 서울특별시 | Special city |
| 2 | ... | ... | ... | ... |

### DB Column Mapping

| Purpose | Physical Column Name | Type | Example Value |
|---|---|---|---|
| Country code storage | `NATN_CD` | CHAR(2) | (alpha-2) |
| Region code storage | `RGN_CD` | VARCHAR(6) | (ISO 3166-2) |
| International phone number | `INTL_TELNO` | VARCHAR(15) | +(calling code)(number) |

### Partial Match Found

If no exact match for the input, show up to 10 partial match results:

| # | Korean Name | English Name | Alpha-2 | Calling Code |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |

### No Results Found

"No international standard code matching the input was found."
Suggest similar country names if available.
