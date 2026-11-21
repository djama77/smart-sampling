from __future__ import annotations
import pandas as pd
import streamlit as st
from src.sampling import sample_size_proportion, simple_random_sample, systematic_sample, stratified_allocation
from src.quality import quality_audit, quality_issues
from src.weights import simple_random_base_weights, stratified_base_weights

st.set_page_config(page_title="SMART SAMPLING", page_icon="📊", layout="wide")
st.title("📊 SMART SAMPLING")
st.caption("Conception, sélection et contrôle des échantillons statistiques")
st.info("Outil d'assistance méthodologique : les paramètres, la base de sondage et les résultats doivent être validés par le statisticien.")
page = st.sidebar.radio("Navigation", ["Tableau de bord", "Taille d'échantillon", "Tirage d'unités", "Allocation stratifiée", "Contrôle qualité", "Pondération"])

def read_uploaded_file(uploaded):
    if uploaded.name.lower().endswith(".csv"):
        try:
            return pd.read_csv(uploaded)
        except UnicodeDecodeError:
            uploaded.seek(0)
            return pd.read_csv(uploaded, encoding="latin-1")
    return pd.read_excel(uploaded)

if page == "Tableau de bord":
    st.subheader("Bienvenue dans SMART SAMPLING")
    c1, c2, c3 = st.columns(3)
    c1.metric("Version", "0.3.0")
    c2.metric("Modules disponibles", "4")
    c3.metric("Statut", "Prototype évolutif")
    st.markdown("""**Fonctionnalités disponibles**
- Calcul de taille d'échantillon pour une proportion.
- Tirage aléatoire simple et systématique reproductible.
- Allocation proportionnelle et allocation de Neyman.
- Contrôles descriptifs de qualité des bases de sondage.

Les anomalies sont signalées pour examen. Aucune donnée n'est corrigée ou supprimée automatiquement.""")

elif page == "Taille d'échantillon":
    st.subheader("Calcul de la taille d'échantillon")
    c1, c2 = st.columns(2)
    with c1:
        N = st.number_input("Taille de la population (N)", min_value=1, value=10000, step=100)
        confidence = st.selectbox("Niveau de confiance", [0.90, 0.95, 0.99], index=1)
    with c2:
        p = st.number_input("Proportion attendue (p)", min_value=0.01, max_value=0.99, value=0.50, step=0.01)
        e = st.number_input("Marge d'erreur (e)", min_value=0.01, max_value=0.50, value=0.05, step=0.01)
        nonresponse = st.number_input("Taux de non-réponse", min_value=0.0, max_value=0.90, value=0.0, step=0.01)
    if st.button("Calculer", type="primary"):
        z = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}[confidence]
        try:
            n = sample_size_proportion(int(N), z, p, e, nonresponse)
            st.success(f"Taille d'échantillon recommandée : {n:,}".replace(",", " "))
            st.latex(r"n_0=\frac{Z^2p(1-p)}{e^2}")
            st.caption("Correction pour population finie, puis ajustement pour la non-réponse.")
        except ValueError as exc:
            st.error(str(exc))

elif page == "Tirage d'unités":
    st.subheader("Tirage à partir d'une base de sondage")
    uploaded = st.file_uploader("Importer une base CSV ou Excel", type=["csv", "xlsx"], key="sample_upload")
    if uploaded:
        try:
            frame = read_uploaded_file(uploaded)
            st.write(f"Base importée : {len(frame)} lignes et {len(frame.columns)} colonnes.")
            st.dataframe(frame.head(10), use_container_width=True)
            if frame.empty:
                st.warning("La base ne contient aucune unité à tirer.")
            else:
                n = st.number_input("Taille de l'échantillon", min_value=1, max_value=len(frame), value=min(30, len(frame)))
                method = st.selectbox("Méthode", ["Aléatoire simple", "Systématique"])
                seed = st.number_input("Graine aléatoire", min_value=0, value=42, step=1)
                if st.button("Effectuer le tirage", type="primary"):
                    result = simple_random_sample(frame, int(n), int(seed)) if method == "Aléatoire simple" else systematic_sample(frame, int(n), int(seed))
                    st.success(f"{len(result)} unités sélectionnées.")
                    st.dataframe(result, use_container_width=True)
                    st.download_button("Télécharger l'échantillon CSV", result.to_csv(index=False).encode("utf-8-sig"), "echantillon.csv", "text/csv")
        except Exception as exc:
            st.error(f"Erreur de lecture ou de traitement : {exc}")

elif page == "Allocation stratifiée":
    st.subheader("Allocation stratifiée")
    example = pd.DataFrame({"strate": ["Strate A", "Strate B", "Strate C"], "effectif": [500, 300, 200], "ecart_type": [10, 15, 8]})
    edited = st.data_editor(example, num_rows="dynamic", use_container_width=True)
    total = st.number_input("Taille totale à répartir", min_value=1, value=100, step=1)
    method = st.selectbox("Méthode d'allocation", ["Proportionnelle", "Neyman"])
    if st.button("Calculer l'allocation", type="primary"):
        try:
            result = stratified_allocation(edited, int(total), "strate", "effectif", "proportional" if method == "Proportionnelle" else "neyman", "ecart_type" if method == "Neyman" else None)
            st.dataframe(result, use_container_width=True)
            st.download_button("Télécharger l'allocation CSV", result.to_csv(index=False).encode("utf-8-sig"), "allocation_stratifiee.csv", "text/csv")
        except (ValueError, TypeError) as exc:
            st.error(str(exc))

elif page == "Contrôle qualité":
    st.subheader("Contrôle qualité de la base de sondage")
    st.caption("Contrôles descriptifs : doublons, identifiants, valeurs manquantes, variables constantes et valeurs atypiques.")
    uploaded = st.file_uploader("Importer une base CSV ou Excel", type=["csv", "xlsx"], key="quality_upload")
    if uploaded:
        try:
            frame = read_uploaded_file(uploaded)
            if frame.empty or len(frame.columns) == 0:
                st.warning("La base importée est vide.")
            else:
                st.dataframe(frame.head(10), use_container_width=True)
                id_options = ["— Aucun identifiant défini —"] + [str(c) for c in frame.columns]
                selected_id = st.selectbox("Variable identifiant (facultatif)", id_options)
                id_column = None if selected_id.startswith("—") else selected_id
                audit = quality_audit(frame, id_column)
                cols = st.columns(4)
                cols[0].metric("Unités", audit["row_count"])
                cols[1].metric("Variables", audit["column_count"])
                cols[2].metric("Lignes dupliquées", audit["duplicate_rows"])
                cols[3].metric("Cellules manquantes", audit["missing_cells"])
                st.markdown("### Valeurs manquantes par variable")
                missing_frame = pd.DataFrame([{"variable": k, "valeurs_manquantes": v} for k, v in audit["missing_by_column"].items()])
                st.dataframe(missing_frame, use_container_width=True)
                st.markdown("### Anomalies à examiner")
                issues = quality_issues(frame, id_column)
                if issues.empty:
                    st.success("Aucune anomalie détectée par les contrôles activés.")
                else:
                    st.dataframe(issues, use_container_width=True)
                    st.download_button("Télécharger le rapport de contrôle CSV", issues.to_csv(index=False).encode("utf-8-sig"), "rapport_controle_qualite.csv", "text/csv")
                st.warning("Les valeurs atypiques sont repérées par la règle descriptive IQR. Elles ne sont pas nécessairement erronées : interpréter les résultats selon le contexte de l'enquête.")
        except Exception as exc:
            st.error(f"Impossible de contrôler cette base : {exc}")


else:
    st.subheader("Probabilités d'inclusion et poids de base")
    st.warning("Ce module couvre uniquement le tirage aléatoire simple sans remise et le tirage aléatoire simple sans remise à l'intérieur de chaque strate. Il ne calcule pas les poids de plans systématiques, en grappes ou à plusieurs degrés.")
    method = st.radio("Plan de sondage", ["Aléatoire simple", "Stratifié (tirage aléatoire simple dans chaque strate)"])
    sample_file = st.file_uploader("Importer le fichier des unités effectivement sélectionnées", type=["csv", "xlsx"], key="weights_sample")
    if sample_file:
        try:
            sample_frame = read_uploaded_file(sample_file)
            if sample_frame.empty:
                st.warning("Le fichier de l'échantillon est vide.")
            else:
                st.write(f"Échantillon : {len(sample_frame)} unités.")
                st.dataframe(sample_frame.head(10), use_container_width=True)
                if method == "Aléatoire simple":
                    population_size = st.number_input("Effectif total de la population (N)", min_value=len(sample_frame), value=max(100, len(sample_frame)), step=1)
                    if st.button("Calculer les probabilités et poids", type="primary"):
                        result = simple_random_base_weights(sample_frame, int(population_size))
                        st.metric("Probabilité d'inclusion de chaque unité", f"{len(result) / int(population_size):.6f}")
                        st.metric("Poids de base", f"{int(population_size) / len(result):.4f}")
                        st.dataframe(result, use_container_width=True)
                        st.download_button("Télécharger les poids CSV", result.to_csv(index=False).encode("utf-8-sig"), "echantillon_avec_poids.csv", "text/csv")
                else:
                    population_file = st.file_uploader("Importer le tableau des effectifs de population par strate (une ligne par strate)", type=["csv", "xlsx"], key="weights_population")
                    if population_file:
                        population_frame = read_uploaded_file(population_file)
                        if not population_frame.empty and len(population_frame.columns) >= 2:
                            sample_stratum = st.selectbox("Variable strate dans l'échantillon", list(sample_frame.columns), key="sample_stratum")
                            pop_stratum = st.selectbox("Variable strate dans la population", list(population_frame.columns), key="pop_stratum")
                            pop_size = st.selectbox("Variable effectif N_h dans la population", [c for c in population_frame.columns if c != pop_stratum], key="pop_size")
                            if st.button("Calculer les probabilités et poids par strate", type="primary"):
                                normalized_population = population_frame[[pop_stratum, pop_size]].rename(columns={pop_stratum: sample_stratum, pop_size: "N_h"})
                                result = stratified_base_weights(sample_frame, normalized_population, sample_stratum, "N_h")
                                st.dataframe(result, use_container_width=True)
                                st.download_button("Télécharger les poids CSV", result.to_csv(index=False).encode("utf-8-sig"), "echantillon_stratifie_avec_poids.csv", "text/csv")
                        else:
                            st.error("Le tableau de population doit contenir au moins deux colonnes et des données.")
        except Exception as exc:
            st.error(f"Calcul impossible : {exc}")
    st.caption("Formules : EAS sans remise, pi_i = n/N et poids de base = N/n. En stratifié, pi_hi = n_h/N_h et poids de base = N_h/n_h. Les poids calculés sont des poids de base de sondage, avant ajustement de non-réponse ou calibration.")
