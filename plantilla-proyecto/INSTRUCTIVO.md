# Instructivo de uso del catálogo `etl.py`

Esta guía explica cómo limpiar archivos CSV con las funciones de `etl.py`, aunque tengas poca experiencia programando. Cada función viene con un ejemplo que puedes copiar, y al final hay casos de uso completos.

**Archivos de esta carpeta**

| Archivo | Para qué sirve |
|---|---|
| `etl.py` | El catálogo de funciones (no hace falta modificarlo). |
| `ventas_prueba.csv` | Datos de prueba con errores puestos a propósito. |
| `app.py` | Ejemplo completo y comentado, con un pequeño dashboard en Streamlit. |
| `INSTRUCTIVO.md` | Esta guía. |

---

## Índice

1. [¿Qué es ETL?](#1-qué-es-etl)
2. [Preparación](#2-preparación)
3. [Cinco ideas básicas antes de empezar](#3-cinco-ideas-básicas-antes-de-empezar)
4. [Catálogo de funciones con ejemplos](#4-catálogo-de-funciones-con-ejemplos)
5. [Orden recomendado de los pasos](#5-orden-recomendado-de-los-pasos)
6. [Casos de uso](#6-casos-de-uso)
7. [El dataset de prueba](#7-el-dataset-de-prueba)
8. [El ejemplo `app.py` y su dashboard](#8-el-ejemplo-apppy-y-su-dashboard)
9. [Errores comunes y advertencias](#9-errores-comunes-y-advertencias)
10. [Tabla de referencia rápida](#10-tabla-de-referencia-rápida)

---

## 1. ¿Qué es ETL?

ETL son las siglas en inglés de los tres pasos para preparar datos:

| Paso | Significa | En este catálogo |
|---|---|---|
| **E**xtract | **Extraer**: leer los datos de un archivo. | `leer_csv` |
| **T**ransform | **Transformar**: limpiar, corregir y convertir. | La mayoría de las funciones |
| **L**oad | **Cargar**: guardar o usar los datos limpios. | `guardar_csv` |

Los archivos reales casi nunca vienen limpios: tienen espacios de más, fechas escritas de mil formas, números con puntos y comas, filas repetidas, celdas con "N/A"… Este catálogo sirve para corregir esos problemas sin tener que escribir todo desde cero.

Las funciones son **genéricas**: no saben nada de tu negocio. Funcionan igual con ventas, alumnos, inventarios o encuestas. Tú les indicas **qué columnas** tratar y **cómo**.

---

## 2. Preparación

### 2.1 Crear un entorno virtual e instalar las librerías

Un **entorno virtual** (`.venv`) es una carpeta donde se instalan las librerías solo para este proyecto, sin afectar al resto de tu computadora. Abre una terminal en esta carpeta y ejecuta:

```bash
python -m venv .venv                  # 1. crear el entorno (solo la primera vez)
.venv\Scripts\activate                # 2. activarlo en Windows (PowerShell o CMD)
# source .venv/bin/activate           #    activarlo en macOS / Linux
pip install -r requirements.txt       # 3. instalar las librerías (solo la primera vez)
```

Cuando el entorno está activo, la terminal muestra `(.venv)` al inicio de la línea. Debes **activarlo cada vez** que abras una terminal nueva (paso 2). En VS Code, elige también ese intérprete: `Ctrl + Shift + P` → *Python: Select Interpreter* → `.venv`.

`requirements.txt` instala tres librerías: `pandas` (obligatoria para el catálogo), y `streamlit` y `plotly`, que solo se necesitan para el dashboard y sus gráficas en `app.py`.

> Si PowerShell no deja activar el entorno y muestra un error de "ejecución de scripts deshabilitada", ejecuta una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentarlo.

### 2.2 Importar el catálogo

Tu script debe estar **en la misma carpeta** que `etl.py`. Al inicio del script escribe:

```python
from etl import *          # trae TODAS las funciones del catálogo
```

O, mejor, importa solo las que vas a usar (así queda claro de dónde sale cada una):

```python
from etl import leer_csv, limpiar_nombres_columnas, guardar_csv
```

---

## 3. Cinco ideas básicas antes de empezar

**1. Un DataFrame es una tabla.** Cuando lees un CSV, pandas lo guarda en una tabla con filas y columnas, como una hoja de Excel. Por costumbre se guarda en una variable llamada `df`.

**2. Cada función devuelve una tabla nueva.** Las funciones **no modifican** tu tabla original: entregan una copia corregida. Por eso **siempre** se escribe así:

```python
df = limpiar_nombres_columnas(df)   # ✅ guardamos el resultado en df
limpiar_nombres_columnas(df)        # ❌ el resultado se pierde
```

**3. Las columnas se indican en una lista, entre corchetes.** Aunque sea una sola:

```python
df = extraer_digitos(df, ["telefono"])               # ✅
df = extraer_digitos(df, ["telefono", "celular"])    # ✅ varias columnas
df = extraer_digitos(df, "telefono")                 # ❌ falta el corchete
```

(Excepción: las funciones que trabajan con **una sola** columna, como `dividir_columna` o `crear_columna_desde_fecha`, reciben el nombre sin corchetes. Está indicado en cada ejemplo).

**4. "Nulo" significa "celda vacía".** pandas muestra las celdas vacías como `NaN`, `<NA>` o `NaT` (en fechas). Cuando una conversión no puede entender un valor (por ejemplo, la fecha `"fecha?"`), lo deja vacío en lugar de inventar un dato.

**5. Algunas opciones se escriben con nombre.** Después de las columnas, las opciones se indican como `nombre=valor`:

```python
df = convertir_fechas_texto(df, ["fecha"], dayfirst=True)
```

Si no escribes una opción, la función usa su valor por defecto.

---

## 4. Catálogo de funciones con ejemplos

### 4.1 Lectura y escritura

#### `leer_csv(ruta, sep=None, encoding="utf-8", decimal=".", thousands=None, dtype=None, ...)`

Lee un archivo CSV y lo convierte en tabla. Si no indicas el separador (`sep`), **lo detecta solo** entre coma `,`, punto y coma `;`, barra `|` o tabulador.

```python
df = leer_csv("ventas_prueba.csv")                 # separador automático
df = leer_csv("ventas_prueba.csv", dtype=str)      # todo como texto (recomendado)
df = leer_csv("datos.csv", sep=";")                # separador indicado a mano
df = leer_csv("datos_viejos.csv", encoding="latin-1")  # archivos con acentos "raros"
```

**Recomendación:** usa `dtype=str` cuando el archivo está desordenado. Así pandas no intenta adivinar tipos (por ejemplo, no convierte el código `"00123"` en el número `123`) y luego tú conviertes cada columna con la función adecuada.

**Cuándo cambiar `encoding`:** si al leer aparece un error *UnicodeDecodeError*, o los acentos se ven como `�`, el archivo probablemente fue guardado con otra codificación; prueba con `encoding="latin-1"`.

#### `guardar_csv(df, ruta, encoding="utf-8-sig", sep=",", index=False)`

Guarda la tabla en un CSV. Si la carpeta de destino no existe, **la crea**. La codificación por defecto (`utf-8-sig`) hace que los acentos se vean bien al abrir el archivo en Excel.

```python
guardar_csv(df, "salida/ventas_limpias.csv")
guardar_csv(df, "salida/ventas_limpias.csv", sep=";")   # si tu Excel espera ";"
```

---

### 4.2 Inspección y diagnóstico

Estas funciones **no cambian** los datos: te ayudan a saber qué problemas tienen.

#### `resumen_dataframe(df)`

Devuelve una tabla con, para cada columna: su tipo, cuántas celdas vacías tiene, qué porcentaje representan y cuántos valores distintos hay. Las columnas con más vacíos aparecen primero.

```python
print(resumen_dataframe(df))
```

```
                    tipo  nulos  porcentaje_nulos  valores_unicos
Observaciones     object     19              95.0               1
Región            object      2              10.0              10
...
```

**Úsala** siempre al empezar, para tener una "radiografía" del archivo.

#### `detectar_filas_vacias(df)`

Indica, fila por fila, si está completamente vacía (también cuenta las que solo tienen espacios). Devuelve `True`/`False` por fila.

```python
vacias = detectar_filas_vacias(df)
print("Filas vacías:", vacias.sum())     # .sum() cuenta los True
```

#### `reporte_duplicados(df, subset=None)`

Cuenta las filas repetidas y te las muestra. Devuelve un diccionario con dos datos:

```python
rep = reporte_duplicados(df)
print(rep["cantidad_filas_duplicadas"])   # número de filas involucradas
print(rep["filas_duplicadas"])            # tabla con esas filas

# Duplicados solo según algunas columnas (p. ej. mismo cliente y misma fecha)
rep = reporte_duplicados(df, subset=["codigo_cliente", "fecha_venta"])
```

> La cantidad incluye **todas** las copias: si una fila aparece 2 veces, cuenta 2.

---

### 4.3 Limpieza de estructura y de texto

#### `limpiar_nombres_columnas(df, minusculas=True, reemplazo="_")`

Deja los nombres de columnas sin espacios, sin tildes, sin símbolos y en minúsculas. Esto evita errores al escribir los nombres después.

```python
df = limpiar_nombres_columnas(df)
```

| Antes | Después |
|---|---|
| `"  Fecha Venta "` | `fecha_venta` |
| `"Código Cliente"` | `codigo_cliente` |
| `"¿Pagado?"` | `pagado` |
| `"Fecha Alta (Excel)"` | `fecha_alta_excel` |
| `"% Avance"` | `avance` |

Opciones: `minusculas=False` conserva mayúsculas; `reemplazo="-"` usa guiones en vez de guiones bajos.

**Consejo:** hazlo como **primer paso** tras leer el archivo, y a partir de ahí usa los nombres nuevos.

#### `limpiar_espacios_texto(df, columnas=None)`

Quita los espacios al inicio y al final, y convierte varios espacios seguidos en uno solo.

```python
df = limpiar_espacios_texto(df)                       # todas las columnas de texto
df = limpiar_espacios_texto(df, ["nombre_cliente"])   # solo una columna
```

`"  Ana   Pérez "` → `"Ana Pérez"`

#### `normalizar_texto(df, columnas=None, minusculas=False, quitar_tildes=False)`

Hace lo mismo que la anterior y, opcionalmente, pasa a minúsculas y/o quita tildes. Útil para comparar textos o buscar sin importar cómo se escribieron.

```python
df = normalizar_texto(df, ["nombre"], minusculas=True, quitar_tildes=True)
```

`"  José  ÁLVAREZ "` → `"jose alvarez"`

#### `estandarizar_nulos(df, valores=None, columnas=None, ignorar_mayusculas=True)`

Muchas personas escriben "N/A", "-", "null" o "ninguno" cuando no hay dato. Esta función convierte todos esos textos en **celdas vacías reales**, para que pandas las reconozca.

Por defecto reconoce: `""`, `" "`, `NA`, `#N/A`, `N/A`, `N.A.`, `NULL`, `NONE`, `NAN`, `-`, `--` (sin importar mayúsculas).

```python
df = estandarizar_nulos(df)

# Con tu propia lista de marcadores
df = estandarizar_nulos(df, valores=["sin dato", "no aplica", "?", "-"])
```

> ⚠️ Si das tu propia lista, **reemplaza** a la lista por defecto (no se suman). Incluye todos los marcadores que necesites.

#### `quitar_caracteres(df, columnas, patron, reemplazo="")`

Borra (o reemplaza) caracteres en columnas de texto. El `patron` es una **expresión regular**, un mini-lenguaje para describir texto. Algunos patrones útiles:

| Patrón | Significa |
|---|---|
| `r"-"` | el guion |
| `r"[\s-]+"` | espacios o guiones |
| `r"[$€]"` | los símbolos `$` o `€` |
| `r"\(.*?\)"` | cualquier texto entre paréntesis |

```python
# Códigos "C-001" y "C 003" -> "C001" y "C003"
df = quitar_caracteres(df, ["codigo_cliente"], r"[\s-]+", "")

# Cambiar barras por guiones
df = quitar_caracteres(df, ["referencia"], r"/", "-")
```

> Los caracteres `. ( ) [ ] + * ? $ | \` tienen significado especial en las expresiones regulares. Para quitar un punto literal escribe `r"\."`, no `"."`.

#### `normalizar_categorias(df, columnas, mapeo=None, minusculas=True)`

Unifica valores de categorías escritos de distintas maneras. Primero pasa todo a minúsculas y quita espacios, y luego aplica el diccionario `mapeo` (`{"como_viene": "como_lo_quiero"}`).

```python
df = normalizar_categorias(
    df,
    ["region"],
    mapeo={
        "norte": "Norte",
        "nte": "Norte",
        "sur": "Sur",
        "centro": "Centro",
    },
)
```

`"NORTE "`, `"nte"`, `"Norte"` → `"Norte"`

> Escribe las claves del mapeo (lado izquierdo) en minúsculas. Los valores que no aparezcan en el mapeo quedan en minúsculas.

---

### 4.4 Conversión de tipos y formatos

Al leer con `dtype=str`, todo es texto. Para poder sumar, promediar o filtrar por fecha, hay que **convertir**.

#### `convertir_numericos(df, columnas, decimal=",", miles=".", errores="coerce")`

Convierte texto en número. Lo más importante es indicar **cómo está escrito** el número:

| El archivo trae | Formato | Escribe |
|---|---|---|
| `1.234,50` | latino / europeo | `decimal=",", miles="."` (es el valor por defecto) |
| `1,234.50` | anglosajón | `decimal=".", miles=","` |

```python
df = convertir_numericos(df, ["monto_venta"])                          # formato latino
df = convertir_numericos(df, ["precio"], decimal=".", miles=",")       # formato anglosajón
```

También elimina símbolos como `$` o espacios: `"$ 2.500,75"` → `2500.75`.

> ⚠️ **Elige bien el formato.** Con los valores por defecto (latino), el texto `"1234.50"` se convierte en `123450` porque el punto se toma como separador de miles. Revisa siempre unas filas antes de convertir.

`errores="coerce"` (por defecto) deja vacío lo que no se pueda convertir. Con `errores="raise"` el programa se detiene y te avisa del primer valor problemático.

#### `convertir_porcentajes(df, columnas, decimal=",", miles=".", escala=1)`

Convierte porcentajes escritos como texto. Elimina el `%`.

```python
df = convertir_porcentajes(df, ["descuento"])              # "12,5%" -> 12.5
df = convertir_porcentajes(df, ["descuento"], escala=100)  # "12,5%" -> 0.125
```

Usa `escala=100` si después vas a multiplicar (por ejemplo, `precio * (1 - descuento)`).

#### `convertir_fechas_texto(df, columnas, formato=None, dayfirst=True, yearfirst=False)`

Convierte fechas escritas como texto en fechas reales.

```python
# Si conoces el formato exacto (lo más seguro):
df = convertir_fechas_texto(df, ["fecha_venta"], formato="%d/%m/%Y")

# Si no lo conoces, indica al menos si el día va primero:
df = convertir_fechas_texto(df, ["fecha_venta"], dayfirst=True)
```

Códigos de formato más usados:

| Código | Significa | Ejemplo |
|---|---|---|
| `%d` | día (2 dígitos) | `05` |
| `%m` | mes (2 dígitos) | `01` |
| `%Y` | año (4 dígitos) | `2026` |
| `%y` | año (2 dígitos) | `26` |
| `%H:%M` | hora y minutos | `14:30` |

| Fecha en el archivo | `formato` |
|---|---|
| `05/01/2026` | `"%d/%m/%Y"` |
| `05-01-2026` | `"%d-%m-%Y"` |
| `2026-01-05` | `"%Y-%m-%d"` |
| `05/01/26 14:30` | `"%d/%m/%y %H:%M"` |

> ⚠️ La fecha `03/04/2024` puede ser 3 de abril o 4 de marzo. Con `dayfirst=True` (por defecto) se lee como **3 de abril**. Si en tu archivo el mes va primero usa `dayfirst=False`, o mejor, indica `formato`.

#### `convertir_fechas_excel(df, columnas, origen="1899-12-30", unidad="D")`

A veces Excel exporta las fechas como números (por ejemplo `45658`). Esta función los convierte en fechas.

```python
df = convertir_fechas_excel(df, ["fecha_alta_excel"])   # 45658 -> 2025-01-01
```

Funciona para el Excel habitual de Windows. Si el archivo viene de un Excel de Mac antiguo y las fechas salen corridas unos 4 años, consulta el origen de fechas de ese archivo.

#### `convertir_booleanos(df, columnas, verdaderos=None, falsos=None)`

Convierte respuestas de tipo sí/no en `True` / `False`.

- Se toman como **verdadero**: `si`, `sí`, `yes`, `true`, `1`, `verdadero`
- Se toman como **falso**: `no`, `false`, `0`, `falso`
- Cualquier otra cosa queda vacía. No importan mayúsculas ni espacios.

```python
df = convertir_booleanos(df, ["pagado"])

# Con tus propias palabras:
df = convertir_booleanos(df, ["asistio"], verdaderos=["asistió", "x"], falsos=["faltó"])
```

#### `extraer_digitos(df, columnas)`

Deja solo los números. Ideal para teléfonos, documentos de identidad o códigos postales.

```python
df = extraer_digitos(df, ["telefono"])
```

`"(55) 1234-5678"` → `"5512345678"` · `"+52 55 1111 2222"` → `"525511112222"`

El resultado sigue siendo **texto** (así no se pierden los ceros iniciales).

---

### 4.5 Filtrado, duplicados y valores faltantes

#### `eliminar_filas_vacias(df)` y `eliminar_columnas_vacias(df)`

Quitan las filas o columnas en las que **no hay ningún dato** (las que solo tienen espacios también cuentan como vacías).

```python
df = eliminar_filas_vacias(df)
df = eliminar_columnas_vacias(df)
```

> Es normal ver un aviso amarillo *FutureWarning* de pandas al usarlas. No es un error; se puede ignorar.

#### `eliminar_duplicados(df, subset=None, conservar="first")`

Elimina filas repetidas y conserva una.

```python
df = eliminar_duplicados(df)                                    # filas idénticas
df = eliminar_duplicados(df, subset=["codigo_cliente"])         # un registro por cliente
df = eliminar_duplicados(df, subset=["codigo_cliente"], conservar="last")  # el último
```

**Consejo:** limpia antes los espacios y mayúsculas. `"Ana Pérez"` y `"Ana  Pérez "` no se consideran iguales hasta que se limpian.

#### `filtrar_nulos(df, columnas, como="cualquiera")`

Quita filas que tienen celdas vacías en las columnas que indiques.

```python
# Quita la fila si falta la fecha O el monto
df = filtrar_nulos(df, ["fecha_venta", "monto_venta"])

# Quita la fila solo si faltan AMBOS
df = filtrar_nulos(df, ["email", "telefono"], como="todos")
```

#### `rellenar_nulos(df, columnas, metodo="valor", valor=None)`

Completa las celdas vacías.

```python
df = rellenar_nulos(df, ["region"], valor="Sin región")   # un valor fijo
df = rellenar_nulos(df, ["descuento"], valor=0)

df = rellenar_nulos(df, ["sucursal"], metodo="anterior")  # copia el valor de arriba
df = rellenar_nulos(df, ["sucursal"], metodo="siguiente") # copia el valor de abajo
```

`metodo="anterior"` es muy útil en reportes de Excel donde una celda agrupada solo tiene el nombre en la primera fila del grupo.

---

### 4.6 Transformaciones de columnas

#### `renombrar_columnas(df, mapeo)`

Cambia el nombre de columnas con un diccionario `{"nombre_actual": "nombre_nuevo"}`.

```python
df = renombrar_columnas(df, {"monto_venta": "monto", "codigo_cliente": "cliente_id"})
```

#### `seleccionar_columnas(df, columnas)`

Se queda solo con las columnas indicadas, en ese orden. Si alguna no existe, avisa con un error `KeyError`.

```python
resumen = seleccionar_columnas(df, ["fecha_venta", "cliente", "monto"])
```

#### `reordenar_columnas(df, columnas_primero)`

Pone primero las columnas indicadas y deja las demás detrás (no borra ninguna).

```python
df = reordenar_columnas(df, ["fecha_venta", "cliente", "monto"])
```

#### `dividir_columna(df, columna, separador, nombres)`

Separa una columna en varias. La columna va **sin corchetes**, los nombres nuevos **con corchetes**.

```python
df = dividir_columna(df, "producto_categoria", "|", ["producto", "categoria"])
```

`"Laptop|Electrónica"` → `producto = "Laptop"`, `categoria = "Electrónica"`

> Si alguna fila tiene más (o menos) partes de las esperadas, la función se detiene con un error que indica cuántas partes encontró. La columna original se conserva.

#### `combinar_columnas(df, columnas, nueva_columna, separador=" ", omitir_nulos=True)`

Une varias columnas de texto en una nueva.

```python
df = combinar_columnas(df, ["nombre", "apellido"], "nombre_completo")
df = combinar_columnas(df, ["codigo_cliente", "nombre_cliente"], "cliente", separador=" - ")
```

Con `omitir_nulos=True` (por defecto) las celdas vacías se saltan: `None` + `"Gómez"` → `"Gómez"`.

#### `crear_columna_desde_fecha(df, columna_fecha, nueva_columna, componente)`

Crea una columna con una parte de la fecha. Componentes posibles: `"anio"` (o `"año"`), `"mes"`, `"dia"` (o `"día"`), `"dia_semana"`, `"hora"`, `"trimestre"`.

```python
df = crear_columna_desde_fecha(df, "fecha_venta", "anio", "anio")
df = crear_columna_desde_fecha(df, "fecha_venta", "mes", "mes")
df = crear_columna_desde_fecha(df, "fecha_venta", "trimestre", "trimestre")
```

En `"dia_semana"`, el lunes es `0` y el domingo es `6`.

#### `ordenar_por_columnas(df, columnas, ascendente=True)`

Ordena las filas.

```python
df = ordenar_por_columnas(df, ["fecha_venta"])                  # más antigua primero
df = ordenar_por_columnas(df, ["monto"], ascendente=False)      # mayor monto primero
```

---

### 4.7 Validaciones

Las validaciones **no cambian** los datos: te dicen si algo está mal para que decidas qué hacer.

#### `validar_columnas(df, obligatorias)`

Devuelve la lista de columnas obligatorias que **faltan**. Si la lista está vacía, todo está bien.

```python
faltantes = validar_columnas(df, ["fecha_venta", "monto_venta", "region"])
if faltantes:
    print("Al archivo le faltan columnas:", faltantes)
```

#### `validar_rango_numerico(df, columna, minimo=None, maximo=None)`

Marca con `True` las filas cuyo valor está fuera del rango permitido.

```python
fuera = validar_rango_numerico(df, "monto_venta", minimo=0, maximo=50_000)
print("Montos fuera de rango:", fuera.sum())
print(df[fuera])               # ver esas filas
df = df[~fuera]                # quitarlas (el ~ significa "lo contrario")
```

> ⚠️ **Indica siempre `minimo` y `maximo` juntos**, o solo `minimo`. Por cómo está escrita la función, si indicas **solo `maximo`**, marca **todos** los valores como fuera de rango. Si no hay mínimo real, usa uno muy bajo, por ejemplo `minimo=-1_000_000_000`.

#### `contar_valores_fuera_catalogo(df, columna, catalogo)`

Cuenta cuántos valores **no** están en la lista de valores permitidos (las celdas vacías no se cuentan).

```python
n = contar_valores_fuera_catalogo(df, "region", ["Norte", "Sur", "Centro"])
print("Regiones no reconocidas:", n)
```

Distingue mayúsculas: `"norte"` no es igual a `"Norte"`. Normaliza la columna antes de validar.

---

## 5. Orden recomendado de los pasos

El orden importa. Este es un orden que funciona en la mayoría de los casos:

```python
from etl import *

# 1. EXTRAER
df = leer_csv("mi_archivo.csv", dtype=str)
print(resumen_dataframe(df))                   # radiografía inicial

# 2. ESTRUCTURA
df = limpiar_nombres_columnas(df)              # primero los nombres
df = estandarizar_nulos(df)                    # "N/A", "-" -> vacío
df = eliminar_filas_vacias(df)
df = eliminar_columnas_vacias(df)

# 3. TEXTO
df = limpiar_espacios_texto(df)
df = normalizar_categorias(df, ["mi_categoria"], mapeo={...})

# 4. DUPLICADOS (después de limpiar el texto)
df = eliminar_duplicados(df)

# 5. TIPOS
df = convertir_numericos(df, ["mi_numero"])
df = convertir_fechas_texto(df, ["mi_fecha"], formato="%d/%m/%Y")

# 6. VALIDAR Y FILTRAR
print(validar_columnas(df, ["mi_fecha", "mi_numero"]))
df = filtrar_nulos(df, ["mi_fecha", "mi_numero"])

# 7. ENRIQUECER Y ORDENAR
df = crear_columna_desde_fecha(df, "mi_fecha", "mes", "mes")
df = ordenar_por_columnas(df, ["mi_fecha"])

# 8. CARGAR
guardar_csv(df, "salida/mi_archivo_limpio.csv")
```

Tres reglas para recordar:

1. **Nombres de columnas primero**: todos los pasos siguientes usan los nombres limpios.
2. **`estandarizar_nulos` antes de convertir**: así `"-"` no se confunde con un signo negativo.
3. **Limpiar texto antes de buscar duplicados**: si no, filas casi iguales no se detectan.

---

## 6. Casos de uso

### Caso 1 — Reporte de ventas exportado de un sistema en español

**Situación:** recibes un CSV separado por `;` con montos como `15.250,00`, fechas `05/01/2026` y descuentos `12,5%`. Quieres el total por mes.

```python
from etl import *

df = leer_csv("ventas.csv", dtype=str)
df = limpiar_nombres_columnas(df)
df = estandarizar_nulos(df)
df = convertir_numericos(df, ["monto_venta"])                  # 15.250,00 -> 15250.0
df = convertir_porcentajes(df, ["descuento"], escala=100)      # 12,5% -> 0.125
df = convertir_fechas_texto(df, ["fecha_venta"], formato="%d/%m/%Y")
df = filtrar_nulos(df, ["fecha_venta", "monto_venta"])
df = crear_columna_desde_fecha(df, "fecha_venta", "mes", "mes")

print(df.groupby("mes")["monto_venta"].sum())                  # total por mes
```

### Caso 2 — Base de contactos para una campaña

**Situación:** tienes una lista de clientes con teléfonos escritos de muchas formas, nombres con espacios de más y clientes repetidos. Necesitas un contacto por cliente.

```python
from etl import *

df = leer_csv("clientes.csv", dtype=str)
df = limpiar_nombres_columnas(df)
df = limpiar_espacios_texto(df)
df = extraer_digitos(df, ["telefono"])                         # (55) 1234-5678 -> 5512345678
df = combinar_columnas(df, ["nombre", "apellido"], "nombre_completo")
df = eliminar_duplicados(df, subset=["telefono"])              # un registro por teléfono
df = filtrar_nulos(df, ["telefono"])
df = seleccionar_columnas(df, ["nombre_completo", "telefono"])
guardar_csv(df, "salida/contactos_campania.csv")
```

### Caso 3 — Encuesta con respuestas Sí/No y opciones escritas a mano

**Situación:** una encuesta donde la gente respondió "Sí", "si", "SI", "yes" y la ciudad como "CDMX", "cdmx", "Ciudad de México".

```python
from etl import *

df = leer_csv("encuesta.csv", dtype=str)
df = limpiar_nombres_columnas(df)
df = estandarizar_nulos(df, valores=["", "-", "no sé", "prefiero no decir"])
df = convertir_booleanos(df, ["recomendaria"])
df = normalizar_categorias(
    df,
    ["ciudad"],
    mapeo={"cdmx": "Ciudad de México", "ciudad de méxico": "Ciudad de México"},
)

print("Porcentaje que recomendaría:", df["recomendaria"].mean() * 100)
print(df["ciudad"].value_counts())                             # respuestas por ciudad
```

### Caso 4 — Revisar un archivo antes de aceptarlo

**Situación:** un proveedor te envía un archivo cada semana y quieres revisar su calidad antes de usarlo, sin modificarlo.

```python
from etl import *

df = leer_csv("archivo_proveedor.csv", dtype=str)
df = limpiar_nombres_columnas(df)

faltantes = validar_columnas(df, ["fecha", "codigo", "cantidad"])
print("Columnas faltantes:", faltantes or "ninguna")
print("Filas vacías:", detectar_filas_vacias(df).sum())
print("Filas duplicadas:", reporte_duplicados(df)["cantidad_filas_duplicadas"])

df = convertir_numericos(df, ["cantidad"])
print("Cantidades fuera de 0–1000:", validar_rango_numerico(df, "cantidad", minimo=0, maximo=1000).sum())
print(resumen_dataframe(df))
```

### Caso 5 — Reporte de Excel con celdas agrupadas

**Situación:** en el reporte, el nombre de la sucursal aparece solo en la primera fila de cada bloque y las demás están vacías.

```python
from etl import *

df = leer_csv("reporte_sucursales.csv", dtype=str)
df = limpiar_nombres_columnas(df)
df = estandarizar_nulos(df)
df = rellenar_nulos(df, ["sucursal"], metodo="anterior")       # copia la sucursal hacia abajo
df = convertir_fechas_excel(df, ["fecha"])                     # 45658 -> 2025-01-01
```

---

## 7. El dataset de prueba

`ventas_prueba.csv` simula una exportación de ventas con **errores a propósito**, para practicar cada función:

| Problema incluido | Ejemplo en el archivo | Función que lo resuelve |
|---|---|---|
| Separador `;` | toda la estructura | `leer_csv` (lo detecta solo) |
| Nombres de columnas con espacios, tildes y símbolos | `"  Fecha Venta "`, `"¿Pagado?"` | `limpiar_nombres_columnas` |
| Marcadores de "sin dato" | `N/A`, `-` | `estandarizar_nulos` |
| Filas totalmente vacías (2) | `;;;;;;;;;;` y una fila solo con espacios | `eliminar_filas_vacias` |
| Columna sin datos | `Observaciones` | `eliminar_columnas_vacias` |
| Espacios de más | `"  Ana   Pérez "` | `limpiar_espacios_texto` |
| Fila duplicada | la venta de María López aparece dos veces | `eliminar_duplicados` |
| Códigos con formato distinto | `C-001`, `C 003` | `quitar_caracteres` |
| Regiones escritas de varias formas | `NORTE `, `nte`, `sur`, `centro ` | `normalizar_categorias` |
| Región fuera del catálogo | `Oeste` | `contar_valores_fuera_catalogo` |
| Dos datos en una columna | `Laptop\|Electrónica` | `dividir_columna` |
| Números en formato latino | `15.250,00` | `convertir_numericos` |
| Monto negativo (imposible) | `-500,00` | `validar_rango_numerico` |
| Porcentajes como texto | `12,5%` | `convertir_porcentajes` |
| Fecha inválida | `fecha?` | `convertir_fechas_texto` + `filtrar_nulos` |
| Fechas como número de Excel | `45658` | `convertir_fechas_excel` |
| Sí/No escrito de muchas formas | `Sí`, `si`, `yes`, `true`, `0` | `convertir_booleanos` |
| Teléfonos con símbolos | `(55) 1234-5678`, `+52 55 1111 2222` | `extraer_digitos` |

El archivo tiene 20 filas. Después de la limpieza de `app.py` quedan **14 ventas válidas**.

---

## 8. El ejemplo `app.py` y su dashboard

### Cómo ejecutarlo

En una terminal, dentro de esta carpeta y con el entorno virtual activo:

```bash
.venv\Scripts\activate
streamlit run app.py
```

Se abrirá el navegador con el dashboard. Para detenerlo, vuelve a la terminal y presiona `Ctrl + C`.

### Qué hace el script

`app.py` aplica **todas** las funciones del catálogo sobre `ventas_prueba.csv`, en el orden de la sección 5, y cada paso tiene un comentario que explica qué corrige. Está dividido en dos partes:

1. **La función `procesar`**: contiene todo el ETL (extraer → transformar → validar). Puedes leerla de arriba abajo como una receta.
2. **El dashboard**: muestra el resultado.

### Qué verás en el dashboard

- **Barra lateral:** un filtro para elegir regiones.
- **Indicadores:** ventas totales, número de ventas y venta promedio.
- **Gráficas interactivas (Plotly):** ventas por región (barras) y ventas por mes (línea). Al pasar el mouse sobre una barra o un punto aparece el monto exacto; también se puede hacer zoom y descargar la gráfica como imagen con los botones de la esquina.
- **Tabla de detalle:** las ventas ya limpias.
- **"¿Qué limpió el ETL?":** una sección desplegable con cuántas filas vacías, duplicadas e inválidas se encontraron, los datos originales sin limpiar (para comparar) y el diagnóstico de `resumen_dataframe`.
- **Botón "Guardar CSV limpio":** guarda el resultado en `salida/ventas_limpias.csv` usando `guardar_csv`.

### Cómo adaptarlo a tus datos

1. Copia tu CSV a esta carpeta y cambia `ARCHIVO_ENTRADA` en `app.py`.
2. Ejecuta primero solo `leer_csv` + `limpiar_nombres_columnas` y mira los nombres que resultan (`print(df.columns)`).
3. Cambia los nombres de columnas de cada paso por los tuyos y borra los pasos que no necesites.
4. Ajusta el dashboard (las columnas que se suman y se agrupan).

---

## 9. Errores comunes y advertencias

| Mensaje o síntoma | Causa probable | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'etl'` | Tu script no está en la misma carpeta que `etl.py`. | Mueve el script o ejecuta desde esta carpeta. |
| `ModuleNotFoundError: No module named 'pandas'` (o `'plotly'`) | El entorno virtual no está activo o faltan librerías. | Activa el `.venv` y ejecuta `pip install -r requirements.txt` (sección 2.1). |
| `KeyError: 'Fecha Venta'` | Usas el nombre viejo después de `limpiar_nombres_columnas`. | Usa el nombre limpio: `'fecha_venta'`. Revisa con `print(df.columns)`. |
| `KeyError: Columnas inexistentes: [...]` | En `seleccionar_columnas` o `reordenar_columnas` escribiste un nombre que no existe. | Revisa la ortografía. |
| `ValueError: La división generó 3 partes; se esperaban 2` | En `dividir_columna`, alguna fila tiene el separador más veces. | Revisa esas filas o ajusta los nombres. |
| `ValueError: Componente no admitido` | En `crear_columna_desde_fecha` el componente está mal escrito. | Usa `anio`, `mes`, `dia`, `dia_semana`, `hora` o `trimestre`. |
| Los montos salen 100 veces más grandes o pequeños | Formato de número equivocado. | Revisa `decimal` y `miles` (sección 4.4). |
| Casi todas las fechas quedan vacías (`NaT`) | El `formato` no coincide con el archivo. | Mira unas filas y ajusta `formato`. |
| Día y mes intercambiados | Fecha ambigua (`03/04/2024`). | Indica `formato` o `dayfirst`. |
| `validar_rango_numerico` marca todo | Se indicó solo `maximo`. | Indica también `minimo`. |
| `UnicodeDecodeError` o acentos como `�` | Codificación del archivo. | `leer_csv(..., encoding="latin-1")` |
| Aviso `FutureWarning: Downcasting behavior...` | Aviso interno de pandas. | No es un error; se puede ignorar. |
| Escribí la función pero nada cambió | No guardaste el resultado. | Escribe `df = funcion(df, ...)`. |

---

## 10. Tabla de referencia rápida

| Necesito… | Función |
|---|---|
| Leer un CSV | `leer_csv(ruta, dtype=str)` |
| Guardar un CSV | `guardar_csv(df, ruta)` |
| Ver un resumen de calidad | `resumen_dataframe(df)` |
| Saber qué filas están vacías | `detectar_filas_vacias(df)` |
| Ver duplicados | `reporte_duplicados(df, subset=None)` |
| Limpiar nombres de columnas | `limpiar_nombres_columnas(df)` |
| Quitar espacios de más | `limpiar_espacios_texto(df, columnas)` |
| Minúsculas / sin tildes | `normalizar_texto(df, columnas, minusculas=True, quitar_tildes=True)` |
| Convertir "N/A", "-" en vacío | `estandarizar_nulos(df)` |
| Borrar o reemplazar caracteres | `quitar_caracteres(df, columnas, patron, reemplazo)` |
| Unificar categorías | `normalizar_categorias(df, columnas, mapeo={...})` |
| Texto → número | `convertir_numericos(df, columnas, decimal, miles)` |
| "12,5%" → número | `convertir_porcentajes(df, columnas, escala=1 o 100)` |
| Texto → fecha | `convertir_fechas_texto(df, columnas, formato=...)` |
| Número de Excel → fecha | `convertir_fechas_excel(df, columnas)` |
| Sí/No → True/False | `convertir_booleanos(df, columnas)` |
| Dejar solo dígitos | `extraer_digitos(df, columnas)` |
| Quitar filas vacías | `eliminar_filas_vacias(df)` |
| Quitar columnas vacías | `eliminar_columnas_vacias(df)` |
| Quitar duplicados | `eliminar_duplicados(df, subset=None)` |
| Quitar filas con vacíos | `filtrar_nulos(df, columnas)` |
| Rellenar vacíos | `rellenar_nulos(df, columnas, valor=...)` |
| Renombrar columnas | `renombrar_columnas(df, {"viejo": "nuevo"})` |
| Quedarme con algunas columnas | `seleccionar_columnas(df, columnas)` |
| Mover columnas al inicio | `reordenar_columnas(df, columnas)` |
| Separar una columna | `dividir_columna(df, columna, separador, nombres)` |
| Unir columnas | `combinar_columnas(df, columnas, nueva_columna)` |
| Sacar año/mes/día de una fecha | `crear_columna_desde_fecha(df, fecha, nueva, componente)` |
| Ordenar filas | `ordenar_por_columnas(df, columnas)` |
| Comprobar columnas obligatorias | `validar_columnas(df, obligatorias)` |
| Detectar valores fuera de rango | `validar_rango_numerico(df, columna, minimo, maximo)` |
| Contar valores no permitidos | `contar_valores_fuera_catalogo(df, columna, catalogo)` |
