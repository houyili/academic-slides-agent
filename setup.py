from setuptools import setup, find_packages
setup(
    name="academic-slides-agent",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0",
        "keyring>=25.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0",
    ],
    extras_require={
        "llm": ["openai>=1.0", "anthropic>=0.30"],
        "dev": ["pytest>=7.0"],
    },
    entry_points={
        "console_scripts": ["slides=academic_slides_agent.cli:main"],
    },
)
