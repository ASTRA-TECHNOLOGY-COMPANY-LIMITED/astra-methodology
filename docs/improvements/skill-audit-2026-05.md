# ASTRA Skill Audit — 2026-05-10

> **⚠️ Post-audit history change (v4.0.0)**: After this audit, the `/ux-publish` skill was removed, and its core functionality (visualizing screens with design-system tokens applied) was integrated into `/service-planner` Step 6 HTML mockup generation. The ux-publish split/slim-down work entries in this document remain valid only as **historical record**; the skill no longer exists in the current codebase.

Analysis of 19 skills against the skill-development guide.

## 1. Progressive Disclosure Not Applied (the biggest issue)

Out of 19 skills, **only 2** use `references/` (catalog-generator, manual-generator). 0 use `examples/` or `scripts/`.

| Skill | Word count | Recommended (1,500–2,000) | references | Priority |
|-------|---:|---:|---|---|
| ux-publish | 8,107 | 4x over | ❌ | P0 |
| project-init | 6,376 | 3x over | ❌ | P0 |
| service-planner | 6,075 | 3x over | ❌ | P0 |
| catalog-generator | 3,975 | 2x over | ✅ | P2 (already partially applied) |
| autorun | 3,890 | 2x over | ❌ | P1 |
| test-run | 3,404 | 1.7x over | ❌ | P2 |
| slack-import | 3,072 | 1.5x over | ❌ | P2 |
| manual-generator | 2,874 | 1.4x over | ✅ | P3 (already partially applied) |

## 2. Insufficient Frontmatter Trigger Phrases

The CLAUDE.md language policy (English auto-trigger / Korean user entry points) and the `>` vs. `"..."` formatting are healthy. However, the *"This skill should be used when the user asks to '...'"* form of utterance triggers recommended by the guide is mostly missing.

| Skill | Missing trigger phrase examples |
|-------|---------------------------------|
| pr-merge | "create a PR for me", "get a review and merge", "fix the issues and merge" |
| service-planner | "do the planning", "organize requirements", "plan a feature" |
| handoff-publish | "UX handoff", "design handover package" |
| autorun | description is at the level of an opening body paragraph (150+ words); needs to be compressed into a core trigger |

## 3. Korean Body Tone

The guide recommends imperative form. In Korean the standard is the plain declarative form ("~한다/~합니다"). Polite form lingers in some skills:
- slack-import 7 instances, autorun 6, service-planner 4, ux-publish 4, manual-generator 3 of "~하세요"

**Verification result**: all 4 instances in ux-publish are *UI messages shown to the user* (e.g., "Please select the designer directory") — not procedural instructions targeting Claude, but user interface text, so polite form is intentional and appropriate. No change. Other skills should be classified in the same way in a separate session.

## 4. Missing Patterns

- No `## Additional Resources` section in any skill → Claude does not become aware of supplementary resources
- Deterministic behaviors such as validation/scaffolding can be extracted into `scripts/` (autorun's stage decisions, project-init's directory creation)

---

## Progress Plan (User Approved)

P0 work: **ux-publish split** + **Korean tone cleanup** in parallel.

### ux-publish split result (complete)

Per the advisor recommendation, landing was integrated into screen-build-guide (6→5 files).

| File | Word count | Kind |
|------|---:|------|
| `skills/ux-publish/SKILL.md` (post-slim) | 1,847 | body |
| `references/common-resources-build.md` | 1,321 | references |
| `references/ai-image-prompts.md` | 884 | references |
| `references/screen-build-guide.md` (landing integrated) | 1,809 | references |
| `assets/COPY-GUIDE-template.md` | 460 | assets |
| `assets/completion-report-template.md` | 436 | assets |

**Outcomes**:
- SKILL.md body: 8,107 → 1,847 words (-77%)
- Passes the advisor verification criterion of `< 2,500`
- Lands in the skill-development guide's recommended 1,500–2,000 word range
- frontmatter description: compressed from 200+ words to 90 words, with 4 trigger phrases stated
- 5 Step entry points carry explicit references/assets references ("first read X")
- Zero information loss (all details distributed across references/assets)

### Korean Tone Cleanup (Deferred)

The 4 instances in ux-publish were all user UI messages; the slim-down naturally compressed those UI messages into procedural instructions, so polite-form count dropped to 0. No separate sweep needed.

For other skills (slack-import 7, autorun 6, service-planner 4, manual-generator 3), it is recommended to first classify polite-form occurrences in a separate session as Claude-facing procedural instructions vs. user UI messages, then clean up only the former.

---

## Recommended Next Work (Separate Session)

**P0 — split with the same pattern**:
- `project-init` (6,376 → ~1,800): move the CLAUDE.md boilerplate (L543-720) to `assets/claude-md-template.md`; move design system templates to `references/`
- `service-planner` (6,075 → ~2,000): move the 6 deliverable templates (market analysis / interview / requirements / use case / IA / feature definition) to `references/deliverable-templates/`

**P1**:
- `autorun` (3,890 → ~1,800): move the per-stage default-decision matrix to `references/auto-defaults.md`
- Strengthen frontmatter descriptions of `pr-merge`, `service-planner`, `handoff-publish`, etc., with trigger phrases

**P2**:
- Split `test-run`, `slack-import`
- `catalog-generator`, `manual-generator` already use references/ — additional compression unnecessary
