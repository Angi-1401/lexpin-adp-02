import pandas as pd

# Cargar el archivo CSV de nómina
nomina = pd.read_csv("nomina.csv")

# A partir de este momento, `nomina` es una variable de tipo DataFrame,
# un tipo especial de pandas que permite manipular datos tabulares de
# manera eficiente.

# Mostrar información general del DataFrame
print(nomina.info())

# Mostrar las primeras filas del DataFrame
print(nomina.head())

# Mostrar las últimas filas del DataFrame
print(nomina.tail())

# Mostrar estadísticas descriptivas del DataFrame
print(nomina.describe())


# Selecciones en un DataFrame

# Columnas
print("Columna SalarioBase:")
print(nomina["SalarioBase"])

print("Columnas Nombre, SalarioBase y Bonos:")
print(nomina[["Nombre", "SalarioBase", "Bono"]])

# Filas
print("Primera fila:")
print(nomina.iloc[0])

print("Primeras tres filas")
print(nomina.iloc[:5])

print("Últimas tres filas:")
print(nomina.iloc[-3:])

print("Dato en la primera fila y columna SalarioBase:")
print(nomina.loc[0, "SalarioBase"])


# Filtrado de columnas

print("Filtrado de columnas con condición SalarioBase >= 3500:")

nomina_filtrada = nomina[nomina["SalarioBase"] >= 3500]
print(nomina_filtrada)


print("Cantidad de empleados con SalarioBase >= 3500:")
print(nomina_filtrada.count())

print("Sumatoria de SalarioBase de los empleados con SalarioBase >= 3500:")
print(nomina_filtrada["SalarioBase"].sum())

print("Promedio de SalarioBase de los empleados con SalarioBase >= 3500:")
print(nomina_filtrada["SalarioBase"].mean())

print("Máximo de SalarioBase de los empleados con SalarioBase >= 3500:")
print(nomina_filtrada["SalarioBase"].max())

print("Mínimo de SalarioBase de los empleados con SalarioBase >= 3500:")
print(nomina_filtrada["SalarioBase"].min())

print("Desviación estándar de SalarioBase de los empleados con SalarioBase >= 3500:")
print(nomina_filtrada["SalarioBase"].std())

print("Varianza de SalarioBase de los empleados con SalarioBase >= 3500:")
print(nomina_filtrada["SalarioBase"].var())


# Filtrado de datos (Plus)

# En pandas los operadores lógicos se representan utilizando símbolos:
# & -> and
# | -> or
# ~ -> not

print(
    "Filtrado de empleados con SalarioBase >= 3500 y que pertenezcan al Departamento de TI:"
)

nomina_filtrada = nomina[
    (nomina["SalarioBase"] >= 3500) & (nomina["Departamento"] == "TI")
]
print(nomina_filtrada)

# Ejercicios:
# Responder las siguientes preguntas utilizando Pandas:
# 1. ¿Cuántos trabajadores tienen un salario neto mayor a 2000?
# 2. ¿Cuántos trabajadores tienen un salario neto menor a 1000
# 3. ¿Cuántos trabajadores con un salario neto entre 1500 y 2500
#    pertenecen al departamento de "TI"?
# 4. ¿Cuántos trabajadores del departamento de "Finanzas" trabajaron
#    más de 10 horas extra?
# 5. ¿Cuántos trabajadores del departamento de "RRHH" tienen un 
#    salario neto menor a 1200 y trabajaron menos de 5 horas extra?
