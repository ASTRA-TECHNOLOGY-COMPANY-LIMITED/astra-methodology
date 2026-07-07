# Catalog Image-Generation Prompts (Step 2, fect-image)

Literal `mcp__fect-image__image_text2img` prompt templates. Substitute the `{...}` placeholders with product/brand/tone data. Use rich, art-directed prompts for premium quality.

## Prompts in this file
- Hero banner (Step 2.B) → `images/hero/`
- Category visual (Step 2.C) → `images/categories/`
- Editorial illustrations (Step 2.D), 5 types → `images/illustrations/`
- Lifestyle shot (Step 2.E) → `images/lifestyle/`

## Hero banner (Step 2.B)

```
Cinematic product catalog hero banner, {product-category} theme,
{DESIGN_TONE} aesthetic, premium commercial photography,
dramatic lighting, shallow depth of field, editorial magazine quality,
{brand-color} color accent, ultra-wide 21:9 composition,
negative space for text overlay on the left third
```

## Category visual (Step 2.C)

Generate one divider image per category when there are 2+ categories.

```
{category-name} product category editorial visual, {DESIGN_TONE} style,
abstract artistic background, luxury commercial catalog quality,
soft gradient lighting, cinematic color grading, 3:2 aspect ratio
```

## Editorial illustrations (Step 2.D)

Placement and generation rules per type:

| Illustration Type | Placement | Prompt Strategy |
|------------------|-----------|----------------|
| **Mood separator** | Between categories | Abstract, atmospheric, brand-color gradients |
| **Lifestyle scene** | Near hero/premium products | Product in aspirational real-life context |
| **Detail texture** | Background for spec sections | Macro texture, material close-up |
| **Infographic base** | Feature comparison sections | Clean geometric, data-visualization style |
| **Brand atmosphere** | Brand story page | Emotional, storytelling visual |

> Generation-count rules (how many of each to produce) live inline in SKILL.md §2.D.

**Mood separator**:
```
Abstract artistic illustration, {DESIGN_TONE} aesthetic,
flowing {brand-color} gradients, organic shapes, editorial magazine divider,
minimalist composition, ultra-clean, no text, 4:1 wide panoramic
```

**Lifestyle scene**:
```
{product-name} in {aspirational-context}, editorial lifestyle photography,
{target-audience-lifestyle} setting, warm natural lighting,
magazine-quality composition, {DESIGN_TONE} color palette, 16:9
```

**Detail texture**:
```
Macro close-up of {product-material/texture}, abstract product detail,
{DESIGN_TONE} color grading, shallow depth of field,
premium material texture, subtle bokeh, 3:2 aspect ratio
```

**Infographic base**:
```
Clean geometric abstract background, {DESIGN_TONE} color scheme,
subtle grid pattern, modern data visualization aesthetic,
plenty of negative space for overlay content, 16:9
```

**Brand atmosphere**:
```
{brand-story-theme} conceptual illustration, {DESIGN_TONE} editorial style,
cinematic dramatic lighting, emotional storytelling mood,
abstract artistic interpretation, premium quality, 2:1 wide
```

## Lifestyle shot (Step 2.E)

For products with no provided images and no Chrome MCP screenshots:

```
{product-name} in real-life premium setting, editorial product photography,
{usage-scene-description}, dramatic studio lighting with natural fill,
{DESIGN_TONE} mood, luxury commercial catalog quality,
styled with complementary props, shallow depth of field, 4:5 portrait
```
