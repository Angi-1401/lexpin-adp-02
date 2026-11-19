"""
TABLERO DE PRECIOS DE TOYOTA COROLLA USADOS
===========================================

Tablero interactivo hecho con Streamlit y Plotly. Permite explorar cómo cambia el
precio de un Toyota Corolla usado según su antigüedad, kilometraje, motor,
combustible, carrocería y equipamiento, a partir del archivo `totyota_corolla.csv`.

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

import re

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from etl import (
    combinar_columnas,
    convertir_booleanos,
    convertir_fechas_texto,
    convertir_numericos,
    eliminar_duplicados,
    eliminar_filas_vacias,
    estandarizar_nulos,
    leer_csv,
    limpiar_espacios_texto,
    quitar_caracteres,
    reporte_duplicados,
    resumen_dataframe,
    validar_columnas,
    validar_rango_numerico,
)

# ---------------------------------------------------------------------------
# 1. CONFIGURACIÓN
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Toyota Corolla usados",
    page_icon="🚗",
    layout="wide",
)

RUTA_ARCHIVO_CSV = "totyota_corolla.csv"

COLUMNAS_TEXTO = ["model", "fuel_type", "color"]

# Columnas con números normales (euros, meses, km, etc.).
COLUMNAS_NUMERICAS = [
    "price",
    "age_08_04",
    "mfg_month",
    "mfg_year",
    "km",
    "hp",
    "cc",
    "doors",
    "cylinders",
    "gears",
    "quarterly_tax",
    "weight",
    "guarantee_period",
]

# Columnas que valen 1 (sí tiene) o 0 (no tiene). Se convierten a Verdadero/Falso.
COLUMNAS_SI_NO = [
    "met_color",
    "automatic",
    "mfr_guarantee",
    "bovag_guarantee",
]

# Equipamiento del auto: también son columnas de sí/no.
COLUMNAS_EQUIPAMIENTO = [
    "abs",
    "airbag_1",
    "airbag_2",
    "airco",
    "automatic_airco",
    "boardcomputer",
    "cd_player",
    "central_lock",
    "powered_windows",
    "power_steering",
    "radio",
    "mistlamps",
    "sport_model",
    "backseat_divider",
    "metallic_rim",
    "radio_cassette",
    "parking_assistant",
    "tow_bar",
]

# Columnas que debe traer el archivo. Si falta alguna, el tablero se detiene
# y muestra un mensaje claro en lugar de un error técnico.
COLUMNAS_ESPERADAS = (
    COLUMNAS_TEXTO + COLUMNAS_NUMERICAS + COLUMNAS_SI_NO + COLUMNAS_EQUIPAMIENTO
)

# Nombres en español que se muestran en pantalla.
NOMBRES = {
    "model": "Modelo",
    "price": "Precio (€)",
    "age_08_04": "Antigüedad (meses)",
    "mfg_month": "Mes de fabricación",
    "mfg_year": "Año de fabricación",
    "km": "Kilometraje (km)",
    "fuel_type": "Combustible",
    "hp": "Potencia (hp)",
    "met_color": "Pintura metalizada",
    "color": "Color",
    "automatic": "Automático",
    "cc": "Cilindrada (cc)",
    "doors": "Puertas",
    "cylinders": "Cilindros",
    "gears": "Marchas",
    "quarterly_tax": "Impuesto trimestral (€)",
    "weight": "Peso (kg)",
    "mfr_guarantee": "Garantía de fábrica",
    "bovag_guarantee": "Garantía BOVAG",
    "guarantee_period": "Garantía (meses)",
    "abs": "Frenos ABS",
    "airbag_1": "Airbag conductor",
    "airbag_2": "Airbag pasajero",
    "airco": "Aire acondicionado",
    "automatic_airco": "Climatizador automático",
    "boardcomputer": "Computadora de a bordo",
    "cd_player": "Reproductor de CD",
    "central_lock": "Cierre centralizado",
    "powered_windows": "Vidrios eléctricos",
    "power_steering": "Dirección asistida",
    "radio": "Radio",
    "mistlamps": "Faros antiniebla",
    "sport_model": "Versión deportiva",
    "backseat_divider": "Asiento trasero abatible",
    "metallic_rim": "Llantas de aleación",
    "radio_cassette": "Radio casete",
    "parking_assistant": "Asistente de estacionamiento",
    "tow_bar": "Enganche de remolque",
    # Columnas calculadas
    "Carroceria": "Carrocería",
    "Motor": "Motor",
    "Edad_Anios": "Antigüedad (años)",
    "Equipamiento_Total": "Equipamiento (n.º de extras)",
    "Fecha_Fabricacion": "Fecha de fabricación",
}

COMBUSTIBLES = {"Petrol": "Gasolina", "Diesel": "Diésel", "CNG": "Gas natural (GNC)"}

# Palabras del nombre del modelo que delatan el tipo de carrocería.
# Se revisan en este orden; la primera que coincide gana.
PATRONES_CARROCERIA = {
    "Monovolumen": r"VERSO|MPV",
    "Familiar (wagon)": r"WAGON|STATION|\bSW\b",
    "Sedán": r"SEDAN|\bSDN\b",
    "Liftback": r"LIFTB|\bLB\b",
    "Hatchback": r"HATCHB|\bHB\b|\b\dDR\b|\b\dD\b|\b\d-DRS\b",
}

# Margen para buscar autos "parecidos" en la pestaña de comparación.
MARGEN_EDAD_MESES = 6
MARGEN_KM = 20_000

# Colores de los gráficos (paleta probada para personas con daltonismo).
COLOR_PRINCIPAL = "#2a78d6"  # azul: se usa cuando el gráfico tiene una sola serie
COLORES_COMBUSTIBLE = {
    "Gasolina": "#2a78d6",  # azul
    "Diésel": "#eb6834",  # naranja
    "Gas natural (GNC)": "#1baf7a",  # verde agua
}


# ---------------------------------------------------------------------------
# 2. ETL: EXTRACCIÓN, TRANSFORMACIÓN Y CARGA
# ---------------------------------------------------------------------------


def detectar_carroceria(modelo: str, puertas: float) -> str:
    """Deduce la carrocería a partir del nombre del modelo."""
    if pd.isna(modelo):
        return "Sin especificar"
    texto = modelo.upper()
    for carroceria, patron in PATRONES_CARROCERIA.items():
        if re.search(patron, texto):
            return carroceria
    # Si el nombre no lo dice, un auto de 2 o 3 puertas es casi siempre hatchback.
    if puertas in (2, 3):
        return "Hatchback"
    return "Sin especificar"


@st.cache_data  # Guarda el resultado en memoria para no reprocesar en cada clic.
def cargar_datos(ruta: str) -> tuple[pd.DataFrame, dict]:
    """Lee el CSV, lo limpia y agrega columnas calculadas para el análisis.

    Devuelve los datos limpios y un pequeño registro de lo que se corrigió.
    """
    registro = {}

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
    df = estandarizar_nulos(df)  # "", "N/A", "null", "-"... pasan a dato faltante
    df = limpiar_espacios_texto(df)  # quita espacios sobrantes (hay dobles en "model")

    # Todos los autos son "TOYOTA Corolla": ese prefijo no aporta, se quita para
    # que los nombres sean más cortos y legibles en los gráficos.
    df = quitar_caracteres(df, ["model"], r"^TOYOTA\s+Corolla\s*", "")

    # Fecha de fabricación: se une año y mes ("2002-10") antes de convertir.
    df = combinar_columnas(
        df, ["mfg_year", "mfg_month"], "Fecha_Fabricacion", separador="-"
    )
    df = convertir_fechas_texto(df, ["Fecha_Fabricacion"], formato="%Y-%m")

    # --- Conversión de tipos ------------------------------------------------
    # El archivo usa punto decimal y no usa separador de miles.
    df = convertir_numericos(df, COLUMNAS_NUMERICAS, decimal=".", miles="")
    df = convertir_booleanos(df, COLUMNAS_SI_NO + COLUMNAS_EQUIPAMIENTO)

    # Un auto tiene 16000 cc de cilindrada: un Corolla tiene entre 1300 y 2000 cc,
    # así que es un cero de más al escribir 1600. Se corrige dividiendo entre 10.
    fuera_de_rango = validar_rango_numerico(df, "cc", minimo=1000, maximo=2500)
    corregibles = fuera_de_rango & (df["cc"] > 2500)
    registro["cc_corregidos"] = int(corregibles.sum())
    df.loc[corregibles, "cc"] = df.loc[corregibles, "cc"] / 10

    registro["duplicados"] = reporte_duplicados(df)["cantidad_filas_duplicadas"] // 2
    df = eliminar_duplicados(df)

    # Combustible en español.
    df["fuel_type"] = df["fuel_type"].map(COMBUSTIBLES).fillna(df["fuel_type"])

    # --- Columnas calculadas ------------------------------------------------
    # La antigüedad viene en meses (medida a agosto de 2004); en años se lee mejor.
    df["Edad_Anios"] = df["age_08_04"] / 12

    # Motor en litros, como se suele decir: 1600 cc -> "1.6 L".
    df["Motor"] = (df["cc"] / 1000).round(1).map(lambda x: f"{x:.1f} L")

    df["Carroceria"] = [
        detectar_carroceria(m, p) for m, p in zip(df["model"], df["doors"])
    ]

    # Cuántos extras de equipamiento trae cada auto.
    df["Equipamiento_Total"] = df[COLUMNAS_EQUIPAMIENTO].sum(axis=1).astype(int)

    return df, registro


df, registro_limpieza = cargar_datos(RUTA_ARCHIVO_CSV)


# ---------------------------------------------------------------------------
# 3. FILTROS (barra lateral)
# ---------------------------------------------------------------------------

st.sidebar.header("Filtros")
st.sidebar.caption(
    "Elige qué autos quieres analizar. Todos los gráficos se actualizan solos."
)

combustibles = [c for c in COLORES_COMBUSTIBLE if c in set(df["fuel_type"])]
combustibles_elegidos = st.sidebar.multiselect(
    "Combustible",
    options=combustibles,
    default=combustibles,
)

carrocerias = sorted(df["Carroceria"].unique())
carrocerias_elegidas = st.sidebar.multiselect(
    "Carrocería",
    options=carrocerias,
    default=carrocerias,
    help="Se dedujo del nombre del modelo (ver pestaña Datos).",
)

anio_min, anio_max = int(df["mfg_year"].min()), int(df["mfg_year"].max())
rango_anios = st.sidebar.slider(
    "Año de fabricación",
    min_value=anio_min,
    max_value=anio_max,
    value=(anio_min, anio_max),
)

precio_min, precio_max = int(df["price"].min()), int(df["price"].max())
rango_precio = st.sidebar.slider(
    "Rango de precio (€)",
    min_value=precio_min,
    max_value=precio_max,
    value=(precio_min, precio_max),
    step=250,
)

datos = df.loc[
    df["fuel_type"].isin(combustibles_elegidos)
    & df["Carroceria"].isin(carrocerias_elegidas)
    & df["mfg_year"].between(*rango_anios)
    & df["price"].between(*rango_precio)
]

if datos.empty:
    st.warning(
        "No hay autos con esos filtros. Prueba a ampliar los rangos o agregar opciones."
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


def euros(valor: float) -> str:
    """Da formato de moneda: 10679.3 -> '€10,679'."""
    return f"€{valor:,.0f}"


st.title("🚗 ¿Cuánto vale un Toyota Corolla usado?")
st.markdown(
    f"Explora el **precio** de {len(df):,} Corolla usados y cómo cambia según su "
    "**antigüedad**, **kilometraje**, **motor** y **equipamiento**."
)

with st.expander("ℹ️ ¿Cómo usar este tablero?"):
    st.markdown("""
        1. Usa los **filtros de la izquierda** para elegir combustible, carrocería, años o precios.
        2. Recorre las **pestañas** de abajo; cada una responde una pregunta.
        3. Pasa el cursor sobre un gráfico para ver los valores exactos.
           Puedes hacer zoom arrastrando y volver a la vista original con doble clic.
        4. En la pestaña **Datos** puedes ver la tabla completa y descargarla.

        **Glosario rápido**
        - **cc**: cilindrada del motor en centímetros cúbicos (1600 cc = motor 1.6 L).
        - **hp**: caballos de fuerza, la potencia del motor.
        - **Hatchback / Liftback / Sedán / Familiar**: formas de carrocería
          (con portón trasero corto, con portón inclinado, con maletero separado, con maletero largo).
        - **Antigüedad**: medida a agosto de 2004, fecha en que se tomaron los datos.
        """)

# --- Indicadores principales ------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Autos mostrados", f"{len(datos):,}")
col2.metric(
    "Precio promedio",
    euros(datos["price"].mean()),
    help=f"La mitad de los autos cuesta menos de {euros(datos['price'].median())} (mediana).",
)
col3.metric("Antigüedad promedio", f"{datos['Edad_Anios'].mean():.1f} años")
col4.metric("Kilometraje promedio", f"{datos['km'].mean():,.0f} km")

tab_precio, tab_dep, tab_motor, tab_equipo, tab_comparar, tab_datos = st.tabs(
    [
        "💶 Precio",
        "📉 Depreciación",
        "⛽ Motor y combustible",
        "🧰 Equipamiento",
        "🔍 Buscar autos parecidos",
        "📋 Datos",
    ]
)

# --- Pestaña: Precio ----------------------------------------------------------
with tab_precio:
    st.subheader("¿Cuánto cuesta la mayoría de los autos?")

    fig = px.histogram(
        datos,
        x="price",
        nbins=40,
        labels=NOMBRES,
        color_discrete_sequence=[COLOR_PRINCIPAL],
    )
    fig.update_traces(
        hovertemplate="%{x}<br>%{y} autos<extra></extra>",
        marker_line_width=1,
        marker_line_color="white",
    )
    fig.update_yaxes(title="Cantidad de autos")
    fig.update_xaxes(tickprefix="€")
    fig.add_vline(
        x=datos["price"].median(),
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Mediana: {euros(datos['price'].median())}",
        annotation_position="top right",
    )
    st.plotly_chart(estilo(fig), width="stretch")
    st.caption(
        "Cada barra agrupa los autos de un rango de precio. "
        "La línea punteada marca la mediana: la mitad cuesta menos y la otra mitad más."
    )

    st.subheader("¿Qué carrocería es más cara?")
    por_carroceria = (
        datos.groupby("Carroceria", as_index=False)
        .agg(price=("price", "mean"), Autos=("price", "size"))
        .sort_values(by="price")  # type: ignore
    )
    fig = px.bar(
        por_carroceria,
        x="price",
        y="Carroceria",
        orientation="h",
        text=por_carroceria["price"].map(euros),
        custom_data=["Autos"],
        labels=NOMBRES,
        color_discrete_sequence=[COLOR_PRINCIPAL],
    )
    fig.update_traces(
        hovertemplate="%{y}<br>%{x:,.0f} € promedio<br>%{customdata[0]} autos<extra></extra>"
    )
    fig.update_xaxes(tickprefix="€")
    st.plotly_chart(estilo(fig, alto=380), width="stretch")
    st.caption(
        "Precio promedio por tipo de carrocería. Pasa el cursor para ver cuántos autos hay de cada una: "
        "un promedio con pocos autos es menos confiable."
    )

# --- Pestaña: Depreciación -----------------------------------------------------
with tab_dep:
    st.subheader("¿Cuánto valor pierde un auto con los años?")

    fig = px.scatter(
        datos,
        x="age_08_04",
        y="price",
        color="fuel_type",
        hover_name="model",
        hover_data={"km": ":,", "mfg_year": True, "fuel_type": False},
        labels=NOMBRES,
        color_discrete_map=COLORES_COMBUSTIBLE,
        category_orders={"fuel_type": list(COLORES_COMBUSTIBLE)},
        opacity=0.6,
    )
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color="white")))
    fig.update_yaxes(tickprefix="€")
    fig.update_layout(legend=dict(orientation="h", y=1.08))
    st.plotly_chart(estilo(fig), width="stretch")
    st.caption(
        "Cada punto es un auto. Mientras más a la derecha, más viejo; mientras más arriba, más caro."
    )

    # Recta de tendencia: cuánto baja el precio, en promedio, por cada año.
    if datos["age_08_04"].nunique() > 1:
        pendiente_mes, _ = np.polyfit(datos["age_08_04"], datos["price"], 1)
        st.info(
            f"En promedio, cada **año** de antigüedad reduce el precio en unos "
            f"**{euros(-pendiente_mes * 12)}**."
        )

    st.subheader("¿Y el kilometraje?")
    fig = px.scatter(
        datos,
        x="km",
        y="price",
        color="fuel_type",
        hover_name="model",
        hover_data={"age_08_04": True, "fuel_type": False},
        labels=NOMBRES,
        color_discrete_map=COLORES_COMBUSTIBLE,
        category_orders={"fuel_type": list(COLORES_COMBUSTIBLE)},
        opacity=0.6,
    )
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color="white")))
    fig.update_yaxes(tickprefix="€")
    fig.update_layout(legend=dict(orientation="h", y=1.08))
    st.plotly_chart(estilo(fig), width="stretch")
    st.caption(
        "Más kilómetros suele significar menor precio, aunque la relación es más débil que con la antigüedad. "
        "Los autos diésel tienden a acumular más kilómetros."
    )

# --- Pestaña: Motor y combustible ---------------------------------------------
with tab_motor:
    st.subheader("¿Cómo varía el precio según el combustible?")

    fig = px.box(
        datos,
        x="price",
        y="fuel_type",
        color="fuel_type",
        points="all",
        hover_name="model",
        hover_data={"age_08_04": True, "km": ":,", "fuel_type": False},
        labels=NOMBRES,
        color_discrete_map=COLORES_COMBUSTIBLE,
        category_orders={"fuel_type": list(COLORES_COMBUSTIBLE)},
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(tickprefix="€")
    st.plotly_chart(estilo(fig, alto=400), width="stretch")
    st.caption(
        "Cada punto es un auto; la caja muestra dónde se concentra la mitad de ellos "
        "y la línea dentro de la caja es la mediana."
    )

    st.subheader("¿Un motor más grande vale más?")
    por_motor = (
        datos.groupby("Motor", as_index=False)
        .agg(
            price=("price", "mean"),
            hp=("hp", "mean"),
            Autos=("price", "size"),
        )
        .sort_values(by="Motor")  # type: ignore
    )
    fig = px.bar(
        por_motor,
        x="Motor",
        y="price",
        text=por_motor["price"].map(euros),
        custom_data=["Autos", "hp"],
        labels=NOMBRES,
        color_discrete_sequence=[COLOR_PRINCIPAL],
    )
    fig.update_traces(
        hovertemplate=(
            "Motor %{x}<br>%{y:,.0f} € promedio<br>%{customdata[1]:.0f} hp promedio"
            "<br>%{customdata[0]} autos<extra></extra>"
        )
    )
    fig = estilo(fig, alto=400)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickprefix="€")
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Precio promedio por tamaño de motor. Pasa el cursor para ver la potencia y cuántos autos hay."
    )

# --- Pestaña: Equipamiento ------------------------------------------------------
with tab_equipo:
    st.subheader("¿Qué extras traen los autos y cuánto se paga por ellos?")

    filas = []
    for col in COLUMNAS_EQUIPAMIENTO:
        con = datos.loc[datos[col] == True, "price"]  # noqa: E712
        sin = datos.loc[datos[col] == False, "price"]  # noqa: E712
        filas.append(
            {
                "Extra": NOMBRES[col],
                "Pct_Con": con.size / len(datos) * 100,
                "Diferencia": (
                    (con.mean() - sin.mean()) if con.size and sin.size else np.nan
                ),
            }
        )
    equipo = pd.DataFrame(filas)

    col_izq, col_der = st.columns(2)
    with col_izq:
        orden = equipo.sort_values("Pct_Con")
        fig = px.bar(
            orden,
            x="Pct_Con",
            y="Extra",
            orientation="h",
            labels={"Pct_Con": "% de autos que lo tienen", "Extra": ""},
            color_discrete_sequence=[COLOR_PRINCIPAL],
        )
        fig.update_traces(hovertemplate="%{y}<br>%{x:.0f}% de los autos<extra></extra>")
        fig.update_xaxes(range=[0, 100], ticksuffix="%")
        st.plotly_chart(estilo(fig, alto=560), width="stretch")
        st.caption("Qué tan común es cada extra entre los autos mostrados.")

    with col_der:
        orden = equipo.dropna(subset=["Diferencia"]).sort_values("Diferencia")  # type: ignore
        fig = px.bar(
            orden,
            x="Diferencia",
            y="Extra",
            orientation="h",
            labels={"Diferencia": "Diferencia de precio promedio (€)", "Extra": ""},
            color_discrete_sequence=[COLOR_PRINCIPAL],
        )
        fig.update_traces(
            hovertemplate="%{y}<br>Con el extra: %{x:+,.0f} € en promedio<extra></extra>"
        )
        fig.update_xaxes(tickprefix="€")
        fig.add_vline(x=0, line_color="gray", line_width=1)
        st.plotly_chart(estilo(fig, alto=560), width="stretch")
        st.caption(
            "Cuánto más (o menos) cuestan, en promedio, los autos que tienen el extra frente a los que no."
        )

    st.warning(
        "⚠️ **Ojo:** la diferencia de precio no es lo que *vale* el extra por sí solo. "
        "Los autos más nuevos suelen traer más extras y además son más caros; "
        "parte de la diferencia se debe a la antigüedad, no al extra."
    )

    st.subheader("Más extras, ¿mayor precio?")
    por_extras = datos.groupby("Equipamiento_Total", as_index=False).agg(
        price=("price", "median"), Autos=("price", "size")
    )
    fig = px.bar(
        por_extras,
        x="Equipamiento_Total",
        y="price",
        custom_data=["Autos"],
        labels={**NOMBRES, "price": "Precio mediano (€)"},
        color_discrete_sequence=[COLOR_PRINCIPAL],
    )
    fig.update_traces(
        hovertemplate="%{x} extras<br>%{y:,.0f} € (mediana)<br>%{customdata[0]} autos<extra></extra>"
    )
    fig = estilo(fig, alto=380)
    fig.update_xaxes(showgrid=False, dtick=1)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickprefix="€")
    st.plotly_chart(fig, width="stretch")
    st.caption("Precio mediano de los autos según cuántos extras traen.")

# --- Pestaña: Buscar autos parecidos -------------------------------------------
with tab_comparar:
    st.subheader("¿Cuánto debería costar un auto como el que buscas?")
    st.markdown(
        "Describe el auto y te mostramos los autos parecidos del archivo y su rango de precios."
    )

    c1, c2, c3 = st.columns(3)
    combustible = c1.selectbox(
        "Combustible", sorted(datos["fuel_type"].unique()), key="buscar_combustible"
    )
    edad = c2.slider(
        "Antigüedad (meses)",
        min_value=int(df["age_08_04"].min()),
        max_value=int(df["age_08_04"].max()),
        value=int(datos["age_08_04"].median()),
    )
    km = c3.slider(
        "Kilometraje (km)",
        min_value=0,
        max_value=int(df["km"].max()),
        value=int(datos["km"].median()),
        step=5_000,
    )

    parecidos = datos[
        (datos["fuel_type"] == combustible)
        & datos["age_08_04"].between(edad - MARGEN_EDAD_MESES, edad + MARGEN_EDAD_MESES)
        & datos["km"].between(km - MARGEN_KM, km + MARGEN_KM)
    ]

    st.caption(
        f"Se consideran parecidos los autos con ±{MARGEN_EDAD_MESES} meses de antigüedad "
        f"y ±{MARGEN_KM:,} km, además de los filtros de la izquierda."
    )

    if parecidos.empty:
        st.warning("No hay autos parecidos. Prueba con otra antigüedad o kilometraje.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Autos parecidos", f"{len(parecidos)}")
        m2.metric("Precio típico (mediana)", euros(parecidos["price"].median()))
        m3.metric(
            "Rango habitual",
            f"{euros(parecidos['price'].quantile(0.25))} – {euros(parecidos['price'].quantile(0.75))}",  # type: ignore
            help="La mitad de los autos parecidos cuesta dentro de este rango.",
        )
        columnas_parecidos = [
            "model",
            "price",
            "age_08_04",
            "km",
            "Motor",
            "Carroceria",
            "Equipamiento_Total",
            "color",
        ]
        st.dataframe(
            parecidos.sort_values("price")[columnas_parecidos].rename(columns=NOMBRES),  # type: ignore
            width="stretch",
            hide_index=True,
        )

# --- Pestaña: Datos -----------------------------------------------------------
with tab_datos:
    st.subheader("Tabla de datos")
    columnas_tabla = ["Carroceria", "Motor"] + COLUMNAS_ESPERADAS
    tabla = datos[columnas_tabla].rename(columns=NOMBRES)  # type: ignore
    st.dataframe(tabla, width="stretch", hide_index=True)

    st.download_button(
        "⬇️ Descargar estos datos (CSV)",
        data=tabla.to_csv(index=False).encode("utf-8-sig"),
        file_name="toyota_corolla_filtrado.csv",
        mime="text/csv",
    )

    with st.expander("🧹 ¿Qué limpieza se hizo a los datos?"):
        st.markdown(f"""
            - **Cilindrada imposible:** {registro_limpieza["cc_corregidos"]} auto(s) decían `16000` cc;
              se interpretó como `1600` cc (un cero de más).
            - **Filas repetidas:** se eliminaron {registro_limpieza["duplicados"]} fila(s) duplicada(s).
            - **Nombre del modelo:** se quitó el prefijo `TOYOTA Corolla` (todos lo tienen) y los espacios dobles.
            - **Columnas 0/1** (equipamiento, garantías, etc.) se convirtieron a Sí/No.
            - **Carrocería:** se dedujo de palabras del modelo (`HATCHB`, `LIFTB`, `SEDAN`, `WAGON`, `VERSO`…).
              Si el nombre no lo indica y el auto tiene 2 o 3 puertas, se asumió hatchback.
            - **Combustible** se tradujo al español y se agregó la antigüedad en años.
            """)
        st.markdown(
            "**Resumen técnico de las columnas** (tipo de dato y valores faltantes):"
        )
        st.dataframe(
            resumen_dataframe(df[columnas_tabla].rename(columns=NOMBRES)),  # type: ignore
            width="stretch",
        )
