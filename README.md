# SMART SAMPLING

Application intelligente de conception et de gestion des échantillons statistiques.

## Objectif
SMART SAMPLING accompagne les statisticiens dans la préparation des enquêtes : calcul de taille d'échantillon, allocation, sélection des unités et documentation des choix méthodologiques. L'application assiste le statisticien sans remplacer son jugement ni sa validation scientifique.

## Première version (V1)
- Calcul de taille d'échantillon pour une proportion, avec correction pour population finie.
- Tirage aléatoire simple sans remise.
- Tirage systématique.
- Échantillonnage stratifié avec allocation proportionnelle ou de Neyman.
- Import de fichiers CSV et Excel.
- Export des résultats en CSV.

## Lancer l'application
Installer les dépendances avec `pip install -r requirements.txt`, puis lancer `streamlit run app.py`.

## Structure
- `app.py` : interface Streamlit
- `src/sampling.py` : méthodes statistiques
- `requirements.txt` : dépendances
- `tests/` : tests à ajouter

## Principes méthodologiques
Les résultats dépendent de la qualité de la base de sondage, de la définition de la population cible et des hypothèses saisies. Les probabilités d'inclusion, les pondérations et les limites du plan doivent être vérifiées avant toute exploitation officielle.

## Statut
Version de démarrage — V1 en développement.
