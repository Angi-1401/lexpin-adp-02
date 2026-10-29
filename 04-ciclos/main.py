"""
Ciclos

Es una estructura de control en programación que permite repetir
un bloque de código un número determinado de veces.
Tiene un límite definido para actuar.

Estructura básica de un ciclo for:

for elemento in iterable:
    instrucciones
"""

for i in range(0, 9):
    print(i)

print("-----------------")

ventas = [120, 85, 150, 200, 95]

print("Ventas realizadas:")
for venta in ventas:
    print(venta)

print("-----------------")

ventas_totales = 0
for venta in ventas:
    ventas_totales = ventas_totales + venta
    print(ventas_totales)

print(f"Total de ventas: {ventas_totales}")

print("-----------------")

"""
List Comprehesions

Las List Comprehensions (comprensión de listas) son una forma
compacta y eficiente de crear nuevas listas en Python a partir de
otros iterables. Reemplazan las estructuras tradicionales de los
ciclos for en una sola línea de código.

Estructura básica de una list comprehesed:
variable = [instrucciones for elemento in iterable]
"""

# Creación de una nueva lista de cuadrados utilizando `for`

"""
for elemento in iterable:
    instrucciones
"""

cuadrados = []
for i in range(1, 6):
    cuadrados.append(i**2)

print(f"Resultado con ciclo `for`: {cuadrados}")

# Creación de una nueva lista de cuadrados utilizando
# List Comprehesions

cuadrado = [i**2 for i in range(1, 6)]

print(f"Resultado con List Comprehension: {cuadrados}")

print("-----------------")

"""
Filtrado condicional

Permite crear una copia del conjunto de datos original la cual
contiene sólo aquellos datos que cumplan con un criterio.

Estructura básica de una list comprehesed:
variable = [instrucciones for elemento in iterable if condicion]
"""

# Dataset original
ventas = [120.50, 45.00, 300.00, 15.99, 510.25, 85.00, 950.00, 8.50, 210.00, 65.40]
print(ventas)

# Filtrar sólo ventas superiores a 200 (>= 200)
ventas_altas = [venta for venta in ventas if venta >= 200]
print(f"Ventas altas: {ventas_altas}")

"""
Feature enginering

Suele utilizarse para etiquetar datos en función de una condición
de sí (True) y no (False).

Estructura básica de una list comprehesed:
variable = [clasificacion_1 if condicion else clasificacion_2 for elemento in iterable]
"""

# Categorizar ventas en función de su valor
categorias_ventas = ["Alta" if venta >= 200 else "Baja" for venta in ventas]
print(f"Ventas categorizadas: {categorias_ventas}")

"""
Transformación con Filtro

Simulación escenario:
Aplicar un impuesto del 16% sólo a aquelas ventas que clasifican en un rango
establecido (>50)
"""

ventas_con_impuesto = [venta * 1.16 for venta in ventas if venta > 50]
print(f"Ventas con impuesto aplicado (16% si venta >50): {ventas_con_impuesto}")

"""
Ejercicio 1:

A partir del dataset:
temperaturas = [19.5, 24.0, 31.2, 28.5, 15.0, 33.6, 12.1, 27.0]

Crea las siguientes listas:
- Temperaturas convertidas a grados Fahrenheit.
  (fórmula: F = C * 1.8 + 32).
- Lista de días calurosos (temperatura >= 25).
- Lista de días frescos (temperatura <= 20).

-----------------

Ejercicio 2:

A partir del dataset:
transacciones = [1200, 450, 8000, 150, 2300, 95]

Aplica una transformación de impuestos basada en el volumen del
monto.
- Si la transacción es >= 100, se aplica una retención del 15%.
(multiplicar por 0.85).
- Si la transacción es < 1000, no se aplica retención y se mantiene
su valor original.

-----------------

Ejercicio 3:

A partir del dataset:
precios = [5, 45, 120, 8, 85, 200, 12, 60]

Aplicar un descuento del 20% a todos los elementos, salvo aquellos
< 10 y >= 100.
"""