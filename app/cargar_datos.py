# 1. IMPORTACION DE LIBRERIAS

import pandas as pd
# Para trabajar con tablas de datos (DataFrames).
# Permite leer archivos Excel, CSV, filtrar, buscar y manipular bases de datos en memoria.

import requests
# Para realizar solicitudes a páginas web
# Permitirá descargar automáticamente los datasets actualizados desde las URLs oficiales de PAMI.

from io import BytesIO
# Convierte los datos descargados en un archivo temporal 
# Es necesario porque el archivo se descarga en memoria y no en disco.

from pathlib import Path
# Para manejar rutas de archivos y carpetas.
# Accede a los datasets de respaldo en la carpeta data/ sin importar dónde este instalado el proyecto.


# 2. RUTA BASE DEL PROYECTO
BASE_DIR = Path(__file__).resolve().parent.parent
# __file__ -> tiene la ubicación del archivo
# parent.parent -> va a la carpeta principal del archivo


# 3. CARPETA DONDE ESTAN LOS ARCHIVOS DE RESPALDO
DATA_DIR = BASE_DIR / "data"
# Esto y #2 permiten que el codigo siga funcinando aunque la ruta del proyecto cambie


# 4. URLS OFICIALES DE PAMI
URL_MEDICAMENTOS = "http://datos.pami.org.ar/dataset/b40f7569-3a23-46bf-8a45-dd7cff41e725/resource/92ad6862-af8e-4047-b2cb-4bfef705feb3/download/afiliados20260504_100332.xlsx"
URL_AGENCIAS = "http://datos.pami.org.ar/dataset/6fda9ef9-7dab-4a1a-879d-a963f05c7fde/resource/f6e33659-84c9-4e97-a271-f9023c8c891c/download/listado-de-agencias-.xlsx"


# 5. ARCHIVOS LOCALES DE RESPALDO
ARCHIVO_MEDICAMENTOS_LOCAL = DATA_DIR / "Dataset_Medicamentos_PAMI.xlsx"
ARCHIVO_AGENCIAS_LOCAL = DATA_DIR / "Dataset_Agencias_PAMI.xlsx"


# 6. DESARROLLO DE CODIGO PARA LA CARGA DE DATOS

def cargar_excel_desde_url(url):
    """
    Función genérica para descargar un archivo Excel desde una URL.

    Proceso:
        1. Realiza una solicitud HTTP a la URL.
        2. Verifica que la descarga haya sido exitosa.
        3. Convierte el contenido descargado en un archivo temporal.
        4. Lee el Excel con pandas.
        5. Devuelve un DataFrame.
    """

    # a. Descarga el archivo desde Internet
    respuesta = requests.get(url, timeout=20)

    # b. Genera un error si la descarga falló
    respuesta.raise_for_status()

    # c. Convierte el contenido descargado en un archivo temporal
    archivo_excel = BytesIO(respuesta.content)

    # d. Lee el Excel y lo transforma en DataFrame
    df = pd.read_excel(archivo_excel)

    # Devuelve el DataFrame obtenido
    return df

# 6.1. CARGA DE DATASETS DE MEDICAMENTOS PAMI (URL OFICIAL Y RESPALDO LOCAL)

def cargar_medicamentos():
    """
    Carga la base de medicamentos de PAMI.

    Estrategia utilizada:
        - Primero intenta descargar el archivo desde la URL oficial.
        - Si la descarga falla, utiliza el archivo local de respaldo.

    Esto permite trabajar siempre con la información más actualizada
    posible sin perder funcionalidad cuando la web de PAMI no responde.
    """

# a. Se intenta obtener la base desde la URL oficial
    try:
        df_medicamentos = cargar_excel_desde_url(URL_MEDICAMENTOS)
        print("Base de medicamentos cargada desde la URL oficial de PAMI.")

# b. Si falla la descarga usamos el respaldo local
    except Exception as error:
        print("No se pudo cargar la base de medicamentos desde la URL oficial.")
        print("Se usará el archivo local de respaldo.")
        print("Error:", error)

# c. Se lo lee como dataframe
        df_medicamentos = pd.read_excel(ARCHIVO_MEDICAMENTOS_LOCAL)

# d. Y se devuelve el dataFrame cargado
    return df_medicamentos


# 6.2. CARGA DE DATASETS DE AGENCIAS PAMI (URL OFICIAL Y RESPALDO LOCAL)

def cargar_agencias():
    """
    Carga la base de agencias de PAMI.

    Estrategia utilizada:
        - Primero intenta descargar la versión oficial actualizada.
        - Si ocurre algún error, utiliza el archivo local de respaldo.

    De esta manera el sistema sigue funcionando aun cuando la
    fuente oficial no esté disponible.
    """

# a. Se intenta obtener la base desde la URL oficial
    try:
        df_agencias = cargar_excel_desde_url(URL_AGENCIAS)
        print("Base de agencias cargada desde la URL oficial de PAMI.")

# b. Si falla la descarga usamos el respaldo local
    except Exception as error:
        print("No se pudo cargar la base de agencias desde la URL oficial.")
        print("Se usará el archivo local de respaldo.")
        print("Error:", error)

# c. Se lo lee como dataframe
        df_agencias = pd.read_excel(ARCHIVO_AGENCIAS_LOCAL)

# d. Y se devuelve el dataFrame cargado
    return df_agencias