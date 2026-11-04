import streamlit as st
import pandas as pd

# Títuto y descripción de la aplicación
st.title("📊 Dasboard de Nómina")
st.write(
    "Esta es una aplicación interactiva básica para aprender a visualizar y filtrar datos con Streamlit y Pandas."
)

# Alertas
# st.info("Esta es una alerta de tipo info.")
# st.success("Esta es una alerta de tipo sucsess")
# st.warning("Esta es una alerta de tipo warning.")
# st.error("Esta es una alerta de tipo error.")


# Cargar datos (Streamlit + Pandas)
@st.cache_data
def cargar_datos():
    return pd.read_csv("nomina.csv")


df = cargar_datos()

st.sidebar.header("🔍 Filtros")

# Filtro por departamento (Selección simple)
departamentos = ["Todos"] + list(df["Departamento"].unique())
dpto_seleccionado = st.sidebar.selectbox("Selecciona un departamento:", departamentos)

# Filtro por departamento (Selección múltiple)
departamentos = list(df["Departamento"].unique())
dptos_seleccionados = st.sidebar.multiselect("Selecciona uno o más departamentos:", departamentos, default=departamentos)

# Aplicar filtro por departamento (selección simple)
if dpto_seleccionado != "Todos":
    df_filtrado = df[df["Departamento"] == dpto_seleccionado]
else:
    df_filtrado = df.copy()

# Aplicar filtro por departamento (selección múltiple)
if dptos_seleccionados:
    df_filtrado = df[df["Departamento"].isin(dptos_seleccionados)]
else:
    df_filtrado = df.copy()

# KPIs
st.subheader("📌 Métricas principales")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Empleados", len(df_filtrado))

with col2:
    st.metric("Salario Promedio", f"$ {df_filtrado['SalarioNeto'].mean():,.2f}")

with col3:
    st.metric("Total Nóminal", f"$ {df_filtrado['SalarioNeto'].sum():,.2f}")

st.divider()

st.subheader("📋 Tabla de datos de nómina")
st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
