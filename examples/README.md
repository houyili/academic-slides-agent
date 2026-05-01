# Examples

## MoE Paper (ICLR 2026)

This is a complete example showing how to configure `academic-slides-agent` for a real paper:

**"Mixture-of-Experts Can Surpass Dense LLMs Under Strictly Equal Resource"**

### Files

| File | Purpose |
|------|---------|
| `paper_config.yaml` | Paper-specific validation config (authors, data points, figures, per-slide specs) |
| `figures/` | Place your pre-rendered figures here |
| `output/` | Generated `slides.md` and `slides.pdf` go here |

### Usage

```bash
# 1. Copy your figures into figures/
cp /path/to/your/figures/*.png examples/moe_paper/figures/

# 2. Generate slides.md (using your AI agent + prompts/meta_sop.md)

# 3. Validate
slides validate output/slides.md --config paper_config.yaml

# 4. Compile
cd output && marp --pdf slides.md --theme ../../themes/academic-emerald-4k.css --allow-local-files
```

### Creating Your Own Example

1. Copy this directory: `cp -r examples/moe_paper examples/my_paper`
2. Edit `paper_config.yaml` with your paper's details
3. Follow the same workflow
