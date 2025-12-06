import pandas as pd
from datainspector import DataProfiler


def test_profiler_summary(tmp_path):
    df = pd.DataFrame({
        "num1": [1, 2, 3, 4],
        "num2": [4, 3, 2, 1],
        "cat": ["a", "b", "a", "c"]
    })

    profiler = DataProfiler(df, output_dir=str(tmp_path))
    summary = profiler.summarize()

    assert summary["shape"] == (4, 3)
    assert summary["duplicate_rows"] == 0
    assert summary["missing_counts"] == {"num1": 0, "num2": 0, "cat": 0}


def test_profiler_plots(tmp_path):
    df = pd.DataFrame({
        "x": [1, 2, 3, 4],
        "y": [5, 6, 7, 8]
    })

    profiler = DataProfiler(df, output_dir=str(tmp_path))

    # Correlation heatmap
    corr = profiler.correlate()
    assert corr["matrix"] is not None
    assert "figure_path" in corr
    assert corr["figure_path"] is not None

    # Distribution plot
    dist_path = profiler.visualize_distributions()
    assert dist_path is not None