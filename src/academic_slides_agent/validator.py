"""Generalized structural validator for Marp slides.

Reads paper_config.yaml to get paper-specific checks (authors, data points,
figures). Core structural checks (Marp config, scoped CSS, file size) are
universal.

Usage:
    python -m academic_slides_agent.validator slides.md --config paper_config.yaml
"""

import re
import sys
import os
import argparse

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


def load_config(config_path: str) -> dict:
    """Load paper-specific config from YAML."""
    if not config_path or not os.path.exists(config_path):
        return {}
    if not _HAS_YAML:
        print("⚠️  pyyaml not installed. Paper-specific checks skipped.")
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate(md_path: str, config=None) :
    """Validate slides.md against universal + paper-specific rules.

    Returns:
        (errors, warnings) — lists of string messages.
    """
    config = config or {}
    if not os.path.exists(md_path):
        return [f"FATAL: {md_path} not found"], []

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    errors = []
    warnings = []

    # ── 1. Frontmatter ──────────────────────────────────────────
    for key in ["marp: true", "math: katex"]:
        if key not in content:
            errors.append(f"[FRONTMATTER] Missing '{key}'")

    if "size:" not in content:
        warnings.append("[FRONTMATTER] No 'size:' specified — defaults to 16:9")

    if "theme: default" in content:
        warnings.append("[FRONTMATTER] Using 'theme: default' — consider custom theme for 4K")

    # ── 2. Pagination ───────────────────────────────────────────
    body = content
    if content.startswith("---"):
        end_yaml = content.find("---", 3)
        if end_yaml > 0:
            body = content[end_yaml + 3:]

    slides = re.split(r"^\s*---\s*$", body, flags=re.MULTILINE)
    n_slides = len(slides)

    min_pages = config.get("min_pages", 8)
    max_pages = config.get("max_pages", 15)

    if n_slides < min_pages:
        errors.append(f"[PAGINATION] Only {n_slides} slides (min {min_pages})")
    elif n_slides > max_pages:
        errors.append(f"[PAGINATION] {n_slides} slides (max {max_pages})")

    # ── 3. Authors ──────────────────────────────────────────────
    for author in config.get("authors", []):
        if author not in content:
            errors.append(f"[AUTHORS] Missing: {author}")

    # ── 4. Affiliations ─────────────────────────────────────────
    for affil in config.get("affiliations", []):
        if affil not in content:
            errors.append(f"[AFFILIATIONS] Missing: {affil}")

    # ── 5. Data Fidelity ────────────────────────────────────────
    for dp in config.get("data_points", []):
        label = dp.get("label", "unknown")
        patterns = dp.get("patterns", [])
        found = any(re.search(p, content, re.IGNORECASE) for p in patterns)
        if not found:
            errors.append(f"[DATA] Missing: {label}")

    # ── 6. Required Figures ─────────────────────────────────────
    for fig in config.get("required_figures", []):
        if fig not in content:
            errors.append(f"[FIGURES] Missing: {fig}")

    # ── 7. Per-Slide Structure ──────────────────────────────────
    slide_specs = config.get("slide_specs", {})
    for slide_num_str, spec in slide_specs.items():
        slide_num = int(slide_num_str)
        if slide_num > n_slides:
            errors.append(f"[SLIDE {slide_num}] Missing — only {n_slides} slides")
            continue
        slide = slides[slide_num - 1]

        for img in spec.get("images", []):
            if img not in slide:
                errors.append(f"[SLIDE {slide_num}] Missing image: {img}")

        if spec.get("scoped_css") and "<style scoped>" not in slide:
            warnings.append(f"[SLIDE {slide_num}] Missing <style scoped>")

        min_lines = spec.get("min_lines", 0)
        actual_lines = len(slide.strip().split("\n"))
        if actual_lines < min_lines:
            warnings.append(
                f"[SLIDE {slide_num}] Only {actual_lines} lines (expected >={min_lines})"
            )

        table_type = spec.get("table")
        if table_type == "markdown" and "|" not in slide:
            errors.append(f"[SLIDE {slide_num}] Expected markdown table")
        if table_type == "html" and "<table" not in slide:
            errors.append(f"[SLIDE {slide_num}] Expected HTML table")

    # ── 8. Forbidden Terms ──────────────────────────────────────
    for term in config.get("forbidden_terms", []):
        if term.lower() in content.lower():
            errors.append(f"[HALLUCINATION] Forbidden: '{term}'")

    # ── 9. Content Density ──────────────────────────────────────
    min_bytes = config.get("min_file_bytes", 15000)
    if len(content) < min_bytes:
        errors.append(
            f"[DENSITY] Only {len(content)} bytes — skeleton detected (need >={min_bytes})"
        )

    # ── 10. Scoped CSS Count ────────────────────────────────────
    scoped_count = len(re.findall(r"<style scoped>", content))
    min_scoped = config.get("min_scoped_css", 0)
    if scoped_count < min_scoped:
        warnings.append(
            f"[CSS] Only {scoped_count} <style scoped> blocks (expected >={min_scoped})"
        )

    return errors, warnings


def print_report(errors: list, warnings: list) -> bool:
    """Print formatted report. Returns True if all checks passed."""
    print("\n" + "=" * 60)
    print("  Academic Slides Agent — Validation Report")
    print("=" * 60)

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        print(f"\n{'=' * 60}")
        print(f"  RESULT: FAIL ({len(errors)} errors, {len(warnings)} warnings)")
        print(f"{'=' * 60}\n")
        return False
    else:
        print(f"\n✅ ALL CHECKS PASSED ({len(warnings)} warnings)")
        print(f"{'=' * 60}\n")
        return True


def main():
    parser = argparse.ArgumentParser(description="Validate Marp slides")
    parser.add_argument("slides", help="Path to slides.md")
    parser.add_argument("--config", default="paper_config.yaml", help="Paper config YAML")
    args = parser.parse_args()

    config = load_config(args.config)
    errors, warnings = validate(args.slides, config)
    passed = print_report(errors, warnings)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
