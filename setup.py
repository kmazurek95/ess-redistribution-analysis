from setuptools import setup, find_packages

setup(
    name="ess_redistribution_analysis",
    version="0.1.0",
    description="Multilevel analysis of redistribution preferences across European welfare states",
    author="Kaleb Mazurek",
    packages=find_packages(exclude=["tests", "notebooks"]),
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
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.0",
            "pytest-cov>=4.1.0",
            "jupyter>=1.0.0",
        ]
    },
)
