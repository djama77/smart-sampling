"""Méthodes de base pour SMART SAMPLING."""
from __future__ import annotations
import math
import numpy as np
import pandas as pd


def sample_size_proportion(population_size: int, confidence_z: float = 1.96,
                           proportion: float = 0.5, margin_error: float = 0.05,
                           non_response_rate: float = 0.0) -> int:
    """Taille pour une proportion, correction de population finie et non-réponse."""
    if population_size <= 0:
        raise ValueError("La taille de la population doit être positive.")
    if confidence_z <= 0:
        raise ValueError("La valeur Z doit être positive.")
    if not 0 < proportion < 1:
        raise ValueError("La proportion doit être comprise entre 0 et 1.")
    if not 0 < margin_error < 1:
        raise ValueError("La marge d'erreur doit être comprise entre 0 et 1.")
    if not 0 <= non_response_rate < 1:
        raise ValueError("Le taux de non-réponse doit être compris entre 0 et 1.")
    n0 = confidence_z**2 * proportion * (1 - proportion) / margin_error**2
    n = n0 / (1 + (n0 - 1) / population_size)
    return min(math.ceil(n / (1 - non_response_rate)), population_size)


def simple_random_sample(frame: pd.DataFrame, sample_size: int,
                         seed: int | None = 42) -> pd.DataFrame:
    """Tirage aléatoire simple sans remise."""
    if frame.empty:
        raise ValueError("La base de sondage est vide.")
    if not 1 <= sample_size <= len(frame):
        raise ValueError("La taille demandée doit être comprise entre 1 et N.")
    return frame.sample(n=sample_size, replace=False, random_state=seed).copy()


def systematic_sample(frame: pd.DataFrame, sample_size: int,
                      seed: int | None = 42) -> pd.DataFrame:
    """Tirage systématique à départ aléatoire."""
    N = len(frame)
    if N == 0:
        raise ValueError("La base de sondage est vide.")
    if not 1 <= sample_size <= N:
        raise ValueError("La taille demandée doit être comprise entre 1 et N.")
    interval = N / sample_size
    rng = np.random.default_rng(seed)
    start = rng.uniform(0, interval)
    positions = np.floor(start + interval * np.arange(sample_size)).astype(int)
    positions = np.clip(positions, 0, N - 1)
    return frame.iloc[positions].copy()


def stratified_allocation(strata: pd.DataFrame, total_sample: int,
                          stratum_column: str, size_column: str,
                          method: str = "proportional",
                          sd_column: str | None = None) -> pd.DataFrame:
    """Allocation proportionnelle ou allocation optimale de Neyman."""
    if not {stratum_column, size_column}.issubset(strata.columns):
        raise ValueError("Les colonnes de strate et d'effectif sont obligatoires.")
    if (strata[size_column] <= 0).any():
        raise ValueError("Les effectifs des strates doivent être positifs.")
    data = strata.copy()
    N = float(data[size_column].sum())
    if total_sample <= 0 or total_sample > N:
        raise ValueError("La taille totale doit être positive et ne pas dépasser N.")
    if method == "proportional":
        weights = data[size_column].astype(float)
    elif method == "neyman":
        if sd_column is None or sd_column not in data.columns:
            raise ValueError("La colonne d'écart-type est requise pour Neyman.")
        if (data[sd_column] < 0).any():
            raise ValueError("Les écarts-types ne peuvent pas être négatifs.")
        weights = data[size_column].astype(float) * data[sd_column].astype(float)
        if weights.sum() == 0:
            raise ValueError("La somme des poids de Neyman est nulle.")
    else:
        raise ValueError("Méthode inconnue.")
    exact = total_sample * weights / weights.sum()
    allocation = np.floor(exact).astype(int)
    remainder = total_sample - int(allocation.sum())
    order = np.argsort(-(exact - allocation).to_numpy())
    for idx in order[:remainder]:
        allocation.iloc[idx] += 1
    data["allocation"] = allocation
    data["poids_de_sondage"] = data[size_column] / data["allocation"]
    return data
