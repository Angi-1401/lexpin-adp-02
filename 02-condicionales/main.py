# Estructuras condicionales
#
# Permiten generar una respuesta por parte del programa en función de si una condición es
# verdadera (True) o falsa (False)

# Si esta soleado y tengo dinero, podré salir de casa.
esta_soleado = True
tengo_dinero = True

if esta_soleado and tengo_dinero:
    print("Podré salir de casa.") # Esta línea sólo se ejecuta si la condición es True.

print("-----------------")

edad = 31

if edad < 1:
    print("Grupo etáreo: < 1")
elif edad >= 1 and edad <= 4:
    print("Grupo etáreo: 1 - 4")
elif edad >= 5 and edad <= 9:
    print("Grupo etáreo: 5 - 9")
elif edad >= 10 and edad <= 14:
    print("Grupo etáreo: 10 - 14")
elif edad >= 15 and edad <= 18:
    print("Grupo etáreo: 15 - 18")
elif edad >= 19 and edad <= 24:
    print("Grupo etáreo: 19 - 24")
elif edad >= 25 and edad <= 29:
    print("Grupo etáreo: 25 - 29")
else:
    print("Grupo etáreo: >= 30")

print("-----------------")

"""
Clasificación de una nota
Solicitar una nota entre 0 y 100 y mostrar el resultado según estas reglas:
- De 90 a 100: Excelente.
- De 70 a 89: Aprobado.
- De 0 a 69: Reprobado.
Ejemplo de entrada: 85

Salida esperada: Aprobado
"""

nota = 85

if nota >= 90:
    print("Excelente")
elif nota >= 70 and nota <= 89:
    print("Aprobado")
else:
    print("Reprobado")


"""
Validación de usuario y contraseña
Solicitar un usuario y contraseña y confirmar sin coinciden con los valores aceptados.
"""

usuario = "paola"
contraseña = "12Paola"

# ¿El usario es exactamente igual a "paola"? Sí (True) | No (False)
# ¿La contraseña es exactamente igual a "123Paola"? Sí (True) | No (False)

if usuario == "paola" and contraseña == "123Paola":
    print("Acceso concedido.")
else:
    print("Acceso denegado.")

"""
Calculadora básica
Solicitar dos números y una operación matemática (+, -, * o /). Mostrar el resultado de la operación seleccionada.

Consideraciones:
- Si el usuario intenta dividir entre cero, mostrar un mensaje de error.
- Si ingresa un operador diferente de los permitidos, mostrar «Operación inválida».
Ejemplo de entrada:

a = 10
b = 5
oper = "*"

Salida esperada: Resultado: 50

-----------------

Determinar el mayor de tres números
Solicitar tres números e indicar cuál es el mayor. Si los tres números son iguales, mostrar un mensaje que lo indique.

Ejemplo de entrada:

a = 12
b = 25
c = 18

Salida esperada: El mayor es 25

-----------------

Determinar si un número es positivo, negativo o cero
Solicitar un número al usuario y determinar si es positivo, negativo o igual a cero.

Consideraciones:
- Si el número es mayor que cero, mostrar «El número es positivo».
- Si el número es menor que cero, mostrar «El número es negativo».
- Si el número es igual a cero, mostrar «El número es cero».

Ejemplo de entrada:

numero: -8

Salida esperada: El número es negativo.
"""