from __future__ import annotations
import pandas as pd
import streamlit as st
from src.sampling import sample_size_proportion, simple_random_sample, systematic_sample, stratified_allocation

st.set_page_config(page_title="SMART SAMPLING", page_icon="📊", layout="wide")
st.title("📊 SMART SAMPLING")
st.caption("Application d'aide à la conception et à la gestion des échantillons statistiques")
st.info("Outil d'assistance méthodologique : les paramètres, la base de sondage et les résultats doivent être validés par le statisticien.")

page = st.sidebar.radio("Navigation", ["Tableau de bord", "Taille d'échantillon", "Tirage d'unités", "Allocation stratifiée"])

if page == "Tableau de bord":
    st.subheader("Bienvenue dans SMART SAMPLING")
    c1, c2, c3 = st.columns(3)
    c1.metric("Version", "0.1.0")
    c2.metric("Modules disponibles", "3")
    c3.metric("Statut", "Prototype")
    st.markdown("### Modules initiaux\n- Calcul de taille d'échantillon pour une proportion.\n- Tirage aléatoire simple et systématique.\n- Allocation proportionnelle et allocation de Neyman.\n\n**Évolutions prévues :** pondérations, probabilités d'inclusion, contrôle qualité et rapports.")

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
    uploaded = st.file_uploader("Importer une base CSV ou Excel", type=["csv", "xlsx"])
    if uploaded:
        try:
            frame = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
            st.write(f"Base importée : {len(frame)} lignes et {len(frame.columns)} colonnes.")
            st.dataframe(frame.head(10), use_container_width=True)
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

else:
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
        except Exception as exc:
            st.error(str(exc))
