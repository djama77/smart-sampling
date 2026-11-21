# SMART SAMPLING

Plateforme open source d'aide à la conception, à la sélection et au contrôle des échantillons statistiques.

## Version 0.2 — contrôle qualité

Fonctionnalités disponibles :
- Calcul de taille d'échantillon pour une proportion, avec correction pour population finie et ajustement de non-réponse.
- Tirage aléatoire simple sans remise et tirage systématique reproductible par graine.
- Allocation stratifiée proportionnelle et allocation de Neyman.
- Import de fichiers CSV et Excel.
- Contrôles descriptifs des lignes dupliquées, identifiants manquants/dupliqués, valeurs manquantes, variables constantes et valeurs atypiques selon la règle IQR.
- Export CSV des résultats de tirage, allocations et constats de qualité.

## Installation et lancement

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
python -m pip install pytest
python -m pytest -q
```

## Structure

- `app.py` : interface Streamlit.
- `src/sampling.py` : calculs de taille, tirages et allocations.
- `src/quality.py` : contrôles descriptifs de qualité.
- `tests/test_quality.py` : tests unitaires des contrôles qualité.

## Interprétation et limites

Les contrôles signalent des anomalies potentielles ; ils ne modifient jamais automatiquement les données. La règle IQR repère des valeurs atypiques, qui ne sont pas nécessairement des erreurs. Les contrôles de couverture, de cohérence métier et de représentativité nécessitent des règles et référentiels propres à chaque enquête.

Les probabilités d'inclusion et les pondérations doivent être calculées en fonction du plan de sondage réellement appliqué. La validation scientifique finale reste sous la responsabilité du statisticien.

## Protection des données

Ne publiez jamais de bases réelles ou confidentielles dans le dépôt GitHub. Utilisez des données fictives pour les démonstrations et les tests.

## Feuille de route

Les prochaines étapes sont les probabilités d'inclusion et les poids de base, puis l'analyse de représentativité, les estimations tenant compte du plan, et les rapports PDF/Excel.
