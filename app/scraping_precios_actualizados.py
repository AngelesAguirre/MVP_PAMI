# ==========================================================
# 1. IMPORTACIÓN DE LIBRERÍAS

import re
import time
import unicodedata
import urllib.parse
import requests
import pandas as pd

from bs4 import BeautifulSoup
# BeautifulSoup permite leer el HTML de una página web.


# ==========================================================
# 2. CONFIGURACIÓN GENERAL DEL SCRAPING

URL_BASE = "https://preciosdemedicamentos.com.ar"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )
}

TIMEOUT = 10


# ==========================================================
# 3. NORMALIZAR TEXTO

def normalizar_texto(texto):
    """
    Normaliza textos para comparar nombres de medicamentos.

    Hace lo siguiente:
    - convierte a texto;
    - pasa a minúscula;
    - quita espacios;
    - elimina acentos.
    """

    texto = str(texto).lower().strip()

    texto_normalizado = unicodedata.normalize("NFKD", texto)

    texto_sin_acentos = "".join(
        caracter
        for caracter in texto_normalizado
        if not unicodedata.combining(caracter)
    )

    return texto_sin_acentos


# ==========================================================
# 4. CONVERTIR PRECIO ARGENTINO A NÚMERO

def convertir_precio_argentino(precio_texto):
    """
    Convierte precios argentinos a número.

    Ejemplo:
    "$11.685" -> 11685
    "$11.685,50" -> 11685.50
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
# 5. ARMAR SLUG DEL MEDICAMENTO (a partir de la MARCA)

def armar_slug_medicamento(fila_medicamento):
    """
    Arma una parte de URL a partir de la marca del medicamento.

    Ejemplo:
    'atorvastatin richet' -> 'atorvastatin-richet'

    Este slug se usa para reconocer, dentro de los resultados
    de búsqueda, cuál es el link que corresponde a la marca
    que estamos buscando (comparando contra el href).
    """

    marca = fila_medicamento.get("MARCA", "")

    marca = normalizar_texto(marca)

    slug = re.sub(r"[^a-z0-9]+", "-", marca)

    slug = slug.strip("-")

    if slug == "":
        return None

    return slug


# ==========================================================
# 5.b ARMAR TÉRMINO DE BÚSQUEDA (a partir de la DROGA)

def armar_termino_busqueda(fila_medicamento):
    """
    El buscador real del sitio (preciosdemedicamentos.com.ar/resultados/<termino>)
    funciona por DROGA (principio activo), no por marca. Por eso el término de
    búsqueda se arma con la columna DROGA del dataset, no con MARCA.

    El sitio arma sus URLs reemplazando espacios y "+" por "_plus_",
    por ejemplo:
    "Ibuprofeno+pseudoefedrina" -> "ibuprofeno_plus_pseudoefedrina"
    "Atorvastatín"              -> "atorvastatín"  (sin tocar el acento,
                                    se codifica en la URL más adelante)
    """

    droga = fila_medicamento.get("DROGA", "")
    droga = str(droga).strip()

    if droga == "" or droga.lower() == "nan":
        return None

    termino = droga.lower()
    termino = termino.replace("+", "_plus_")
    termino = re.sub(r"\s+", "_plus_", termino)

    return termino


# ==========================================================
# 6. DESCARGAR HTML

def obtener_html(url):
    """
    Descarga el HTML de una página.

    Devuelve:
    - HTML si la página responde bien;
    - None si ocurre un error.
    """

    try:
        respuesta = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        if respuesta.status_code == 200:
            return respuesta.text

        return None

    except requests.RequestException:
        return None


# ==========================================================
# 6.b EXTRAER NÚMEROS DE UN TEXTO (para comparar presentaciones)

def extraer_numeros(texto):
    """
    Extrae todos los números de un texto.
    Sirve para comparar presentaciones (mg, cantidad de comprimidos, etc.)
    y así elegir, entre varias presentaciones de la misma marca,
    la que corresponde a la fila del dataset.
    """

    texto_normalizado = normalizar_texto(texto)

    return set(re.findall(r"\d+", texto_normalizado))


# ==========================================================
# 7. BUSCAR LINK DEL MEDICAMENTO

def buscar_link_medicamento(fila_medicamento):
    """
    Busca el link correcto del medicamento en la página de resultados
    del sitio.

    IMPORTANTE:
    El sitio NO tiene endpoints tipo "/?s=" o "/buscar?q=" (esos devuelven
    la home, no resultados). El buscador real vive en:

        https://preciosdemedicamentos.com.ar/resultados/<droga>

    y busca por DROGA (principio activo), devolviendo todas las marcas
    que la contienen. De ahí extraemos el link "/medicamento/..." cuyo
    slug coincide con la MARCA que buscamos, y si hay varias presentaciones
    de la misma marca (distintos mg, x30 / x60, etc.) usamos la columna
    PRESENTACION del dataset para elegir la correcta.
    """

    slug_marca = armar_slug_medicamento(fila_medicamento)

    if slug_marca is None:
        return None

    termino_busqueda = armar_termino_busqueda(fila_medicamento)

    urls_busqueda = []

    if termino_busqueda is not None:
        termino_codificado = urllib.parse.quote(termino_busqueda, safe="_")
        urls_busqueda.append(f"{URL_BASE}/resultados/{termino_codificado}")

    # Fallback: si no hay droga disponible, probamos buscar directamente
    # por la marca (no garantizado, pero no cuesta intentarlo).
    marca_normalizada = normalizar_texto(fila_medicamento.get("MARCA", ""))
    if marca_normalizada != "":
        termino_marca = re.sub(r"\s+", "_plus_", marca_normalizada)
        termino_marca_codificado = urllib.parse.quote(termino_marca, safe="_")
        urls_busqueda.append(f"{URL_BASE}/resultados/{termino_marca_codificado}")

    presentacion_texto = fila_medicamento.get("PRESENTACION", "")
    numeros_presentacion = extraer_numeros(presentacion_texto)

    for url_busqueda in urls_busqueda:

        html = obtener_html(url_busqueda)

        if html is None:
            continue

        soup = BeautifulSoup(html, "html.parser")

        candidatos = []

        for enlace in soup.find_all("a", href=True):

            href = enlace["href"]

            if "/medicamento/" not in href:
                continue

            href_normalizado = normalizar_texto(href)

            if slug_marca not in href_normalizado:
                continue

            if href.startswith("http"):
                url_medicamento = href
            else:
                url_medicamento = URL_BASE + href

            # Contexto alrededor del link (fila de la tabla / bloque),
            # para poder comparar presentación (mg, cantidad, etc.)
            contenedor = enlace.find_parent(["tr", "li", "div", "td"])
            texto_contexto = contenedor.get_text(" ") if contenedor else enlace.get_text(" ")

            numeros_contexto = extraer_numeros(texto_contexto)

            coincidencias = len(numeros_presentacion & numeros_contexto)

            candidatos.append((coincidencias, url_medicamento))

        if len(candidatos) == 0:
            continue

        # Elegimos el candidato cuya presentación (números) mejor coincide
        # con la fila del dataset. Si hay empate, se queda con el primero.
        candidatos.sort(key=lambda item: item[0], reverse=True)

        return candidatos[0][1]

    return None


# ==========================================================
# 8. EXTRAER PRECIO PAMI DESDE PÁGINA DEL MEDICAMENTO

def extraer_precio_pami_desde_pagina(url_medicamento):
    """
    Extrae exclusivamente el precio que aparece después de 'Precio PAMI'.
    """

    html = obtener_html(url_medicamento)

    if html is None:
        return None

    soup = BeautifulSoup(html, "html.parser")

    texto = soup.get_text("\n")

    lineas = [
        linea.strip()
        for linea in texto.split("\n")
        if linea.strip() != ""
    ]

    patron_precio = re.compile(r"\$\s?[\d\.\,]+")

    for i, linea in enumerate(lineas):

        linea_normalizada = normalizar_texto(linea)

        if linea_normalizada.startswith("precio pami"):

            precios = patron_precio.findall(linea)

            if len(precios) > 0:
                return convertir_precio_argentino(precios[0])

            for linea_siguiente in lineas[i + 1:i + 4]:

                precios_siguiente = patron_precio.findall(linea_siguiente)

                if len(precios_siguiente) > 0:
                    return convertir_precio_argentino(precios_siguiente[0])

    return None


# ==========================================================
# 9. BUSCAR PRECIO ACTUALIZADO

def buscar_precio_actualizado_medicamento(fila_medicamento):
    """
    Busca el precio PAMI actualizado del medicamento.

    Devuelve:
    - precio encontrado;
    - None si no encuentra precio.
    """

    url_medicamento = buscar_link_medicamento(fila_medicamento)

    if url_medicamento is None:
        return None

    precio_pami = extraer_precio_pami_desde_pagina(url_medicamento)

    return precio_pami


# ==========================================================
# 10. COMPARAR PRECIO DATASET VS PRECIO WEB

def actualizar_precio_con_web(fila_medicamento):
    """
    Compara el precio del dataset PAMI con el precio actualizado web.

    Regla:
    - Si la web devuelve un precio mayor, se usa ese precio.
    - Si la web no devuelve precio o devuelve uno menor, se mantiene PAMI.

    El usuario ve un único valor final en A_PAGAR.
    """

    fila_actualizada = fila_medicamento.copy()

    precio_dataset = fila_actualizada.get("A_PAGAR", 0)

    try:
        precio_dataset = float(precio_dataset)
    except ValueError:
        precio_dataset = 0

    precio_web = buscar_precio_actualizado_medicamento(fila_actualizada)

    if precio_web is not None and precio_web > precio_dataset:
        fila_actualizada["A_PAGAR"] = precio_web
    else:
        fila_actualizada["A_PAGAR"] = precio_dataset

    return fila_actualizada


# ==========================================================
# 11. ACTUALIZAR TABLA COMPLETA

def actualizar_tabla_con_web(df_medicamentos_seleccionados):
    """
    Actualiza una tabla completa de medicamentos seleccionados.

    Recorre cada medicamento y aplica:
    A_PAGAR = mayor entre dataset PAMI y precio web.
    """

    if df_medicamentos_seleccionados.empty:
        return df_medicamentos_seleccionados

    medicamentos_actualizados = []

    for _, fila in df_medicamentos_seleccionados.iterrows():

        fila_actualizada = actualizar_precio_con_web(fila)

        medicamentos_actualizados.append(fila_actualizada)

        time.sleep(0.4)

    df_actualizado = pd.DataFrame(medicamentos_actualizados)

    return df_actualizado