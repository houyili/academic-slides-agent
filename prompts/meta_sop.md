# Meta SOP: Academic Oral Presentation Generation

## Overview
This is a **paper-agnostic** skill for generating high-fidelity 4K Marp presentations for any academic oral talk. Given any paper + outline, the Agent should:
1. Analyze the paper to extract structural fingerprint
2. Generate a paper-specific SOP
3. Generate slides following that SOP
4. Validate with a paper-specific validator
5. Iterate until all checks pass

## Phase 1: Paper Analysis (READ-ONLY)

Read the following inputs and extract:

### Required Inputs
- **Paper source** (`.tex` files or PDF)
- **Presentation outline** (narrative arc — NOT paper section order)
- **Pre-rendered figures** (PNG/PDF plots)
- **Data tables** (xlsx/csv with authoritative numbers)

### Extraction Checklist
From the paper, extract and document:
1. **Title** (exact wording)
2. **All authors** (full names with affiliations and superscripts)
3. **All affiliations** (with superscript mapping)
4. **Conference info** (venue, year, track: oral/poster/spotlight)
5. **Key numerical claims** (the 5-10 most critical numbers that MUST appear)
6. **Required figures** (filename → slide mapping)
7. **Required tables** (which tables, markdown vs HTML vs image crop)
8. **Core research question** (verbatim from paper)
9. **Methodology steps** (pipeline/framework structure)
10. **Key conclusions** (2-3 headline results)

Output this as a `paper_fingerprint.json` structured file.

## Phase 2: Generate Paper-Specific SOP

Using the extracted fingerprint, generate a `slides_sop.md` that specifies:
- Exact slide count and per-slide content plan
- Which figures/tables appear on which slide
- Per-slide layout type (two-column, grid, full-width, etc.)
- Key data points that must appear on each slide
- CSS design tokens (color palette matching paper/conference theme)

### Slide Layout Patterns (reusable templates)

| Layout | Use When | CSS Pattern |
|--------|----------|-------------|
| **Title** | Slide 1 always | Centered, logo bar, author grid |
| **Two-Column Text** | Motivation, framing | `.cols { display: flex; gap: 80px }` |
| **Question Box** | Core RQ | Dark gradient box + stat cards |
| **Dual Figure** | Comparing two plots | Side-by-side `img` with captions + equations |
| **Three-Card Grid** | Methodology pipeline | `grid-template-columns: repeat(3, 1fr)` |
| **Table + Image Grid** | Ablation results | Top: markdown table, Bottom: 2×2 image grid |
| **Figure + Bullet Analysis** | Experimental results | Left: large figure, Right: bullet findings |
| **Full HTML Table** | Large data table (>10 rows) | HTML `<table>` with row highlighting classes |
| **Figure + Data Table** | Sweet spot / key result | Left: figure + analysis, Right: HTML table |
| **2×2 Eval Grid** | Benchmark results | `grid-template-columns: 1fr 1fr` + findings card |
| **Conclusion Cards** | Summary / guidance | Left: stacked cards, Right: example/guidance |
| **Thank You / Q&A** | Final slide always | Centered huge text, contact info, QR code |

## Phase 3: Generate Slides

### CRITICAL Marp Rendering Rules (UNIVERSAL — applies to ALL papers)

#### Rule 1: Markdown Inside HTML is BROKEN
Marp **cannot** render `**bold**` or `$math$` inside HTML containers (`<div>`, `<table>`, `<ul>`, `<td>`).

**Inside HTML containers, you MUST use:**
- `<b>text</b>` NOT `**text**`
- `<i>text</i>` NOT `*text*`
- `<i>N</i>` NOT `$N$`
- `<i>r<sub>a</sub></i>` NOT `$r_a$`
- `&kappa;`, `&alpha;`, `&beta;` NOT `$\kappa$`, `$\alpha$`, `$\beta$`
- `&approx;`, `&times;`, `&rarr;` NOT `$\approx$`, `$\times$`, `$\rightarrow$`

**Exception:** If a `<div>` has `markdown="1"` attribute AND the math block has **blank lines above and below**, KaTeX will render. Use this sparingly.

#### Rule 2: Every Slide Needs `<style scoped>`
A single global CSS block produces broken layouts on 4K canvas. Each slide needs its own scoped CSS with pixel-perfect sizing for its specific content.

#### Rule 3: HTML Tables for Large Data
Tables with >8 rows MUST use HTML `<table>` with custom CSS classes (e.g., `.row-highlight { background: #fff7ed; border: 3px solid #f97316; }`). Markdown tables break at this size on 4K.

#### Rule 4: Image Crops for Complex Tables
Multi-column ablation tables from the paper should be pre-cropped as PNG images and embedded via `<img>`. Marp cannot render them as text.

#### Rule 5: File Size is a Quality Proxy
- **< 10KB**: Empty skeleton — guaranteed failure
- **10-20KB**: Minimal content — likely missing slides
- **20-35KB**: Adequate for 10-11 slides
- **35-45KB**: Good density for 12-13 slides
- **> 45KB**: May have redundant CSS

#### Rule 6: Canvas Configuration
```yaml
---
marp: true
theme: theme-4k    # NEVER use 'default' for 4K
size: 4k
math: katex
paginate: true
---
```

### CSS Design System (Adaptable Palette)

The following is the default **Academic Emerald** palette. Replace colors to match conference/paper branding:

```css
/* Primary */   --primary-dark: #064e3b;  --primary: #10b981;  --primary-light: #a7f3d0;
/* Secondary */ --accent: #059669;  --text: #1e293b;  --text-light: #475569;
/* Amber */     --amber: #f59e0b;  --amber-bg: #fef3c7;
/* Surface */   --bg: linear-gradient(175deg, #f8faff, #eef2ff);  --card: #fff;
/* Font */      font-family: 'Inter', system-ui, sans-serif;
```

## Phase 4: Generate Paper-Specific Validator

Create a `validate.py` that checks:
1. **Frontmatter**: `marp: true`, `size: 4k`, `math: katex`
2. **Pagination**: Slide count within expected range
3. **Authors**: All author names present
4. **Affiliations**: All institution names present
5. **Data Fidelity**: All key numerical claims present (from fingerprint)
6. **Required Figures**: All figure filenames referenced
7. **Per-Slide Structure**: Each slide has expected images/tables
8. **Forbidden Terms**: No hallucinated terminology
9. **Scoped CSS**: Each slide has `<style scoped>`
10. **Content Density**: File size > 20KB threshold

Exit 0 = all pass. Exit 1 = failures found.

## Phase 5: Judge Loop

```
while true:
  1. Agent generates/fixes slides.md
  2. Run: marp --pdf slides.md --theme theme-4k.css --allow-local-files
  3. Run: python3 validate.py slides.md
  4. If Exit 0 → DONE
  5. If Exit 1 → Feed errors back to Agent → goto 1
```

The `judge_loop.py` orchestrator drives this cycle. It should:
- Cap iterations at MAX_ITER (default: 5)
- Log each iteration's error count
- Stop early if error count stops decreasing (stuck)

## Anti-Patterns (NEVER DO THESE)

1. ❌ Using `theme: default` for 4K presentations
2. ❌ Writing `**bold**` inside `<div>` — it renders as raw `**text**`
3. ❌ Writing `$math$` inside `<td>` — it renders as raw `$x$`
4. ❌ Using markdown tables for >8 row data — layout breaks
5. ❌ Generating < 500 lines — guaranteed skeleton
6. ❌ Self-evaluating as Agent1 — always use Python validator
7. ❌ Inventing hardware numbers ("2000 H100") — say "Thousands of GPU"
8. ❌ Skipping `<style scoped>` — slides will have wrong sizing
9. ❌ Copying gold standard verbatim — the skill must GENERATE, not copy
