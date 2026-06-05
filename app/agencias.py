# 1. IMPORTACIÓN DE LIBRERÍAS Y FUNCIONES NECESARIAS

import pandas as pd
# Para trabajar con tablas de datos.
# Se usa para limpiar, filtrar y seleccionar agencias.

try:
    from app.cargar_datos import cargar_agencias
except ModuleNotFoundError:
    from cargar_datos import cargar_agencias
# Permite cargar agencias tanto si ejecutamos el proyecto completo
# como si hacemos pruebas locales desde app/main.py.


# 2. CARGA Y LIMPIEZA DE LA BASE DE AGENCIAS

def obtener_agencias_limpias():
    """
    Carga la base de agencias de PAMI y la deja lista para usar.

    Esta función reemplaza la parte del notebook donde:
    - se corregía el encabezado;
    - se eliminaban columnas no utilizadas;
    - se renombraban columnas;
    - se limpiaban espacios;
    - se agrupaban UGL por provincia.
    """

    # a. Cargar la base desde cargar_datos.py
    df_agencias = cargar_agencias()

    # b. Crear copia para no modificar el dataset original
    df_agencias_limpio = df_agencias.copy()

    # c. Corregir encabezado si el Excel trae filas iniciales innecesarias
    if "c_ugl ID" not in df_agencias_limpio.columns:
        df_agencias_limpio.columns = df_agencias_limpio.iloc[1]
        df_agencias_limpio = df_agencias_limpio.iloc[2:].copy()
        df_agencias_limpio = df_agencias_limpio.reset_index(drop=True)

    # d. Limpiar nombres de columnas
    df_agencias_limpio.columns = (df_agencias_limpio.columns
                                  .astype(str)
                                  .str.strip())

    # e. Eliminar columnas que no se usan
    df_agencias_limpio = df_agencias_limpio.drop(
        columns=[columna for columna in ["c_agencia ID", "c_agencia"]
                 if columna in df_agencias_limpio.columns],
        errors="ignore")

    # f. Renombrar columnas para que sean más claras
    df_agencias_limpio = df_agencias_limpio.rename(columns={
        "c_ugl ID": "ID_UGL",
        "c_ugl": "ID_UGL",
        "d_ugl ID": "Ubicacion_Territorial",
        "d_ugl": "Ubicacion_Territorial",
        "d_agencia ID": "Nombre_Agencia",
        "d_agencia": "Nombre_Agencia",
        "localidad_desc": "Localidad",
        "Localidad DESC": "Localidad",
        "domicilio ID": "Domicilio",
        "domicilio": "Domicilio"})

    # g. Limpiar espacios en columnas de texto
    for columna in df_agencias_limpio.select_dtypes(include="object"):
        df_agencias_limpio[columna] = (df_agencias_limpio[columna]
                                       .astype(str)
                                       .str.strip())

    # h. Pasar columnas clave a mayúsculas
    for columna in ["Ubicacion_Territorial", "Localidad", "Nombre_Agencia"]:
        if columna in df_agencias_limpio.columns:
            df_agencias_limpio[columna] = (df_agencias_limpio[columna]
                                           .astype(str)
                                           .str.strip()
                                           .str.upper())

    # i. Crear columna Provincia
    df_agencias_limpio["Provincia"] = df_agencias_limpio["Ubicacion_Territorial"]

    # j. Reagrupar UGL de Buenos Aires y CABA
    ugl_buenos_aires = ["BAHIA BLANCA",
                        "CAPITAL FEDERAL",
                        "LA PLATA",
                        "SAN MARTIN",
                        "LANUS",
                        "MAR DEL PLATA",
                        "MORON",
                        "AZUL",
                        "JUNIN",
                        "LUJAN",
                        "SAN JUSTO",
                        "QUILMES",
                        "CHIVILCOY"]

    df_agencias_limpio.loc[df_agencias_limpio["Ubicacion_Territorial"].isin(ugl_buenos_aires),
                           "Provincia"] = "BUENOS AIRES"

    # k. Reagrupar casos especiales
    df_agencias_limpio.loc[df_agencias_limpio["Ubicacion_Territorial"] == "RIO CUARTO",
                           "Provincia"] = "CORDOBA"

    df_agencias_limpio.loc[df_agencias_limpio["Ubicacion_Territorial"] == "CONCORDIA",
                           "Provincia"] = "ENTRE RIOS"

    return df_agencias_limpio


# 3. OPCIONES PARA LISTAS DESPLEGABLES

def obtener_provincias(df_agencias):
    """
    Devuelve provincias disponibles para el primer selector.
    """

    return (df_agencias["Provincia"]
            .dropna()
            .sort_values()
            .unique()
            .tolist())


def obtener_ubicaciones_por_provincia(df_agencias, provincia):
    """
    Devuelve las UGL/ubicaciones territoriales de una provincia.
    """

    agencias_provincia = df_agencias[df_agencias["Provincia"] == provincia]

    return (agencias_provincia["Ubicacion_Territorial"]
            .dropna()
            .sort_values()
            .unique()
            .tolist())


def obtener_localidades_por_ubicacion(df_agencias, provincia, ubicacion):
    """
    Devuelve las localidades disponibles dentro de una UGL.
    """

    agencias_ubicacion = df_agencias[(df_agencias["Provincia"] == provincia) &
                                     (df_agencias["Ubicacion_Territorial"] == ubicacion)]

    return (agencias_ubicacion["Localidad"]
            .dropna()
            .sort_values()
            .unique()
            .tolist())


# 4. FILTRAR AGENCIAS SEGÚN SELECCIÓN DEL USUARIO

def obtener_agencias_por_localidad(df_agencias, provincia, ubicacion, localidad):
    """
    Devuelve agencias disponibles para provincia, UGL y localidad.
    """

    agencias = df_agencias[(df_agencias["Provincia"] == provincia) &
                           (df_agencias["Ubicacion_Territorial"] == ubicacion) &
                           (df_agencias["Localidad"] == localidad)].copy()

    agencias = agencias.reset_index(drop=True)

    return agencias


def obtener_localidades_alternativas(df_agencias, provincia, ubicacion, localidad_elegida):
    """
    Devuelve otras localidades dentro de la misma UGL.

    Se usa cuando la primera localidad tiene una sola agencia
    y se necesita ofrecer al usuario una segunda localidad cercana.
    """

    localidades = obtener_localidades_por_ubicacion(df_agencias,provincia,ubicacion)

    localidades_alternativas = [localidad for localidad in localidades
                                if localidad != localidad_elegida]

    return localidades_alternativas


# 5. TEXTO PARA MOSTRAR EN LISTAS DESPLEGABLES

def crear_texto_opcion_agencia(fila):
    """
    Crea un texto claro para mostrar cada agencia en Streamlit.
    """

    nombre = fila.get("Nombre_Agencia", "")
    domicilio = fila.get("Domicilio", "")
    localidad = fila.get("Localidad", "")

    return f"{nombre} | {domicilio} | {localidad}"


# 6. LÓGICA DE SELECCIÓN DE AGENCIAS

def evaluar_agencias_de_localidad(agencias_localidad):
    """
    Evalúa cuántas agencias tiene una localidad.

    Devuelve:
    - 'sin_agencias' si no hay agencias;
    - 'una_agencia' si debe seleccionarse automáticamente;
    - 'varias_agencias' si el usuario puede elegir.
    """

    cantidad = len(agencias_localidad)

    if cantidad == 0:
        return "sin_agencias"

    if cantidad == 1:
        return "una_agencia"

    return "varias_agencias"


def seleccionar_unica_agencia(agencias_localidad):
    """
    Si la localidad tiene una sola agencia, la devuelve automáticamente.
    """

    if len(agencias_localidad) == 1:
        return agencias_localidad.iloc[0]

    return None


def seleccionar_dos_agencias_misma_localidad(agencias_localidad, indice_1, indice_2):
    """
    Selecciona dos agencias dentro de la misma localidad.

    Esta función se usará cuando la localidad elegida tenga dos o más agencias.
    En Streamlit, los índices vendrán de listas desplegables.
    """

    agencia_1 = agencias_localidad.iloc[indice_1]
    agencia_2 = agencias_localidad.iloc[indice_2]

    agencias_seleccionadas = [agencia_1, agencia_2]

    return agencias_seleccionadas


def seleccionar_segunda_agencia(agencias_segunda_localidad, indice_agencia=None):
    """
    Selecciona la segunda agencia.

    Casos:
    - Si la segunda localidad tiene una sola agencia, se selecciona automáticamente.
    - Si tiene varias agencias, se usa el índice elegido por el usuario.
    """

    cantidad = len(agencias_segunda_localidad)

    if cantidad == 0:
        return None

    if cantidad == 1:
        return agencias_segunda_localidad.iloc[0]

    if indice_agencia is not None:
        return agencias_segunda_localidad.iloc[indice_agencia]

    return None


# 7. ARMAR RESUMEN FINAL DE AGENCIAS

def armar_resumen_agencias(agencias_seleccionadas):
    """
    Convierte las agencias seleccionadas en una tabla final.

    Esta tabla será mostrada al usuario y luego podrá incluirse en el PDF.
    """

    df_seleccionadas = pd.DataFrame(agencias_seleccionadas)

    if df_seleccionadas.empty:
        return df_seleccionadas

    columnas_mostrar = ["Nombre_Agencia",
                        "Domicilio",
                        "Localidad",
                        "Ubicacion_Territorial",
                        "Provincia"]

    columnas_existentes = [columna for columna in columnas_mostrar
                           if columna in df_seleccionadas.columns]

    return df_seleccionadas[columnas_existentes]