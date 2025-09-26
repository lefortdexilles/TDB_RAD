import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title = "Tableau de bord Effectifs étranger par service",
                   layout='wide'   )

df = pd.read_excel('socle_rh_24.xlsx',sheet_name='Feuil1')

# NETTOYAGE DE DONNEES

df = df[df['Cat Stat'] != "G0"]
df = df[['région', 'Pays', 'Correspondance', 'ETP']]

df.dropna(inplace=True)

pivot_df = df.pivot_table(index=['région', 'Pays'], 
                          columns='Correspondance', 
                          values='ETP', 
                          aggfunc='sum', 
                          fill_value=0).reset_index()

pivot_df.columns.name = None

# Exemple de DataFrame

# --- Moyennes par région ---
moyennes_region = pivot_df.groupby('région')[["Chancellerie", "Consulaire","DCSD", "EAF/AF/EXT", "SCAC", "Support"]].mean().reset_index()
moyennes_region['Pays'] = "moyenne régionale"

# --- Moyenne globale (toutes régions confondues) ---
moyenne_globale = pivot_df[["Chancellerie", "Consulaire","DCSD", "EAF/AF/EXT", "SCAC", "Support"]].mean().to_frame().T
moyenne_globale.insert(0, 'Pays', "moyenne mondiale")
moyenne_globale.insert(0, 'région', "GLOBAL")

# --- Concaténation ---
df_ext = pd.concat([pivot_df, moyennes_region, moyenne_globale], ignore_index=True)


regions = df_ext["région"].unique()

selected_region = st.sidebar.selectbox("Selectionnez une Region:", regions)

filtered_countries = df_ext[df_ext["région"] == selected_region]["Pays"].unique()

selected_country = st.sidebar.selectbox("Selectionnez un pays:", filtered_countries)

region = selected_region
dfx = df_ext[df_ext['région']==region]
pays = selected_country
df_subset = df_ext[df_ext["Pays"].isin([pays, "moyenne régionale", "moyenne mondiale"])]

df_subset = df_subset[(df_subset["région"]==region) | (df_subset["région"]=="GLOBAL")]

# Colonnes à utiliser comme catégories
categories = ["Chancellerie", "Consulaire", "DCSD", "EAF/AF/EXT", "SCAC", "Support"]
N = len(categories)

# Angles pour chaque catégorie
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # fermer le cercle

# Création du radar chart
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

# Boucle sur les lignes du DataFrame
for i, row in df_subset.iterrows():
    values = row[categories].tolist()
    values += values[:1]  # fermer le cercle
    ax.plot(angles, values, linewidth=2, label=row["Pays"])
    ax.fill(angles, values, alpha=0.25)

# Labels des catégories
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)

# Légende
plt.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))
plt.title("Radar des ETP et comparaison", y=1.1)

st.pyplot(fig)