import pandas as pd
import pytest

from src.quality import quality_audit, quality_issues


def test_quality_audit_counts_missing_duplicates_and_ids():
    frame = pd.DataFrame({
        "id": [1, 1, 3, None],
        "district": ["A", "A", "B", "B"],
        "households": [10, 10, 12, 1000],
    })
    result = quality_audit(frame, "id")
    assert result["row_count"] == 4
    assert result["duplicate_rows"] == 1
    assert result["duplicate_ids"] == 1
    assert result["missing_ids"] == 1
    assert result["missing_cells"] == 1
    assert "district" not in result["constant_columns"]


def test_quality_issues_returns_expected_columns():
    frame = pd.DataFrame({"id": [1, 1, None], "value": [2, None, 2]})
    issues = quality_issues(frame, "id")
    assert list(issues.columns) == ["controle", "variable", "effectif", "gravite"]
    assert "Identifiants dupliqués" in issues["controle"].tolist()
    assert "Valeurs manquantes" in issues["controle"].tolist()


def test_unknown_identifier_is_rejected():
    with pytest.raises(ValueError, match="absente"):
        quality_audit(pd.DataFrame({"x": [1, 2]}), "id")


def test_empty_dataframe_without_columns_is_rejected():
    with pytest.raises(ValueError):
        quality_audit(pd.DataFrame())
