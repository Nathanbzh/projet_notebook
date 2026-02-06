import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px

# Configuration de la page pour utiliser toute la largeur
st.set_page_config(page_title="Dashboard Salaires Data Science", layout="wide")

### 1. Importation des librairies et chargement des données
# Chargement des données
# On utilise un décorateur @st.cache_data pour garder les données en mémoire et ne pas recharger à chaque interaction
@st.cache_data
def load_data():
    if os.path.exists("data/ds_salaries.csv"):
        return pd.read_csv("data/ds_salaries.csv")
    else:
        # Fallback si le fichier n'est pas dans un sous-dossier data
        return pd.read_csv("ds_salaries.csv")

df = load_data()

### 2. Exploration visuelle des données
st.title("📊 Visualisation des Salaires en Data Science")
st.markdown("Explorez les tendances des salaires à travers différentes visualisations interactives.")

if st.checkbox("Afficher un aperçu des données"):
    st.write(df.head())

# Statistique générales avec describe pandas 
st.subheader("📌 Statistiques générales")
st.write(df.describe())
st.markdown("---")

### 3. Distribution des salaires en France
# On filtre sur 'FR' et on utilise un boxplot pour voir la médiane et les outliers
st.subheader("📈 Distribution des salaires en France")

df_france = df[df['company_location'] == 'FR']

if not df_france.empty:
    fig_fr = px.box(
        df_france, 
        x="experience_level", 
        y="salary_in_usd", 
        color="experience_level",
        title="Distribution des salaires en France par niveau d'expérience",
        labels={"salary_in_usd": "Salaire (USD)", "experience_level": "Niveau d'expérience"}
    )
    st.plotly_chart(fig_fr, use_container_width=True)
else:
    st.warning("Pas de données disponibles pour la France.")

st.markdown("---")

### 4. Analyse des tendances de salaires
st.subheader("🔍 Analyse des tendances de salaires")

# Choix de la catégorie pour l'analyse
category = st.selectbox(
    "Choisissez une catégorie d'analyse :", 
    ['experience_level', 'employment_type', 'job_title', 'company_location']
)

# On groupe par la catégorie choisie et on fait la moyenne
# On reset_index pour que la catégorie redevienne une colonne utilisable par Plotly
df_grouped = df.groupby(category)['salary_in_usd'].mean().reset_index().sort_values(by='salary_in_usd', ascending=False).head(10)

fig_bar = px.bar(
    df_grouped, 
    x=category, 
    y="salary_in_usd",
    title=f"Salaire moyen par {category} (Top 10)",
    color="salary_in_usd",
    color_continuous_scale="Viridis"
)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

### 5. Corrélation entre variables
st.subheader("🔗 Corrélations entre variables numériques")

# Sélectionner uniquement les colonnes numériques pour la corrélation
numeric_df = df.select_dtypes(include=[np.number])

# Calcul de la matrice de corrélation
corr_matrix = numeric_df.corr()

# Affichage du heatmap avec sns.heatmap
fig_corr, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
st.pyplot(fig_corr)

st.markdown("---")

### 6. Analyse interactive des variations de salaire
st.subheader("📅 Évolution des salaires pour les postes les plus courants")

# 1. On compte les titres pour trouver les 5 plus fréquents
top_jobs = df['job_title'].value_counts().head(5).index

# 2. On filtre le dataframe pour ne garder que ces jobs
df_top_jobs = df[df['job_title'].isin(top_jobs)]

# 3. On groupe par année et par job pour avoir la moyenne
df_evolution = df_top_jobs.groupby(['work_year', 'job_title'])['salary_in_usd'].mean().reset_index()

# 4. Graphique linéaire
fig_line = px.line(
    df_evolution, 
    x="work_year", 
    y="salary_in_usd", 
    color="job_title",
    markers=True,
    title="Évolution du salaire moyen par an (Top 5 Jobs)"
)
st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

### 7. Salaire médian par expérience et taille d'entreprise
st.subheader("🏢 Salaire médian par Expérience et Taille d'entreprise")

# Calcul de la médiane
df_median = df.groupby(['experience_level', 'company_size'])['salary_in_usd'].median().reset_index()

fig_grouped_bar = px.bar(
    df_median, 
    x="experience_level", 
    y="salary_in_usd", 
    color="company_size", 
    barmode="group",
    title="Comparaison des salaires médians selon la taille de l'entreprise"
)
st.plotly_chart(fig_grouped_bar, use_container_width=True)

st.markdown("---")

### 8. Ajout de filtres dynamiques
st.subheader("🎚️ Filtrage par salaire")

min_salary = int(df['salary_in_usd'].min())
max_salary = int(df['salary_in_usd'].max())

# Slider double pour sélectionner une plage min-max
salary_range = st.slider(
    "Sélectionnez la plage de salaire (USD)",
    min_value=min_salary,
    max_value=max_salary,
    value=(min_salary, max_salary)
)

# Filtrage
df_filtered_salary = df[(df['salary_in_usd'] >= salary_range[0]) & (df['salary_in_usd'] <= salary_range[1])]
st.write(f"Nombre de profils correspondants : **{len(df_filtered_salary)}**")

st.markdown("---")

### 9. Impact du télétravail sur le salaire
st.subheader("🏠 Impact du télétravail sur le salaire")

# Boxplot pour voir la distribution des salaires selon le ratio de télétravail (0, 50, 100)
# On force remote_ratio en string pour qu'il soit traité comme une catégorie et non un nombre continu
df['remote_ratio_str'] = df['remote_ratio'].astype(str) + '%'

fig_remote = px.box(
    df,
    x='remote_ratio_str',
    y='salary_in_usd',
    color='remote_ratio_str',
    title="Distribution des salaires selon le taux de télétravail",
    category_orders={"remote_ratio_str": ["0%", "50%", "100%"]}
)
st.plotly_chart(fig_remote, use_container_width=True)

st.markdown("---")

### 10. Filtrage avancé
st.subheader("⚡ Filtrage avancé croisé")

col1, col2 = st.columns(2)

with col1:
    selected_exp = st.multiselect(
        "Sélectionnez le niveau d'expérience", 
        options=df['experience_level'].unique(),
        default=df['experience_level'].unique()
    )

with col2:
    selected_size = st.multiselect(
        "Sélectionnez la taille d'entreprise", 
        options=df['company_size'].unique(),
        default=df['company_size'].unique()
    )

# Application du filtre
df_final_filter = df[
    (df['experience_level'].isin(selected_exp)) & 
    (df['company_size'].isin(selected_size))
]

st.write(f"Données filtrées : {len(df_final_filter)} lignes")
st.dataframe(df_final_filter)