"""
ESS Redistribution Analysis Package

A Python package for multilevel analysis of redistribution preferences
across European welfare states.

Modules:
    - data_loader: Load ESS and country-level data
    - data_prep: Data transformation and preprocessing
    - models: Multilevel modeling functions (requires pymer4 + R)
    - visualization: Plotting and visualization functions
    - utils: Utility functions (logging, validation, etc.)

Note: All notebooks use direct imports (e.g., `from data_prep import ...`)
to avoid circular import issues. This __init__.py is intentionally minimal.
"""

__version__ = "0.1.0"
__author__ = "Kaleb Mazurek"
