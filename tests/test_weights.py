import pandas as pd
import pytest

from src.weights import simple_random_base_weights, stratified_base_weights


def test_simple_random_base_weights():
    sample = pd.DataFrame({"id": [2, 5, 8]})
    result = simple_random_base_weights(sample, 30)
    assert result["probabilite_inclusion"].tolist() == pytest.approx([0.1] * 3)
    assert result["poids_base"].tolist() == pytest.approx([10.0] * 3)
    assert "poids_base" not in sample.columns


def test_simple_random_rejects_sample_larger_than_population():
    with pytest.raises(ValueError, match="dépasser"):
        simple_random_base_weights(pd.DataFrame({"id": [1, 2]}), 1)


def test_stratified_base_weights():
    sample = pd.DataFrame({"id": [1, 2, 3, 4], "strate": ["A", "A", "B", "B"]})
    population = pd.DataFrame({"strate": ["A", "B"], "N_h": [100, 50]})
    result = stratified_base_weights(sample, population, "strate", "N_h")
    assert result["probabilite_inclusion"].tolist() == pytest.approx([0.02, 0.02, 0.04, 0.04])
    assert result["poids_base"].tolist() == pytest.approx([50, 50, 25, 25])


def test_stratified_rejects_unknown_stratum():
    sample = pd.DataFrame({"strate": ["A", "C"]})
    population = pd.DataFrame({"strate": ["A", "B"], "N_h": [10, 20]})
    with pytest.raises(ValueError, match="absentes"):
        stratified_base_weights(sample, population, "strate", "N_h")


def test_stratified_rejects_duplicate_population_strata():
    sample = pd.DataFrame({"strate": ["A"]})
    population = pd.DataFrame({"strate": ["A", "A"], "N_h": [10, 12]})
    with pytest.raises(ValueError, match="unique"):
        stratified_base_weights(sample, population, "strate", "N_h")


def test_stratified_allows_population_stratum_not_selected():
    sample = pd.DataFrame({"strate": ["A", "A"]})
    population = pd.DataFrame({"strate": ["A", "B"], "N_h": [20, 80]})
    result = stratified_base_weights(sample, population, "strate", "N_h")
    assert result["poids_base"].tolist() == pytest.approx([10, 10])
