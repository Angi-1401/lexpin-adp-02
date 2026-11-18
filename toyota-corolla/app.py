import pandas as pd
import plotly.express as px
import streamlit as st

from generic_etl import *

# -----------------------------------------------
# 1. CONFIGURACIÓN
# ------------------------------------------------

st.set_page_config(page_title="Dasboard Toyota Corolla", page_icon="🚗", layout="wide")

st.title("Dasboard Toyota Corolla")
st.subheader("Análisis exploratorio")

# -----------------------------------------------
# 2. CARGA DE DATOS
# ------------------------------------------------

data = leer_csv("./ToyotaCorolla.csv")

# -----------------------------------------------
# 3. PROCESO ETL
# ------------------------------------------------


COLUMNAS_TEXTO = ["model", "fuel_type", "color"]
COLUMNAS_NUMERICAS = [
    "price",
    "km",
    "age_08_04",
    "hp",
    "cc",
    "weight",
    "mfg_month",
    "mfg_year",
]
COLUMNAS_OBLIGATORIAS = COLUMNAS_TEXTO + COLUMNAS_NUMERICAS

df = data.copy()

# Validar columnas obligatorias
columnas_faltantes = validar_columnas(df, COLUMNAS_OBLIGATORIAS)

# Normalizar datos
df = limpiar_nombres_columnas(df)
df = estandarizar_nulos(df)
df = limpiar_espacios_texto(df)
df = normalizar_texto(df, COLUMNAS_TEXTO)

# Estandarizar tipos de datos
df = convertir_numericos(df, COLUMNAS_NUMERICAS)

# Crear columna antiguedad
df["mfg_date"] = pd.to_datetime(
    dict(year=df["mfg_year"], month=df["mfg_month"], day=1), errors="coerce"
)

# -----------------------------------------------
# 4. DEFINICIÓN DE FILTROS
# ------------------------------------------------

if len(columnas_faltantes) > 0:
    st.error("Faltan columnas obligatorias")
    st.dataframe(columnas_faltantes)
    st.stop

st.sidebar.title("Filtros")

modelos = sorted(df["model"].unique())
modelo_seleccionado = st.sidebar.multiselect("Modelo", modelos, default=modelos)

combustibles = sorted(df["fuel_type"].unique())
combustible_seleccionado = st.sidebar.multiselect(
    "Combustible", combustibles, default=combustibles
)

precio_min = int(df["price"].min())
precio_max = int(df["price"].max())
precio_rango = st.sidebar.slider(
    "Precio", precio_min, precio_max, (precio_min, precio_max)
)

km_min = int(df["km"].min())
km_max = int(df["km"].max())
km_rango = st.sidebar.slider("Kilometraje", km_min, km_max, (km_min, km_max))

# -----------------------------------------------
# 5. APLICACIÓN DE FILTROS
# ------------------------------------------------

if modelo_seleccionado:
    df = df[df["model"].isin(modelo_seleccionado)]

if combustible_seleccionado:
    df = df[df["fuel_type"].isin(combustible_seleccionado)]

df = df[df["price"].between(precio_rango[0], precio_rango[1])]

df = df[df["km"].between(km_rango[0], km_rango[1])]

if df.empty:
    st.warning("No se encontraron registros con los filtros aplicados")
    st.stop()

# -----------------------------------------------
# 6. INDICADORES KPI
# ------------------------------------------------

st.subheader("Indicadores KPI")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Vehículos", f"{len(df):,}")
col2.metric("Precio promedio", f"{df['price'].mean():,.2f}")
col3.metric("Precio mediano", f"{df['price'].median():,.2f}")
col4.metric("Kilometraje promedio", f"{df['km'].mean():,.2f}")
col5.metric("Antiguedad promedio", f"{df['age_08_04'].mean():,.2f} meses")

st.divider()

# -----------------------------------------------
# 7. VISUALIZACIONES
# ------------------------------------------------

st.subheader("Análisis Visual")

col1, col2 = st.columns(2)

with col1:
    fig_precio = px.histogram(
        df,
        x="price",
        nbins=30,  # Número de bins para el histograma
        title="Distribución de Precios",
        labels={"price": "Precio", "count": "Cantidad"},
        template="plotly_white",
    )
    st.plotly_chart(fig_precio)

with col2:
    fig_km = px.scatter(
        df,
        x="km",
        y="price",
        color="fuel_type",
        title="Kilometraje vs Precio",
        hover_data=["model", "age_08_04", "hp"],
        labels={"km": "Kilometraje", "price": "Precio", "fuel_type": "Combustible"},
        template="plotly_white",
    )
    st.plotly_chart(fig_km)
