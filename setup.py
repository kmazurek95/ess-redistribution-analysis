"""
Setup script for ESS Redistribution Analysis package

This allows the src/ directory to be installed as a package, making imports cleaner
in notebooks (e.g., `from src.data_loader import load_ess_data`).
"""

from setuptools import setup, find_packages

setup(
    name="ess_redistribution_analysis",
    version="0.1.0",
    description="Multilevel analysis of redistribution preferences across European welfare states",
    author="Kaleb Mazurek",
    author_email="kalebmazurek@gmail.com",
    url="https://github.com/kmazurek95/ess-redistribution-analysis",
    packages=find_packages(exclude=["tests", "notebooks", "docs"]),
    python_requires=">=3.10",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "statsmodels>=0.14.0",
        "pymer4>=0.8.0",
        "scikit-learn>=1.3.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "plotly>=5.14.0",
        "pyreadstat>=1.2.0",
        "openpyxl>=3.1.0",
        "rpy2>=3.5.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "tqdm>=4.65.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.0",
            "pytest-cov>=4.1.0",
            "black>=23.3.0",
            "flake8>=6.0.0",
            "mypy>=1.3.0",
            "jupyter>=1.0.0",
            "ipykernel>=6.22.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="multilevel-modeling welfare-state comparative-politics redistribution ESS",
    project_urls={
        "Documentation": "https://github.com/kmazurek95/ess-redistribution-analysis/blob/main/README.md",
        "Source": "https://github.com/kmazurek95/ess-redistribution-analysis",
        "Tracker": "https://github.com/kmazurek95/ess-redistribution-analysis/issues",
    },
)
