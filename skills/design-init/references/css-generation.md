# design-tokens.css Generation (design-init Step 6 detail)

Read this when running Step 6 (`--regenerate-css`, or the auto-call from Step 4). It covers Front Matter parsing, reference resolution, and the CSS file structure. The transformation-rules table stays in SKILL.md Step 6 as the mainline mapping.

## Step 6.1: Front Matter parsing + reference resolution

The DESIGN.md Front Matter is standard YAML, but semantic tokens use the ASTRA-specific reference syntax `"{tokens.color.primitive.neutral.0}"` (instead of YAML anchors, for readability). Therefore handle in two stages:

```bash
python3 - <<'PY'
import yaml, re, sys

with open('docs/design-system/DESIGN.md') as f:
    content = f.read()
m = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
if not m:
    sys.exit("DESIGN.md Front Matter missing")
data = yaml.safe_load(m.group(1))

# Resolve reference syntax: "{tokens.color.primitive.neutral.0}" → CSS var()
REF_RE = re.compile(r'^\{([^}]+)\}$')

def resolve_ref(value):
    """If value is a reference string, convert to CSS variable name (delegate actual value lookup to the CSS variable chain)."""
    if not isinstance(value, str):
        return value
    m = REF_RE.match(value)
    if not m:
        return value
    path = m.group(1).split('.')
    # tokens.color.primitive.neutral.0 → --primitive-neutral-0
    # tokens.color.semantic.surface.base → --surface-base
    if path[:3] == ['tokens', 'color', 'primitive']:
        return f"var(--primitive-{path[3]}-{path[4]})"
    if path[:3] == ['tokens', 'color', 'semantic']:
        # path[3]=group, path[4]=name
        kebab = path[4].replace('_', '-')
        return f"var(--{path[3]}-{kebab})"
    # Others (typography·spacing·motion etc.) — extend as needed
    return f"var(--{'-'.join(path[1:]).replace('_','-')})"

def walk(node):
    if isinstance(node, dict):
        return {k: walk(v) for k, v in node.items()}
    if isinstance(node, list):
        return [walk(x) for x in node]
    return resolve_ref(node)

resolved = walk(data)
# Then apply Step 6.2 transformation rules
PY
```

**Important**: References are converted to CSS variable chains (not OKLCH value lookups). For example, the generated CSS contains `--surface-base: var(--primitive-neutral-0)`, and the browser chain-resolves at runtime. This is the key mechanism that cleanly supports dark mode token overrides.

## Step 6.3: Write the CSS file

Add an auto-generation warning at the top:

```css
/* ============================================================================
 * AUTO-GENERATED from docs/design-system/DESIGN.md — DO NOT EDIT BY HAND
 * Regenerate: /design-init --regenerate-css
 * Generated: {YYYY-MM-DDTHH:mm:ss}
 * Source version: {meta.version from DESIGN.md}
 * ============================================================================
 */
:root {
  /* Primitive */
  --primitive-primary-50: oklch(...);
  ...
  /* Semantic */
  --surface-base: var(--primitive-neutral-0);
  ...
}
```

## Step 6.4: Show change diff

```bash
if [ -f "$EXISTING_CSS" ]; then
  diff -u "${EXISTING_CSS}" "${EXISTING_CSS}.new" | head -40 || true
fi
mv "${EXISTING_CSS}.new" "$EXISTING_CSS"
```
