# Hardened Slide Generation — Rubric Checklist Template

This is a **paper-agnostic** rubric template. Copy it into your workspace and adapt the paper-specific items before starting generation.

## Universal Rendering Rules (NEVER violate)

### Lesson 1: Markdown Inside HTML is BROKEN
- [ ] All `<div>`, `<table>`, `<td>` content uses HTML tags only
- [ ] No `**bold**` inside HTML containers (use `<b>`)
- [ ] No `$math$` inside HTML containers (use `<i>`, `<sub>`, `&kappa;`, etc.)

### Lesson 2: Every Slide Needs `<style scoped>`
- [ ] Each slide has its own `<style scoped>` block
- [ ] Font sizes are tuned per-slide for 4K canvas

### Lesson 3: HTML Tables for Large Data
- [ ] Tables with >8 rows use HTML `<table>` (not Markdown `|---|`)
- [ ] Row highlighting uses CSS classes

### Lesson 4: Image Crops for Complex Tables
- [ ] Multi-column ablation tables are pre-cropped PNG images
- [ ] Images have `border-radius` and `box-shadow`

### Lesson 5: Content Density
- [ ] Total file size > 20KB (not a skeleton)
- [ ] Each slide has meaningful content (not just a heading)

### Lesson 6: Generator Does NOT Self-Evaluate
- [ ] Agent1 did not modify this rubric
- [ ] Only Agent2 or the Python validator updated checkboxes

### Lesson 7: Use Custom Theme
- [ ] `theme:` in frontmatter points to a real `.css` file (not `default`)
- [ ] `size: 4k` is set in frontmatter
- [ ] `math: katex` is set in frontmatter

## Paper-Specific Checks (CUSTOMIZE PER PAPER)

### Authors & Affiliations
- [ ] All authors listed with correct superscripts
- [ ] All affiliations present

### Data Fidelity
- [ ] Key numerical claims match paper source exactly
- [ ] No invented/approximated numbers

### Required Figures
- [ ] All required figures referenced on correct slides
- [ ] Figure captions match paper

### Forbidden Terms
- [ ] No hallucinated terminology
- [ ] No invented model names

## Compilation
- [ ] `marp --pdf slides.md --theme <theme>.css --allow-local-files` succeeds
- [ ] PDF page count matches slide count
- [ ] No visible rendering artifacts in PDF
