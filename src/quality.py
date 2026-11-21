"""Contrôles descriptifs de qualité d'une base de sondage.

Ces contrôles signalent des anomalies potentielles ; ils ne corrigent jamais
automatiquement les données et ne remplacent pas la validation métier.
"""
from __future__ import annotations

import pandas as pd


def quality_audit(frame: pd.DataFrame, id_column: str | None = None) -> dict:
    """Produit un bilan reproductible des anomalies détectables dans un DataFrame."""
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("La base doit être un DataFrame pandas.")
    if frame.empty and len(frame.columns) == 0:
        raise ValueError("La base ne contient aucune ligne ni colonne.")

    missing = frame.isna().sum().astype(int).to_dict()
    duplicate_rows = int(frame.duplicated().sum())
    duplicate_ids = 0
    missing_ids = 0
    if id_column:
        if id_column not in frame.columns:
            raise ValueError(f"La variable identifiant « {id_column} » est absente.")
        missing_ids = int(frame[id_column].isna().sum())
        duplicate_ids = int(frame.loc[frame[id_column].notna(), id_column].duplicated().sum())

    constant_columns = [
        str(col) for col in frame.columns
        if frame[col].nunique(dropna=True) <= 1
    ]
    numeric_outliers = {}
    for col in frame.select_dtypes(include="number").columns:
        values = frame[col].dropna()
        if len(values) < 4:
            numeric_outliers[str(col)] = 0
            continue
        q1, q3 = values.quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr == 0:
            count = int((values != q1).sum())
        else:
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            count = int(((values < lower) | (values > upper)).sum())
        numeric_outliers[str(col)] = count

    return {
        "row_count": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "duplicate_rows": duplicate_rows,
        "missing_by_column": missing,
        "missing_cells": int(frame.isna().sum().sum()),
        "duplicate_ids": duplicate_ids,
        "missing_ids": missing_ids,
        "constant_columns": constant_columns,
        "numeric_outliers": numeric_outliers,
    }


def quality_issues(frame: pd.DataFrame, id_column: str | None = None) -> pd.DataFrame:
    """Retourne une liste tabulaire des constats, sans modifier la base."""
    audit = quality_audit(frame, id_column)
    rows = []
    if audit["duplicate_rows"]:
        rows.append({"controle": "Lignes entièrement dupliquées", "variable": "Toutes", "effectif": audit["duplicate_rows"], "gravite": "À vérifier"})
    if audit["missing_ids"]:
        rows.append({"controle": "Identifiants manquants", "variable": id_column, "effectif": audit["missing_ids"], "gravite": "Élevée"})
    if audit["duplicate_ids"]:
        rows.append({"controle": "Identifiants dupliqués", "variable": id_column, "effectif": audit["duplicate_ids"], "gravite": "Élevée"})
    for col, count in audit["missing_by_column"].items():
        if count:
            rows.append({"controle": "Valeurs manquantes", "variable": str(col), "effectif": count, "gravite": "À vérifier"})
    for col in audit["constant_columns"]:
        rows.append({"controle": "Variable constante ou entièrement vide", "variable": col, "effectif": 1, "gravite": "À vérifier"})
    for col, count in audit["numeric_outliers"].items():
        if count:
            rows.append({"controle": "Valeurs atypiques (règle IQR)", "variable": col, "effectif": count, "gravite": "À examiner"})
    return pd.DataFrame(rows, columns=["controle", "variable", "effectif", "gravite"])
