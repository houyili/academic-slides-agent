"""Tests for the structural validator."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from academic_slides_agent.validator import validate, load_config


def test_empty_file_fails():
    """An empty file should fail with multiple errors."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("")
        f.flush()
        errors, warnings = validate(f.name)
    os.unlink(f.name)
    assert len(errors) > 0, "Empty file should produce errors"
    assert any("FRONTMATTER" in e for e in errors)


def test_minimal_valid():
    """A minimal valid Marp file should pass universal checks."""
    content = """---
marp: true
math: katex
size: 4k
---

# Slide 1

Content here

---

# Slide 2

More content

---

# Slide 3

---

# Slide 4

---

# Slide 5

---

# Slide 6

---

# Slide 7

---

# Slide 8

End
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        f.flush()
        errors, warnings = validate(f.name, {"min_file_bytes": 100, "min_pages": 8})
    os.unlink(f.name)
    assert len(errors) == 0, f"Minimal valid should have 0 errors, got: {errors}"


def test_missing_author():
    """Config with required authors should flag missing ones."""
    content = """---
marp: true
math: katex
---
# Title
Some content here that is long enough
""" + "x" * 15000
    config = {"authors": ["John Doe", "Jane Smith"], "min_file_bytes": 100}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        f.flush()
        errors, warnings = validate(f.name, config)
    os.unlink(f.name)
    author_errors = [e for e in errors if "AUTHORS" in e]
    assert len(author_errors) == 2


def test_data_point_detection():
    """Data points should be found via regex patterns."""
    content = """---
marp: true
math: katex
---
# Results
The accuracy was 42.0% on the benchmark.
""" + "x" * 15000
    config = {
        "data_points": [
            {"label": "accuracy", "patterns": [r"42\.0%"]},
            {"label": "missing_metric", "patterns": [r"99\.9%"]},
        ],
        "min_file_bytes": 100,
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        f.flush()
        errors, warnings = validate(f.name, config)
    os.unlink(f.name)
    data_errors = [e for e in errors if "DATA" in e]
    assert len(data_errors) == 1
    assert "missing_metric" in data_errors[0]


def test_forbidden_terms():
    """Forbidden terms should trigger hallucination errors."""
    content = """---
marp: true
math: katex
---
# Title
We used the Ultra-MoE architecture.
""" + "x" * 15000
    config = {"forbidden_terms": ["Ultra-MoE"], "min_file_bytes": 100}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        f.flush()
        errors, warnings = validate(f.name, config)
    os.unlink(f.name)
    hall_errors = [e for e in errors if "HALLUCINATION" in e]
    assert len(hall_errors) == 1


def test_config_loading():
    """YAML config should load correctly."""
    yaml_content = """
title: "Test Paper"
authors:
  - "Test Author"
min_pages: 5
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        f.flush()
        config = load_config(f.name)
    os.unlink(f.name)
    assert config["title"] == "Test Paper"
    assert config["authors"] == ["Test Author"]
    assert config["min_pages"] == 5


if __name__ == "__main__":
    test_empty_file_fails()
    print("✅ test_empty_file_fails")
    test_minimal_valid()
    print("✅ test_minimal_valid")
    test_missing_author()
    print("✅ test_missing_author")
    test_data_point_detection()
    print("✅ test_data_point_detection")
    test_forbidden_terms()
    print("✅ test_forbidden_terms")
    test_config_loading()
    print("✅ test_config_loading")
    print("\n🎉 All tests passed!")
