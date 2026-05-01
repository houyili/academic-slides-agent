# ICLR 2026 Oral Presentation: Hardened Generation Skill

## FATAL LESSONS (from 4 failed iterations)

### Lesson 1: Markdown Inside HTML is BROKEN in Marp
**`**bold**` and `$math$` SILENTLY FAIL inside HTML containers (`<div>`, `<table>`, `<ul>`).**
You MUST use HTML tags directly:
- `<b>text</b>` not `**text**`
- `<i>N</i>` not `$N$`
- `<i>r<sub>a</sub></i>` not `$r_a$`
- `&kappa;` not `$\kappa$`
- `&approx;` not `$\approx$`

Only use `$...$` KaTeX when inside a `markdown="1"` container with **blank lines** around the math.

### Lesson 2: Post-Processor is Mandatory
After generating slides.md, ALWAYS run `fix_markdown.py` to convert any remaining `**` → `<b>` and `$var$` → `<i>var</i>` inside HTML containers.

### Lesson 3: Never Use Markdown Tables for Complex Data
Use pre-cropped **table image PNGs** (`figures/tables/table-1.png`) for architecture ablation tables.
Use raw **HTML `<table>` with custom CSS classes** for the 7B results table (17 rows × 7 columns).

### Lesson 4: Every Slide Needs `<style scoped>`
The gold standard has **11 separate `<style scoped>` blocks** — one per slide — with pixel-perfect sizing. A single global CSS block produces garbage on 4K canvas.

### Lesson 5: File Size is a Quality Proxy
- **Gold standard**: 42,492 bytes, 1,038 lines
- **Skeleton garbage**: 2,481 bytes, 96 lines
- If your output is under 20KB, it's a skeleton. Re-generate.

### Lesson 6: Python Rubric Must Check CONTENT, Not Just Structure
The validator must check:
- All 10 author names individually
- All 4 affiliations individually
- 10+ specific data points (BPC 0.4590, r_a=20.07%, 68B, etc.)
- Forbidden hallucination terms
- Figure paths for all 11 required figures
- Font-family and color consistency in CSS
- Takeaway sentences near key charts

### Lesson 7: Use `theme: theme-4k` and `size: 4k`
Never use `theme: default` for 4K presentations. The `theme-4k.css` file is required.

## Pipeline Commands
```bash
# 1. Generate slides.md (Agent)
# 2. Post-process markdown
python3 fix_markdown.py
# 3. Compile to 4K PDF
marp --pdf slides.md --theme theme-4k.css --allow-local-files
# 4. Validate
python3 validate_rubric.py --workspace .
```
