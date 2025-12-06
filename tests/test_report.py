import pandas as pd
from datainspector import DataProfiler, DataValidator, ReportGenerator


def test_report_generation(tmp_path):
    df = pd.DataFrame({
        "num1": [1, 2, 3],
        "num2": [4, 5, 6]
    })

    schema = {
        "columns": {
            "num1": {"type": "int", "required": True}
        }
    }

    profiler = DataProfiler(df, output_dir=str(tmp_path))
    profile = profiler.summarize()
    corr = profiler.correlate()
    dist = profiler.visualize_distributions()

    validator = DataValidator(schema=schema)
    validation = validator.validate(df)

    rg = ReportGenerator(output_dir=str(tmp_path))
    html_path = rg.compile_report(profile, validation, corr.get("figure_path"), dist)

    assert html_path.endswith(".html")
