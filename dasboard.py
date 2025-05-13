
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

    df = df[df["Year"].notna() & df["Rating"].notna()]
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df = df[df["Year"] > 1900]

    df["Main_Genre"] = df["Genre"].apply(lambda x: x.split(",")[0] if isinstance(x, str) else "Desconocido")
    df["Genre_Count"] = df["Genre"].apply(lambda x: len(x.split(",")) if isinstance(x, str) else 0)

    return df

df = cargar_datos()

# ===============================
# KPIs MÁS GRÁFICOS Y VISUALES
# ===============================
st.subheader("📊 Indicadores Clave Visuales")

kpi_tabs = st.tabs(["🎬 Total Películas", "⭐ Promedio Rating", "📅 Año con Más Películas",
                    "🎞️ Más Antigua", "📆 Más Reciente", "🏆 Rating Máximo",
                    "💔 Rating Mínimo", "🎭 Géneros Únicos", "🎬 Máx. Géneros por Película"])

with kpi_tabs[0]:
    fig = px.bar(x=["Películas"], y=[df.shape[0]],
                 title="Total de Películas", text=[df.shape[0]],
                 color_discrete_sequence=["#4C78A8"])
    fig.update_layout(yaxis_title="Cantidad", xaxis_title=None, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

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

with kpi_tabs[2]:
    top_year = df["Year"].value_counts().idxmax()
    count = df["Year"].value_counts().max()
    fig = px.bar(x=[top_year], y=[count], text=[count],
                 title="Año con más Películas", labels={"x": "Año", "y": "Cantidad"},
                 color_discrete_sequence=["#F58518"])
    st.plotly_chart(fig, use_container_width=True)

with kpi_tabs[3]:
    oldest = int(df["Year"].min())
    st.markdown(f"## 🎞️ Año más antiguo: `{oldest}`")

with kpi_tabs[4]:
    latest = int(df["Year"].max())
    st.markdown(f"## 📆 Año más reciente: `{latest}`")

with kpi_tabs[5]:
    max_rating = df["Rating"].max()
    st.markdown(f"## 🏆 Calificación más alta: `{max_rating}`")

with kpi_tabs[6]:
    min_rating = df["Rating"].min()
    st.markdown(f"## 💔 Calificación más baja: `{min_rating}`")

with kpi_tabs[7]:
    num_genres = df['Main_Genre'].nunique()
    st.markdown(f"## 🎭 Géneros únicos: `{num_genres}`")

with kpi_tabs[8]:
    max_genres = df["Genre_Count"].max()
    st.markdown(f"## 🎬 Máx. géneros por película: `{max_genres}`")

# ===============================
# NUEVOS KPIs: CLASIFICACIÓN, DIRECTORES, ESTRELLAS
# ===============================
st.subheader("📽️ Indicadores Visuales por Clasificación, Directores y Estrellas")

kpi2_tabs = st.tabs(["🎫 Clasificación", "🎬 Directores Top", "⭐ Estrellas Frecuentes"])

# Clasificación
with kpi2_tabs[0]:
    if "Certificate" in df.columns:
        cert_data = df["Certificate"].dropna().value_counts().reset_index()
        cert_data.columns = ["Clasificación", "Cantidad"]
        fig_cert = px.bar(cert_data, x="Clasificación", y="Cantidad",
                          color="Clasificación", title="Películas por Clasificación",
                          color_discrete_sequence=px.colors.qualitative.Plotly)
        st.plotly_chart(fig_cert, use_container_width=True)
    else:
        st.warning("No se encontró la columna 'Certificate'.")

# Directores
with kpi2_tabs[1]:
    if "Director" in df.columns:
        top_directors = df["Director"].dropna().value_counts().head(10).reset_index()
        top_directors.columns = ["Director", "Cantidad"]
        fig_dir = px.bar(top_directors, x="Cantidad", y="Director",
                         orientation='h', title="Top 10 Directores con Más Películas",
                         color="Cantidad", color_continuous_scale="Blues")
        fig_dir.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_dir, use_container_width=True)
    else:
        st.warning("No se encontró la columna 'Director'.")

# Estrellas
with kpi2_tabs[2]:
    star_cols = ["Star1", "Star2", "Star3", "Star4"]
    stars = pd.Series(dtype=str)

    for col in star_cols:
        if col in df.columns:
            stars = pd.concat([stars, df[col].dropna()])

    top_stars = stars.value_counts().head(10).reset_index()
    top_stars.columns = ["Estrella", "Apariciones"]
    fig_star = px.bar(top_stars, x="Apariciones", y="Estrella",
                      orientation='h', title="⭐ Top 10 Estrellas más Frecuentes",
                      color="Apariciones", color_continuous_scale="Oranges")
    fig_star.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_star, use_container_width=True)

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
