"""
TABLERO NUTRICIONAL DE BEBIDAS DE STARBUCKS
===========================================

Tablero interactivo hecho con Streamlit y Plotly. Permite explorar las calorías,
el azúcar, la cafeína y los macronutrientes de las bebidas del archivo
`starbucks.csv`.

Cómo ejecutarlo (desde esta carpeta):
    pip install -r requirements.txt
    streamlit run app.py

Organización del archivo:
    1. Configuración  -> constantes que se pueden ajustar sin saber programar.
    2. ETL            -> lectura, limpieza y transformación de los datos
                         (usa las funciones genéricas de `etl.py`).
    3. Filtros        -> barra lateral donde la persona elige qué ver.
    4. Visualización  -> indicadores, gráficos y tabla de datos.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from etl import (
    convertir_numericos,
    convertir_porcentajes,
    eliminar_duplicados,
    eliminar_filas_vacias,
    estandarizar_nulos,
    leer_csv,
    limpiar_espacios_texto,
    quitar_caracteres,
    resumen_dataframe,
    validar_columnas,
)

# ---------------------------------------------------------------------------
# 1. CONFIGURACIÓN
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Bebidas de Starbucks",
    page_icon="☕",
    layout="wide",
)

RUTA_ARCHIVO_CSV = "starbucks.csv"

# Columnas que debe traer el archivo. Si falta alguna, el tablero se detiene
# y muestra un mensaje claro en lugar de un error técnico.
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

COLUMNAS_TEXTO = ["Beverage_Category", "Beverage", "Beverage_Prep"]

# Columnas con números normales (gramos, miligramos, calorías).
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
    "Caffeine_(mg)",
]

# Columnas escritas como porcentaje ("20%"). Se convierten a número: 20.
# "% DV" = porcentaje del valor diario recomendado.
COLUMNAS_PORCENTUALES = [
    "Vitamin_A_(% DV)",
    "Vitamin_C_(% DV)",
    "Calcium_(% DV)",
    "Iron_(% DV)",
]

# Nombres en español que se muestran en pantalla.
NOMBRES = {
    "Beverage_Category": "Categoría",
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
    "Vitamin_A_(% DV)": "Vitamina A (% VD)",
    "Vitamin_C_(% DV)": "Vitamina C (% VD)",
    "Calcium_(% DV)": "Calcio (% VD)",
    "Iron_(% DV)": "Hierro (% VD)",
    "Caffeine_(mg)": "Cafeína (mg)",
    "Pct_Cal_Fat": "Grasa",
    "Pct_Cal_Carb": "Carbohidratos",
    "Pct_Cal_Protein": "Proteína",
}

# Umbral a partir del cual consideramos que una bebida tiene "mucha" cafeína.
ALTA_CAFEINA_MG = 150

# Colores de los gráficos (paleta probada para personas con daltonismo).
COLOR_PRINCIPAL = "#2a78d6"  # azul: se usa cuando el gráfico tiene una sola serie
COLORES_MACROS = {
    "Grasa": "#eb6834",  # naranja
    "Carbohidratos": "#2a78d6",  # azul
    "Proteína": "#1baf7a",  # verde agua
}


# ---------------------------------------------------------------------------
# 2. ETL: EXTRACCIÓN, TRANSFORMACIÓN Y CARGA
# ---------------------------------------------------------------------------


@st.cache_data  # Guarda el resultado en memoria para no reprocesar en cada clic.
def cargar_datos(ruta: str) -> pd.DataFrame:
    """Lee el CSV, lo limpia y agrega columnas calculadas para el análisis."""

    # --- Extracción ---------------------------------------------------------
    # Se lee todo como texto para limpiar con calma antes de convertir.
    df = leer_csv(ruta, sep=",", dtype=str)

    # Validación: ¿están todas las columnas esperadas?
    faltantes = validar_columnas(df, COLUMNAS_ESPERADAS)
    if faltantes:
        st.error(f"Faltan estas columnas en el archivo CSV: {', '.join(faltantes)}")
        st.stop()

    # --- Limpieza -----------------------------------------------------------
    df = eliminar_filas_vacias(df)
    df = limpiar_espacios_texto(df)  # quita espacios sobrantes en el texto

    # Un valor de grasa aparece como "3 2" en lugar de "3.2".
    # Se reemplaza el espacio entre dos dígitos por un punto decimal.
    df = quitar_caracteres(df, ["Total_Fat_(g)"], r"(\d)\s+(\d)", r"\1.\2")

    # La cafeína a veces dice "Varies" (varía). No es un número, así que se
    # marca como dato faltante en lugar de inventar un valor.
    df = estandarizar_nulos(df, ["varies"], columnas=["Caffeine_(mg)"])

    # --- Conversión de tipos ------------------------------------------------
    # El archivo usa punto decimal (3.5) y no usa separador de miles.
    df = convertir_numericos(df, COLUMNAS_NUMERICAS, decimal=".", miles="")
    df = convertir_porcentajes(df, COLUMNAS_PORCENTUALES, decimal=".", miles="")

    df = eliminar_duplicados(df)

    # --- Columnas calculadas ------------------------------------------------
    # Cada gramo de grasa aporta 9 kcal; carbohidratos y proteína aportan 4.
    cal_grasa = df["Total_Fat_(g)"] * 9
    cal_carb = df["Total_Carbohydrates_(g)"] * 4
    cal_prot = df["Protein_(g)"] * 4
    total = (cal_grasa + cal_carb + cal_prot).where(lambda s: s > 0)
    df["Pct_Cal_Fat"] = cal_grasa / total * 100
    df["Pct_Cal_Carb"] = cal_carb / total * 100
    df["Pct_Cal_Protein"] = cal_prot / total * 100

    # Porcentaje de las calorías que viene del azúcar.
    df["Pct_Cal_Azucar"] = (
        df["Sugars_(g)"] * 4 / df["Calories"].where(lambda s: s > 0)
    ) * 100

    # Las preparaciones se repiten dentro de una bebida (por ejemplo, "2% Milk"
    # aparece en varios tamaños). Se numeran para poder distinguirlas.
    df["Opcion"] = df.groupby("Beverage").cumcount() + 1

    return df


df = cargar_datos(RUTA_ARCHIVO_CSV)


# ---------------------------------------------------------------------------
# 3. FILTROS (barra lateral)
# ---------------------------------------------------------------------------

st.sidebar.header("Filtros")
st.sidebar.caption(
    "Elige qué bebidas quieres analizar. Todos los gráficos se actualizan solos."
)

categorias = sorted(df["Beverage_Category"].dropna().unique())
categorias_elegidas = st.sidebar.multiselect(
    "Categorías de bebida",
    options=categorias,
    default=categorias,
    help="Borra o agrega categorías para comparar solo las que te interesan.",
)

cal_min, cal_max = int(df["Calories"].min()), int(df["Calories"].max())
rango_calorias = st.sidebar.slider(
    "Rango de calorías (kcal)",
    min_value=cal_min,
    max_value=cal_max,
    value=(cal_min, cal_max),
    step=10,
)

datos = df.loc[
    df["Beverage_Category"].isin(categorias_elegidas)
    & df["Calories"].between(*rango_calorias)
]

if datos.empty:
    st.warning(
        "No hay bebidas con esos filtros. Prueba a ampliar el rango o agregar categorías."
    )
    st.stop()


# ---------------------------------------------------------------------------
# 4. VISUALIZACIÓN
# ---------------------------------------------------------------------------


def estilo(fig, alto=450):
    """Aplica un estilo sencillo y uniforme a todos los gráficos."""
    fig.update_layout(
        height=alto,
        margin=dict(l=10, r=10, t=40, b=10),
        legend_title_text="",
        hoverlabel=dict(font_size=13),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    fig.update_yaxes(showgrid=False)
    return fig


st.title("☕ ¿Qué tiene tu bebida de Starbucks?")
st.markdown(
    "Explora las **calorías**, el **azúcar** y la **cafeína** de "
    f"{df['Beverage'].nunique()} bebidas en sus distintos tamaños y tipos de leche."
)

with st.expander("ℹ️ ¿Cómo usar este tablero?"):
    st.markdown("""
        1. Usa los **filtros de la izquierda** para elegir categorías o un rango de calorías.
        2. Recorre las **pestañas** de abajo; cada una responde una pregunta.
        3. Pasa el cursor sobre un gráfico para ver los valores exactos.
           Puedes hacer zoom arrastrando y volver a la vista original con doble clic.
        4. En la pestaña **Datos** puedes ver la tabla completa y descargarla.

        **Glosario rápido**
        - **kcal**: kilocalorías, la energía que aporta la bebida.
        - **% VD**: porcentaje del valor diario recomendado de un nutriente.
        - **Short / Tall / Grande / Venti**: tamaños, de menor a mayor.
        """)

# --- Indicadores principales ------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Bebidas mostradas",
    f"{len(datos)}",
    help="Cada combinación de bebida y preparación cuenta como una.",
)
col2.metric("Calorías promedio", f"{datos['Calories'].mean():.0f} kcal")
col3.metric("Azúcar promedio", f"{datos['Sugars_(g)'].mean():.0f} g")
col4.metric(
    "Cafeína promedio",
    f"{datos['Caffeine_(mg)'].mean():.0f} mg",
    help="No incluye bebidas cuya cafeína 'varía' según el té elegido.",
)

tab_cal, tab_azucar, tab_cafeina, tab_comparar, tab_datos = st.tabs(
    ["🔥 Calorías", "🍬 Azúcar", "⚡ Cafeína", "🔍 Comparar preparaciones", "📋 Datos"]
)

# --- Pestaña: Calorías --------------------------------------------------------
with tab_cal:
    st.subheader("¿Qué categorías tienen más calorías?")

    por_categoria = (
        datos.groupby("Beverage_Category", as_index=False)
        .agg(
            Calories=("Calories", "mean"),
            Pct_Cal_Fat=("Pct_Cal_Fat", "mean"),
            Pct_Cal_Carb=("Pct_Cal_Carb", "mean"),
            Pct_Cal_Protein=("Pct_Cal_Protein", "mean"),
        )
        .sort_values(by="Calories")  # type: ignore
    )

    fig = px.bar(
        por_categoria,
        x="Calories",
        y="Beverage_Category",
        orientation="h",
        text_auto=True,
        labels=NOMBRES,
        color_discrete_sequence=[COLOR_PRINCIPAL],
    )
    fig.update_traces(hovertemplate="%{y}<br>%{x:.0f} kcal promedio<extra></extra>")
    st.plotly_chart(estilo(fig), width="stretch")
    st.caption(
        "Promedio de calorías por categoría, considerando todos los tamaños y tipos de leche."
    )

    st.subheader("¿De dónde vienen esas calorías?")
    macros = por_categoria.melt(
        id_vars="Beverage_Category",
        value_vars=["Pct_Cal_Carb", "Pct_Cal_Fat", "Pct_Cal_Protein"],
        var_name="Macronutriente",
        value_name="Porcentaje",
    )
    macros["Macronutriente"] = macros["Macronutriente"].map(NOMBRES)

    fig = px.bar(
        macros,
        x="Porcentaje",
        y="Beverage_Category",
        color="Macronutriente",
        orientation="h",
        labels=NOMBRES,
        color_discrete_map=COLORES_MACROS,
        category_orders={"Beverage_Category": list(por_categoria["Beverage_Category"])},
    )
    fig.update_traces(
        hovertemplate="%{y}<br>%{x:.0f}% de las calorías<extra>%{fullData.name}</extra>"
    )
    fig.update_layout(barmode="stack", bargap=0.3, legend=dict(orientation="h", y=1.08))
    fig.update_xaxes(range=[0, 100], ticksuffix="%", title="% de las calorías")
    st.plotly_chart(estilo(fig), width="stretch")
    st.caption(
        "Reparto de las calorías entre carbohidratos, grasa y proteína. "
        "En casi todas las categorías, la mayor parte viene de los carbohidratos (principalmente azúcar)."
    )

# --- Pestaña: Azúcar ----------------------------------------------------------
with tab_azucar:
    st.subheader("¿Más calorías significa más azúcar?")

    fig = px.scatter(
        datos,
        x="Calories",
        y="Sugars_(g)",
        hover_name="Beverage",
        hover_data={"Beverage_Prep": True, "Beverage_Category": True},
        labels=NOMBRES,
        color_discrete_sequence=[COLOR_PRINCIPAL],
        opacity=0.7,
    )
    fig.update_traces(marker=dict(size=9, line=dict(width=1, color="white")))
    st.plotly_chart(estilo(fig), width="stretch")
    st.caption(
        "Cada punto es una bebida. Mientras más arriba a la derecha, más calorías y más azúcar tiene."
    )

    st.subheader("Las 10 bebidas con más azúcar")
    top_azucar = datos.nlargest(10, "Sugars_(g)").sort_values("Sugars_(g)")  # type: ignore
    top_azucar = top_azucar.assign(
        Etiqueta=top_azucar["Beverage"] + " · " + top_azucar["Beverage_Prep"]
    )
    fig = px.bar(
        top_azucar,
        x="Sugars_(g)",
        y="Etiqueta",
        orientation="h",
        text_auto=True,
        labels={**NOMBRES, "Etiqueta": ""},
        color_discrete_sequence=[COLOR_PRINCIPAL],
    )
    fig.update_traces(hovertemplate="%{y}<br>%{x:.0f} g de azúcar<extra></extra>")
    st.plotly_chart(estilo(fig), width="stretch")
    st.caption(
        "Como referencia, la OMS recomienda no superar unos 50 g de azúcares libres al día."
    )

# --- Pestaña: Cafeína ---------------------------------------------------------
with tab_cafeina:
    st.subheader("¿Cuánta cafeína tiene cada categoría?")

    con_cafeina = datos.dropna(subset=["Caffeine_(mg)"])  # type: ignore
    fig = px.box(
        con_cafeina,
        x="Caffeine_(mg)",
        y="Beverage_Category",
        points="all",
        hover_name="Beverage",
        hover_data={"Beverage_Prep": True},
        labels=NOMBRES,
        color_discrete_sequence=[COLOR_PRINCIPAL],
    )
    fig.add_vline(
        x=ALTA_CAFEINA_MG,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"{ALTA_CAFEINA_MG} mg",
        annotation_position="top",
    )
    st.plotly_chart(estilo(fig, alto=500), width="stretch")
    st.caption(
        "Cada punto es una bebida; la caja muestra dónde se concentra la mitad de ellas. "
        f"La línea punteada marca {ALTA_CAFEINA_MG} mg, a partir de la cual consideramos que hay mucha cafeína."
    )

    altas = (con_cafeina["Caffeine_(mg)"] > ALTA_CAFEINA_MG).sum()
    sin_dato = datos["Caffeine_(mg)"].isna().sum()
    st.info(
        f"**{altas}** de {len(con_cafeina)} bebidas superan los {ALTA_CAFEINA_MG} mg de cafeína."
        + (
            f" Otras {sin_dato} no tienen un valor fijo (su cafeína 'varía')."
            if sin_dato
            else ""
        )
    )

# --- Pestaña: Comparar preparaciones -----------------------------------------
with tab_comparar:
    st.subheader("¿Cómo cambia una bebida según el tamaño y la leche?")

    bebida = st.selectbox("Elige una bebida", sorted(datos["Beverage"].unique()))
    nutriente = st.radio(
        "¿Qué quieres comparar?",
        ["Calories", "Sugars_(g)", "Total_Fat_(g)", "Protein_(g)", "Caffeine_(mg)"],
        format_func=NOMBRES.get,
        horizontal=True,
    )

    una_bebida = datos[datos["Beverage"] == bebida].copy()
    # Etiqueta única por fila: las preparaciones repetidas llevan su número de opción.
    repetidas = una_bebida["Beverage_Prep"].duplicated(keep=False)
    una_bebida["Etiqueta"] = una_bebida["Beverage_Prep"].where(
        ~repetidas,
        una_bebida["Beverage_Prep"]
        + " (opción "
        + una_bebida["Opcion"].astype(str)
        + ")",
    )

    fig = px.bar(
        una_bebida,
        x="Etiqueta",
        y=nutriente,
        text_auto=True,
        labels={**NOMBRES, "Etiqueta": "Preparación"},
        color_discrete_sequence=[COLOR_PRINCIPAL],
    )
    fig.update_traces(hovertemplate="%{x}<br>%{y}<extra></extra>")
    fig = estilo(fig)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Las preparaciones aparecen en el orden del menú: de tamaño menor (Short) a mayor (Venti). "
        "Cuando una preparación se repite, corresponde a un tamaño más grande."
    )

    minimo, maximo = una_bebida[nutriente].min(), una_bebida[nutriente].max()
    if pd.notna(minimo) and maximo > minimo:
        st.success(
            f"Elegir la opción más ligera en lugar de la más pesada ahorra **{maximo - minimo:.0f}** "
            f"{NOMBRES[nutriente].split('(')[-1].rstrip(')')} de {NOMBRES[nutriente].split(' (')[0].lower()}."
        )

# --- Pestaña: Datos -----------------------------------------------------------
with tab_datos:
    st.subheader("Tabla de datos")
    columnas_tabla = list(NOMBRES)[:18]  # solo las columnas originales, ya limpias
    tabla = datos[columnas_tabla].rename(columns=NOMBRES)  # type: ignore
    st.dataframe(tabla, width="stretch", hide_index=True)

    st.download_button(
        "⬇️ Descargar estos datos (CSV)",
        data=tabla.to_csv(index=False).encode("utf-8-sig"),
        file_name="starbucks_filtrado.csv",
        mime="text/csv",
    )

    with st.expander("🧹 ¿Qué limpieza se hizo a los datos?"):
        st.markdown("""
            - **Valores con errores de escritura:** `"3 2"` se interpretó como `3.2` gramos de grasa.
            - **Cafeína "Varies":** se dejó como dato faltante porque depende del té elegido.
            - **Porcentajes:** `"20%"` se convirtió en el número `20`.
            - Se quitaron espacios sobrantes y filas duplicadas o vacías.
            """)
        st.markdown(
            "**Resumen técnico de las columnas** (tipo de dato y valores faltantes):"
        )
        st.dataframe(
            resumen_dataframe(df[columnas_tabla].rename(columns=NOMBRES)),  # type: ignore
            width="stretch",
        )
