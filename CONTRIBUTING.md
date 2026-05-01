# Contributing to Academic Slides Agent

Thank you for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/houyili/academic-slides-agent.git
cd academic-slides-agent
pip3 install -r requirements.txt
pip3 install pytest  # for running tests
```

## Running Tests

```bash
PYTHONPATH=src python3 -m pytest tests/ -v
```

## Code Style

- Python 3.9+ compatible (no `dict | None` syntax, use `Optional[dict]`)
- Use type hints where practical
- Docstrings for all public functions

## What to Contribute

- **New themes** in `themes/` — academic color schemes for different conferences
- **Bug fixes** — especially rendering edge cases
- **New validator checks** — common slide quality issues
- **Example configs** — `paper_config.yaml` for different paper types
- **Documentation** — tutorials, guides, FAQs

## Pull Request Process

1. Fork the repo and create a feature branch
2. Run tests: `PYTHONPATH=src python3 -m pytest tests/ -v`
3. Run the validator on a sample: `PYTHONPATH=src python3 -m academic_slides_agent validate <slides.md>`
4. Submit a PR with a clear description

## Reporting Issues

Include:
- Your OS and Python version
- Marp CLI version (`marp --version`)
- Full error output
- Minimal `slides.md` that reproduces the issue
