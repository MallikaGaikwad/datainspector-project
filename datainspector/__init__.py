"""
datainspector: A lightweight Python library for exploring and validating structured datasets.

Why use this instead of calling pandas/numpy directly?

- `DataProfiler` standardizes common profiling tasks (shape, dtypes, missingness,
  correlations, basic plots) into a single call and returns a consistent dictionary
  structure plus figure paths.
- `ReportGenerator` is written to consume this standardized output, so users can plug
  any dataset into the same reporting pipeline without rewriting profiling code.

Public API:
    - DataProfiler
    - DataValidator
    - ReportGenerator
"""

from .profiler import DataProfiler
from .validator import DataValidator
from .report import ReportGenerator

__all__ = ["DataProfiler", "DataValidator", "ReportGenerator"]
__version__ = "0.1.0"

