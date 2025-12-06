import pandas as pd
from datainspector import DataValidator


def test_validator_basic():
    schema = {
        "columns": {
            "age": {"type": "int", "required": True, "min": 18, "max": 60},
            "plan": {"type": "string", "required": False, "allowed": ["A", "B"]}
        }
    }

    df = pd.DataFrame({
        "age": [25, 30, 75],   # 75 will violate max
        "plan": ["A", "C", "B"]  # "C" will violate allowed set
    })

    validator = DataValidator(schema=schema)
    results = validator.validate(df)

    assert results["passed"] is False
    assert "age" in results["columns"]
    assert "plan" in results["columns"]
    assert len(results["columns"]["age"]["issues"]) > 0
    assert len(results["columns"]["plan"]["issues"]) > 0

    summary = validator.generate_summary(results)
    assert "Columns with issues" in summary