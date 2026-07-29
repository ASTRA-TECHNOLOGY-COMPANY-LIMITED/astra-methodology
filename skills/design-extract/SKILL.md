---
name: design-extract
description: "Extracts an OKLCH color palette, font families, and spacing heuristics from design references (images, PDFs, URLs, screenshots) via Vision MCP or WebFetch, and writes a draft DESIGN.md Front Matter report to docs/design-system/extract-report-{date}.md. Report-only — merging into DESIGN.md happens via /design-init --apply-extract. Use when analyzing reference designs, competitor sites, or brand guideline documents."
argument-hint: "<paths-or-urls> [--auto]"
allowed-tools: Read, Write, Bash, Glob, Grep, WebFetch, AskUserQuestion, TodoWrite
---

# /design-extract — Reference-Based Design Token Extraction Skill

Analyzes design references such as images, PDFs, and URLs to extract OKLCH colors, fonts, and spacing tokens, and converts them into a draft DESIGN.md Front Matter.

## Design Philosophy

This skill implements the "reference-anchored design" principle (`vibe-coding-design-guide.md`) in code. To avoid the generic look produced by AI coding, abstract descriptions ("modern·clean") must be replaced with concrete references converted into tokens. This skill automates that conversion.

## Procedure

### Step 0: Argument parsing and input classification

The first positional argument of `$ARGUMENTS` is `<paths-or-urls>` (comma- or space-separated).

```bash
# Classify each input as one of four kinds
classify_input() {
  local input="$1"
  if [[ "$input" =~ ^https?:// ]]; then echo "url"
  elif [[ -f "$input" && "$input" =~ \.(png|jpg|jpeg|webp)$ ]]; then echo "image"
  elif [[ -f "$input" && "$input" =~ \.pdf$ ]]; then echo "pdf"
  elif [[ -d "$input" ]]; then echo "directory"
  else echo "unknown"; fi
}
```

Options:
- `--auto`: handle all HITL with defaults

> **This skill always generates the report only** (v5.4.0+ one-way policy). Merging into DESIGN.md only happens when the user explicitly invokes `/design-init --apply-extract=<report-path>` — to prevent a circular call (/design-extract ↔ /design-init).

### Step 1: Environment check

Check whether Vision MCP is available:

```bash
# Check whether fect-mcp is registered in the Claude Code MCP server list
# If unavailable, fall back to heuristics (direct CSS/HTML parsing)
HAS_VISION_MCP=$(claude mcp list 2>/dev/null | grep -c "fect-mcp" || echo 0)
```

| Environment | Extraction accuracy | Response |
|-------------|---------------------|----------|
| Vision MCP available | High (dominant-color clustering, font estimation) | Use first |
| WebFetch only | Medium (HTML/CSS parsing) | Handle URL inputs only |
| Neither | Low (manual input required) | Ask the user to enter tokens directly |

### Step 2: Per-input extraction workflow

#### Step 2A: Image extraction (requires Vision MCP)

```
mcp__fect-mcp__vision_analyze({
  image_path: "{input}",
  prompt: "Extract the following from this image: (1) 5-7 dominant colors as OKLCH. (2) 1-2 background/surface colors. (3) 1-2 accent colors. (4) Estimated font family (sans-serif/serif/mono). (5) Layout density (compact/comfortable/spacious). (6) Estimated border radius (sharp 0px / soft 4-8px / round 12-24px / pill). (7) Shadow usage intensity (none/subtle/medium/strong). Output as JSON."
})
```

Parse the response JSON to build an extraction-result dict.

#### Step 2B: PDF extraction

Render the PDF pages as images, then apply Step 2A to each page. Brand guideline PDFs usually carry explicit color hex codes and font names, so use `vision_ocr` to extract text and regex-match:

```
mcp__fect-mcp__vision_ocr({ image_path: "{rendered_page}" })
```

- `#[0-9A-Fa-f]{6}` → extract hex color → convert to `oklch()`
- `font-family: ['"]?([A-Za-z\s]+)['"]?` → font name

#### Step 2C: URL extraction

```bash
# 1. Fetch HTML
WebFetch(url="{input}", prompt="From the head section of this page, extract link[rel=stylesheet] / style tag contents and brand color hex/rgb/oklch values and font-family used in body class names")
```

From the WebFetch result:
- Extract `:root { --color-...: ... }` CSS custom properties
- Extract `font-family: ...` declarations
- Back-infer color families from Tailwind classes like `bg-blue-600` / `text-zinc-900`

If a browser backend is available (ego (lite) or Chrome MCP), take screenshots and additionally apply Step 2A to improve accuracy.

#### Step 2D: Directory extraction

Apply Step 2A to every `.png/.jpg/.webp` file in the directory. Gather dominant colors from multiple images and run frequency-based clustering (k=7).

### Step 3: Color → OKLCH conversion and ASTRA 11-step expansion

Expand the extracted dominant colors (typically 5-7) into the ASTRA standard 11 steps (50~950).

#### Step 3.1: hex/rgb → OKLCH conversion

Run the bundled conversion script (Ottosson OKLab algorithm, no external dependencies):

```bash
python3 "$CLAUDE_PLUGIN_ROOT/skills/design-extract/scripts/color-convert.py" "#3b82f6"
# → oklch(62.3% 0.188 259.8)

# Multiple colors at once
python3 "$CLAUDE_PLUGIN_ROOT/skills/design-extract/scripts/color-convert.py" "#3b82f6" "#10b981" "#f59e0b"

# stdin input
echo "#3b82f6" | python3 "$CLAUDE_PLUGIN_ROOT/skills/design-extract/scripts/color-convert.py" -
```

The output format follows the DESIGN.md Front Matter `tokens.color.primitive.*` convention (`oklch(L% C H)`). Pipe every extracted hex value through this script to guarantee consistency. If rgb()/rgba() input is needed, convert it to hex first, then call.

#### Step 3.2: Identify a single Primary color

From the extracted colors, pick a Primary that satisfies all of:
1. Non-neutral chroma (`chroma > 0.05`)
2. Most frequently occurring
3. Can guarantee WCAG contrast ≥ 4.5 (text/background combinations)

If multiple candidates exist, confirm with `AskUserQuestion` (in `--auto`, criterion #1 wins).

#### Step 3.3: Apply 11-step lightness curve

Keep the chosen Primary's hue·chroma and vary only the L value across 11 steps using the curve below:

```
shade  L (%)
50     97.0
100    93.2
200    87.0
300    78.5
400    70.7
500    62.3   ← anchor (preserve the Primary color's chroma)
600    54.6
700    48.8
800    42.4
900    37.9
950    28.2
```

Reference the same lightness curve in `$CLAUDE_PLUGIN_ROOT/skills/design-init/assets/color-palettes.yaml` for consistency.

### Step 4: Font mapping

Map extracted font names to the ASTRA recommended font set:

| Extracted family pattern | Mapping | Note |
|--------------------------|---------|------|
| Geist, GeistSans, geist-sans | Geist | Direct match |
| Inter, InterDisplay | Inter | Tailwind default |
| Manrope, manrope | Manrope | Vercel style |
| SF Pro, SFPro | -apple-system | Apple system |
| Pretendard | Pretendard | Korean script default kept |
| (Serif) Playfair, Lora, Merriweather | + serif accent | Activate Body §3 heading serif option |
| (Mono) JetBrains, Fira Code, IBM Plex Mono | JetBrains Mono | code/data areas |

Organize the extraction result in the following form:

```yaml
typography:
  fonts:
    sans:    "{primary_sans}, Pretendard Variable, Pretendard, -apple-system, sans-serif"
    mono:    "{primary_mono}, ui-monospace, monospace"
    heading: "{heading_font}"  # if a separate heading font was detected
```

### Step 5: Density/Radius/Shadow heuristics

Convert the layout heuristics from image analysis into tokens as follows:

| Heuristic | spacing default | radius default | shadow usage |
|-----------|-----------------|----------------|--------------|
| compact | 4px base, button h=32px | sm (4px) | xs/sm only |
| comfortable | 4px base, button h=40px | xl (12px) | md dominant |
| spacious | 4px base, button h=44px | 2xl (16px) | lg/xl dominant |
| sharp | — | none/sm | — |
| pill | — | full | — |

### Step 6: Generate extract report

Write the following to `docs/design-system/extract-report-{YYYY-MM-DD}.md`:

```markdown
# Design Extract Report

## Source References
- {input 1 — kind · path · analysis timestamp}
- {input 2 — ...}

## Extracted Tokens (Front Matter draft)
\`\`\`yaml
brand:
  inspired_by:
    - "{reference 1}"
    - "{reference 2}"
tokens:
  color:
    primitive:
      primary:
        50: ...
        ...
  typography:
    fonts:
      sans: "..."
...
\`\`\`

## Detected Patterns
- Layout density: {compact|comfortable|spacious}
- Radius preference: {sharp|soft|round|pill}
- Shadow usage: {none|subtle|medium|strong}
- Iconography: {line|filled|emoji|mixed}

## Aesthetic Flags
- [ ] Purple→Blue gradient hero (anti-AI red flag)
- [ ] Generic shadcn default look
- [ ] Distinctive element detected: {e.g., serif accent in headings}

## Confidence
- Color extraction: {high|medium|low} (Primary identified from {n} candidate colors)
- Font extraction: {high|medium|low} (source: CSS / OCR / estimation)
- Density extraction: {high|medium|low}

## Next Step (user decision)
1. Review the report: `cat docs/design-system/extract-report-{date}.md`
2. To merge into DESIGN.md, explicitly invoke:
   `/design-init --apply-extract=docs/design-system/extract-report-{date}.md`
3. To review only without merging, simply stop here.
```

> **This skill ends here** — it does not auto-invoke `/design-init`. One-way single-call principle (incorporates advisor feedback, v5.4.0).

## Workflow checklist

- [ ] Step 0: argument parsing + input classification (image/pdf/url/directory)
- [ ] Step 1: environment check (Vision MCP / WebFetch availability)
- [ ] Step 2: per-input-type extraction (2A/2B/2C/2D)
- [ ] Step 3: hex → OKLCH conversion + 11-step lightness expansion
- [ ] Step 4: font mapping (ASTRA recommended set)
- [ ] Step 5: density/radius/shadow heuristics
- [ ] Step 6: generate extract-report then stop (user merges via /design-init --apply-extract=...)

## Per-input-type accuracy guide

| Input | Accuracy | Recommended use |
|-------|----------|-----------------|
| Brand guideline PDF (hex codes explicit) | ⭐⭐⭐⭐⭐ | Most accurate. Always use first |
| Official design system site (e.g., stripe.com/design) | ⭐⭐⭐⭐ | Extract CSS custom properties directly |
| Competitor UI screenshot | ⭐⭐⭐ | Dominant color accurate; fonts estimated |
| Figma export image | ⭐⭐⭐ | spacing/radius derivable from grid analysis |
| Photo or art reference | ⭐⭐ | Trust colors only. Ignore font/spacing |

## Anti-patterns — strictly forbidden

- **Extract only — never edit DESIGN.md directly**: Merging is `/design-init`'s job. This skill only extracts and drafts.
- **Never adopt a color without WCAG verification**: Include contrast check results in the Step 6 report. Mark anything below 4.5 as a warning.
- **Do not adopt every candidate**: Even when 7 dominant colors are extracted, Primary is 1. Record the rest in the report only.
- **Do not attempt image processing without Vision MCP**: When heuristics are unreliable, ask the user to enter hex codes directly instead.

## Evaluation scenarios

1. **Brand PDF (OCR + hex extraction)**: 5 hex colors extracted via OCR and converted to OKLCH accurately. Font names matched from PDF body text.
2. **Competitor URL (CSS parsing)**: Colors/fonts extracted accurately from `:root` custom properties. Tailwind-class inference works as a secondary signal.
3. **Screenshot only (Vision MCP)**: Primary is picked from 5 dominant colors based on chroma. Layout density estimation matches ground truth.

## Four-principles application

- **Think Before Coding**: In Step 1, when Vision MCP is missing, clearly notify the user and let them decide.
- **Simplicity First**: After extraction, automatically align to the ASTRA standard 11-step curve. The user does not have to enter 50/100/200 one by one.
- **Surgical Changes**: This skill never edits DESIGN.md directly. It stops at producing the report + invocation guidance for /design-init.
- **Goal-Driven Execution**: The contrast/aesthetic flags in the Step 6 report are the explicit PASS criteria. The user reviews the report and decides the next step.
