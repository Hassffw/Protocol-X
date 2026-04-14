from pathlib import Path

from setuptools import find_packages, setup

ROOT = Path(__file__).parent
README = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""

setup(
    name="protocol-x",
    version="0.2.0",
    description="Token-sparende Prompting-Infrastruktur mit PX Mapping",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Phoenixclub",
    packages=find_packages(exclude=("tests", "examples")),
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "openai": ["openai>=1.40.0"],
        "anthropic": ["anthropic>=0.29"],
        "deepseek": ["deepseek>=0.1.0"],
        "all": ["openai>=1.40.0", "anthropic>=0.29", "deepseek>=0.1.0"],
    },
    entry_points={"console_scripts": ["px-protocol=protocol_x.cli:run"]},
    include_package_data=True,
)
