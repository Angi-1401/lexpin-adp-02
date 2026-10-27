# Estructuras de datos

venta_1 = 120
venta_2 = 85
venta_3 = 150

# Lista
#
# Es una colección ordenada y modificable.
# Puede contener números, textos o elementos de diferente tipo.

# Lista homogénea (Todos los datos son de un mismo tipo)
ventas = [120, 85, 150]

# Lista no homogénea (Existen distintos tipos de datos dentro de la misma lista)
frankenstein = [512, "Manzana", True, None, 322.78, "Hola"]


ventas = [120, 85, 150, 200, 95]

# Índice: Valor numérico que refiere a la posición de un elemento en la lista.
# Nota importante: El índice siempre inicia desde el cero y se incrementa de forma secuencial.

print(ventas)       # Permite acceder al conjuto de datos completo.
print(ventas[0])    # Permite acceder a la primera posición en la lista.
print(ventas[-1])   # Permite acceder a la última posición en la lista.
print(ventas[1:4])  # Segmento (o slices): Extrae parte de una lista.

print(len(ventas))  # Permite devolver el número de elementos en una lista.

print("-----------------")

ventas = [120, 85, 150]

ventas.append(200)              # Agregar un elemento al final de la lista.
ventas.extend([95, 110])        # Agregar varios elementos al final de la lista.
ventas.insert(1, 0)             # Agregar un elemento en una posición definida.

ventas.remove(150)              # Eliminar la primera coincidencia.
ultimo = ventas.pop()           # Eliminar y devolver el último elemento en la lista.

ventas.sort()                   # Ordernar la lista de forma ascendente. Nota: Agrega el parámetro reverse=True para orden descendente.
ventas.reverse()                # Invertir el orden de la lista.

ocurrencias = ventas.count(85)  # Cuenta el número de ocurrencias de un elemento en la lista.

print(ventas)
print(ultimo)
print(ocurrencias)

print("-----------------")

print(sum(ventas))  # Suma todos los elementos de la lista.
print(max(ventas))  # Encuentra el mayor elemento en una lista.
print(min(ventas))  # Encuentra el menor elemento en una lista.

# Tuplas
#
# Es una colección ordenada y son inalterables.
# Puede contener números, textos o elementos de diferente tipo.

metricas = (120, 85, 150) # Estos valores ya no pueden modificarse.

"""
Responde las siguientes preguntas sin ejecutar el código:

1. Si ejecutamos el siguiente código, ¿qué imprime?

datos = [10, 20, 30]
datos.append(40)
datos.remove(20)
print(datos)

2. Si ejecutamos el siguiente código, ¿qué imprime?

numeros = [1, 2, 3, 4, 5]
numeros.pop()
numeros.insert(0, 0)
print(numeros)

3. Si ejecutamos el siguiente código, ¿qué imprime?

frutas = ["manzana", "banana", "cereza"]
frutas.sort()
print(frutas)

Compara tus respuestas con la ejecución real de cada algoritmo.
"""