# 1. IMPORTACIÓN DE LIBRERÍAS Y FUNCIONES NECESARIAS

import pandas as pd
# Para trabajar con tablas de datos.
# Se usa para limpiar, filtrar, seleccionar y sumar medicamentos.

# Import para cuando el proyecto se ejecute como paquete completo
# from app.cargar_datos import cargar_medicamentos
# Import temporal para pruebas locales
from cargar_datos import cargar_medicamentos
# Importa la función creada en cargar_datos.py.
# Esa función carga la base de medicamentos desde la URL oficial de PAMI
# o desde el archivo local de respaldo si la URL falla.


# 2. CARGA Y LIMPIEZA DE LA BASE DE MEDICAMENTOS

def obtener_medicamentos_limpios():
    """
    Carga la base de medicamentos y realiza una limpieza inicial.

    Esta función reemplaza la parte del notebook donde:
    - Se cargaba el dataset;
    - Se limpiaban nombres de columnas;
    - Se quitaban espacios;
    - Se convertía COPAGO en número;
    - Se renombraba COPAGO como A_PAGAR.
    """

    # a. Cargar la base desde cargar_datos.py
    df_medicamentos = cargar_medicamentos()

    # b. Crear una copia para no modificar el dataset original
    df_medicamentos_limpio = df_medicamentos.copy()

    # c. Limpiar nombres de columnas
    # Se eliminan espacios y se pasan a mayúscula para evitar errores
    df_medicamentos_limpio.columns = (df_medicamentos_limpio.columns.str.strip().str.upper())

    # d. Limpiar espacios en columnas de texto
    for columna in df_medicamentos_limpio.select_dtypes(include="object"):
        df_medicamentos_limpio[columna] = (df_medicamentos_limpio[columna].astype(str).str.strip())

    # e. Convertir COPAGO en número si la columna existe
    if "COPAGO" in df_medicamentos_limpio.columns:

        df_medicamentos_limpio["COPAGO"] = (df_medicamentos_limpio["COPAGO"]
                                            .astype(str)
                                            .str.replace("$", "", regex=False)
                                            .str.replace(",", "", regex=False)
                                            .str.strip())

        df_medicamentos_limpio["COPAGO"] = pd.to_numeric(df_medicamentos_limpio["COPAGO"],errors="coerce")

    # f. Renombrar COPAGO como A_PAGAR
        df_medicamentos_limpio = df_medicamentos_limpio.rename(columns={"COPAGO": "A_PAGAR"})

    return df_medicamentos_limpio


# 3. FUNCIÓN REUTILIZABLE DE BÚSQUEDA DE MEDICAMENTOS

def buscar_medicamento(busqueda, df_medicamentos):
    """
    Busca medicamentos a partir del texto ingresado por el usuario.

    La búsqueda se realiza sobre varias columnas:
    - DROGA
    - MARCA
    - PRESENTACION
    - LABORATORIO

    Ejemplo:
    Si el usuario escribe:
    'indalten amlodipina 10'

    El sistema busca filas donde aparezcan todas esas palabras,
    aunque estén distribuidas en distintas columnas.
    """

    # a. Estandarizar la búsqueda
    busqueda = str(busqueda).strip().lower()

    # b. Si la búsqueda está vacía, devuelve un dataframe vacío
    if busqueda == "":
        return pd.DataFrame()

    # c. Separar la búsqueda en palabras
    palabras = busqueda.split()

    # d. Columnas donde se realizará la búsqueda
    columnas_busqueda = ["DROGA","MARCA","PRESENTACION","LABORATORIO"]

    # e. Verificar qué columnas existen realmente en el dataset
    columnas_existentes = [columna for columna in columnas_busqueda
                           if columna in df_medicamentos.columns]

    # f. Crear copia para no modificar la base original
    df = df_medicamentos.copy()

    # g. Crear columna auxiliar que une los datos útiles de cada fila
    df["TEXTO_BUSQUEDA"] = (df[columnas_existentes]
                            .astype(str)
                            .agg(" ".join, axis=1)
                            .str.lower())

    # h. Filtrar filas que contengan todas las palabras buscadas
    resultado = df[df["TEXTO_BUSQUEDA"].apply(lambda texto: all(palabra in texto for palabra in palabras))]

    # i. Eliminar columna auxiliar antes de devolver el resultado
    resultado = resultado.drop(columns=["TEXTO_BUSQUEDA"])

    return resultado


# 4. PREPARAR RESULTADOS PARA MOSTRAR EN LA INTERFAZ

def preparar_opciones_medicamentos(resultado_busqueda):
    """
    Prepara los medicamentos encontrados para mostrarlos en Streamlit.

    En el notebook se mostraban con display().
    En el sistema final se mostrarán en listas desplegables o tablas.
    """

    # a. Columnas útiles para que el usuario identifique su medicamento
    columnas_mostrar = ["DROGA","MARCA","PRESENTACION","LABORATORIO","COBERTURA","A_PAGAR"]

    # b. Usar solamente las columnas que existan en la base
    columnas_existentes = [columna for columna in columnas_mostrar
                           if columna in resultado_busqueda.columns]

    # c. Crear tabla simplificada
    opciones = resultado_busqueda[columnas_existentes].copy()

    # d. Reiniciar índice para que sea más fácil de leer
    opciones = opciones.reset_index(drop=True)

    return opciones


# 5. CREAR TEXTO PARA LISTAS DESPLEGABLES

def crear_texto_opcion_medicamento(fila):
    """
    Crea un texto claro para mostrar cada medicamento en una lista desplegable.

    Esto reemplaza la selección por número de índice que usábamos en Colab.
    """

    droga = fila.get("DROGA", "")
    marca = fila.get("MARCA", "")
    presentacion = fila.get("PRESENTACION", "")
    laboratorio = fila.get("LABORATORIO", "")

    texto = f"{marca} | {droga} | {presentacion} | {laboratorio}"

    return texto


# 6. CALCULAR TOTAL A PAGAR

def calcular_total_medicamentos(df_medicamentos_seleccionados):
    """
    Suma el total a pagar por los medicamentos seleccionados.

    En el notebook esto se hacía con:
    total_a_pagar = df_seleccionados["A_PAGAR"].sum()
    """

    # a. Si no hay medicamentos seleccionados, el total es 0
    if df_medicamentos_seleccionados.empty:
        return 0

    # b. Verificar que exista la columna A_PAGAR
    if "A_PAGAR" not in df_medicamentos_seleccionados.columns:
        return 0

    # c. Sumar el gasto total
    total = df_medicamentos_seleccionados["A_PAGAR"].sum()

    return total


# 7. ARMAR RESUMEN FINAL DE MEDICAMENTOS

def armar_resumen_medicamentos(medicamentos_seleccionados):
    """
    Recibe una lista de medicamentos seleccionados y la convierte en dataframe.

    Esta función permite construir la tabla final que después verá el usuario.
    """

    # a. Convertir lista en dataframe
    df_seleccionados = pd.DataFrame(medicamentos_seleccionados)

    # b. Si no hay medicamentos seleccionados, devolver tabla vacía y total 0
    if df_seleccionados.empty:
        return df_seleccionados, 0

    # c. Calcular total a pagar
    total_a_pagar = calcular_total_medicamentos(df_seleccionados)

    return df_seleccionados, total_a_pagar