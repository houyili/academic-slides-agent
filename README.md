# 🎓 Academic Slides Agent

A multi-agent pipeline for generating high-fidelity **4K academic presentations** from research papers using [Marp](https://marp.app/).

> *Born from 6 failed iterations and forensic debugging of an ICLR 2026 oral presentation. Every anti-pattern in this tool was learned the hard way.*

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Paper + Outline + Figures                      │
└──────────────────┬──────────────────────────────┘
                   ▼
┌──────────────────────────────────────┐
│  Agent1 (Generator)                  │
│  Reads: meta_sop.md + paper config   │
│  Writes: slides.md                   │
│  DOES NOT self-evaluate              │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│  Compiler (Marp CLI)                 │
│  slides.md → slides.pdf (4K)        │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│  Validator (Python)                  │
│  Checks: structure, data, figures    │
│  Exit 0 = pass, Exit 1 = fail       │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│  Agent2 (Evaluator) [optional]       │
│  VLM visual inspection of PDF        │
│  Updates rubric checkboxes           │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│  Judge Loop                          │
│  All pass? → Done ✅                 │
│  Failures? → Back to Agent1 🔄      │
│  Max 5 iterations                    │
└──────────────────────────────────────┘
```

## Quick Start

### 1. Install

```bash
git clone https://github.com/houyili/academic-slides-agent.git
cd academic-slides-agent
chmod +x setup.sh && ./setup.sh
```

**Alternative** (if `pip install` fails on older systems):
```bash
pip3 install -r requirements.txt
export PYTHONPATH=src  # add to .bashrc/.zshrc for persistence
python3 -m academic_slides_agent --help
```

**Prerequisites:**
- Python ≥ 3.9
- Node.js ≥ 18 (for Marp CLI)

### 2. Configure API Keys

Keys are stored in your system's **secure credential store** (macOS Keychain, Linux Secret Service, Windows Credential Locker):

```bash
slides setup-keys
```

Or use environment variables as fallback:
```bash
cp .env.example .env
# Edit .env with your keys
```

### 3. Create Paper Config

Use the interactive wizard or create manually:

```bash
slides init  # Interactive — prompts for title, authors, figures, data points
```

Or create `paper_config.yaml` manually (see `examples/moe_paper/paper_config.yaml`):

```yaml
title: "Your Paper Title"
conference: "ICLR 2026"
authors: ["Author One", "Author Two"]
affiliations: ["University A", "Company B"]
data_points:
  - label: "key metric"
    patterns: ["42\\.0%"]
required_figures: ["figure1", "chart2"]
```

### 4. Generate & Validate

```bash
# Validate existing slides
slides validate slides.md --config paper_config.yaml

# Compile to PDF
slides compile --workspace . --theme themes/academic-emerald-4k.css

# Full judge loop
slides run --workspace . --config paper_config.yaml --theme themes/academic-emerald-4k.css
```

### 5. Use with AI Agents

Feed the prompts in `prompts/` to your preferred AI coding agent:

1. Give it `prompts/meta_sop.md` — universal Marp rendering rules
2. Give it `prompts/agent1_generator.md` — generator role instructions
3. Give it your `paper_config.yaml` — paper-specific constraints
4. Let it generate `slides.md`
5. Run `slides validate` to check quality
6. If fails → feed errors back to the agent → repeat

## Key Lessons (Why This Tool Exists)

| # | Lesson | Impact |
|---|--------|--------|
| 1 | **Markdown inside HTML is BROKEN in Marp** | `**bold**` and `$math$` silently fail inside `<div>`, `<table>` |
| 2 | **Every slide needs `<style scoped>`** | Global CSS alone produces garbage on 4K canvas |
| 3 | **HTML tables for large data** | Markdown tables break at >8 rows on 4K |
| 4 | **Image crops for complex tables** | Pre-crop paper tables as PNG — Marp can't render them |
| 5 | **File size is a quality proxy** | < 15KB = skeleton garbage, ≥ 30KB = real content |
| 6 | **Generator must NOT self-evaluate** | Prevents reward hacking — always use Python validator |
| 7 | **Never use `theme: default` for 4K** | Must use custom theme with proper font sizing |

## Project Structure

```
academic-slides-agent/
├── src/academic_slides_agent/
│   ├── cli.py              # CLI entry point
│   ├── keychain.py          # Secure API key management
│   ├── validator.py         # Structural validator
│   └── judge_loop.py        # Loop orchestrator
├── prompts/
│   ├── meta_sop.md          # Universal rendering rules
│   ├── agent1_generator.md  # Generator role prompt
│   ├── agent2_evaluator.md  # Evaluator role prompt
│   └── rubric_template.md   # Checklist template
├── themes/
│   └── academic-emerald-4k.css
├── examples/moe_paper/      # ICLR 2026 MoE paper example
├── tests/                   # Unit tests
├── setup.sh                 # One-click install
├── pyproject.toml            # Dependencies
├── requirements.txt          # Pip fallback
└── .env.example              # API key template
```

## Dependencies

| Package | Version | Required | Purpose |
|---------|---------|:--------:|---------|
| `@marp-team/marp-cli` | ≥ 4.0 | ✅ | Markdown → PDF/PPTX |
| `click` | ≥ 8.0 | ✅ | CLI framework |
| `keyring` | ≥ 25.0 | ✅ | System credential store |
| `pyyaml` | ≥ 6.0 | ✅ | Config files |
| `python-dotenv` | ≥ 1.0 | ✅ | .env fallback |
| `openai` | ≥ 1.0 | Optional | LLM API for auto-generation |
| `anthropic` | ≥ 0.30 | Optional | LLM API for auto-generation |

Install optional LLM deps: `pip install academic-slides-agent[llm]`

## Platform Compatibility

| OS | Status | Notes |
|----|:------:|-------|
| **macOS** | ✅ Full | Homebrew for Node.js, native Keychain Access |
| **Linux (Ubuntu/Debian)** | ✅ Full | apt for Node.js, GNOME Keyring / KDE Wallet |
| **Linux (Fedora/RHEL)** | ✅ Full | dnf for Node.js |
| **Linux (Arch)** | ✅ Full | pacman for Node.js |
| **Windows (WSL)** | ✅ Full | Uses Linux path within WSL |
| **Windows (native)** | ⚠️ Partial | Requires manual Node.js install; Credential Locker works |

## Testing

```bash
# Run all tests
PYTHONPATH=src python3 tests/test_validator.py

# Or with pytest (if installed)
PYTHONPATH=src pytest tests/ -v
```

## Security

- **API keys** are stored in your OS's native credential store via the `keyring` library
  - macOS: Keychain Access
  - Linux: GNOME Keyring / KDE Wallet
  - Windows: Credential Locker
- **No keys are ever written to files** in the repo
- `.env` is in `.gitignore` as a safety net
- No personal information is included in the codebase

## License

MIT
