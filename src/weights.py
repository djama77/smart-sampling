"""Probabilités d'inclusion et poids de base pour plans probabilistes simples."""
from __future__ import annotations

import pandas as pd


def simple_random_base_weights(sample: pd.DataFrame, population_size: int) -> pd.DataFrame:
    """Ajoute pi_i=n/N et le poids de base N/n pour un EAS sans remise."""
    if not isinstance(sample, pd.DataFrame) or sample.empty:
        raise ValueError("L'échantillon doit contenir au moins une unité.")
    if not isinstance(population_size, int) or isinstance(population_size, bool) or population_size <= 0:
        raise ValueError("La taille de population doit être un entier positif.")
    n = len(sample)
    if n > population_size:
        raise ValueError("La taille de l'échantillon ne peut pas dépasser la population.")
    result = sample.copy()
    result["probabilite_inclusion"] = n / population_size
    result["poids_base"] = population_size / n
    return result


def stratified_base_weights(
    sample: pd.DataFrame,
    population_by_stratum: pd.DataFrame,
    stratum_column: str,
    population_column: str,
) -> pd.DataFrame:
    """Ajoute pi_hi=n_h/N_h et N_h/n_h pour un EAS sans remise dans chaque strate.

    La table de population doit contenir une ligne par strate et son effectif N_h.
    Les strates sans unité observée dans l'échantillon sont signalées par l'absence
    de poids dans cet échantillon ; aucun poids n'est imputé.
    """
    if not isinstance(sample, pd.DataFrame) or sample.empty:
        raise ValueError("L'échantillon doit contenir au moins une unité.")
    required = {stratum_column}
    if not required.issubset(sample.columns):
        raise ValueError("La variable de strate est absente de l'échantillon.")
    if sample[stratum_column].isna().any():
        raise ValueError("L'échantillon contient des unités sans strate.")
    if not {stratum_column, population_column}.issubset(population_by_stratum.columns):
        raise ValueError("La table de population doit contenir la strate et son effectif.")
    pop = population_by_stratum[[stratum_column, population_column]].copy()
    if pop.empty or pop[stratum_column].isna().any() or pop[stratum_column].duplicated().any():
        raise ValueError("La table de population doit avoir une ligne unique et renseignée par strate.")
    if not pd.api.types.is_numeric_dtype(pop[population_column]):
        raise ValueError("Les effectifs de population doivent être numériques.")
    if pop[population_column].isna().any() or (pop[population_column] <= 0).any():
        raise ValueError("Les effectifs de population par strate doivent être positifs.")
    if (pop[population_column] % 1 != 0).any():
        raise ValueError("Les effectifs de population doivent être des entiers.")
    counts = sample.groupby(stratum_column, dropna=False).size().rename("n_h")
    meta = pop.set_index(stratum_column).join(counts)
    if (meta["n_h"].fillna(0) > meta[population_column]).any():
        raise ValueError("L'échantillon dépasse l'effectif de population d'au moins une strate.")
    unknown = set(sample[stratum_column].unique()) - set(meta.index)
    if unknown:
        raise ValueError("Certaines strates de l'échantillon sont absentes de la table de population.")
    meta["probabilite_inclusion"] = meta["n_h"] / meta[population_column]
    meta["poids_base"] = meta[population_column] / meta["n_h"]
    result = sample.copy()
    mapping_pi = meta["probabilite_inclusion"].to_dict()
    mapping_weight = meta["poids_base"].to_dict()
    result["probabilite_inclusion"] = result[stratum_column].map(mapping_pi)
    result["poids_base"] = result[stratum_column].map(mapping_weight)
    return result
