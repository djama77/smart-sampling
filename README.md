# SMART SAMPLING

Plateforme open source d'aide à la conception, à la sélection et au contrôle des échantillons statistiques.

## Version 0.3 — probabilités d'inclusion et poids de base

Fonctionnalités :
- Calcul de taille d'échantillon pour une proportion, avec correction pour population finie et ajustement de non-réponse.
- Tirage aléatoire simple sans remise et tirage systématique reproductible par graine.
- Allocation stratifiée proportionnelle et allocation de Neyman.
- Contrôles descriptifs des bases : doublons, identifiants manquants/dupliqués, valeurs manquantes, variables constantes et valeurs atypiques (IQR).
- Probabilités d'inclusion et poids de base pour l'échantillonnage aléatoire simple sans remise.
- Probabilités d'inclusion et poids de base pour un tirage aléatoire simple sans remise dans chaque strate.
- Import CSV/Excel et export des résultats en CSV.

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
- `src/weights.py` : probabilités d'inclusion et poids de base.
- `tests/` : tests unitaires.

## Formules et domaine de validité

Pour un échantillonnage aléatoire simple sans remise (EAS), avec une population de taille N et un échantillon de taille n :
- Probabilité d'inclusion de premier ordre : pi_i = n/N.
- Poids de base : d_i = 1/pi_i = N/n.

Pour un plan stratifié avec EAS sans remise dans chaque strate h :
- Probabilité d'inclusion : pi_hi = n_h/N_h.
- Poids de base : d_hi = 1/pi_hi = N_h/n_h.

Ces formules ne doivent pas être appliquées à un plan systématique, en grappes ou à plusieurs degrés sans calcul spécifique des probabilités d'inclusion. Les poids produits ici sont des poids de base : ils ne comprennent ni ajustement de non-réponse ni calibration. Le fichier fourni au module de pondération doit contenir les unités effectivement sélectionnées ; les effectifs N_h doivent provenir d'un état de population validé.

## Interprétation et limites

Les valeurs atypiques IQR sont des observations à examiner, pas nécessairement des erreurs. Les contrôles ne modifient jamais automatiquement les données. Les probabilités et poids dépendent du plan réellement exécuté et doivent être documentés et validés par un statisticien.

## Protection des données

Ne publiez jamais de bases réelles ou confidentielles dans le dépôt GitHub. Utilisez des données fictives pour les démonstrations et les tests.
