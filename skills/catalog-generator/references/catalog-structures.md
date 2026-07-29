# Catalog Data & Output Structures

Reference skeletons for two structures used by the pipeline.

## Sections in this file
- Product data normalization schema (Step 0.B)
- Output directory structure (Step 1.A)

## Product data normalization schema (Step 0.B)

Normalize all collected product data into this internal standard structure:

```json
{
  "catalog": {
    "name": "{catalog-name}",
    "brand": "{brand-name}",
    "tagline": "{brand-slogan}",
    "contact": { "phone": "", "email": "", "website": "", "address": "" }
  },
  "categories": [
    {
      "id": "cat-01",
      "name": "{category-name}",
      "description": "{category-description}",
      "products": [
        {
          "id": "prod-001",
          "name": "{product-name}",
          "price": 0,
          "originalPrice": null,
          "description": "{product-description}",
          "features": ["{feature-1}", "{feature-2}"],
          "specs": { "{spec-key}": "{value}" },
          "images": ["{image-path}"],
          "badges": [],
          "crossSell": ["{related-product-id}"],
          "tier": "standard|premium|budget"
        }
      ]
    }
  ]
}
```

## Output directory structure (Step 1.A)

```
catalog/{catalog-name}/
├── index.html              # Cover + TOC + navigation hub
├── pages/                  # Individual page HTML files
│   ├── 01-cover.html       # Cover (standalone view)
│   ├── 02-brand-story.html # Brand story (optional)
│   ├── 03-{category}.html  # Category product pages
│   ├── {NN}-showcase.html  # Screenshot showcase — "See it in action" (when SERVICE_URL)
│   └── XX-contact.html     # Order/contact info
├── assets/
│   ├── tokens.css          # Design tokens (colors, typography, spacing)
│   ├── catalog-base.css    # Layout & typography
│   ├── catalog-components.css  # Product cards, badges, CTAs, screenshots, illustrations
│   ├── catalog-print.css   # Print-optimized styles
│   └── catalog-interactions.css # Hover, transitions, animations
├── images/                 # Product images + AI-generated visuals
│   ├── hero/               # Hero banner images
│   ├── products/           # Product images
│   ├── lifestyle/          # Lifestyle shots (AI-generated)
│   ├── illustrations/      # Editorial illustrations (AI-generated, mood/atmosphere)
│   ├── categories/         # Category visuals (AI-generated)
│   └── screenshots/        # Browser-captured screenshots
│       ├── desktop/        # Desktop viewport (1280×800)
│       ├── tablet/         # Tablet viewport (768×1024)
│       └── mobile/         # Mobile viewport (375×812)
└── shared/
    ├── nav.js              # Navigation (page transitions, TOC)
    ├── interactions.js     # Interactions (filter, search, gallery, screenshot tabs)
    └── theme.js            # Dark mode, font size adjustment
```
