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
