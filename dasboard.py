# imdb_dashboard_streamlit.py

import pandas as pd
import streamlit as st
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# ===============================
# CONFIGURACIÓN INICIAL STREAMLIT
# ===============================
st.set_page_config(page_title="Dashboard IMDb", layout="wide")
st.title("🎬 Dashboard de Puntuaciones de Películas")

# ===============================
# CARGA DE DATOS
# ===============================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("imdb_movies.csv")
    
    # Filtrar columnas necesarias
    columnas_requeridas = ["Title", "Year", "Rating", "Genre"]
    df = df[[col for col in columnas_requeridas if col in df.columns]]

    # Limpiar datos
    df.dropna(subset=["Year", "Rating"], inplace=True)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df.dropna(subset=["Year", "Rating"], inplace=True)
    df = df[df["Year"] > 1900]  # Filtrar valores atípicos

    # Procesar géneros
    df["Main_Genre"] = df["Genre"].apply(lambda x: x.split(",")[0] if isinstance(x, str) else "Desconocido")
    df["Genre_Count"] = df["Genre"].apply(lambda x: len(x.split(",")) if isinstance(x, str) else 0)

    return df

df = cargar_datos()

# ===============================
# KPIs (9 indicadores)
# ===============================
st.subheader("📊 Indicadores Clave")

# Primera fila de KPIs
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total de Películas", df.shape[0])
kpi2.metric("Calificación Promedio", f"{df['Rating'].mean():.2f}")
kpi3.metric("Año con Más Películas", df['Year'].value_counts().idxmax())

# Segunda fila de KPIs
kpi4, kpi5, kpi6 = st.columns(3)
kpi4.metric("Película Más Antigua", int(df["Year"].min()))
kpi5.metric("Película Más Reciente", int(df["Year"].max()))
kpi6.metric("Calificación Máxima", f"{df['Rating'].max():.1f}")

# Tercera fila de KPIs
kpi7, kpi8, kpi9 = st.columns(3)
kpi7.metric("Calificación Mínima", f"{df['Rating'].min():.1f}")
kpi8.metric("Géneros Únicos", df['Main_Genre'].nunique())
pelis_max_generos = df.loc[df['Genre_Count'].idxmax()]
kpi9.metric("Máx. Géneros en una Película", pelis_max_generos['Genre_Count'])

# ===============================
# EVOLUCIÓN DE PUNTUACIONES
# ===============================
st.subheader("📈 Evolución de Calificaciones por Año")

ratings_por_anio = df.groupby("Year")["Rating"].mean().reset_index()

fig1 = px.line(ratings_por_anio, x="Year", y="Rating", markers=True,
               title="Evolución de Puntuaciones Promedio por Año")
st.plotly_chart(fig1, use_container_width=True)

# ===============================
# HISTOGRAMA DE PELÍCULAS POR AÑO
# ===============================
st.subheader("🎞 Distribución de Películas por Año")

fig2 = px.histogram(df, x="Year", nbins=50,
                    title="Cantidad de Películas por Año")
st.plotly_chart(fig2, use_container_width=True)

# ===============================
# BOXPLOT DE CALIFICACIONES POR GÉNERO
# ===============================
st.subheader("🎭 Distribución de Calificaciones por Género")

fig3 = px.box(df, x="Main_Genre", y="Rating", points="all",
              title="Calificaciones por Género")
fig3.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig3, use_container_width=True)

# ===============================
# TOP 10 PELÍCULAS MEJOR CALIFICADAS
# ===============================
st.subheader("🏆 Top 10 Películas Mejor Calificadas")

top10 = df.sort_values("Rating", ascending=False).head(10)[["Title", "Year", "Rating"]]
st.table(top10.reset_index(drop=True))

# ===============================
# PIE DE PÁGINA
# ===============================
st.caption("📽️ Creado por Diego | Datos IMDb")
