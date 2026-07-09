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

def agregar_titulo_seccion(pdf, texto):
    """
    Agrega un título de sección destacado: fondo de color, tipografía en
    negrita y mayúscula, con las letras en azul institucional.
    """

    ancho_util = pdf.w - pdf.l_margin - pdf.r_margin
    alto = 9

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

    agregar_titulo_seccion(pdf, "Resumen economico")

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

    agregar_titulo_seccion(pdf, "Medicamentos seleccionados")

    if df_medicamentos.empty:
        pdf.set_font("Arial", "", 11)
        pdf.set_text_color(*COLOR_BLACK)
        pdf.cell(0, 8, "No se seleccionaron medicamentos.", ln=True)
        pdf.ln(6)
        return

    anchos = [45, 50, 35, 40]
    encabezados = ["DROGA", "MARCA", "COBERTURA", "A PAGAR"]

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
        droga = limpiar_texto_pdf(fila.get("DROGA", ""))[:25]
        marca = limpiar_texto_pdf(fila.get("MARCA", ""))[:28]
        cobertura = limpiar_texto_pdf(fila.get("COBERTURA", ""))
        a_pagar = formatear_pesos(float(fila.get("A_PAGAR", 0)))

        pdf.cell(45, 8, droga, border=1)
        pdf.cell(50, 8, marca, border=1)
        pdf.cell(35, 8, cobertura, border=1, align="C")
        pdf.cell(40, 8, a_pagar, border=1, align="R")
        pdf.ln()

    pdf.ln(6)


# 9. AGREGAR AGENCIAS (en dos columnas para aprovechar el espacio)

def agregar_agencias(pdf, df_agencias):
    """
    Agrega las agencias PAMI seleccionadas distribuidas en dos columnas
    (una al lado de la otra) para no desperdiciar espacio en la hoja.
    """

    agregar_titulo_seccion(pdf, "Agencias PAMI seleccionadas")

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

def agregar_beneficios(pdf, mensaje_beneficios=None, enfermedad_seleccionada="Ninguna"):
    """
    Agrega al PDF las advertencias sobre posibles beneficios.

    mensaje_beneficios:
        Texto generado por beneficios.py / analisis_gasto.py.

    enfermedad_seleccionada:
        Enfermedad indicada por el usuario en el sistema.
    """

    agregar_titulo_seccion(pdf, "Posibles beneficios y tramites a consultar")

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(*COLOR_BLACK)

    enfermedad = limpiar_texto_pdf(enfermedad_seleccionada)

    pdf.multi_cell(0, 7, f"Enfermedad o condicion informada por el usuario: {enfermedad}")

    pdf.ln(2)

    if mensaje_beneficios:
        texto = limpiar_texto_pdf(mensaje_beneficios)
    else:
        texto = ("No se cargaron alertas especificas de beneficios. De todos modos, la cobertura real puede "
            "variar segun autorizaciones particulares de PAMI.")

    pdf.multi_cell(0, 7, texto)
    pdf.ln(6)


# 11. AGREGAR MENSAJE FINAL

def agregar_mensaje_final(pdf):
    """
    Agrega aclaración general final.
    """

    agregar_titulo_seccion(pdf, "Informacion importante")

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(*COLOR_BLACK)

    texto = (
        "Este resumen es orientativo. Los valores pueden variar segun la actualizacion de precios, la "
        "cobertura vigente de PAMI y la situacion particular del afiliado. Los beneficios no son automaticos. "
        "Para confirmar requisitos, cobertura, empadronamientos o tramites, se recomienda consultar en la "
        "agencia PAMI seleccionada.")

    pdf.multi_cell(0, 7, limpiar_texto_pdf(texto))


# 12. GENERAR PDF FINAL

def generar_pdf_resumen(resumen,
                        df_medicamentos,
                        df_agencias,
                        mensaje_beneficios=None,
                        enfermedad_seleccionada="Ninguna",
                        nombre_archivo="resumen_pami.pdf"):
    """
    Genera el PDF final del sistema.
    """

    ruta_pdf = PDF_DIR / nombre_archivo

    pdf = PDFResumenPAMI()
    pdf.add_page()

    agregar_resumen_economico(pdf, resumen)
    agregar_medicamentos(pdf, df_medicamentos)
    agregar_agencias(pdf, df_agencias)
    agregar_beneficios(pdf,mensaje_beneficios=mensaje_beneficios,
                       enfermedad_seleccionada=enfermedad_seleccionada)
    agregar_mensaje_final(pdf)

    pdf.output(str(ruta_pdf))

    return ruta_pdf