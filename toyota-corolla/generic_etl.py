"""
CATÁLOGO GENERAL DE FUNCIONES ETL PARA ARCHIVOS CSV
===================================================

Las funciones son genéricas: no contienen reglas de negocio ni suponen una estructura
específica de datos.

Dependencias:
    pip install pandas

Uso rápido:
    import pandas as pd
    from generic_etl import *

    df = leer_csv("datos.csv")
    df = limpiar_nombres_columnas(df)
    df = limpiar_texto(df)
    df = convertir_fechas_excel(df, ["fecha_excel"])
    df = convertir_fechas_texto(df, ["fecha_texto"], dayfirst=True)
    df = convertir_porcentajes(df, ["tasa"])
    df = eliminar_duplicados(df)
    guardar_csv(df, "datos_limpios.csv")

Notas:
- Las funciones que reciben `columnas=None` trabajan sobre todas las columnas compatibles.
- Las conversiones inválidas normalmente producen pd.NA, NaN o NaT; no inventan valores.
- En fechas numéricas de Excel se asume el sistema de fechas habitual de Excel
  para Windows (origen 1899-12-30). Verifique el sistema de origen de su archivo.
- Para fechas escritas como texto, indique `dayfirst=True` o `False` cuando conozca
  el formato. Fechas como 03/04/2024 son ambiguas si no se conoce el orden.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path
from typing import Iterable, Literal, Optional, Sequence, cast

import pandas as pd

# ---------------------------------------------------------------------------
# 1. Lectura y escritura
# ---------------------------------------------------------------------------


def leer_csv(
    ruta,
    *,
    sep=None,
    encoding="utf-8",
    decimal=".",
    thousands=None,
    dtype=None,
    parse_dates=False,
    **kwargs,
):
    """Lee un CSV. Si sep=None, intenta detectar el separador con csv.Sniffer."""
    ruta = Path(ruta)
    if sep is None:
        muestra = ruta.read_text(encoding=encoding, errors="replace")[:8192]
        try:
            sep = csv.Sniffer().sniff(muestra, delimiters=",;|\t").delimiter
        except csv.Error:
            sep = ","
    return pd.read_csv(
        ruta,
        sep=sep,
        encoding=encoding,
        decimal=decimal,
        thousands=thousands,
        dtype=dtype,
        parse_dates=parse_dates,
        **kwargs,
    )


def guardar_csv(df, ruta, *, encoding="utf-8-sig", sep=",", index=False):
    """Guarda un DataFrame en CSV; utf-8-sig facilita abrirlo en Excel."""
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=index, encoding=encoding, sep=sep)


# ---------------------------------------------------------------------------
# 2. Inspección y diagnóstico
# ---------------------------------------------------------------------------


def resumen_dataframe(df):
    """Devuelve dimensiones, tipos, nulos, únicos y porcentaje de nulos."""
    return pd.DataFrame(
        {
            "tipo": df.dtypes.astype(str),
            "nulos": df.isna().sum(),
            "porcentaje_nulos": (df.isna().mean() * 100).round(2),
            "valores_unicos": df.nunique(dropna=True),
        }
    ).sort_values("porcentaje_nulos", ascending=False)


def detectar_filas_vacias(df):
    """Devuelve las filas cuyos valores son todos nulos o espacios."""
    temporal = df.replace(r"^\s*$", pd.NA, regex=True)
    return temporal.isna().all(axis=1)


def reporte_duplicados(df, subset=None):
    """Resume cuántas filas están duplicadas según todas las columnas o subset."""
    mascara = df.duplicated(subset=subset, keep=False)
    return {
        "cantidad_filas_duplicadas": int(mascara.sum()),
        "filas_duplicadas": df.loc[mascara].copy(),
    }


# ---------------------------------------------------------------------------
# 3. Limpieza estructural y de texto
# ---------------------------------------------------------------------------


def limpiar_nombres_columnas(df, *, minusculas=True, reemplazo="_"):
    """Quita espacios, tildes y símbolos de los nombres de columnas."""
    resultado = df.copy()
    nombres = []
    for nombre in resultado.columns:
        texto = str(nombre).strip()
        texto = unicodedata.normalize("NFKD", texto)
        texto = "".join(c for c in texto if not unicodedata.combining(c))
        texto = re.sub(r"[^\w]+", reemplazo, texto, flags=re.UNICODE)
        texto = re.sub(rf"{re.escape(reemplazo)}+", reemplazo, texto).strip(reemplazo)
        nombres.append(texto.lower() if minusculas else texto)
    resultado.columns = nombres
    return resultado


def limpiar_espacios_texto(df, columnas=None):
    """Recorta extremos y reemplaza secuencias de espacios por un espacio."""
    resultado = df.copy()
    columnas = columnas or resultado.select_dtypes(include=["object", "string"]).columns
    for col in columnas:
        resultado[col] = (
            resultado[col]
            .astype("string")
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )
    return resultado


def normalizar_texto(df, columnas=None, *, minusculas=False, quitar_tildes=False):
    """Normaliza texto opcionalmente a minúsculas y/o sin tildes."""
    resultado = limpiar_espacios_texto(df, columnas)
    columnas = columnas or resultado.select_dtypes(include=["object", "string"]).columns
    for col in columnas:
        serie = resultado[col].astype("string")
        if minusculas:
            serie = serie.str.lower()
        if quitar_tildes:
            serie = serie.map(
                lambda x: (
                    unicodedata.normalize("NFKD", x)
                    .encode("ascii", "ignore")
                    .decode("ascii")
                    if pd.notna(x)
                    else x
                )
            )
        resultado[col] = serie
    return resultado


def estandarizar_nulos(df, valores=None, *, columnas=None, ignorar_mayusculas=True):
    """Convierte marcadores frecuentes (''/'N/A'/'null', etc.) en valores nulos."""
    resultado = df.copy()
    valores = (
        valores
        if valores is not None
        else ["", " ", "NA", "#N/A", "N/A", "N.A.", "NULL", "NONE", "NAN", "-", "--"]
    )
    columnas = columnas or resultado.columns
    conjunto = {
        str(v).strip().casefold() if ignorar_mayusculas else str(v).strip()
        for v in valores
    }
    for col in columnas:
        if pd.api.types.is_object_dtype(resultado[col]) or pd.api.types.is_string_dtype(
            resultado[col]
        ):
            clave = resultado[col].astype("string").str.strip()
            if ignorar_mayusculas:
                mascara = clave.str.casefold().isin(conjunto)
            else:
                mascara = clave.isin(conjunto)
            resultado.loc[mascara.fillna(False), col] = pd.NA
    return resultado


def quitar_caracteres(df, columnas, patron, reemplazo=""):
    """Aplica una expresión regular a columnas de texto seleccionadas."""
    resultado = df.copy()
    for col in columnas:
        resultado[col] = (
            resultado[col].astype("string").str.replace(patron, reemplazo, regex=True)
        )
    return resultado


def normalizar_categorias(df, columnas, *, mapeo=None, minusculas=True):
    """Homogeneiza categorías de texto; mapeo permite definir equivalencias."""
    resultado = df.copy()
    mapeo = mapeo or {}
    mapeo_normalizado = {str(k).casefold(): v for k, v in mapeo.items()}
    for col in columnas:
        serie = resultado[col].astype("string").str.strip()
        if minusculas:
            serie = serie.str.casefold()
        resultado[col] = serie.map(
            lambda x: mapeo_normalizado.get(x, x) if pd.notna(x) else x
        )
    return resultado


# ---------------------------------------------------------------------------
# 4. Conversión de tipos y formatos
# ---------------------------------------------------------------------------


def convertir_numericos(
    df,
    columnas,
    *,
    decimal=",",
    miles=".",
    errores: Literal["raise", "coerce"] = "coerce",
):
    """
    Convierte texto a número admitiendo separadores decimales y de miles.
    Ejemplo formato latino: decimal=',' y miles='.'.
    Ejemplo formato anglosajón: decimal='.' y miles=','.
    """
    resultado = df.copy()
    for col in columnas:
        serie = resultado[col].astype("string").str.strip()
        if miles:
            serie = serie.str.replace(miles, "", regex=False)
        if decimal and decimal != ".":
            serie = serie.str.replace(decimal, ".", regex=False)
        serie = serie.str.replace(r"[^\d.eE+-]", "", regex=True)
        resultado[col] = pd.to_numeric(serie, errors=errores)
    return resultado


def convertir_porcentajes(df, columnas, *, decimal=",", miles=".", escala=1):
    """
    Convierte '12,5%' en 12.5 (escala=1) o 0.125 (escala=100).
    El símbolo % se elimina. Los valores sin % también se convierten.
    """
    resultado = df.copy()
    for col in columnas:
        serie = (
            resultado[col]
            .astype("string")
            .str.strip()
            .str.replace("%", "", regex=False)
        )
        if miles:
            serie = serie.str.replace(miles, "", regex=False)
        if decimal and decimal != ".":
            serie = serie.str.replace(decimal, ".", regex=False)
        resultado[col] = pd.to_numeric(serie, errors="coerce") / escala
    return resultado

def convertir_fechas_excel(
    df,
    columnas,
    *,
    origen="1899-12-30",
    unidad: Literal["D", "s", "ms", "us", "ns"] = "D",
):
    """
    Convierte números seriales de Excel a fecha/hora.
    Para fechas de Excel habituales: origen='1899-12-30', unidad='D'.
    """
    resultado = df.copy()
    for col in columnas:
        valores = pd.to_numeric(resultado[col], errors="coerce")
        resultado[col] = pd.to_datetime(
            valores, unit=unidad, origin=origen, errors="coerce"
        )
    return resultado


def convertir_fechas_texto(
    df, columnas, *, formato=None, dayfirst=True, yearfirst=False
):
    """
    Convierte fechas escritas como texto.
    Si se conoce el formato, se recomienda especificarlo, p. ej. '%d-%m-%Y'.
    dayfirst=True interpreta 03/04/2024 como 3 de abril.
    """
    resultado = df.copy()
    for col in columnas:
        resultado[col] = pd.to_datetime(
            resultado[col],
            format=formato,
            errors="coerce",
            dayfirst=dayfirst,
            yearfirst=yearfirst,
        )
    return resultado


def convertir_booleanos(df, columnas, *, verdaderos=None, falsos=None):
    """Convierte representaciones comunes de sí/no a booleanos anulables."""
    resultado = df.copy()
    verdaderos = {
        str(x).casefold()
        for x in (verdaderos or ["si", "sí", "yes", "true", "1", "1.0", "verdadero"])
    }
    falsos = {
        str(x).casefold() for x in (falsos or ["no", "false", "0", "0.0", "falso"])
    }
    for col in columnas:
        serie = resultado[col].astype("string").str.strip().str.casefold()
        convertido = serie.map(
            lambda x: True if x in verdaderos else (False if x in falsos else pd.NA)
        )
        resultado[col] = convertido.astype("boolean")
    return resultado


def extraer_digitos(df, columnas):
    """Conserva solo dígitos en columnas indicadas (útil para códigos/teléfonos)."""
    resultado = df.copy()
    for col in columnas:
        resultado[col] = (
            resultado[col].astype("string").str.replace(r"\D+", "", regex=True)
        )
    return resultado


# ---------------------------------------------------------------------------
# 5. Filtrado, duplicados y valores faltantes
# ---------------------------------------------------------------------------


def eliminar_filas_vacias(df):
    """Elimina filas completamente vacías (incluidos campos con solo espacios)."""
    mascara = detectar_filas_vacias(df)
    return df.loc[~mascara].copy()


def eliminar_columnas_vacias(df):
    """Elimina columnas cuyos valores son todos nulos o espacios."""
    temporal = df.replace(r"^\s*$", pd.NA, regex=True)
    return df.loc[:, ~temporal.isna().all(axis=0)].copy()


def eliminar_duplicados(df, subset=None, *, conservar="first"):
    """Elimina duplicados por todas las columnas o por las indicadas."""
    return df.drop_duplicates(subset=subset, keep=conservar).copy()


def filtrar_nulos(df, columnas, *, como="cualquiera"):
    """Filtra filas con nulos: como='cualquiera' o como='todos'."""
    mascara = (
        df[columnas].isna().any(axis=1)
        if como == "cualquiera"
        else df[columnas].isna().all(axis=1)
    )
    return df.loc[~mascara].copy()


def rellenar_nulos(df, columnas, *, metodo="valor", valor=None):
    """Rellena nulos con un valor fijo o con forward/backward fill."""
    resultado = df.copy()
    for col in columnas:
        if metodo == "valor":
            resultado[col] = resultado[col].fillna(valor)
        elif metodo == "anterior":
            resultado[col] = resultado[col].ffill()
        elif metodo == "siguiente":
            resultado[col] = resultado[col].bfill()
        else:
            raise ValueError("metodo debe ser 'valor', 'anterior' o 'siguiente'")
    return resultado


# ---------------------------------------------------------------------------
# 6. Transformaciones de columnas
# ---------------------------------------------------------------------------


def renombrar_columnas(df, mapeo):
    """Renombra columnas usando un diccionario {nombre_actual: nombre_nuevo}."""
    return df.rename(columns=mapeo).copy()


def seleccionar_columnas(df, columnas):
    """Devuelve solo las columnas indicadas que existan en el DataFrame."""
    inexistentes = [c for c in columnas if c not in df.columns]
    if inexistentes:
        raise KeyError(f"Columnas inexistentes: {inexistentes}")
    return df.loc[:, columnas].copy()


def reordenar_columnas(df, columnas_primero):
    """Coloca primero las columnas indicadas y conserva después las restantes."""
    faltantes = [c for c in columnas_primero if c not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas inexistentes: {faltantes}")
    resto = [c for c in df.columns if c not in columnas_primero]
    return df[columnas_primero + resto].copy()


def dividir_columna(df, columna, separador, nombres, *, expandir=True):
    """Divide una columna de texto en varias columnas."""
    resultado = df.copy()
    partes = resultado[columna].astype("string").str.split(separador, expand=expandir)
    if partes.shape[1] != len(nombres):
        raise ValueError(
            f"La división generó {partes.shape[1]} partes; se esperaban {len(nombres)}"
        )
    partes.columns = nombres
    for col in nombres:
        resultado[col] = partes[col]
    return resultado


def combinar_columnas(df, columnas, nueva_columna, *, separador=" ", omitir_nulos=True):
    """Combina varias columnas de texto en una nueva columna."""
    resultado = df.copy()
    datos = resultado[columnas].astype("string")
    if omitir_nulos:
        resultado[nueva_columna] = datos.fillna("").apply(
            lambda fila: separador.join(x for x in fila if x.strip()), axis=1
        )
    else:
        resultado[nueva_columna] = datos.agg(separador.join, axis=1)
    return resultado


def crear_columna_desde_fecha(df, columna_fecha, nueva_columna, componente):
    """Extrae año, mes, día, día de semana u hora desde una fecha."""
    resultado = df.copy()
    fecha = pd.to_datetime(resultado[columna_fecha], errors="coerce")
    componentes = {
        "anio": fecha.dt.year,
        "año": fecha.dt.year,
        "mes": fecha.dt.month,
        "dia": fecha.dt.day,
        "día": fecha.dt.day,
        "dia_semana": fecha.dt.dayofweek,
        "hora": fecha.dt.hour,
        "trimestre": fecha.dt.quarter,
    }
    if componente not in componentes:
        raise ValueError(f"Componente no admitido. Opciones: {list(componentes)}")
    resultado[nueva_columna] = componentes[componente]
    return resultado


def ordenar_por_columnas(df, columnas, *, ascendente=True):
    """Ordena filas por una o varias columnas."""
    return df.sort_values(by=columnas, ascending=ascendente).copy()


# ---------------------------------------------------------------------------
# 7. Validaciones genéricas
# ---------------------------------------------------------------------------


def validar_columnas(df, obligatorias):
    """Comprueba que existan columnas requeridas; devuelve las faltantes."""
    return [col for col in obligatorias if col not in df.columns]


def validar_rango_numerico(df, columna, minimo=None, maximo=None):
    """Devuelve una máscara booleana de valores numéricos fuera del rango."""
    valores = pd.to_numeric(df[columna], errors="coerce")
    mascara = valores.notna()
    if minimo is not None:
        mascara &= valores < minimo
    if maximo is not None:
        mascara |= valores > maximo
    return mascara


def contar_valores_fuera_catalogo(df, columna, catalogo):
    """Cuenta valores no nulos que no pertenecen a un catálogo permitido."""
    serie = df[columna].astype("string").str.strip()
    permitidos = {str(x).strip() for x in catalogo}
    return int((serie.notna() & ~serie.isin(permitidos)).sum())
