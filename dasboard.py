# imdb_dashboard_streamlit.py

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

    columnas_requeridas = ["Title", "Year", "Rating", "Genre"]
    df = df[[col for col in columnas_requeridas if col in df.columns]]

    df.dropna(subset=["Year", "Rating"], inplace=True)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df.dropna(subset=["Year", "Rating"], inplace=True)
    df = df[df["Year"] > 1900]

    df["Main_Genre"] = df["Genre"].apply(lambda x: x.split(",")[0] if isinstance(x, str) else "Desconocido")
    df["Genre_Count"] = df["Genre"].apply(lambda x: len(x.split(",")) if isinstance(x, str) else 0)

    return df

df = cargar_datos()

# ===============================
# KPIs VISUALES
# ===============================
st.subheader("📊 Indicadores Clave con Visualización")

pelis_max_generos = df.loc[df['Genre_Count'].idxmax()]

fig_kpis = make_subplots(rows=3, cols=3, specs=[[{"type": "indicator"}]*3]*3)

fig_kpis.add_trace(go.Indicator(
    mode="number",
    value=df.shape[0],
    title={"text": "🎬 Total de Películas"},
), row=1, col=1)

fig_kpis.add_trace(go.Indicator(
    mode="gauge+number",
    value=df["Rating"].mean(),
    title={"text": "⭐ Calificación Promedio"},
    gauge={"axis": {"range": [0, 10]}, "bar": {"color": "gold"}}
), row=1, col=2)

fig_kpis.add_trace(go.Indicator(
    mode="number",
    value=df["Year"].value_counts().idxmax(),
    title={"text": "📅 Año más Productivo"}
), row=1, col=3)

fig_kpis.add_trace(go.Indicator(
    mode="number",
    value=int(df["Year"].min()),
    title={"text": "🎞️ Película Más Antigua"}
), row=2, col=1)

fig_kpis.add_trace(go.Indicator(
    mode="number",
    value=int(df["Year"].max()),
    title={"text": "📆 Película Más Reciente"}
), row=2, col=2)

fig_kpis.add_trace(go.Indicator(
    mode="number",
    value=df["Rating"].max(),
    title={"text": "🏆 Calificación Máxima"}
), row=2, col=3)

fig_kpis.add_trace(go.Indicator(
    mode="number",
    value=df["Rating"].min(),
    title={"text": "💔 Calificación Mínima"}
), row=3, col=1)

fig_kpis.add_trace(go.Indicator(
    mode="number",
    value=df['Main_Genre'].nunique(),
    title={"text": "🎭 Géneros Únicos"}
), row=3, col=2)

fig_kpis.add_trace(go.Indicator(
    mode="number",
    value=pelis_max_generos['Genre_Count'],
    title={"text": "🎬 Máx. Géneros por Película"}
), row=3, col=3)

fig_kpis.update_layout(height=700, showlegend=False)
st.plotly_chart(fig_kpis, use_container_width=True)

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
# PELÍCULAS POR GÉNERO (GRÁFICO DONA)
# ===============================
st.subheader("🍿 Películas por Género Principal")

genero_counts = df['Main_Genre'].value_counts().reset_index()
genero_counts.columns = ['Género', 'Cantidad']

fig4 = px.pie(genero_counts, values='Cantidad', names='Género', hole=0.4,
              title="Distribución de Películas por Género Principal")
st.plotly_chart(fig4, use_container_width=True)

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
