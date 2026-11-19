"""
app.py — Ejemplo de uso del catálogo etl.py con un dashboard en Streamlit
=========================================================================

Cómo ejecutarlo (desde esta carpeta):
    python -m venv .venv               (solo la primera vez)
    .venv/Scripts/activate
    pip install -r requirements.txt    (solo la primera vez)
    streamlit run app.py

Qué hace:
    1. EXTRAER   -> lee el archivo ventas_prueba.csv (datos "sucios" a propósito).
    2. TRANSFORMAR -> lo limpia paso a paso con las funciones de etl.py.
    3. CARGAR    -> muestra los datos limpios en un tablero y permite guardarlos.
"""

from pathlib import Path

import plotly.express as px
import streamlit as st

# Importamos SOLO las funciones del catálogo que vamos a usar.
# (etl.py debe estar en la misma carpeta que este archivo).
from etl import (
    combinar_columnas,
    contar_valores_fuera_catalogo,
    convertir_booleanos,
    convertir_fechas_excel,
    convertir_fechas_texto,
    convertir_numericos,
    convertir_porcentajes,
    crear_columna_desde_fecha,
    detectar_filas_vacias,
    dividir_columna,
    eliminar_columnas_vacias,
    eliminar_duplicados,
    eliminar_filas_vacias,
    estandarizar_nulos,
    extraer_digitos,
    filtrar_nulos,
    guardar_csv,
    leer_csv,
    limpiar_espacios_texto,
    limpiar_nombres_columnas,
    normalizar_categorias,
    normalizar_texto,
    ordenar_por_columnas,
    quitar_caracteres,
    rellenar_nulos,
    renombrar_columnas,
    reordenar_columnas,
    reporte_duplicados,
    resumen_dataframe,
    seleccionar_columnas,
    validar_columnas,
    validar_rango_numerico,
)

# Rutas de los archivos, relativas a la carpeta donde está app.py
CARPETA = Path(__file__).parent
ARCHIVO_ENTRADA = CARPETA / "ventas_prueba.csv"
ARCHIVO_SALIDA = CARPETA / "salida" / "ventas_limpias.csv"

# Regiones que consideramos válidas (nuestro "catálogo" de valores permitidos)
REGIONES_VALIDAS = ["Norte", "Sur", "Centro", "Sin región"]

# Ajustes de las gráficas
COLOR_SERIE = "#2a78d6"  # un solo color: cada gráfica muestra una sola serie
MESES = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
         7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}


def estilo_grafica(fig):
    """Estilo común para las gráficas de Plotly: limpio y fácil de leer."""
    fig.update_layout(
        height=320,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis_title=None,
        yaxis_title=None,
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",     # 15000 -> $15,000
        hoverlabel_font_size=13,
    )
    fig.update_xaxes(showgrid=False)
    return fig


# ---------------------------------------------------------------------------
# PROCESO ETL
# ---------------------------------------------------------------------------
# @st.cache_data hace que Streamlit guarde el resultado y no repita la
# limpieza cada vez que el usuario mueve un filtro del tablero.
@st.cache_data
def procesar(ruta):
    # ===================== 1. EXTRAER =====================
    # dtype=str: leemos TODO como texto para que pandas no "adivine" tipos.
    # Así nosotros decidimos cómo convertir cada columna.
    # No indicamos sep: leer_csv detecta solo que el separador es ";".
    crudo = leer_csv(ruta, dtype=str)

    # Diagnóstico ANTES de limpiar (para mostrarlo en el tablero)
    resumen_antes = resumen_dataframe(crudo)
    filas_vacias = int(detectar_filas_vacias(crudo).sum())
    duplicados = reporte_duplicados(crudo)["cantidad_filas_duplicadas"]

    # ===================== 2. TRANSFORMAR =====================
    df = crudo

    # 2.1 Nombres de columnas: "  Fecha Venta " -> "fecha_venta",
    #     "¿Pagado?" -> "pagado", "Región" -> "region", etc.
    df = limpiar_nombres_columnas(df)

    # 2.2 Textos como "N/A", "-", "" pasan a ser vacíos reales (nulos).
    #     Debe hacerse ANTES de convertir números o fechas.
    df = estandarizar_nulos(df)

    # 2.3 Quitar filas y columnas que no tienen ningún dato.
    #     (La columna "observaciones" está vacía y desaparece).
    df = eliminar_filas_vacias(df)
    df = eliminar_columnas_vacias(df)

    # 2.4 Quitar espacios sobrantes: "  Ana   Pérez " -> "Ana Pérez"
    df = limpiar_espacios_texto(df)

    # 2.5 Quitar filas repetidas (ahora que los textos ya están limpios).
    df = eliminar_duplicados(df)

    # 2.6 Códigos de cliente uniformes: "C-001" y "C 003" -> "C001", "C003".
    #     El patrón r"[\s-]+" significa "espacios o guiones".
    df = quitar_caracteres(df, ["codigo_cliente"], r"[\s-]+", "")

    # 2.7 Regiones escritas de muchas formas ("NORTE ", "nte", "sur")
    #     se unifican con un diccionario de equivalencias.
    df = normalizar_categorias(
        df,
        ["region"],
        mapeo={
            "norte": "Norte",
            "nte": "Norte",
            "sur": "Sur",
            "centro": "Centro",
            "oeste": "Oeste",
        },
    )
    # Las ventas sin región se marcan como "Sin región".
    df = rellenar_nulos(df, ["region"], valor="Sin región")

    # 2.8 "Laptop|Electrónica" se separa en dos columnas.
    df = dividir_columna(df, "producto_categoria", "|", ["producto", "categoria"])

    # 2.9 Montos en formato latino: "15.250,00" -> 15250.0
    df = convertir_numericos(df, ["monto_venta"], decimal=",", miles=".")

    # 2.10 Descuentos: "12,5%" -> 0.125 (escala=100). Sin dato = 0.
    df = convertir_porcentajes(df, ["descuento"], escala=100)
    df = rellenar_nulos(df, ["descuento"], valor=0)

    # 2.11 Fechas escritas como texto día/mes/año: "05/01/2026" -> 5 de enero.
    #      "fecha?" no es una fecha válida y queda vacía (NaT).
    df = convertir_fechas_texto(df, ["fecha_venta"], formato="%d/%m/%Y")

    # 2.12 Fechas de Excel guardadas como número: 45658 -> 2025-01-01
    df = convertir_fechas_excel(df, ["fecha_alta_excel"])

    # 2.13 "Sí", "si", "yes", "true", "1" -> True ; "No", "no", "0" -> False
    df = convertir_booleanos(df, ["pagado"])

    # 2.14 Teléfonos solo con números: "(55) 1234-5678" -> "5512345678"
    df = extraer_digitos(df, ["telefono"])

    # 2.15 Ejemplo de normalizar_texto (aquí solo limpia espacios; si
    #      quisiéramos, minusculas=True o quitar_tildes=True).
    df = normalizar_texto(df, ["nombre_cliente"])

    # ===================== VALIDACIONES =====================
    # ¿Están las columnas que el tablero necesita?
    faltantes = validar_columnas(df, ["fecha_venta", "monto_venta", "region"])
    if faltantes:
        raise ValueError(f"Faltan columnas en el archivo: {faltantes}")

    # Montos imposibles (negativos o demasiado grandes).
    # IMPORTANTE: indicar SIEMPRE minimo y maximo juntos (ver instructivo).
    fuera_de_rango = validar_rango_numerico(df, "monto_venta", minimo=0, maximo=50_000)
    cantidad_fuera_rango = int(fuera_de_rango.sum())

    # Regiones que no están en nuestro catálogo (p. ej. "Oeste").
    regiones_desconocidas = contar_valores_fuera_catalogo(df, "region", REGIONES_VALIDAS)

    # Descartamos las filas que no sirven para el análisis:
    df = df.loc[~fuera_de_rango]                        # montos imposibles
    df = filtrar_nulos(df, ["fecha_venta", "monto_venta"])  # sin fecha o sin monto

    # ===================== COLUMNAS NUEVAS Y ORDEN =====================
    df = crear_columna_desde_fecha(df, "fecha_venta", "anio", "anio")
    df = crear_columna_desde_fecha(df, "fecha_venta", "mes", "mes")
    df = combinar_columnas(df, ["codigo_cliente", "nombre_cliente"], "cliente", separador=" - ")
    df = renombrar_columnas(df, {"monto_venta": "monto"})
    df = reordenar_columnas(df, ["fecha_venta", "cliente", "region", "producto", "categoria", "monto"])
    df = ordenar_por_columnas(df, ["fecha_venta"])

    # Convertimos el monto a número decimal común para graficarlo sin problemas.
    df["monto"] = df["monto"].astype(float)

    calidad = {
        "filas_originales": len(crudo),
        "filas_vacias": filas_vacias,
        "filas_duplicadas": duplicados,
        "montos_fuera_rango": cantidad_fuera_rango,
        "regiones_desconocidas": regiones_desconocidas,
        "filas_finales": len(df),
    }
    return crudo, df, resumen_antes, calidad


# ---------------------------------------------------------------------------
# 3. CARGAR / MOSTRAR: el dashboard
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Dashboard de ventas", layout="wide")
st.title("Dashboard de ventas")
st.caption("Datos de prueba limpiados con el catálogo etl.py")

crudo, limpio, resumen_antes, calidad = procesar(ARCHIVO_ENTRADA)

# --- Filtro en la barra lateral ---
st.sidebar.header("Filtros")
regiones = sorted(limpio["region"].unique())
elegidas = st.sidebar.multiselect("Región", regiones, default=regiones)
datos = limpio[limpio["region"].isin(elegidas)]

if datos.empty:
    st.warning("No hay datos para las regiones elegidas.")
    st.stop()

# --- Indicadores principales ---
c1, c2, c3 = st.columns(3)
c1.metric("Ventas totales", f"${datos['monto'].sum():,.2f}")
c2.metric("Número de ventas", len(datos))
c3.metric("Venta promedio", f"${datos['monto'].mean():,.2f}")

# --- Gráficas (Plotly) ---
# Preparamos dos tablas pequeñas: total por región y total por mes.
por_region = (
    datos.groupby("region", as_index=False)["monto"].sum()
    .sort_values("monto", ascending=False)       # la región que más vende, primero
)
por_mes = datos.groupby("mes", as_index=False)["monto"].sum()
por_mes["nombre_mes"] = por_mes["mes"].map(MESES)  # 1 -> "Ene", 2 -> "Feb", ...

g1, g2 = st.columns(2)
with g1:
    st.subheader("Ventas por región")
    fig_region = px.bar(por_region, x="region", y="monto")
    fig_region.update_traces(
        marker_color=COLOR_SERIE,
        marker_cornerradius=4,                    # esquinas redondeadas
        hovertemplate="<b>%{x}</b><br>Ventas: $%{y:,.2f}<extra></extra>",
    )
    fig_region.update_layout(bargap=0.45)         # barras más delgadas
    st.plotly_chart(estilo_grafica(fig_region), width="stretch")

with g2:
    st.subheader("Ventas por mes")
    fig_mes = px.line(por_mes, x="nombre_mes", y="monto", markers=True)
    fig_mes.update_traces(
        line_color=COLOR_SERIE,
        line_width=2,
        marker_size=8,
        hovertemplate="<b>%{x}</b><br>Ventas: $%{y:,.2f}<extra></extra>",
    )
    st.plotly_chart(estilo_grafica(fig_mes), width="stretch")

# --- Tabla de datos limpios (solo algunas columnas) ---
st.subheader("Detalle de ventas")
st.dataframe(
    seleccionar_columnas(datos, ["fecha_venta", "cliente", "region", "producto", "monto", "pagado"]),
    hide_index=True,
)

# --- Reporte de calidad: qué encontró y corrigió el ETL ---
with st.expander("¿Qué limpió el ETL?"):
    st.write(
        f"- Filas en el archivo original: **{calidad['filas_originales']}**\n"
        f"- Filas vacías eliminadas: **{calidad['filas_vacias']}**\n"
        f"- Filas que estaban duplicadas: **{calidad['filas_duplicadas']}**\n"
        f"- Montos fuera de rango descartados: **{calidad['montos_fuera_rango']}**\n"
        f"- Ventas con región fuera del catálogo: **{calidad['regiones_desconocidas']}**\n"
        f"- Filas finales listas para analizar: **{calidad['filas_finales']}**"
    )
    st.markdown("**Datos originales (sin limpiar)**")
    st.dataframe(crudo)
    st.markdown("**Diagnóstico de los datos originales**")
    st.dataframe(resumen_antes)

# --- Guardar resultado ---
if st.button("Guardar CSV limpio"):
    guardar_csv(limpio, ARCHIVO_SALIDA)
    st.success(f"Archivo guardado en: {ARCHIVO_SALIDA}")
