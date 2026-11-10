import streamlit as st
import pandas as pd
import plotly.express as px

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

# # Filtro por departamento (Selección simple)
# departamentos = ["Todos"] + list(df["Departamento"].unique())
# dpto_seleccionado = st.sidebar.selectbox("Selecciona un departamento:", departamentos)

# Filtro por departamento (Selección múltiple)
departamentos = list(df["Departamento"].unique())
dptos_seleccionados = st.sidebar.multiselect(
    "Selecciona uno o más departamentos:", departamentos, default=departamentos
)

# # Aplicar filtro por departamento (selección simple)
# if dpto_seleccionado != "Todos":
#     df_filtrado = df[df["Departamento"] == dpto_seleccionado]
# else:
#     df_filtrado = df.copy()

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

# ---- Sección 1 ----

st.subheader("Distribución de nómina por departamento")

# Agrupación de datos utilizando Pandas groupby para obtener el gasto total de
# salario neto por departamento y posteriormente representar en gráfico de barras
df_dept_costo = (
    df_filtrado.groupby("Departamento")["SalarioNeto"]  # Agrupación
    .sum()  # Suma de los valores agrupados
    .reset_index()  # Reiniciar el índice después de la agrupación
    .sort_values(
        by="SalarioNeto", ascending=False
    )  # Ordenar de mayor a menor gasto por departamento
)

# Crear gráfico de barras utilizando Plotly Express para visualizar el gasto total
# de salario neto por departamento
fig_dept_costo = px.bar(
    df_dept_costo,  # Datos a graficar
    x="SalarioNeto",  # Eje X representa el gasto total de salario neto
    y="Departamento",  # Eje Y representa los departamentos
    title="Gasto total de salario neto por departamento",  # Título del gráfico
    labels={
        "Departamento": "Departamento",
        "SalarioNeto": "Gasto total ($)",
    },  # Etiquetas de los ejes
    text_auto=True,  # Mostrar los valores de cada barra en el gráfico
    color="Departamento",  # Asignar un color diferente a cada departamento
)
fig_dept_costo.update_yaxes(
    tickformat="$,.2f"
)  # Formatear los valores del eje Y como moneda

# Mostrar el gráfico de barras en Streamlit
st.plotly_chart(fig_dept_costo, use_container_width=True)

st.divider()

# ---- Sección 2 ----

st.subheader("Impacto de horas extras en el presupuesto")

HORA_ESTANDAR = 160  # Número de horas estándar por mes

# Crear nueva columna para calcular el costo de las horas extra
df_filtrado["CostoHorasExtra"] = (
    df_filtrado["SalarioBase"] / HORA_ESTANDAR
) * df_filtrado["HorasExtra"]

df_horas_extra = (
    df_filtrado.groupby("Departamento")
    .agg(
        horas_extra_trabajadas=(
            "HorasExtra",
            "sum",
        ),  # Suma de las horas extra trabajadas por departamento
        costo_horas_extra=(
            "CostoHorasExtra",
            "sum",
        ),  # Suma del costo de las horas extra por departamento
    )
    .reset_index()  # Reiniciar el índice después de la agregación
)

fig_horas_extra = px.bar(
    df_horas_extra,
    x=["horas_extra_trabajadas", "costo_horas_extra"],
    y="Departamento",
    title="Total de horas extra trabajadas por departamento y costo estimado",
    barmode="group",  # Mostrar las barras agrupadas por departamento
    labels={
        "Departamento": "Departamento",
        "SalarioNeto": "Monto ($)",
    },
    text_auto=True,
)
st.plotly_chart(fig_horas_extra, use_container_width=True)

st.subheader("📋 Tabla de datos de nómina")
st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
