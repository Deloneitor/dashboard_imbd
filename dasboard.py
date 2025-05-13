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
    df.dropna(subset=["Year", "Rating"], inplace=True)
    df["Year"] = df["Year"].astype(int)
    df = df[df["Year"] > 1900]  # Filtrar valores atípicos
    return df

df = cargar_datos()

# ===============================
# KPIs
# ===============================
st.subheader("📊 Indicadores Clave")

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total de Películas", df.shape[0])
kpi2.metric("Calificación Promedio", f"{df['Rating'].mean():.2f}")
kpi3.metric("Año con Más Películas", df['Year'].value_counts().idxmax())

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

df["Main_Genre"] = df["Genre"].apply(lambda x: x.split(",")[0] if isinstance(x, str) else "Desconocido")

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
