import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------
# Configuración y contrato de datos
# ---------------------------------------------------

st.set_page_config(
    page_title="Análisis nutricional de bebidas de Starbucks",
    page_icon="☕",
    layout="wide",
)

# Mapeo de datos

RUTA_ARCHIVO_CSV = "./starbucks.csv"

# Columnas esperadas en el archivo CSV.
# Si el archivo CSV no contiene estas columnas,
# se generará un error al intentar cargar los datos.
COLUMNAS_ESPERADAS = [
    "Beverage_Category",
    "Beverage",
    "Beverage_Prep",
    "Calories",
    "Total_Fat_(g)",
    "Trans_Fat_(g)",
    "Saturated_Fat_(g)",
    "Sodium_(mg)",
    "Total_Carbohydrates_(g)",
    "Cholesterol_(mg)",
    "Dietary_Fibre_(g)",
    "Sugars_(g)",
    "Protein_(g)",
    "Vitamin_A_(% DV)",
    "Vitamin_C_(% DV)",
    "Calcium_(% DV)",
    "Iron_(% DV)",
    "Caffeine_(mg)",
]

# Columnas de tipo texto en el archivo CSV.
COLUMNAS_TEXTO = [
    "Beverage_Category",
    "Beverage",
    "Beverage_Prep",
]

# Columnas de tipo numérico en el archivo CSV.
COLUMNAS_NUMERICAS = [
    "Calories",
    "Total_Fat_(g)",
    "Trans_Fat_(g)",
    "Saturated_Fat_(g)",
    "Sodium_(mg)",
    "Total_Carbohydrates_(g)",
    "Cholesterol_(mg)",
    "Dietary_Fibre_(g)",
    "Sugars_(g)",
    "Protein_(g)",
    "Vitamin_A_(% DV)",
    "Vitamin_C_(% DV)",
    "Calcium_(% DV)",
    "Iron_(% DV)",
    "Caffeine_(mg)",
]

# Columnas de tipo texto que representan porcentajes.
# Deberán ser transformadas en números antes de realizar cálculos.
COLUMNAS_PORCENTUALES = [
    "Vitamin_A_(% DV)",
    "Vitamin_C_(% DV)",
    "Calcium_(% DV)",
    "Iron_(% DV)",
    "Caffeine_(mg)",
]

# Nombres de visualización para las columnas del archivo CSV.
DISPLAY_NAMES = {
    "Beverage_Category": "Categoría de bebida",
    "Beverage": "Bebida",
    "Beverage_Prep": "Preparación",
    "Calories": "Calorías (kcal)",
    "Total_Fat_(g)": "Grasa total (g)",
    "Trans_Fat_(g)": "Grasa trans (g)",
    "Saturated_Fat_(g)": "Grasa saturada (g)",
    "Sodium_(mg)": "Sodio (mg)",
    "Total_Carbohydrates_(g)": "Carbohidratos (g)",
    "Cholesterol_(mg)": "Colesterol (mg)",
    "Dietary_Fibre_(g)": "Fibra (g)",
    "Sugars_(g)": "Azúcares (g)",
    "Protein_(g)": "Proteína (g)",
    "Vitamin_A_(% DV)": "Vitamina A (% DV)",
    "Vitamin_C_(% DV)": "Vitamina C (% DV)",
    "Calcium_(% DV)": "Calcio (% DV)",
    "Iron_(% DV)": "Hierro (% DV)",
    "Caffeine_(mg)": "Cafeína (mg)",
}

# ---------------------------------------------------
# ETL
# ---------------------------------------------------

df = pd.read_csv(RUTA_ARCHIVO_CSV)

# Validación #1:
# ¿Todas las columnas esperadas están presentes en el archivo CSV?

columnas_faltantes = [col for col in COLUMNAS_ESPERADAS if col not in df.columns]
if columnas_faltantes:
    st.error(
        f"Faltan las siguientes columnas en el archivo CSV: {', '.join(columnas_faltantes)}"
    )
    st.stop()  # Detener la ejecución si faltan columnas.


# Validación #2:
# ¿Todas las columnas numéricas contienen valores válidos (números)?

# for col in COLUMNAS_NUMERICAS:
#     if not pd.api.types.is_numeric_dtype(df[col]):
#         st.warning(f"La columna '{col}' debe contener solo valores numéricos.")

# Transformación 1:
# Convertir las columnas porcentuales a valores numéricos.

for col in COLUMNAS_PORCENTUALES:
    df[col] = df[col].str.replace("%", "")

# Transformación 2:
# Convertir las columnas numéricas en valores válidos (números).

for col in COLUMNAS_NUMERICAS:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Transformación 3:
# Ajustar porcentajes a valores decimales.

for col in COLUMNAS_PORCENTUALES:
    df[col] = pd.to_numeric(df[col], errors="coerce") / 100


# Transformación 4:
# Eliminar espacios al principio y final de los valores en las columnas
# de texto.

for col in COLUMNAS_TEXTO:
    df[col] = df[col].str.strip()


# Creación de columnas adicionales para el análisis

# Perfil calórico y distribución de macronutrientes
df["Cal_Fat"] = df["Total_Fat_(g)"] * 9
df["Cal_Carb"] = df["Total_Carbohydrates_(g)"] * 4
df["Cal_Protein"] = df["Protein_(g)"] * 4
df["Pct_Cal_Fat"] = (df["Cal_Fat"] / df["Calories"]) * 100
df["Pct_Cal_Carb"] = (df["Cal_Carb"] / df["Calories"]) * 100
df["Pct_Cal_Protein"] = (df["Cal_Protein"] / df["Calories"]) * 100

# Densidad de azúcares libres vs. carga calórica total
df["Cal_From_Sugar"] = df["Sugars_(g)"] * 4
df["Sugar_Cal_Ratio"] = (df["Cal_From_Sugar"] / df["Calories"]) * 100

# Impacto de la preparación en la modificación nutricional
df["Delta_Calories"] = df.groupby("Beverage")["Calories"].transform(
    lambda x: x - x.min()
)

# Relación nutrimental: densidad de calcio y hierro vs. densidad energética
df["Nutrient_Density_Index"] = (df["Calcium_(% DV)"] + df["Iron_(% DV)"]) / (df["Calories"] / 100)

# Distribución y exposición a la cafeína por categoría de bebida
ALTA_CAFEINA = 150
df["High_Caffeine"] = df["Caffeine_(mg)"] > ALTA_CAFEINA


# ---------------------------------------------------
# Visualización de los datos procesados
# ---------------------------------------------------

st.title("Análisis nutricional de bebidas de Starbucks")

tab_perfil_calorico, tab_densidad_azucar, tab_impacto_preparacion, tab_relacion_nutrimental, tab_cafeina, tab_datos = st.tabs(
    ["Perfil Calórico", "Densidad de Azúcar", "Impacto de Preparación", "Relación Nutrimental", "Cafeína", "Datos"]
)

with tab_perfil_calorico:
    st.subheader("Perfil Calórico")

    # Agrupar bebidas por categoría y calcular el promedio de calorías y macronutrientes
    df_perfil_calorico = df.groupby("Beverage").agg(
        Calories=("Calories", "mean"),
        Total_Fat=("Total_Fat_(g)", "mean"),
        Total_Carbohydrates=("Total_Carbohydrates_(g)", "mean"),
        Protein=("Protein_(g)", "mean")
    ).reset_index()
    st.dataframe(df_perfil_calorico)

    fig = px.bar(
        df_perfil_calorico,
        x=["Total_Fat", "Total_Carbohydrates", "Protein"],
        y="Beverage",
        title="Distribución de Macronutrientes por Bebida",
        labels={"value": "Gramos", "variable": "Macronutriente"},
        barmode="stack",
    )
    st.plotly_chart(fig)


with tab_datos:
    st.dataframe(df)