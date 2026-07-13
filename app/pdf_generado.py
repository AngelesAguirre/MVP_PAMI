# 1. IMPORTACIÓN DE LIBRERÍAS

from fpdf import FPDF
# FPDF permite crear documentos PDF desde Python.

from pathlib import Path
# Path permite manejar rutas de carpetas y archivos.


# 2. CONFIGURACIÓN DE RUTAS

BASE_DIR = Path(__file__).resolve().parent.parent
# Ubica la carpeta principal del proyecto.

PDF_DIR = BASE_DIR / "pdfs"
# Carpeta donde se guardarán los PDF generados.

PDF_DIR.mkdir(exist_ok=True)
# Crea la carpeta pdfs si todavía no existe.

# Ruta del logo institucional (el mismo que se usa en el sistema de Streamlit).
# Si en tu proyecto el logo está guardado en otra carpeta (por ejemplo dentro
# de "assets/" o "static/"), actualizá esta linea con la ruta correcta.
LOGO_PATH = BASE_DIR / "logo_PAMI.png"


# 3. PALETA DE COLORES INSTITUCIONAL PAMI
# Estos son los únicos colores que se usan en todo el documento, tomados
# directamente del sitio oficial de PAMI.

COLOR_NAVY = (11, 35, 68)        # Azul oscuro institucional
COLOR_SLATE = (69, 101, 141)     # Azul grisáceo
COLOR_ORANGE = (248, 149, 29)    # Naranja
COLOR_TEAL = (80, 184, 177)      # Verde azulado
COLOR_PURPLE = (145, 110, 175)   # Violeta
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)


# 4. FUNCIONES AUXILIARES

def limpiar_texto_pdf(texto):
    """
    Limpia caracteres que pueden generar error en FPDF.
    """

    texto = str(texto)

    reemplazos = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
                  "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
                  "ñ": "n", "Ñ": "N",
                  "–": "-", "—": "-",
                  "“": '"', "”": '"',
                  "‘": "'", "’": "'"}

    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)

    return texto


def formatear_pesos(valor):
    """
    Convierte un número en texto con formato de pesos argentinos.
    """

    return f"${valor:,.2f}"


def escribir_multicell_completo(pdf, alto, texto):
    """
    Escribe un multi_cell() de ancho completo (de margen a margen),
    garantizando primero que el cursor esté ubicado en el margen
    izquierdo.

    Por qué existe esta función:
    Distintas versiones de la librería fpdf2 difieren en si, al
    terminar un multi_cell(), el cursor X vuelve solo al margen
    izquierdo o queda ubicado más a la derecha (cerca del borde de la
    última línea escrita). Si se encadenan dos multi_cell(0, ...) sin
    resetear la posición, el segundo puede calcular un ancho
    disponible casi nulo y lanzar FPDFException
    ("Not enough horizontal space to render a single character").

    Llamando siempre a pdf.set_x(pdf.l_margin) antes de cada
    multi_cell de ancho completo, este comportamiento queda fijo sin
    importar la versión de fpdf2 instalada.
    """

    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, alto, texto)


# 5. CLASE PERSONALIZADA DEL PDF

class PDFResumenPAMI(FPDF):
    """
    Define el formato general del PDF.
    """

    def header(self):
        """
        Encabezado automático de cada página: logo institucional centrado,
        título del sistema y subtítulo "Resumen de Consulta".
        """

        y_actual = 8

        # Logo centrado en la parte superior de la hoja.
        if LOGO_PATH.exists():
            ancho_logo = 26
            x_centro = (self.w - ancho_logo) / 2
            self.image(str(LOGO_PATH), x=x_centro, y=y_actual, w=ancho_logo)
            self.set_y(y_actual + ancho_logo + 2)
        else:
            self.set_y(y_actual)

        # Título principal (igual al del sistema de Streamlit).
        self.set_font("Arial", "B", 17)
        self.set_text_color(*COLOR_NAVY)
        self.cell(0, 8, limpiar_texto_pdf("Sistema de Orientacion sobre Medicamentos"),
                  ln=True, align="C")

        # Subtítulo.
        self.set_font("Arial", "", 12)
        self.set_text_color(*COLOR_SLATE)
        self.cell(0, 7, limpiar_texto_pdf("Resumen de Consulta"), ln=True, align="C")

        # Línea decorativa debajo del encabezado.
        self.set_draw_color(*COLOR_ORANGE)
        self.set_line_width(0.8)
        y_linea = self.get_y() + 2
        self.line(self.l_margin, y_linea, self.w - self.r_margin, y_linea)

        self.set_text_color(*COLOR_BLACK)
        self.set_y(y_linea + 6)

    def footer(self):
        """
        Pie de página automático.
        """

        self.set_y(-15)

        self.set_draw_color(*COLOR_ORANGE)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())

        self.set_font("Arial", "I", 8)
        self.set_text_color(*COLOR_SLATE)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")
        self.set_text_color(*COLOR_BLACK)


# 6. TÍTULO DE SECCIÓN (estilo institucional, sin numeración)

def verificar_espacio_disponible(pdf, alto_necesario):
    """
    Controla que quede lugar suficiente en la página actual antes de
    dibujar algo (por ejemplo, un título de sección seguido de su
    contenido).

    Si no queda espacio suficiente, fuerza un salto de página manual.

    Esto evita el problema de "título huérfano": que un título de
    sección quede solo al final de una hoja y todo su contenido pase
    a la hoja siguiente. FPDF sólo hace saltos de página automáticos
    cuando el contenido ya no entra, sin tener en cuenta que el título
    y el contenido deberían mantenerse juntos.
    """

    espacio_restante = (pdf.h - pdf.b_margin) - pdf.get_y()

    if espacio_restante < alto_necesario:
        pdf.add_page()


def agregar_titulo_seccion(pdf, texto, alto_minimo_contenido=25):
    """
    Agrega un título de sección destacado: fondo de color, tipografía en
    negrita y mayúscula, con las letras en azul institucional.

    alto_minimo_contenido:
        Estimación (en mm) del espacio que como mínimo va a ocupar el
        contenido que sigue a este título. Se usa junto con
        verificar_espacio_disponible() para que el título nunca quede
        solo al final de una página, separado del contenido que le
        corresponde.
    """

    alto = 9

    # Antes de dibujar el título, nos aseguramos de que el título y al
    # menos una porción representativa de su contenido entren juntos
    # en la página actual. Si no entran, se pasa de página ANTES de
    # dibujar el título (no después), evitando que quede huérfano.
    verificar_espacio_disponible(pdf, alto + 4 + alto_minimo_contenido)

    ancho_util = pdf.w - pdf.l_margin - pdf.r_margin

    x = pdf.l_margin
    y = pdf.get_y()

    # Fondo en contraste con el color del texto.
    pdf.set_fill_color(*COLOR_TEAL)
    pdf.rect(x, y, ancho_util, alto, style="F")

    # Texto en azul institucional, en negrita y mayúscula.
    pdf.set_xy(x, y)
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(*COLOR_NAVY)
    pdf.cell(ancho_util, alto, limpiar_texto_pdf(texto.upper()), align="C")

    pdf.set_text_color(*COLOR_BLACK)
    pdf.set_xy(x, y + alto)
    pdf.ln(4)


# 7. AGREGAR RESUMEN ECONÓMICO

def agregar_resumen_economico(pdf, resumen):
    """
    Agrega ingreso, gasto, saldo y porcentaje al PDF.
    """

    agregar_titulo_seccion(pdf, "Resumen economico", alto_minimo_contenido=45)

    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(*COLOR_BLACK)

    ingreso = formatear_pesos(resumen["Ingreso_Jubilatorio"])
    gasto = formatear_pesos(resumen["Gasto_Total_Medicamentos"])
    saldo = formatear_pesos(resumen["Saldo_Restante"])
    porcentaje = resumen["Porcentaje_Gasto_Medicamentos"]
    cantidad = resumen["Cantidad_Medicamentos"]

    pdf.cell(0, 8, f"Ingreso jubilatorio informado: {ingreso}", ln=True)
    pdf.cell(0, 8, f"Cantidad de medicamentos seleccionados: {cantidad}", ln=True)
    pdf.cell(0, 8, f"Gasto total estimado en medicamentos: {gasto}", ln=True)

    # El saldo restante se destaca en azul institucional y negrita.
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(*COLOR_NAVY)
    pdf.cell(0, 8, f"Saldo restante luego de pagar medicamentos: {saldo}", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(*COLOR_BLACK)
    pdf.cell(0, 8, f"Porcentaje del ingreso destinado a medicamentos: {porcentaje:.2f}%", ln=True)

    pdf.ln(6)


# 8. AGREGAR MEDICAMENTOS

def agregar_medicamentos(pdf, df_medicamentos):
    """
    Agrega tabla de medicamentos seleccionados. La primera fila (encabezado)
    tiene fondo de color, texto centrado, en negrita y en mayúscula.
    """

    agregar_titulo_seccion(pdf, "Medicamentos seleccionados", alto_minimo_contenido=25)

    if df_medicamentos.empty:
        pdf.set_font("Arial", "", 11)
        pdf.set_text_color(*COLOR_BLACK)
        pdf.cell(0, 8, "No se seleccionaron medicamentos.", ln=True)
        pdf.ln(6)
        return

    # Los anchos se calculan como proporción del ancho útil de la página
    # (en vez de valores fijos en mm) para que la tabla siempre ocupe
    # todo el espacio disponible, sin importar el tamaño de página.
    ancho_util = pdf.w - pdf.l_margin - pdf.r_margin

    proporciones = [0.20, 0.24, 0.20, 0.16, 0.20]
    # DROGA, MARCA, PRESENTACION, COBERTURA, A PAGAR

    anchos = [ancho_util * proporcion for proporcion in proporciones]
    encabezados = ["DROGA", "MARCA", "PRESENTACION", "COBERTURA", "A PAGAR"]

    # Encabezado de la tabla: fondo de color, texto centrado, negrita y mayúscula.
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(*COLOR_NAVY)
    pdf.set_text_color(*COLOR_WHITE)

    for ancho, titulo in zip(anchos, encabezados):
        pdf.cell(ancho, 9, titulo, border=1, align="C", fill=True)
    pdf.ln()

    # Filas de datos.
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(*COLOR_BLACK)

    for _, fila in df_medicamentos.iterrows():
        droga = limpiar_texto_pdf(fila.get("DROGA", ""))[:22]
        marca = limpiar_texto_pdf(fila.get("MARCA", ""))[:24]
        presentacion = limpiar_texto_pdf(fila.get("PRESENTACION", ""))[:18]
        cobertura = limpiar_texto_pdf(fila.get("COBERTURA", ""))
        a_pagar = formatear_pesos(float(fila.get("A_PAGAR", 0)))

        pdf.cell(anchos[0], 8, droga, border=1)
        pdf.cell(anchos[1], 8, marca, border=1)
        pdf.cell(anchos[2], 8, presentacion, border=1, align="C")
        pdf.cell(anchos[3], 8, cobertura, border=1, align="C")
        pdf.cell(anchos[4], 8, a_pagar, border=1, align="R")
        pdf.ln()

    pdf.ln(6)


# 9. AGREGAR AGENCIAS (en dos columnas para aprovechar el espacio)

def agregar_agencias(pdf, df_agencias):
    """
    Agrega las agencias PAMI seleccionadas distribuidas en dos columnas
    (una al lado de la otra) para no desperdiciar espacio en la hoja.
    """

    agregar_titulo_seccion(pdf, "Agencias PAMI seleccionadas", alto_minimo_contenido=35)

    if df_agencias.empty:
        pdf.set_font("Arial", "", 11)
        pdf.set_text_color(*COLOR_BLACK)
        pdf.cell(0, 8, "No se seleccionaron agencias.", ln=True)
        pdf.ln(6)
        return

    ancho_util = pdf.w - pdf.l_margin - pdf.r_margin
    espacio_entre_columnas = 6
    ancho_columna = (ancho_util - espacio_entre_columnas) / 2

    x_columna_izquierda = pdf.l_margin
    x_columna_derecha = pdf.l_margin + ancho_columna + espacio_entre_columnas

    filas = list(df_agencias.iterrows())

    # Se procesan las agencias de a pares (una fila de tarjetas por par).
    for inicio_par in range(0, len(filas), 2):
        par = filas[inicio_par:inicio_par + 2]
        y_inicio_fila = pdf.get_y()
        y_maximo = y_inicio_fila

        for posicion, (indice, fila) in enumerate(par):
            x = x_columna_izquierda if posicion == 0 else x_columna_derecha

            nombre = limpiar_texto_pdf(fila.get("Nombre_Agencia", ""))
            domicilio = limpiar_texto_pdf(fila.get("Domicilio", ""))
            localidad = limpiar_texto_pdf(fila.get("Localidad", ""))
            provincia = limpiar_texto_pdf(fila.get("Provincia", ""))

            # Encabezado de la tarjeta de agencia.
            pdf.set_xy(x, y_inicio_fila)
            pdf.set_fill_color(*COLOR_SLATE)
            pdf.set_text_color(*COLOR_WHITE)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(ancho_columna, 8, f"AGENCIA {inicio_par + posicion + 1}",
                     border=0, align="C", fill=True)

            # Nombre de la agencia.
            # IMPORTANTE: acá se usa set_xy() (no set_x()) antes de cada
            # multi_cell porque las tarjetas van en columnas angostas
            # (ancho_columna), no de margen a margen. Cada multi_cell
            # necesita su propia coordenada X explícita (x, no l_margin).
            pdf.set_xy(x, y_inicio_fila + 8)
            pdf.set_text_color(*COLOR_NAVY)
            pdf.set_font("Arial", "B", 10)
            pdf.multi_cell(ancho_columna, 6, nombre)

            # Datos de contacto.
            pdf.set_text_color(*COLOR_BLACK)
            pdf.set_font("Arial", "", 9)

            pdf.set_x(x)
            pdf.multi_cell(ancho_columna, 5.5, f"Domicilio: {domicilio}")

            pdf.set_x(x)
            pdf.multi_cell(ancho_columna, 5.5, f"Localidad: {localidad}")

            pdf.set_x(x)
            pdf.multi_cell(ancho_columna, 5.5, f"Provincia: {provincia}")

            if pdf.get_y() > y_maximo:
                y_maximo = pdf.get_y()

        pdf.set_xy(pdf.l_margin, y_maximo + 4)

    pdf.ln(4)


# 10. AGREGAR BENEFICIOS Y TRÁMITES

def agregar_item_alerta(pdf, titulo, mensaje):
    """
    Dibuja un único ítem de alerta dentro de la sección de beneficios:
    - título en negrita, color navy, en su propia línea;
    - debajo, el desarrollo breve en texto normal.

    Se controla que el título de la alerta no quede separado de su
    desarrollo si justo cae al final de una página.

    Ambos multi_cell se escriben con escribir_multicell_completo(),
    que fuerza el cursor al margen izquierdo antes de escribir. Esto
    evita el error "Not enough horizontal space to render a single
    character", que aparece cuando fpdf2 no resetea el cursor X al
    margen izquierdo después de un multi_cell(0, ...) (el
    comportamiento exacto varía según la versión de la librería).
    """

    # Estimamos que un ítem ocupa al menos el título + 2 líneas de texto.
    verificar_espacio_disponible(pdf, 7 + 14)

    pdf.set_font("Arial", "B", 10.5)
    pdf.set_text_color(*COLOR_NAVY)
    escribir_multicell_completo(pdf, 7, limpiar_texto_pdf(titulo))

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(*COLOR_BLACK)
    escribir_multicell_completo(pdf, 6.5, limpiar_texto_pdf(mensaje))

    pdf.ln(4)


def agregar_beneficios(pdf, alertas_beneficios=None, mensaje_beneficios=None, enfermedad_seleccionada="Ninguna"):
    """
    Agrega al PDF las advertencias sobre posibles beneficios, separadas
    por ítems (una alerta = un ítem, con título en negrita y desarrollo
    breve debajo).

    alertas_beneficios:
        Lista de diccionarios generada por
        beneficios.generar_alertas_beneficios(), cada uno con al menos
        "titulo" y "mensaje". Es la forma preferida de pasar los datos,
        porque permite dar a cada alerta su propio estilo.

    mensaje_beneficios:
        Texto plano (de compatibilidad) generado por
        beneficios.crear_mensaje_alertas(). Sólo se usa como respaldo si
        no se recibió alertas_beneficios.

    enfermedad_seleccionada:
        Enfermedad indicada por el usuario en el sistema.
    """

    agregar_titulo_seccion(pdf, "Posibles beneficios y tramites a consultar", alto_minimo_contenido=45)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(*COLOR_BLACK)

    enfermedad = limpiar_texto_pdf(enfermedad_seleccionada)

    escribir_multicell_completo(pdf, 7, f"Enfermedad o condicion informada por el usuario: {enfermedad}")
    pdf.ln(3)

    # Aclaración general: el sistema es orientativo y las gestiones se
    # confirman en la agencia PAMI seleccionada.
    pdf.set_font("Arial", "I", 9.5)
    pdf.set_text_color(*COLOR_SLATE)
    escribir_multicell_completo(pdf, 6, limpiar_texto_pdf(
        "Las siguientes alertas son orientativas y no implican aprobacion automatica de ningun beneficio. "
        "Para confirmar requisitos e iniciar los tramites, acerquese a una de las agencias PAMI seleccionadas."))
    pdf.set_text_color(*COLOR_BLACK)
    pdf.ln(4)

    # Caso preferido: se recibió la lista estructurada de alertas.
    if alertas_beneficios:
        for alerta in alertas_beneficios:
            titulo = alerta.get("titulo") or "Alerta"
            mensaje = alerta.get("mensaje", "")

            if mensaje:
                agregar_item_alerta(pdf, titulo, mensaje)

    # Respaldo: sólo se recibió el mensaje en texto plano. Se quitan los
    # "**" de negrita markdown porque FPDF no los interpreta y se
    # verían literalmente en el PDF.
    elif mensaje_beneficios:
        texto_sin_markdown = mensaje_beneficios.replace("**", "")
        pdf.set_font("Arial", "", 10)
        escribir_multicell_completo(pdf, 7, limpiar_texto_pdf(texto_sin_markdown))
        pdf.ln(4)

    # No hay alertas ni mensaje: se avisa que no se detectó nada especial.
    else:
        pdf.set_font("Arial", "", 10)
        escribir_multicell_completo(pdf, 7, limpiar_texto_pdf(
            "No se detectaron alertas automaticas de beneficios adicionales segun los datos ingresados. De "
            "todos modos, la cobertura real puede variar segun la situacion particular del afiliado y las "
            "autorizaciones vigentes de PAMI."))
        pdf.ln(4)


# 11. AGREGAR MENSAJE FINAL

def agregar_mensaje_final(pdf, mes_aguinaldo=False):
    """
    Agrega aclaración general final.

    mes_aguinaldo:
        Indica si el ingreso informado por el usuario corresponde en
        realidad al mes anterior a Junio o Diciembre, porque esos meses
        incluyen el aguinaldo (SAC) y no se usan para el cálculo.
    """

    agregar_titulo_seccion(pdf, "Informacion importante", alto_minimo_contenido=30)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(*COLOR_BLACK)

    # a. Aclaración sobre el aguinaldo, si corresponde.
    # Se muestra primero porque afecta directamente la lectura del ingreso
    # jubilatorio usado en el resto del informe.
    if mes_aguinaldo:
        texto_aguinaldo = (
            "Aclaracion sobre el aguinaldo: el usuario indico que el mes consultado (Junio o Diciembre) "
            "incluye el aguinaldo (SAC). Por eso, el ingreso jubilatorio utilizado en este informe "
            "corresponde al mes anterior (Mayo o Noviembre), que no incluye aguinaldo, para no distorsionar "
            "el calculo del gasto en medicamentos ni las alertas de beneficios.")

        pdf.set_font("Arial", "B", 10)
        escribir_multicell_completo(pdf, 7, limpiar_texto_pdf(texto_aguinaldo))
        pdf.set_font("Arial", "", 10)
        pdf.ln(2)

    texto = (
        "Este resumen es orientativo. Los valores pueden variar segun la actualizacion de precios, la "
        "cobertura vigente de PAMI y la situacion particular del afiliado. Los beneficios no son automaticos. "
        "Para confirmar requisitos, cobertura, empadronamientos o tramites, se recomienda consultar en la "
        "agencia PAMI seleccionada.")

    escribir_multicell_completo(pdf, 7, limpiar_texto_pdf(texto))


# 12. GENERAR PDF FINAL

def generar_pdf_resumen(resumen,
                        df_medicamentos,
                        df_agencias,
                        alertas_beneficios=None,
                        mensaje_beneficios=None,
                        enfermedad_seleccionada="Ninguna",
                        mes_aguinaldo=False,
                        nombre_archivo="resumen_pami.pdf"):
    """
    Genera el PDF final del sistema.

    alertas_beneficios:
        Lista de alertas (con "titulo" y "mensaje") generada por
        beneficios.generar_alertas_beneficios(). Es la forma preferida
        de mostrar los beneficios en el PDF, separados por ítems.

    mensaje_beneficios:
        Texto de respaldo (compatibilidad hacia atrás) usado únicamente
        si no se recibió alertas_beneficios.

    mes_aguinaldo:
        Indica si el usuario marcó que el mes original consultado
        (Junio o Diciembre) incluye aguinaldo, y que por lo tanto el
        ingreso jubilatorio usado en el análisis corresponde al mes
        anterior (Mayo o Noviembre).
    """

    ruta_pdf = PDF_DIR / nombre_archivo

    pdf = PDFResumenPAMI()
    pdf.add_page()

    agregar_resumen_economico(pdf, resumen)
    agregar_medicamentos(pdf, df_medicamentos)
    agregar_agencias(pdf, df_agencias)
    agregar_beneficios(pdf,
                       alertas_beneficios=alertas_beneficios,
                       mensaje_beneficios=mensaje_beneficios,
                       enfermedad_seleccionada=enfermedad_seleccionada)
    agregar_mensaje_final(pdf, mes_aguinaldo=mes_aguinaldo)

    pdf.output(str(ruta_pdf))

    return ruta_pdf