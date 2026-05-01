"""Judge Loop Orchestrator.

Drives the generate → compile → validate cycle.
Reads a rubric checklist (markdown with [ ] / [x]) and/or runs
the Python validator. Stops when all checks pass or max iterations hit.

Usage:
    python -m academic_slides_agent.judge_loop --workspace ./my_slides/
"""

import os
import re
import sys
import subprocess
import argparse


def count_rubric_checkboxes(rubric_path: str):
    """Count checked/unchecked items in a markdown rubric.

    Returns:
        (total, unchecked_count, unchecked_descriptions)
    """
    if not os.path.exists(rubric_path):
        return 0, 0, []

    with open(rubric_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"^\s*-\s*\[([ xX])\]\s*(.*)", re.MULTILINE)
    matches = pattern.findall(content)

    total = len(matches)
    unchecked = [(desc,) for status, desc in matches if status == " "]

    return total, len(unchecked), [d[0] for d in unchecked]


def run_validator(workspace: str, config_path: str) -> bool:
    """Run the Python validator. Returns True if passed."""
    slides_md = os.path.join(workspace, "slides.md")
    if not os.path.exists(slides_md):
        print(f"  ❌ slides.md not found in {workspace}")
        return False

    cmd = [
        sys.executable, "-m", "academic_slides_agent.validator",
        slides_md, "--config", config_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0


def run_compiler(workspace: str, theme: str = "") -> bool:
    """Run Marp CLI to compile slides. Returns True if successful."""
    slides_md = os.path.join(workspace, "slides.md")
    cmd = ["marp", "--pdf", slides_md, "--allow-local-files"]

    # Resolve theme path: try as-is, then relative to workspace, then relative to repo root
    if theme:
        theme_resolved = None
        for candidate in [theme, os.path.join(workspace, theme), os.path.abspath(theme)]:
            if os.path.exists(candidate):
                theme_resolved = os.path.abspath(candidate)
                break
        if theme_resolved:
            cmd.extend(["--theme", theme_resolved])
        else:
            print(f"  ⚠️  Theme not found: {theme}")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=workspace)
    if result.returncode != 0:
        print(f"  ❌ Marp compilation failed:\n{result.stderr}")
        return False
    print(f"  ✅ Compiled: slides.pdf")
    return True


def judge_loop(
    workspace: str,
    config_path: str = "paper_config.yaml",
    rubric_path: str = "",
    theme: str = "",
    max_iterations: int = 5,
) -> bool:
    """Run the full judge loop.

    Returns True if all checks eventually pass.
    """
    config_full = os.path.join(workspace, config_path)
    rubric_full = os.path.join(workspace, rubric_path) if rubric_path else ""
    theme_full = os.path.join(workspace, theme) if theme else ""

    prev_errors = float("inf")

    for iteration in range(1, max_iterations + 1):
        print(f"\n{'=' * 50}")
        print(f"  Judge Loop — Iteration {iteration}/{max_iterations}")
        print(f"{'=' * 50}")

        # Step 1: Compile
        print("\n📄 Step 1: Compiling slides...")
        if not run_compiler(workspace, theme_full):
            print("  ⚠️  Compilation failed. Agent must fix syntax errors.")
            continue

        # Step 2: Python validator
        print("\n🔍 Step 2: Running validator...")
        validator_passed = run_validator(workspace, config_full)

        # Step 3: Rubric checkboxes (if provided)
        rubric_passed = True
        if rubric_full and os.path.exists(rubric_full):
            total, unchecked, items = count_rubric_checkboxes(rubric_full)
            if unchecked > 0:
                rubric_passed = False
                print(f"\n📋 Rubric: {total - unchecked}/{total} checked")
                for item in items[:5]:
                    print(f"  [ ] {item[:80]}")

        # Step 4: Decide
        if validator_passed and rubric_passed:
            print(f"\n🎉 ALL CHECKS PASSED on iteration {iteration}!")
            return True

        # Stuck detection
        # (would need error count from validator — simplified here)
        if iteration >= max_iterations:
            print(f"\n⚠️  Max iterations ({max_iterations}) reached. Stopping.")
            return False

        print(f"\n🔄 Errors remain. Agent must fix and re-generate slides.md.")

    return False


def main():
    parser = argparse.ArgumentParser(description="Judge Loop Orchestrator")
    parser.add_argument("--workspace", default=".", help="Workspace directory")
    parser.add_argument("--config", default="paper_config.yaml", help="Config YAML")
    parser.add_argument("--rubric", default="", help="Rubric markdown (optional)")
    parser.add_argument("--theme", default="", help="Marp theme CSS (optional)")
    parser.add_argument("--max-iter", type=int, default=5, help="Max iterations")
    args = parser.parse_args()

    success = judge_loop(
        args.workspace, args.config, args.rubric, args.theme, args.max_iter
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
