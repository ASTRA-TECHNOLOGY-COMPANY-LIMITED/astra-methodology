# International Standard Code Detailed Reference Guide

## 1. ISO 3166-1 Country Codes

### Overview
ISO 3166-1 is an international standard for identifying countries and dependent territories.

### Data File
`data/iso_3166_1_countries.json` — 249 entries

### Schema
```json
{
  "koreanName": "대한민국",
  "englishName": "Korea (the Republic of)",
  "alpha2": "KR",
  "alpha3": "KOR",
  "numeric": "410",
  "independent": true
}
```

| Field | Description | Example |
|---|---|---|
| `koreanName` | Korean country name | 대한민국, 미국, 일본 |
| `englishName` | ISO official English name | Korea (the Republic of) |
| `alpha2` | 2-letter alphabetic code | KR, US, JP |
| `alpha3` | 3-letter alphabetic code | KOR, USA, JPN |
| `numeric` | 3-digit numeric code (zero-padded) | 410, 840, 392 |
| `independent` | Whether the country is independent | true/false |

### Frequently Used Country Codes

| Korean Name | alpha-2 | alpha-3 | numeric | Calling Code |
|---|---|---|---|---|
| 대한민국 | KR | KOR | 410 | +82 |
| 미국 | US | USA | 840 | +1 |
| 일본 | JP | JPN | 392 | +81 |
| 중국 | CN | CHN | 156 | +86 |
| 영국 | GB | GBR | 826 | +44 |
| 독일 | DE | DEU | 276 | +49 |
| 프랑스 | FR | FRA | 250 | +33 |
| 캐나다 | CA | CAN | 124 | +1 |
| 호주 | AU | AUS | 036 | +61 |
| 인도 | IN | IND | 356 | +91 |
| 싱가포르 | SG | SGP | 702 | +65 |
| 대만 | TW | TWN | 158 | +886 |
| 태국 | TH | THA | 764 | +66 |
| 베트남 | VN | VNM | 704 | +84 |
| 필리핀 | PH | PHL | 608 | +63 |

### Usage Rules

1. **Use alpha-2 as the primary identifier**: Use alpha-2 for DB storage, API parameters, and internal logic
2. **alpha-3 is for display/exchange**: Use in ISO standard document exchange and official reports
3. **numeric is for alphabet-independent scenarios**: When identification independent of character systems is needed in multilingual environments
4. **`independent` filtering**: Filter with `independent: true` to show only independent countries in dropdowns

---

## 2. ISO 3166-2 Region/Administrative Division Codes

### Overview
ISO 3166-2 is an international standard for identifying administrative divisions (cities/provinces/states/prefectures, etc.) within each country.

### Data File
`data/iso_3166_2_regions.json` — 21 countries, 653 administrative divisions

### Schema
```json
{
  "KR": {
    "countryNameEn": "South Korea",
    "countryNameKo": "대한민국",
    "alpha2": "KR",
    "subdivisionCount": 17,
    "subdivisions": [
      {
        "code": "KR-11",
        "nameEn": "Seoul",
        "nameLocal": "서울특별시",
        "type": "Special city"
      }
    ]
  }
}
```

| Field | Description | Example |
|---|---|---|
| `code` | ISO 3166-2 code (country-subdivision) | KR-11, US-CA, JP-13 |
| `nameEn` | English region name | Seoul, California, Tokyo |
| `nameLocal` | Local language region name (if available) | 서울특별시, 東京都 |
| `type` | Administrative division type | Special city, State, Prefecture |

### Included Countries

| Country | alpha-2 | Number of Divisions | Division Type |
|---|---|---|---|
| 대한민국 | KR | 17 | Special city, Metropolitan city, Province, Special autonomous city/province |
| United States | US | 57 | State, District, Territory |
| Japan | JP | 47 | Prefecture (都道府県) |
| China | CN | 34 | Province, Municipality, Autonomous Region, SAR |
| United Kingdom | GB | 4 | Country (England, Scotland, Wales, NI) |
| Germany | DE | 16 | Land (Bundesland) |
| France | FR | 18 | Region (Région) |
| Canada | CA | 13 | Province, Territory |
| Australia | AU | 8 | State, Territory |
| India | IN | 36 | State, Union Territory |
| Brazil | BR | 27 | State, Federal District |
| Italy | IT | 20 | Region (Regione) |
| Spain | ES | 19 | Autonomous Community, City |
| Russia | RU | 85 | Oblast, Republic, Krai, City, Autonomous |
| Mexico | MX | 32 | State, Federal District |
| Indonesia | ID | 38 | Province (Provinsi) |
| Thailand | TH | 77 | Province (Changwat) |
| Vietnam | VN | 63 | Province, Municipality |
| Philippines | PH | 82 | Province, City, District |
| Singapore | SG | 5 | District |
| Taiwan | TW | 22 | City, County |

### Usage Rules

1. **Link to country selection**: Dynamically load the administrative division list for the selected country
2. **Preserve code format**: Store the full `KR-11` (country code + hyphen + subdivision code)
3. **Locale-aware display names**: Use `nameLocal` for Korean UI, `nameEn` for English UI
4. **Handle unsupported countries**: For countries not in the data, hide region selection or switch to free-text input

---

## 3. ITU-T E.164 International Telephone Calling Codes

### Overview
ITU-T E.164 is an international standard that defines the international public telecommunication numbering plan.

### Data File
`data/country_calling_codes.json` — 245 entries

### Schema
```json
{
  "countryNameEn": "South Korea",
  "countryNameKo": "대한민국",
  "alpha2": "KR",
  "callingCode": "+82",
  "zone": 8
}
```

When shared codes exist:
```json
{
  "countryNameEn": "United States",
  "countryNameKo": "미국",
  "alpha2": "US",
  "callingCode": "+1",
  "zone": 1,
  "sharedWith": ["CA", "PR", "VI", "GU", "AS", "MP"]
}
```

| Field | Description | Example |
|---|---|---|
| `countryNameEn` | English country name | South Korea |
| `countryNameKo` | Korean country name | 대한민국 |
| `alpha2` | ISO 3166-1 alpha-2 | KR |
| `callingCode` | International calling code (with + prefix) | +82 |
| `zone` | ITU zone number (1-9) | 8 |
| `sharedWith` | List of countries sharing the same calling code (optional) | ["CA", "PR"] |

### ITU Zone Classification

| Zone | Region | Representative Calling Code |
|---|---|---|
| 1 | North America (NANP) | +1 |
| 2 | Africa | +2xx |
| 3 | Southern/Eastern Europe | +3xx |
| 4 | Northern/Western Europe | +4x |
| 5 | Central/South America | +5xx |
| 6 | Southeast Asia/Oceania | +6x |
| 7 | Russia/CIS | +7 |
| 8 | East Asia | +8x |
| 9 | West Asia/South Asia | +9xx |

### Usage Rules

1. **Store in full E.164 format**: `+calling code + local number` (without spaces/hyphens). Maximum 15 digits
2. **Separate calling code and local number input**: In the UI, use country selection (auto-set calling code) + local number input
3. **Calling code display format**: Display as `+82` format (including + symbol)
4. **Shared code caution**: +1 is shared by NANP countries including the US/Canada. Distinguish countries by alpha-2

---

## 4. Component Implementation Patterns

### 4.1 Country Selector

#### TypeScript/React

```tsx
import countriesData from '@/data/iso_3166_1_countries.json';

interface CountryOption {
  value: string;   // alpha-2
  label: string;   // display name
  alpha3: string;
  numeric: string;
}

// Priority countries sorted first
const PRIORITY_COUNTRIES = ['KR', 'US', 'JP', 'CN', 'GB', 'DE'];

export function getCountryOptions(locale: 'ko' | 'en' = 'ko'): CountryOption[] {
  const countries = countriesData
    .filter((c) => c.independent)
    .map((c) => ({
      value: c.alpha2,
      label: locale === 'ko' ? c.koreanName : c.englishName,
      alpha3: c.alpha3,
      numeric: c.numeric,
    }));

  const priority = countries.filter((c) => PRIORITY_COUNTRIES.includes(c.value));
  const rest = countries
    .filter((c) => !PRIORITY_COUNTRIES.includes(c.value))
    .sort((a, b) => a.label.localeCompare(b.label, locale));

  return [...priority, ...rest];
}
```

#### Java/Spring

```java
@Service
public class CountryService {

  private List<CountryDto> countries;

  @PostConstruct
  public void init() {
    ObjectMapper mapper = new ObjectMapper();
    InputStream is = getClass().getResourceAsStream("/data/iso_3166_1_countries.json");
    countries = mapper.readValue(is, new TypeReference<List<CountryDto>>() {});
  }

  public List<CountryDto> getCountries(boolean independentOnly) {
    return countries.stream()
        .filter(c -> !independentOnly || c.isIndependent())
        .sorted(Comparator.comparing(CountryDto::getKoreanName))
        .collect(Collectors.toList());
  }

  public Optional<CountryDto> findByAlpha2(String alpha2) {
    return countries.stream()
        .filter(c -> c.getAlpha2().equalsIgnoreCase(alpha2))
        .findFirst();
  }
}
```

#### Python/FastAPI

```python
import json
from pathlib import Path
from functools import lru_cache

@lru_cache
def load_countries() -> list[dict]:
    path = Path(__file__).parent / "data" / "iso_3166_1_countries.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def get_country_options(independent_only: bool = True, locale: str = "ko") -> list[dict]:
    countries = load_countries()
    if independent_only:
        countries = [c for c in countries if c["independent"]]
    name_key = "koreanName" if locale == "ko" else "englishName"
    return [
        {"value": c["alpha2"], "label": c[name_key]}
        for c in sorted(countries, key=lambda c: c[name_key])
    ]
```

### 4.2 Region Selector

#### TypeScript/React

```tsx
import regionsData from '@/data/iso_3166_2_regions.json';

interface RegionOption {
  value: string;   // ISO 3166-2 code (e.g., "KR-11")
  label: string;   // display name
  type: string;    // administrative division type
}

export function getRegionOptions(
  countryCode: string,
  locale: 'ko' | 'en' = 'ko',
): RegionOption[] {
  const country = regionsData[countryCode as keyof typeof regionsData];
  if (!country) {
    return [];
  }

  return country.subdivisions.map((s) => ({
    value: s.code,
    label: locale === 'ko' && s.nameLocal ? s.nameLocal : s.nameEn,
    type: s.type,
  }));
}
```

#### Java/Spring

```java
@Service
public class RegionService {

  private Map<String, RegionCountryDto> regions;

  @PostConstruct
  public void init() {
    ObjectMapper mapper = new ObjectMapper();
    InputStream is = getClass().getResourceAsStream("/data/iso_3166_2_regions.json");
    regions = mapper.readValue(is, new TypeReference<Map<String, RegionCountryDto>>() {});
  }

  public List<SubdivisionDto> getRegions(String countryCode) {
    RegionCountryDto country = regions.get(countryCode.toUpperCase());
    if (country == null) {
      return Collections.emptyList();
    }
    return country.getSubdivisions();
  }
}
```

#### Python/FastAPI

```python
import json
from pathlib import Path
from functools import lru_cache

@lru_cache
def load_regions() -> dict:
    path = Path(__file__).parent / "data" / "iso_3166_2_regions.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def get_region_options(country_code: str, locale: str = "ko") -> list[dict]:
    regions = load_regions()
    country = regions.get(country_code.upper())
    if not country:
        return []
    name_key = "nameLocal" if locale == "ko" else "nameEn"
    return [
        {
            "value": s["code"],
            "label": s.get(name_key) or s["nameEn"],
            "type": s["type"],
        }
        for s in country["subdivisions"]
    ]
```

### 4.3 Phone Number Input

#### TypeScript/React

```tsx
import callingCodesData from '@/data/country_calling_codes.json';

interface CallingCodeOption {
  value: string;       // callingCode (e.g., "+82")
  label: string;       // display name
  alpha2: string;      // country code
  countryName: string; // country name
}

const PRIORITY_COUNTRIES = ['KR', 'US', 'JP', 'CN'];

export function getCallingCodeOptions(locale: 'ko' | 'en' = 'ko'): CallingCodeOption[] {
  const codes = callingCodesData.map((c) => ({
    value: c.callingCode,
    label: `${c.callingCode} ${locale === 'ko' ? c.countryNameKo : c.countryNameEn}`,
    alpha2: c.alpha2,
    countryName: locale === 'ko' ? c.countryNameKo : c.countryNameEn,
  }));

  const priority = codes.filter((c) => PRIORITY_COUNTRIES.includes(c.alpha2));
  const rest = codes
    .filter((c) => !PRIORITY_COUNTRIES.includes(c.alpha2))
    .sort((a, b) => a.countryName.localeCompare(b.countryName, locale));

  return [...priority, ...rest];
}

// E.164 phone number composition
export function toE164(callingCode: string, localNumber: string): string {
  const digits = localNumber.replace(/[^0-9]/g, '');
  // Remove leading 0 (converting from domestic to international format)
  const normalized = digits.startsWith('0') ? digits.slice(1) : digits;
  return `${callingCode}${normalized}`;
}

// E.164 phone number parsing
export function parseE164(
  e164: string,
): { callingCode: string; localNumber: string } | null {
  const match = callingCodesData
    .map((c) => c.callingCode)
    .sort((a, b) => b.length - a.length) // Match longest code first
    .find((code) => e164.startsWith(code));

  if (!match) {
    return null;
  }

  return {
    callingCode: match,
    localNumber: e164.slice(match.length),
  };
}
```

#### Java/Spring

```java
@Service
public class PhoneNumberService {

  private List<CallingCodeDto> callingCodes;

  @PostConstruct
  public void init() {
    ObjectMapper mapper = new ObjectMapper();
    InputStream is = getClass().getResourceAsStream("/data/country_calling_codes.json");
    callingCodes = mapper.readValue(is, new TypeReference<List<CallingCodeDto>>() {});
  }

  public String toE164(String callingCode, String localNumber) {
    String digits = localNumber.replaceAll("[^0-9]", "");
    if (digits.startsWith("0")) {
      digits = digits.substring(1);
    }
    return callingCode + digits;
  }

  public Optional<CallingCodeDto> findByAlpha2(String alpha2) {
    return callingCodes.stream()
        .filter(c -> c.getAlpha2().equalsIgnoreCase(alpha2))
        .findFirst();
  }

  public List<CallingCodeDto> getCallingCodes() {
    return Collections.unmodifiableList(callingCodes);
  }
}
```

#### Python/FastAPI

```python
import re
import json
from pathlib import Path
from functools import lru_cache

@lru_cache
def load_calling_codes() -> list[dict]:
    path = Path(__file__).parent / "data" / "country_calling_codes.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def to_e164(calling_code: str, local_number: str) -> str:
    digits = re.sub(r"[^0-9]", "", local_number)
    if digits.startswith("0"):
        digits = digits[1:]
    return f"{calling_code}{digits}"

def parse_e164(e164: str) -> dict | None:
    codes = sorted(
        [c["callingCode"] for c in load_calling_codes()],
        key=len,
        reverse=True,
    )
    for code in codes:
        if e164.startswith(code):
            return {"callingCode": code, "localNumber": e164[len(code):]}
    return None
```

### 4.4 Address Input Form

Country -> Region -> Detailed address linked pattern:

```typescript
// Address data model
interface InternationalAddress {
  countryCode: string;     // ISO 3166-1 alpha-2 (e.g., "KR")
  regionCode: string;      // ISO 3166-2 (e.g., "KR-11")
  addressLine1: string;    // Primary address
  addressLine2?: string;   // Detailed address
  postalCode?: string;     // Postal code
}

// Update region list on country change
function onCountryChange(countryCode: string): void {
  const regions = getRegionOptions(countryCode);
  // Update region selection dropdown
  // Reset previous region selection
}
```

---

## 5. DB Column Mapping Rules

International standard code-related DB columns follow the rules below alongside the public data standard:

| Logical Name | Physical Column Name | Type | Reference Standard |
|---|---|---|---|
| Country code | NATN_CD | CHAR(2) | ISO 3166-1 alpha-2 |
| Country code (3-letter) | NATN_A3_CD | CHAR(3) | ISO 3166-1 alpha-3 |
| Country numeric code | NATN_NO | CHAR(3) | ISO 3166-1 numeric |
| Region code | RGN_CD | VARCHAR(6) | ISO 3166-2 |
| International phone number | INTL_TELNO | VARCHAR(15) | E.164 |
| Country calling code | NATN_TELNO | VARCHAR(5) | ITU-T calling code |
| Country name (Korean) | NATN_KO_NM | VARCHAR(50) | iso_3166_1_countries.json |
| Country name (English) | NATN_EN_NM | VARCHAR(100) | iso_3166_1_countries.json |
| Region name (local) | RGN_LCL_NM | VARCHAR(100) | iso_3166_2_regions.json |
| Region name (English) | RGN_EN_NM | VARCHAR(100) | iso_3166_2_regions.json |

### JPA Entity Example

```java
@Entity
@Table(name = "TB_INTL_ADDR")
public class InternationalAddress {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  @Column(name = "INTL_ADDR_SN")
  private Long internationalAddressSn;

  @Column(name = "NATN_CD", length = 2, nullable = false,
      columnDefinition = "CHAR(2)")
  private String nationCode;

  @Column(name = "RGN_CD", length = 6)
  private String regionCode;

  @Column(name = "INTL_TELNO", length = 15)
  private String internationalPhoneNumber;

  @Column(name = "NATN_TELNO", length = 5)
  private String nationPhoneNumber;

  @Column(name = "ADDR1", length = 200, nullable = false)
  private String addressLine1;

  @Column(name = "ADDR2", length = 200)
  private String addressLine2;

  @Column(name = "REG_DT")
  private LocalDateTime regDt;

  @Column(name = "CHG_DT")
  private LocalDateTime chgDt;
}
```

---

## 6. Validation Rules

### Country Code Validation
- alpha-2: Exactly 2 uppercase alphabetic characters, verify existence in `iso_3166_1_countries.json`
- alpha-3: Exactly 3 uppercase alphabetic characters

### Region Code Validation
- Format: `{alpha-2}-{subdivision code}` (e.g., `KR-11`, `US-CA`)
- Verify that the country code portion is a valid ISO 3166-1 alpha-2
- Verify that the code exists in the corresponding country's `iso_3166_2_regions.json`

### Phone Number Validation
- E.164 format: starts with `+`, maximum 15 digit characters
- Regex: `^\+[1-9]\d{1,14}$`
- Verify that the calling code exists in `country_calling_codes.json`

```typescript
// Validation functions
export function isValidCountryCode(code: string): boolean {
  return /^[A-Z]{2}$/.test(code)
    && countriesData.some((c) => c.alpha2 === code);
}

export function isValidRegionCode(code: string): boolean {
  const [country] = code.split('-');
  const regionData = regionsData[country as keyof typeof regionsData];
  return regionData?.subdivisions.some((s) => s.code === code) ?? false;
}

export function isValidE164(phone: string): boolean {
  return /^\+[1-9]\d{1,14}$/.test(phone);
}
```
