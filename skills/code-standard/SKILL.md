---
name: code-standard
description: >
  Automatically provides support for writing code based on ISO 3166-1/3166-2 and
  ITU-T E.164 standard data when implementing components that handle international
  standard codes such as phone number inputs, country selectors, and region selectors.
---

# International Standard Code Application Skill

When implementing phone number, country code, and region code related components, you must follow the standards below.
For the detailed guide, refer to code-standard-reference.md in this directory.

## Application Targets

Automatically applied when writing/modifying files that meet the following conditions:

- File name contains `phone`, `tel`, `country`, `region`, `address`, `locale`, `i18n`, `intl`
- Code contains logic related to phone number input, country selection, or region/address selection
- Code handles country codes (alpha-2/alpha-3), region codes (ISO 3166-2), or international phone number data

## Reference Data Files

| File | Standard | Contents |
|---|---|---|
| `data/iso_3166_1_countries.json` | ISO 3166-1 | 249 countries — alpha-2, alpha-3, numeric, Korean name, English name, independence status |
| `data/iso_3166_2_regions.json` | ISO 3166-2 | 21 countries, 653 administrative regions — region code, English name, local name, subdivision type |
| `data/country_calling_codes.json` | ITU-T E.164 | 245 entries — international calling codes, ITU zone, shared code information |

## Core Rules

### 1. Use ISO 3166-1 alpha-2 codes for country identification

- Use 2-character uppercase alpha-2 codes for all fields that identify a country (e.g., `KR`, `US`, `JP`)
- Store as codes, not full name strings — display names are looked up from `iso_3166_1_countries.json`
- Use alpha-3 when 3-character codes are needed (e.g., `KOR`, `USA`, `JPN`)

```typescript
// Good
interface Address {
  countryCode: string;  // ISO 3166-1 alpha-2 (e.g., "KR")
  regionCode: string;   // ISO 3166-2 (e.g., "KR-11")
}

// Bad
interface Address {
  country: string;  // "South Korea" — direct string storage prohibited
}
```

### 2. Use ISO 3166-2 codes for regions/administrative divisions

- Use ISO 3166-2 codes for fields that identify a region (e.g., `KR-11`, `US-CA`)
- Code format: `{alpha-2}-{subdivision}` (country code + hyphen + subdivision code)
- Region lists are filtered from `iso_3166_2_regions.json` based on the selected country

### 3. Phone numbers must follow E.164 format

- International phone number format: `+{country code}{number}` (e.g., `+821012345678`)
- Country codes are looked up from `country_calling_codes.json`
- Input UI should separate country selection and number input
- Store in full E.164 format when saving

```typescript
// Good: Separate country code and number input, store as E.164
const phoneNumber = `${callingCode}${localNumber.replace(/[^0-9]/g, '')}`;
// e.g., "+82" + "1012345678" → "+821012345678"

// Bad: Free-form text input
const phone = userInput; // Format not guaranteed
```

### 4. Country/region selection UI data should be constructed from standard JSON files

**Country selection dropdown**:
- Construct list from `iso_3166_1_countries.json`
- Display: Korean name or English name (depending on locale)
- Value: alpha-2 code
- Place major countries at the top (Korea, USA, Japan, China, etc.)

**Region selection dropdown**:
- Filter administrative regions for the selected country from `iso_3166_2_regions.json`
- Display: local name (`nameLocal`) or English name (`nameEn`)
- Value: ISO 3166-2 code (e.g., `KR-11`)
- Update region list in conjunction with country selection

**Phone number country code selector**:
- Construct list from `country_calling_codes.json`
- Display: `flag + country name + calling code` (e.g., `🇰🇷 South Korea +82`)
- Value: callingCode (e.g., `+82`)
- Store alpha-2 code alongside for country identification

### 5. Data model field rules

| Field Purpose | Recommended Field Name | Type | Description |
|---|---|---|---|
| Country code | `countryCode` / `NATN_CD` | CHAR(2) | ISO 3166-1 alpha-2 |
| Country code (3-char) | `countryAlpha3` / `NATN_A3_CD` | CHAR(3) | ISO 3166-1 alpha-3 |
| Region code | `regionCode` / `RGN_CD` | VARCHAR(6) | ISO 3166-2 (e.g., KR-11) |
| International phone number | `phoneNumber` / `INTL_TELNO` | VARCHAR(15) | E.164 full number |
| Calling code | `callingCode` / `NATN_TELNO` | VARCHAR(5) | International calling code (e.g., +82) |

### 6. Language-specific implementation patterns

#### TypeScript/React

```typescript
// Country selection component data type
interface Country {
  koreanName: string;
  englishName: string;
  alpha2: string;      // Used as value
  alpha3: string;
  numeric: string;
}

// Region selection data type
interface Region {
  code: string;        // ISO 3166-2 code (e.g., "KR-11")
  nameEn: string;
  nameLocal?: string;
  type: string;
}

// Phone number input data type
interface CallingCode {
  countryNameKo: string;
  alpha2: string;
  callingCode: string;  // e.g., "+82"
}
```

#### Java/Spring

```java
// Country code field
@Column(name = "NATN_CD", length = 2, columnDefinition = "CHAR(2)")
private String nationCode;  // ISO 3166-1 alpha-2

// Region code field
@Column(name = "RGN_CD", length = 6)
private String regionCode;  // ISO 3166-2 (e.g., "KR-11")

// International phone number field
@Column(name = "INTL_TELNO", length = 15)
private String internationalPhoneNumber;  // E.164 format
```

#### Python/Django

```python
# Country code field
nation_code = models.CharField(
    max_length=2, verbose_name="Country Code"
)  # ISO 3166-1 alpha-2

# Region code field
region_code = models.CharField(
    max_length=6, verbose_name="Region Code"
)  # ISO 3166-2

# International phone number field
intl_phone_number = models.CharField(
    max_length=15, verbose_name="International Phone Number"
)  # E.164 format
```
