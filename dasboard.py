# imdb_dashboard_streamlit.py

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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
# KPIs MÁS GRÁFICOS Y VISUALES
# ===============================
st.subheader("📊 Indicadores Clave Visuales")

pelis_max_generos = df.loc[df['Genre_Count'].idxmax()]

kpi_tabs = st.tabs(["🎬 Total Películas", "⭐ Promedio Rating", "📅 Año con Más Películas",
                    "🎞️ Más Antigua", "📆 Más Reciente", "🏆 Rating Máximo",
                    "💔 Rating Mínimo", "🎭 Géneros Únicos", "🎬 Máx. Géneros en una Película"])

# 1. Total Películas
with kpi_tabs[0]:
    fig = px.bar(x=["Películas"], y=[df.shape[0]],
                 title="Total de Películas", text=[df.shape[0]],
                 color_discrete_sequence=["#4C78A8"])
    fig.update_layout(yaxis_title="Cantidad", xaxis_title=None, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# 2. Promedio Rating
with kpi_tabs[1]:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(df["Rating"].mean(), 2),
        title={"text": "Promedio de Rating"},
        gauge={"axis": {"range": [0, 10]},
               "bar": {"color": "gold"},
               "steps": [{"range": [0, 5], "color": "#ffe6e6"},
                         {"range": [5, 7], "color": "#ffffcc"},
                         {"range": [7, 10], "color": "#e6ffe6"}]}
    ))
    st.plotly_chart(fig, use_container_width=True)

# 3. Año con más películas
with kpi_tabs[2]:
    top_year = df["Year"].value_counts().idxmax()
    count = df["Year"].value_counts().max()
    fig = px.bar(x=[top_year], y=[count], text=[count],
                 title="Año con más Películas", labels={"x": "Año", "y": "Cantidad"},
                 color_discrete_sequence=["#F58518"])
    st.plotly_chart(fig, use_container_width=True)

# 4. Película más antigua
with kpi_tabs[3]:
    oldest = int(df["Year"].min())
    st.markdown(f"## 🎞️ Año más antiguo: `{oldest}`")

# 5. Película más reciente
with kpi_tabs[4]:
    latest = int(df["Year"].max())
    st.markdown(f"## 📆 Año más reciente: `{latest}`")

# 6. Calificación máxima
with kpi_tabs[5]:
    max_rating = df["Rating"].max()
    st.markdown(f"## 🏆 Calificación más alta: `{max_rating}`")

# 7. Calificación mínima
with kpi_tabs[6]:
    min_rating = df["Rating"].min()
    st.markdown(f"## 💔 Calificación más baja: `{min_rating}`")

# 8. Géneros únicos
with kpi_tabs[7]:
    num_genres = df['Main_Genre'].nunique()
    st.markdown(f"## 🎭 Géneros únicos: `{num_genres}`")

# 9. Máx. géneros en una película
with kpi_tabs[8]:
    max_genres = df["Genre_Count"].max()
    st.markdown(f"## 🎬 Máx. géneros por película: `{max_genres}`")

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
