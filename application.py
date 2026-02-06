"""
📝 **Instructions** :
- Installez toutes les bibliothèques nécessaires en fonction des imports présents dans le code, utilisez la commande suivante :conda create -n projet python pandas numpy ..........
- Complétez les sections en écrivant votre code où c’est indiqué.
- Ajoutez des commentaires clairs pour expliquer vos choix.
- Utilisez des emoji avec windows + ;
- Interprétez les résultats de vos visualisations (quelques phrases).

Le lien vers le repértoire github : https://github.com/Nathanbzh/projet_notebook
L'application est accessible au lien suivant : https://projetnotebook-vqu6wkikgrgvamaxvlib2s.streamlit.app/
"""
 


### 1. Importation des librairies et chargement des données
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px

# Configuration de la page pour une meilleure disposition
st.set_page_config(page_title="Dashboard Salaires", layout="wide")

# Chargement des données
# On utilise le décorateur cache pour la performance
@st.cache_data
def load_data():
    if os.path.exists("data/ds_salaries.csv"):
        return pd.read_csv("data/ds_salaries.csv")
    return pd.read_csv("ds_salaries.csv")

df = load_data()


### 2. Exploration visuelle des données
#votre code 
st.title("📊 Visualisation des Salaires en Data Science")
st.markdown("Explorez les tendances des salaires à travers différentes visualisations interactives.")

if st.checkbox("Afficher un aperçu des données"):
    st.write(df.head())

#Statistique générales avec describe pandas 
#votre code 
st.subheader("📌 Statistiques générales")
st.write(df.describe())
st.write("Ces statistiques permettent de voir rapidement la distribution des salaires et d'identifier les valeurs aberrantes potentielles.")


### 3. Distribution des salaires en France par rôle et niveau d'expérience, uilisant px.box et st.plotly_chart
#votre code 
st.subheader("📈 Distribution des salaires en France")

df_france = df[df['company_location'] == 'FR']

if not df_france.empty:
    fig_fr = px.box(df_france, x="experience_level", y="salary_in_usd", color="experience_level", 
                    title="Distribution des salaires en France")
    st.plotly_chart(fig_fr, use_container_width=True)
    st.write("On observe la médiane des salaires français selon l'expérience. Les seniors ont logiquement une dispersion plus grande.")
else:
    st.warning("Pas de données pour la France.")


### 4. Analyse des tendances de salaires :
#### Salaire moyen par catégorie : en choisisant une des : ['experience_level', 'employment_type', 'job_title', 'company_location'], utilisant px.bar et st.selectbox 
st.markdown("### Salaire moyen par catégorie")

option = st.selectbox("Choisir la catégorie :", ['experience_level', 'employment_type', 'job_title', 'company_location'])

df_mean = df.groupby(option)['salary_in_usd'].mean().reset_index().sort_values(by='salary_in_usd', ascending=False).head(10)

fig_bar = px.bar(df_mean, x=option, y='salary_in_usd', color='salary_in_usd', title=f"Salaire moyen par {option}")
st.plotly_chart(fig_bar, use_container_width=True)


### 5. Corrélation entre variables
# Sélectionner uniquement les colonnes numériques pour la corrélation
#votre code 
numeric_df = df.select_dtypes(include=[np.number])

# Calcul de la matrice de corrélation
#votre code
corr = numeric_df.corr()

# Affichage du heatmap avec sns.heatmap
#votre code 
st.subheader("🔗 Corrélations entre variables numériques")

fig_corr, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig_corr)
st.write("La matrice montre les liens entre salaire, année et télétravail. Une corrélation forte indiquerait une dépendance linéaire.")


### 6. Analyse interactive des variations de salaire
# Une évolution des salaires pour les 10 postes les plus courants
# count of job titles pour selectionner les postes
# calcule du salaire moyen par an
#utilisez px.line
#votre code 
st.subheader("Évolution des salaires (Top 10 postes)")

top_jobs = df['job_title'].value_counts().head(10).index
df_top = df[df['job_title'].isin(top_jobs)]
df_evo = df_top.groupby(['work_year', 'job_title'])['salary_in_usd'].mean().reset_index()

fig_line = px.line(df_evo, x='work_year', y='salary_in_usd', color='job_title', markers=True)
st.plotly_chart(fig_line, use_container_width=True)


### 7. Salaire médian par expérience et taille d'entreprise
# utilisez median(), px.bar
#votre code 
st.subheader("Salaire médian par Expérience et Taille")

df_median = df.groupby(['experience_level', 'company_size'])['salary_in_usd'].median().reset_index()

fig_med = px.bar(df_median, x='experience_level', y='salary_in_usd', color='company_size', barmode='group')
st.plotly_chart(fig_med, use_container_width=True)


### 8. Ajout de filtres dynamiques
#Filtrer les données par salaire utilisant st.slider pour selectionner les plages 
#votre code 
st.subheader("Filtre par salaire")

min_sal, max_sal = int(df.salary_in_usd.min()), int(df.salary_in_usd.max())
plage = st.slider("Sélectionnez la plage de salaire", min_sal, max_sal, (min_sal, max_sal))

df_filtre_sal = df[(df.salary_in_usd >= plage[0]) & (df.salary_in_usd <= plage[1])]
st.write(f"Nombre de profils : {len(df_filtre_sal)}")


### 9.  Impact du télétravail sur le salaire selon le pays
st.subheader("Impact du télétravail")

# Conversion pour affichage catégoriel propre
df['remote_str'] = df['remote_ratio'].astype(str) + '%'
fig_remote = px.box(df, x='remote_str', y='salary_in_usd', title="Distribution des salaires selon le télétravail")
st.plotly_chart(fig_remote, use_container_width=True)


### 10. Filtrage avancé des données avec deux st.multiselect, un qui indique "Sélectionnez le niveau d'expérience" et l'autre "Sélectionnez la taille d'entreprise"
#votre code 
st.subheader("Filtrage avancé")

col1, col2 = st.columns(2)

with col1:
    choix_exp = st.multiselect("Sélectionnez le niveau d'expérience", df['experience_level'].unique())

with col2:
    choix_taille = st.multiselect("Sélectionnez la taille d'entreprise", df['company_size'].unique())

if choix_exp and choix_taille:
    df_final = df[df['experience_level'].isin(choix_exp) & df['company_size'].isin(choix_taille)]
    st.dataframe(df_final)
else:
    st.info("Veuillez sélectionner au moins une valeur dans chaque filtre pour voir les résultats.")