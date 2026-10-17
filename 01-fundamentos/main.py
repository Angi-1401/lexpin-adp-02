# Instrucción print
# Permite imprimir (mostrar) datos en la consola.

print("Estoy aprendiendo Python :D")
print(367)

print("-----------------")

# Tipos de datos

# str: Representa texto.
# int: Representa números enteros.
# float: Representa números de punto flotante (decimales).
# bool: Representar un estado de Verdadero (True) o Falso (False).
# none: Representa la ausencia de datos.

# Variables
# Es una cajita en la cual podemos almacenar datos.
# Cada variable puede almacenar un dato a la vez; y este puede variar con el tiempo.
# Estructura de una variable:
#
#   nombre_de_la_variable = valor

edad = 26                   # Variable de tipo int
salario = 275.9             # Variable de tipo float
nombre = "María Angélica"   # Variable de tipo str
cedula = "27393807"         # Variable de tipo str
tiene_hijos = False         # Variable de tipo bool
nulo = None                 # Variable de tipo none

print(f"¡Hola! Mi nombre es {nombre}. Tengo {edad} de edad y gano {salario} Bs. en mi empleo :'D")

print("-----------------")

# Tip: Si necesitas trabajar con un tipo de dato numérico que no puedes
# utilizar en un cálculo matemático (ej.: cédulas, nros. de teléfono, etc.),
# define tu dato dentro de una variable de tipo str.

# Operadores

# Operadores de asignación
# (x) Asignación (=): Permite asignar valorse a las variables.

a = 24
b = 32

# Operadores aritméticos
# (x) Suma (+): Permite sumar valores numéricos.
# (x) Resta (-): Permite restar valores numéricos.
# (x) Multiplicación (*): Permite multiplicar valores numéricos.
# (x) División (/): Permite dividir valores numéricos.
# (x) Módulo (%): Permite retornar el resto de una división.
# (x) Potenciación (**): Permite efectuar potencias numéricas.

print(a + b)
print(a - b)
print(a * b)
print(a / b)
print(a % b)
print(a ** b)

print("-----------------")

# Operadores relacionales
# (x) Igualdad (==): Permite determinar si dos o más valores son iguales.
# (x) Desigualdad (!=): Permite determinar si dos o más valores son distintos.
# (x) Mayor que (>): Permite determinar si un valor es mayor a otro.
# (x) Menor que (<): Permite determinar si un valor es menor a otro.
# (X) Mayor o igual que (>=): Permite determinar si un valor es mayor o igual a otro.
# (X) Menor o igual que (<=): Permite determinar si un valor es menor o igual a otro.

print(a == b)   # False
print(a != b)   # True
print(a > b)    # False
print(a < b)    # True
print(a >= b)   # False
print(a <= b)   # True

print("-----------------")

# Operadores lógicos
# (x) AND (and): Devuelve True cuando todos sus valores son True. Si, al menos, uno es False, devuelve False.
# (x) OR (or): Devuelve True cuando, al menos, uno de sus valores True. Si todos sus valores son False, devuelve False.
# (x) NOT (not): Permite convertir valores True en False y viceversa.

esta_soleado = False
tengo_dinero = False

# Si esta soleado y tengo dinero, podré salir de casa.
salida = esta_soleado and tengo_dinero
print(salida)

# Si esta soleado o tengo dinero, podré salir de casa.
salida = esta_soleado or tengo_dinero
print(salida)

# Si esta soleado o tengo dinero, podré salir de casa (demostración de not).
salida = (not esta_soleado) or tengo_dinero
print(salida)

"""
Ejercicios:

Crea dos variables (a y b; a siendo una variable de tipo int y b una variable de tipo float)
y muestra en pantalla el resultado de:
    - Suma de ambos.
    - Resta de ambos.
    - Multiplicación de ambos.
    - División de ambos.

Crea dos vairables (a y b; ambas variables de tipo int) y responde las siguientes preguntas
imprimiendo el resultado de la comparación en un print:
    - ¿Son iguales?
    - ¿Son distintas?
    - ¿Quién es mayor que quién?
    - ¿Quién es menor que quién?

Sin ejecutar el código, define cual podría ser el resultado de las siguientes expresiones:
    Nivel fácil:
    - True and False
    - True or False
    - True and not False

    Nivel medio:
    - True or False and False
    - (True or False) and False
    - not True and False or True

    Nivel Difícil:
    - True and not True or False and True
    - (True and False) or not (True or False)
    - False or not False and True or False

    Nivel Leyenda:
    - not (True or False) and (not False or True)
    - True and not (False or True and False) or False
    - not not True and (False or not (True and False))
    - not (not (True or False) and not (False or True))

Coloca tus respuestas junto a la expresión y compara tus resultados con los arrojados por la ejecución del código.
"""