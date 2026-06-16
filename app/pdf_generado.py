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


# 3. FUNCIONES AUXILIARES

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


# 4. CLASE PERSONALIZADA DEL PDF

class PDFResumenPAMI(FPDF):
    """
    Define el formato general del PDF.
    """

    def header(self):
        """
        Encabezado automático de cada página.
        """

        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Resumen de Consulta PAMI", ln=True, align="C")

        self.set_font("Arial", "", 11)
        self.cell(0,8,"Sistema de apoyo para jubilados y pensionados",ln=True,align="C")

        self.ln(8)

    def footer(self):
        """
        Pie de página automático.
        """

        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")


# 5. AGREGAR RESUMEN ECONÓMICO

def agregar_resumen_economico(pdf, resumen):
    """
    Agrega ingreso, gasto, saldo y porcentaje al PDF.
    """

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "1. Resumen economico", ln=True)

    pdf.set_font("Arial", "", 11)

    ingreso = formatear_pesos(resumen["Ingreso_Jubilatorio"])
    gasto = formatear_pesos(resumen["Gasto_Total_Medicamentos"])
    saldo = formatear_pesos(resumen["Saldo_Restante"])
    porcentaje = resumen["Porcentaje_Gasto_Medicamentos"]
    cantidad = resumen["Cantidad_Medicamentos"]

    pdf.cell(0, 8, f"Ingreso jubilatorio informado: {ingreso}", ln=True)
    pdf.cell(0, 8, f"Cantidad de medicamentos seleccionados: {cantidad}", ln=True)
    pdf.cell(0, 8, f"Gasto total estimado en medicamentos: {gasto}", ln=True)
    pdf.cell(0, 8, f"Saldo restante luego de pagar medicamentos: {saldo}", ln=True)
    pdf.cell(0, 8, f"Porcentaje del ingreso destinado a medicamentos: {porcentaje:.2f}%", ln=True)

    pdf.ln(6)


# 6. AGREGAR MEDICAMENTOS

def agregar_medicamentos(pdf, df_medicamentos):
    """
    Agrega tabla de medicamentos seleccionados.
    """

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "2. Medicamentos seleccionados", ln=True)

    if df_medicamentos.empty:
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, "No se seleccionaron medicamentos.", ln=True)
        pdf.ln(6)
        return

    pdf.set_font("Arial", "B", 9)

    pdf.cell(45, 8, "Droga", border=1)
    pdf.cell(50, 8, "Marca", border=1)
    pdf.cell(35, 8, "Cobertura", border=1)
    pdf.cell(40, 8, "A pagar", border=1, ln=True)

    pdf.set_font("Arial", "", 8)

    for _, fila in df_medicamentos.iterrows():
        droga = limpiar_texto_pdf(fila.get("DROGA", ""))[:25]
        marca = limpiar_texto_pdf(fila.get("MARCA", ""))[:28]
        cobertura = limpiar_texto_pdf(fila.get("COBERTURA", ""))
        a_pagar = formatear_pesos(float(fila.get("A_PAGAR", 0)))

        pdf.cell(45, 8, droga, border=1)
        pdf.cell(50, 8, marca, border=1)
        pdf.cell(35, 8, cobertura, border=1)
        pdf.cell(40, 8, a_pagar, border=1, ln=True)

    pdf.ln(6)


# 7. AGREGAR AGENCIAS

def agregar_agencias(pdf, df_agencias):
    """
    Agrega agencias PAMI seleccionadas o sugeridas.
    """

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "3. Agencias PAMI seleccionadas", ln=True)

    if df_agencias.empty:
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, "No se seleccionaron agencias.", ln=True)
        pdf.ln(6)
        return

    for indice, fila in df_agencias.iterrows():
        nombre = limpiar_texto_pdf(fila.get("Nombre_Agencia", ""))
        domicilio = limpiar_texto_pdf(fila.get("Domicilio", ""))
        localidad = limpiar_texto_pdf(fila.get("Localidad", ""))
        provincia = limpiar_texto_pdf(fila.get("Provincia", ""))

        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, f"Agencia {indice + 1}: {nombre}", ln=True)

        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 7, f"Domicilio: {domicilio}", ln=True)
        pdf.cell(0, 7, f"Localidad: {localidad}", ln=True)
        pdf.cell(0, 7, f"Provincia: {provincia}", ln=True)

        pdf.ln(3)


# 8. AGREGAR BENEFICIOS Y TRÁMITES

def agregar_beneficios(pdf, mensaje_beneficios=None, enfermedad_seleccionada="Ninguna"):
    """
    Agrega al PDF las advertencias sobre posibles beneficios.

    mensaje_beneficios:
        Texto generado por beneficios.py / analisis_gasto.py.

    enfermedad_seleccionada:
        Enfermedad indicada por el usuario en el sistema.
    """

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "4. Posibles beneficios y tramites a consultar", ln=True)

    pdf.set_font("Arial", "", 10)

    enfermedad = limpiar_texto_pdf(enfermedad_seleccionada)

    pdf.multi_cell(0,7,f"Enfermedad o condicion informada por el usuario: {enfermedad}")

    pdf.ln(2)

    if mensaje_beneficios:
        texto = limpiar_texto_pdf(mensaje_beneficios)
    else:
        texto = ("No se cargaron alertas especificas de beneficios. De todos modos, la cobertura real puede "
            "variar segun autorizaciones particulares de PAMI.")

    pdf.multi_cell(0, 7, texto)
    pdf.ln(6)


# 9. AGREGAR MENSAJE FINAL

def agregar_mensaje_final(pdf):
    """
    Agrega aclaración general final.
    """

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "5. Informacion importante", ln=True)

    pdf.set_font("Arial", "", 10)

    texto = (
        "Este resumen es orientativo. Los valores pueden variar segun la actualizacion de precios, la "
        "cobertura vigente de PAMI y la situacion particular del afiliado. Los beneficios no son automaticos. "
        "Para confirmar requisitos, cobertura, empadronamientos o tramites, se recomienda consultar en la "
        "agencia PAMI seleccionada.")

    pdf.multi_cell(0, 7, limpiar_texto_pdf(texto))


# 10. GENERAR PDF FINAL

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