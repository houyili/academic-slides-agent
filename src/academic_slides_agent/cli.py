"""CLI entry point for academic-slides-agent."""

import click
import os
import sys

from . import __version__


@click.group()
@click.version_option(version=__version__, prog_name="academic-slides-agent")
def main():
    """Academic Slides Agent — Generate 4K presentations from research papers."""
    pass


@main.command()
def setup_keys():
    """Store LLM API keys in the system keychain."""
    from .keychain import interactive_setup
    interactive_setup()


@main.command()
@click.option("--output", "-o", default="paper_config.yaml", help="Output file path")
def init(output):
    """Interactively create a paper_config.yaml for your paper."""
    import yaml

    print("\n📝 Academic Slides Agent — Paper Config Generator")
    print("=" * 50)

    config = {}
    config["title"] = input("\nPaper title: ").strip()
    config["conference"] = input("Conference (e.g., ICLR 2026): ").strip()

    authors_input = input("Authors (comma-separated): ").strip()
    config["authors"] = [a.strip() for a in authors_input.split(",") if a.strip()]

    affils_input = input("Affiliations (comma-separated): ").strip()
    config["affiliations"] = [a.strip() for a in affils_input.split(",") if a.strip()]

    config["min_pages"] = int(input("Min slide count [8]: ").strip() or "8")
    config["max_pages"] = int(input("Max slide count [15]: ").strip() or "15")
    config["min_file_bytes"] = 5000
    config["min_scoped_css"] = config["min_pages"] - 2

    figs_input = input("Required figure filenames (comma-separated, no ext): ").strip()
    if figs_input:
        config["required_figures"] = [f.strip() for f in figs_input.split(",") if f.strip()]

    print("\n📊 Key data points (enter empty label to stop):")
    config["data_points"] = []
    while True:
        label = input("  Data point label: ").strip()
        if not label:
            break
        pattern = input(f"  Regex pattern for '{label}': ").strip()
        config["data_points"].append({"label": label, "patterns": [pattern]})

    with open(output, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"\n✅ Config saved to: {output}")
    print(f"   Edit it to add slide_specs, forbidden_terms, etc.")


@main.command()
@click.argument("slides_md")
@click.option("--config", default="paper_config.yaml", help="Paper config YAML")
def validate(slides_md, config):
    """Validate slides.md against paper config."""
    from .validator import validate as run_validate, print_report, load_config
    cfg = load_config(config)
    errors, warnings = run_validate(slides_md, cfg)
    passed = print_report(errors, warnings)
    sys.exit(0 if passed else 1)


@main.command()
@click.option("--workspace", default=".", help="Workspace directory")
@click.option("--theme", default="", help="Marp theme CSS file")
def compile(workspace, theme):
    """Compile slides.md to PDF using Marp."""
    from .judge_loop import run_compiler
    success = run_compiler(workspace, theme)
    sys.exit(0 if success else 1)


@main.command()
@click.option("--workspace", default=".", help="Workspace directory")
@click.option("--config", default="paper_config.yaml", help="Paper config YAML")
@click.option("--rubric", default="", help="Rubric checklist markdown")
@click.option("--theme", default="", help="Marp theme CSS file")
@click.option("--max-iter", default=5, help="Max judge loop iterations")
def run(workspace, config, rubric, theme, max_iter):
    """Run the full judge loop (compile → validate → iterate)."""
    from .judge_loop import judge_loop
    success = judge_loop(workspace, config, rubric, theme, max_iter)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
