# ==========================================================
# 1. IMPORTACIÓN DE LIBRERÍAS

import re
import unicodedata
import requests

from bs4 import BeautifulSoup
# BeautifulSoup permite leer el HTML de la página de ANSES.


# ==========================================================
# 2. CONFIGURACIÓN GENERAL DEL SCRAPING

URL_ANSES_MOVILIDAD = "https://www.anses.gob.ar/aumentos-por-movilidad-para-jubilaciones-pensiones-y-asignaciones"
# Esta es la página oficial que ANSES actualiza todos los meses con el
# aumento por movilidad, el haber mínimo vigente y el bono previsional.

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )
}
# Se simula un navegador real para reducir el riesgo de que el sitio
# bloquee la solicitud.

TIMEOUT = 10


# ==========================================================
# 3. VALORES DE RESPALDO (ÚLTIMA ACTUALIZACIÓN MANUAL CONOCIDA)
# Se usan únicamente si falla la descarga o si ANSES cambia el formato
# del texto y el scraping no logra reconocer los valores.
# IMPORTANTE: si el sistema empieza a usar seguido el respaldo (revisar
# el campo "fuente" del resultado), conviene actualizar estos números
# a mano consultando la página de ANSES.

HABER_MINIMO_RESPALDO = 411989.33
BONO_RESPALDO = 70000.0


# ==========================================================
# 4. NORMALIZAR TEXTO

def normalizar_texto(texto):
    """
    Normaliza un texto para poder aplicar expresiones regulares sin
    depender de mayúsculas, tildes o espacios extra.
    """

    texto = str(texto).lower().strip()

    texto_normalizado = unicodedata.normalize("NFKD", texto)

    texto_sin_acentos = "".join(caracter
                                for caracter in texto_normalizado
                                if not unicodedata.combining(caracter))

    return texto_sin_acentos


# ==========================================================
# 5. CONVERTIR PRECIO ARGENTINO A NÚMERO

def convertir_precio_argentino(precio_texto):
    """
    Convierte un precio con formato argentino en número.

    Ejemplo:
    "481.989,33" -> 481989.33
    """

    if precio_texto is None:
        return None

    precio_texto = str(precio_texto)
    precio_texto = precio_texto.replace("$", "")
    precio_texto = precio_texto.replace(".", "")
    precio_texto = precio_texto.replace(",", ".")
    precio_texto = precio_texto.strip()

    try:
        return float(precio_texto)
    except ValueError:
        return None


# ==========================================================
# 6. DESCARGAR HTML DE LA PÁGINA DE ANSES

def obtener_html_anses(url=URL_ANSES_MOVILIDAD):
    """
    Descarga el HTML de la página de movilidad de ANSES.

    Devuelve:
        - el texto plano de la página (sin etiquetas HTML) si la
          descarga fue exitosa;
        - None si ocurre cualquier error.
    """

    try:
        respuesta = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

        if respuesta.status_code != 200:
            return None

        soup = BeautifulSoup(respuesta.text, "html.parser")

        return soup.get_text(" ")

    except requests.RequestException:
        return None


# ==========================================================
# 7. EXTRAER HABER MÍNIMO Y BONO DESDE EL TEXTO DE LA PÁGINA

def extraer_valores_previsionales(texto_pagina):
    """
    Busca, dentro del texto de la página de ANSES, el bono previsional y
    el monto total (haber mínimo + bono) que reciben quienes cobran la
    jubilación mínima.

    ANSES publica una frase con este formato (ejemplo real):
        "quienes cobran la jubilación mínima, junto con el bono de
        70 mil pesos, recibirán $481.989,33."

    De ahí se extrae:
        - el bono (por ejemplo, 70 mil pesos -> 70000);
        - el monto total con bono (por ejemplo, $481.989,33).

    El haber mínimo (sin bono) se calcula restando el bono al total,
    ya que ANSES no siempre publica el haber mínimo "solo" de forma
    explícita en esta página.

    Devuelve:
        Un diccionario con "haber_minimo", "bono" y "tope_con_bono",
        o None si no pudo reconocer el patrón esperado.
    """

    if texto_pagina is None:
        return None

    texto = normalizar_texto(texto_pagina)

    # a. Patrón principal: "...jubilacion minima, junto con el bono de
    # 70 mil pesos, recibiran $481.989,33..."
    patron = re.compile(
        r"jubilacion minima,\s*junto con el bono de\s*(\d+)\s*mil pesos,\s*"
        r"recibir[a-z]*\s*\$?\s*([\d\.,]+)"
    )

    coincidencia = patron.search(texto)

    if coincidencia is None:
        return None

    bono_en_miles = coincidencia.group(1)
    texto_tope_con_bono = coincidencia.group(2)

    bono = float(bono_en_miles) * 1000
    tope_con_bono = convertir_precio_argentino(texto_tope_con_bono)

    if tope_con_bono is None:
        return None

    haber_minimo = tope_con_bono - bono

    return {"haber_minimo": haber_minimo,
            "bono": bono,
            "tope_con_bono": tope_con_bono}


# ==========================================================
# 8. FUNCIÓN PRINCIPAL: OBTENER VALORES PREVISIONALES ACTUALIZADOS

def obtener_valores_previsionales_actualizados():
    """
    Devuelve el haber mínimo y el bono previsional vigentes.

    Estrategia utilizada (igual que en cargar_datos.py):
        - Primero intenta obtener los valores actualizados desde la
          página oficial de ANSES.
        - Si la descarga falla, o si el texto de la página cambió y no
          se pudo reconocer el patrón esperado, se usan los valores de
          respaldo definidos en este archivo.

    Devuelve:
        Un diccionario con:
            - haber_minimo: haber mínimo previsional (sin bono).
            - bono: bono previsional de referencia.
            - tope_con_bono: haber_minimo + bono.
            - fuente: "web" o "respaldo", según de dónde salieron los
              valores. Sirve para detectar si conviene actualizar el
              respaldo a mano.
    """

    # a. Se intenta descargar y leer la página oficial
    try:
        texto_pagina = obtener_html_anses()
        valores = extraer_valores_previsionales(texto_pagina)

        if valores is None:
            raise ValueError("No se pudo reconocer el formato de la página de ANSES.")

        valores["fuente"] = "web"
        print("Valores previsionales actualizados desde la web de ANSES.")

        return valores

    # b. Si algo falla, se usan los valores de respaldo
    except Exception as error:
        print("No se pudo actualizar el haber mínimo y el bono desde ANSES.")
        print("Se usarán los valores de respaldo.")
        print("Error:", error)

        return {"haber_minimo": HABER_MINIMO_RESPALDO,
                "bono": BONO_RESPALDO,
                "tope_con_bono": HABER_MINIMO_RESPALDO + BONO_RESPALDO,
                "fuente": "respaldo"}