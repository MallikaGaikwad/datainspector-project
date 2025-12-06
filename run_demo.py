import pandas as pd

from datainspector import DataProfiler, DataValidator, ReportGenerator


def main() -> None:
    # 1. Load example data
    df = pd.read_csv("examples/benefits_small.csv")

    # 2. Load validation schema
    validator = DataValidator.load_schema("examples/benefits_schema.json")

    # 3. Profile the dataset
    profiler = DataProfiler(df, output_dir="reports")
    profile_summary = profiler.summarize()
    corr_info = profiler.correlate()
    dist_fig_path = profiler.visualize_distributions()

    # 4. Validate the dataset
    validation_results = validator.validate(df)

    # 5. Generate report
    report_gen = ReportGenerator(output_dir="reports", title="datainspector Example Report")
    html_path = report_gen.compile_report(
        profile=profile_summary,
        validation=validation_results,
        corr_fig=corr_info.get("figure_path"),
        dist_fig=dist_fig_path,
    )

    print("Report saved to:", html_path)


if __name__ == "__main__":
    main()