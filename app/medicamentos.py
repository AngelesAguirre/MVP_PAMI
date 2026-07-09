# 1. IMPORTACIÓN DE LIBRERÍAS Y FUNCIONES NECESARIAS

import pandas as pd
# Para trabajar con tablas de datos.
# Se usa para limpiar, filtrar, seleccionar y sumar medicamentos.

import unicodedata
# Permite normalizar texto.
# En este caso lo usamos para quitar acentos y tildes.

# Import para cargar la base de medicamentos.
# El try/except permite que funcione tanto:
# - cuando ejecutamos Streamlit desde la raíz del proyecto;
# - como cuando probamos módulos desde la carpeta app.

try:
    from app.cargar_datos import cargar_medicamentos
except ModuleNotFoundError:
    from cargar_datos import cargar_medicamentos

# Importa la función creada en cargar_datos.py.
# Esa función carga la base de medicamentos desde la URL oficial de PAMI o desde el archivo local de respaldo si la URL falla.


# 2. FUNCIÓN PARA NORMALIZAR TEXTO

def normalizar_texto(texto):
    """
    Normaliza un texto para mejorar la búsqueda.
    Esta función:
    - Convierte el texto a string;
    - Pasa todo a minúsculas;
    - Quita espacios al inicio y al final;
    - Elimina acentos y tildes.
    Esto permite que el sistema encuentre medicamentos aunque
    el usuario escriba sin acentos o con acentos.
    """

    # a. Convertir el valor a texto
    texto = str(texto)

    # b. Pasar a minúsculas y quitar espacios de los extremos
    texto = texto.lower().strip()

    # c. Descomponer caracteres acentuados
    # Por ejemplo:"á" se separa en "a" + acento.
    texto_normalizado = unicodedata.normalize("NFKD", texto)

    # d. Reconstruir el texto eliminando las marcas de acento
    texto_sin_acentos = "".join(caracter
                                for caracter in texto_normalizado
                                if not unicodedata.combining(caracter))
    return texto_sin_acentos


# 3. CARGA Y LIMPIEZA DE LA BASE DE MEDICAMENTOS

def obtener_medicamentos_limpios():
    """
    Carga la base de medicamentos y realiza una limpieza inicial.
    Esta función reemplaza la parte del notebook donde:
    - Se cargaba el dataset;
    - Se limpiaban nombres de columnas;
    - Se quitaban espacios;
    - Se convertía COPAGO en número;
    - Se renombraba COPAGO como A_PAGAR;
    - Se normalizaban textos para que la búsqueda no dependa de acentos.
    """

    # a. Cargar la base desde cargar_datos.py
    df_medicamentos = cargar_medicamentos()

    # b. Crear una copia para no modificar el dataset original
    df_medicamentos_limpio = df_medicamentos.copy()

    # c. Limpiar nombres de columnas
    # Se eliminan espacios y se pasan a mayúscula para evitar errores.
    df_medicamentos_limpio.columns = (df_medicamentos_limpio.columns
                                      .str.strip()
                                      .str.upper())

    # d. Limpiar espacios en columnas de texto
    for columna in df_medicamentos_limpio.select_dtypes(include="object"):
        df_medicamentos_limpio[columna] = (df_medicamentos_limpio[columna]
                                           .astype(str)
                                           .str.strip())

    # e. Quitar acentos de las columnas de texto originales
    # Esto modifica las columnas que verá el usuario.
    # Por ejemplo: "insulina aspártica" pasará a verse como "insulina aspartica".
    # Se toma esta decisión para que la base quede estandarizada y no dependa del uso de tildes.
    for columna in df_medicamentos_limpio.select_dtypes(include="object"):
        df_medicamentos_limpio[columna] = (df_medicamentos_limpio[columna]
                                           .apply(normalizar_texto))

    # f. Convertir COPAGO en número si la columna existe
    if "COPAGO" in df_medicamentos_limpio.columns:

        df_medicamentos_limpio["COPAGO"] = (df_medicamentos_limpio["COPAGO"]
                                            .astype(str)
                                            .str.replace("$", "", regex=False)
                                            .str.replace(",", "", regex=False)
                                            .str.strip())

        df_medicamentos_limpio["COPAGO"] = pd.to_numeric(df_medicamentos_limpio["COPAGO"],
                                                         errors="coerce")

        # g. Renombrar COPAGO como A_PAGAR
        df_medicamentos_limpio = df_medicamentos_limpio.rename(columns={"COPAGO": "A_PAGAR"})

    return df_medicamentos_limpio


# 4. FUNCIÓN REUTILIZABLE DE BÚSQUEDA DE MEDICAMENTOS

def buscar_medicamento(busqueda, df_medicamentos):
    """
    Busca medicamentos a partir del texto ingresado por el usuario.
    La búsqueda se realiza sobre varias columnas:
    - DROGA
    - MARCA
    - PRESENTACION
    - LABORATORIO
    La búsqueda ahora es insensible a acentos.
    Ejemplo:
        Si el dataset contiene:
            "atorvastatin calcico"
        El usuario puede escribir:
            "atorvastatin cálcico"
            "atorvastatin calcico"
            "ATORVASTATIN CALCICO"
        Y el sistema debería devolver el mismo resultado.
    """

    # a. Estandarizar la búsqueda del usuario
    # Se usa normalizar_texto() para:
    # - pasar a minúscula;
    # - quitar espacios;
    # - eliminar acentos.
    busqueda = normalizar_texto(busqueda)

    # b. Si la búsqueda está vacía, devuelve un dataframe vacío
    if busqueda == "":
        return pd.DataFrame()

    # c. Separar la búsqueda en palabras
    # Ejemplo:"atorvastatin calcico" -> ["atorvastatin", "calcico"]
    palabras = busqueda.split()

    # d. Columnas donde se realizará la búsqueda
    columnas_busqueda = ["DROGA","MARCA","PRESENTACION","LABORATORIO"]

    # e. Verificar qué columnas existen realmente en el dataset
    columnas_existentes = [columna
                           for columna in columnas_busqueda
                           if columna in df_medicamentos.columns]

    # f. Crear copia para no modificar la base original
    df = df_medicamentos.copy()

    # g. Crear columna auxiliar que une los datos útiles de cada fila
    # Aunque la base ya fue normalizada en obtener_medicamentos_limpios(), se normalizar_texto por seguridad.
    # Esto evita problemas si en algún momento se llama a buscar_medicamento() con una base no normalizada.
    df["TEXTO_BUSQUEDA"] = (df[columnas_existentes]
                            .astype(str)
                            .agg(" ".join, axis=1)
                            .apply(normalizar_texto))

    # h. Filtrar filas que contengan todas las palabras buscadas
    # all() exige que todas las palabras escritas por el usuario aparezcan dentro del texto de búsqueda.
    resultado = df[df["TEXTO_BUSQUEDA"].apply(lambda texto: all(palabra in texto
                                                                for palabra in palabras))]

    # i. Eliminar columna auxiliar antes de devolver el resultado
    resultado = resultado.drop(columns=["TEXTO_BUSQUEDA"])

    return resultado

# 5. PREPARAR RESULTADOS PARA MOSTRAR EN LA INTERFAZ

def preparar_opciones_medicamentos(resultado_busqueda):
    """
    Prepara los medicamentos encontrados para mostrarlos en Streamlit.
    Esta función toma únicamente las columnas útiles para el usuario,
    reinicia el índice y devuelve una tabla lista para mostrar.
    El índice comienza desde 1 para facilitar la lectura,
    ya que resulta más natural para el usuario que comenzar desde 0.
    """

    # a. Columnas que resultan útiles para identificar correctamente el medicamento encontrado.
    columnas_mostrar = ["DROGA","MARCA","PRESENTACION","LABORATORIO","COBERTURA","A_PAGAR"]

    # b. Verificar cuáles de esas columnas existen realmente
    # dentro del dataset cargado.
    columnas_existentes = [columna for columna in columnas_mostrar
                           if columna in resultado_busqueda.columns]

    # c. Crear una copia solamente con esas columnas.
    opciones = resultado_busqueda[columnas_existentes].copy()

    # d. Reiniciar el índice para evitar conservar el índice
    # original del dataset.
    opciones = opciones.reset_index(drop=True)

    return opciones


# 6. CREAR TEXTO PARA LISTAS DESPLEGABLES

def crear_texto_opcion_medicamento(fila):
    """
    Genera un texto descriptivo para cada medicamento.
    Este texto es el que aparecerá dentro de los selectbox
    o listas desplegables de Streamlit.
    Se incluyen:
    - Marca
    - Droga
    - Presentación
    - Laboratorio
    para facilitar la identificación del medicamento.
    """

    droga = fila.get("DROGA", "")
    marca = fila.get("MARCA", "")
    presentacion = fila.get("PRESENTACION", "")
    laboratorio = fila.get("LABORATORIO", "")

    texto = (f"{marca} | "f"{droga} | "f"{presentacion} | "f"{laboratorio}")

    return texto


# 7. CALCULAR TOTAL A PAGAR

def calcular_total_medicamentos(df_medicamentos_seleccionados):
    """
    Calcula el gasto total en medicamentos.

    El cálculo consiste simplemente en sumar la columna
    A_PAGAR de todos los medicamentos seleccionados.

    Si la tabla está vacía o no existe la columna,
    devuelve cero.
    """

    # a. Si no hay medicamentos seleccionados, no existe gasto.
    if df_medicamentos_seleccionados.empty:
        return 0

    # b. Verificar que exista la columna A_PAGAR.
    if "A_PAGAR" not in df_medicamentos_seleccionados.columns:
        return 0

    # c. Sumar todos los importes.
    total = df_medicamentos_seleccionados["A_PAGAR"].sum()

    return total


# 8. ARMAR RESUMEN FINAL DE MEDICAMENTOS

def armar_resumen_medicamentos(medicamentos_seleccionados):
    """
    Convierte la lista de medicamentos elegidos por el usuario
    en un DataFrame y calcula automáticamente
    el gasto total.
    Esta función concentra toda la información que luego
    será utilizada por:
    - análisis de gasto;
    - beneficios;
    - PDF;
    - Streamlit.
    """

    # a. Convertir la lista de medicamentos seleccionados en un DataFrame.
    df_seleccionados = pd.DataFrame(medicamentos_seleccionados)

    # b. Si el usuario todavía no seleccionó medicamentos, devolver una tabla vacía y un gasto igual a cero.
    if df_seleccionados.empty:
        return df_seleccionados, 0

    # c. Reiniciar el índice para eliminar los índices originales.
    df_seleccionados = df_seleccionados.reset_index(drop=True)

    # e. Calcular automáticamente el gasto total.
    total_a_pagar = calcular_total_medicamentos(df_seleccionados)

    return df_seleccionados, total_a_pagar