# 1. IMPORTACIÓN DE LIBRERÍAS

import sqlite3
# Librería estándar de Python para trabajar con bases de datos SQLite.
# No requiere instalación adicional (no hace falta agregarla a requirements.txt).

from pathlib import Path
# Para manejar rutas de carpetas y archivos.

from datetime import datetime
# Para registrar la fecha de cada consulta.


# 2. CONFIGURACIÓN DE RUTAS

BASE_DIR = Path(__file__).resolve().parent.parent
# Misma lógica que cargar_datos.py y pdf_generado.py:
# __file__ está en app/, entonces parent.parent es la raíz del proyecto.

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

RUTA_BASE_DATOS = DATA_DIR / "estadisticas.db"
# La base se guarda dentro de la carpeta data/, junto a los Excel de respaldo.

# IMPORTANTE - Persistencia en Streamlit Community Cloud:
# El filesystem de Streamlit Cloud es efímero. Este archivo .db se conserva
# mientras la app esté corriendo, pero se BORRA cada vez que la app se reinicia
# o se hace un nuevo deploy (push a GitHub). Para persistencia real a largo
# plazo habría que migrar esto a una base externa (ej. Supabase o Turso, que
# tienen planes gratuitos). Para el alcance de este MVP, SQLite local alcanza
# para demostrar la funcionalidad de "medicamentos más consultados".


# 3. CREAR LA TABLA SI NO EXISTE

def inicializar_base_datos():
    """
    Crea la tabla 'medicamentos_consultados' si todavía no existe.

    Se guarda únicamente información no sensible del medicamento:
    - droga
    - marca
    - fecha de la consulta

    NUNCA se guarda información del afiliado (ingreso, enfermedad, etc.),
    para mantener el registro anónimo y liviano.
    """

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicamentos_consultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            droga TEXT,
            marca TEXT,
            fecha TEXT
        )
    """)

    # Tabla de análisis realizados: cada vez que un usuario aprieta
    # "Generar análisis", se guarda un resumen anónimo (sin nombre, sin
    # ningún dato que identifique al afiliado) con los montos y
    # porcentajes involucrados. Esto permite calcular estadísticas
    # agregadas de uso real del sistema, como el porcentaje promedio del
    # ingreso que los usuarios destinan a medicamentos.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analisis_realizados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingreso_jubilatorio REAL,
            gasto_total_medicamentos REAL,
            cantidad_medicamentos INTEGER,
            porcentaje_gasto REAL,
            fecha TEXT
        )
    """)

    conexion.commit()
    conexion.close()


# 4. REGISTRAR UN MEDICAMENTO CONSULTADO

def registrar_medicamento(droga, marca):
    """
    Guarda en la base un nuevo registro cada vez que un usuario
    agrega un medicamento a su consulta.

    Parámetros:
        droga: nombre de la droga/principio activo.
        marca: nombre comercial del medicamento.

    Esta función se llama desde streamlit_app.py, dentro del botón
    "Agregar medicamento", inmediatamente después de que el medicamento
    se agrega a session_state.
    """

    inicializar_base_datos()

    droga = str(droga).strip()
    marca = str(marca).strip()

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO medicamentos_consultados (droga, marca, fecha)
        VALUES (?, ?, ?)
    """, (droga, marca, fecha_actual))

    conexion.commit()
    conexion.close()


# 5. OBTENER LOS MEDICAMENTOS MÁS CONSULTADOS

def obtener_top_medicamentos(cantidad=10):
    """
    Devuelve los medicamentos más consultados históricamente.

    Parámetro:
        cantidad: cantidad de resultados a devolver (por defecto 10).

    Devuelve:
        Una lista de tuplas (droga, marca, cantidad_consultas),
        ordenada de mayor a menor cantidad de consultas.
    """

    inicializar_base_datos()

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT droga, marca, COUNT(*) as cantidad_consultas
        FROM medicamentos_consultados
        GROUP BY droga, marca
        ORDER BY cantidad_consultas DESC
        LIMIT ?
    """, (cantidad,))

    resultados = cursor.fetchall()

    conexion.close()

    return resultados


# 6. OBTENER CANTIDAD TOTAL DE CONSULTAS REGISTRADAS

def obtener_cantidad_total_consultas():
    """
    Devuelve la cantidad total de medicamentos registrados en la base.

    Sirve para mostrar un dato de contexto junto al ranking
    (por ejemplo: "sobre un total de 340 consultas registradas").
    """

    inicializar_base_datos()

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM medicamentos_consultados")

    total = cursor.fetchone()[0]

    conexion.close()

    return total


# 7. REGISTRAR UN ANÁLISIS COMPLETO (para estadísticas agregadas)

def registrar_analisis(ingreso_jubilatorio, gasto_total_medicamentos,
                       cantidad_medicamentos, porcentaje_gasto):
    """
    Guarda, de forma anónima, el resumen de un análisis completo cada
    vez que un usuario aprieta "Generar análisis" en el sistema.

    NO se guarda ningún dato que identifique al afiliado (ni nombre, ni
    enfermedad, ni agencias elegidas): solo los montos y porcentajes
    necesarios para calcular promedios generales de uso del sistema.

    Esta función se llama desde streamlit_app.py, dentro del botón
    "Generar análisis", una vez que el análisis se calculó con éxito.
    """

    inicializar_base_datos()

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO analisis_realizados
            (ingreso_jubilatorio, gasto_total_medicamentos, cantidad_medicamentos, porcentaje_gasto, fecha)
        VALUES (?, ?, ?, ?, ?)
    """, (float(ingreso_jubilatorio), float(gasto_total_medicamentos),
          int(cantidad_medicamentos), float(porcentaje_gasto), fecha_actual))

    conexion.commit()
    conexion.close()


# 8. OBTENER ESTADÍSTICAS AGREGADAS DE LOS ANÁLISIS REALIZADOS

def obtener_estadisticas_analisis():
    """
    Calcula estadísticas agregadas sobre todos los análisis realizados
    hasta ahora por los usuarios del sistema.

    Devuelve un diccionario con:
        - cantidad_analisis: cuántos análisis se generaron en total.
        - promedio_ingreso: ingreso jubilatorio promedio informado.
        - promedio_gasto_total: gasto promedio en medicamentos.
        - promedio_porcentaje_gasto: porcentaje promedio del ingreso
          destinado a medicamentos (el dato más útil para entender el
          impacto real del gasto en medicamentos sobre los afiliados
          que usaron el sistema).
        - promedio_cantidad_medicamentos: cantidad promedio de
          medicamentos por consulta.

    Si todavía no hay ningún análisis registrado, todos los promedios
    se devuelven en 0 para evitar errores de división por cero.
    """

    inicializar_base_datos()

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            AVG(ingreso_jubilatorio),
            AVG(gasto_total_medicamentos),
            AVG(porcentaje_gasto),
            AVG(cantidad_medicamentos)
        FROM analisis_realizados
    """)

    fila = cursor.fetchone()
    conexion.close()

    cantidad_analisis = fila[0] or 0

    if cantidad_analisis == 0:
        return {
            "cantidad_analisis": 0,
            "promedio_ingreso": 0.0,
            "promedio_gasto_total": 0.0,
            "promedio_porcentaje_gasto": 0.0,
            "promedio_cantidad_medicamentos": 0.0
        }

    return {
        "cantidad_analisis": cantidad_analisis,
        "promedio_ingreso": fila[1] or 0.0,
        "promedio_gasto_total": fila[2] or 0.0,
        "promedio_porcentaje_gasto": fila[3] or 0.0,
        "promedio_cantidad_medicamentos": fila[4] or 0.0
    }