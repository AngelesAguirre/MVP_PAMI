# 1. IMPORTACIÓN DE LIBRERÍAS

from fpdf import FPDF
# FPDF permite crear documentos PDF desde Python
# Con esta librería se pueden escribir textos, tablas y guardar el archivo final

from pathlib import Path
# Path permite manejar rutas de carpetas y archivos
# Guarda el PDF sin depender de una ruta fija de una computadora


# 2. CONFIGURACIÓN DE RUTAS

BASE_DIR = Path(__file__).resolve().parent.parent
# __file__ indica dónde está ubicado este archivo.
# parent.parent sube dos niveles:
# pdf_generado.py -> app -> carpeta principal del proyecto.

PDF_DIR = BASE_DIR / "pdfs"
# Define la carpeta donde se guardarán los PDFs generados

PDF_DIR.mkdir(exist_ok=True)
# mkdir() crea una carpeta.
# exist_ok=True evita error si la carpeta ya existe.


# 3. FUNCIÓN PARA FORMATEAR VALORES EN PESOS

def formatear_pesos(valor):
    """
    Convierte un valor numérico en texto con formato de pesos argentinos.
    """

    return f"${valor:,.2f}"


# 4. CLASE PERSONALIZADA DEL PDF

class PDFResumenPAMI(FPDF):
    """
    Esta clase define el formato general del PDF.

    Hereda de FPDF, lo que significa que toma todas las herramientas
    de FPDF y además permite personalizar encabezado y pie de página.
    """

    def header(self):
        """
        header() se ejecuta automáticamente al inicio de cada página.
        """

        self.set_font("Arial", "B", 16)
        # set_font(fuente, estilo, tamaño)
        # "Arial" = tipo de letra.
        # "B" = negrita.
        # 16 = tamaño de fuente.

        self.cell(0, 10, "Resumen de Consulta PAMI", ln=True, align="C")
        # cell(ancho, alto, texto, ln, align)
        # ancho 0 = ocupa todo el ancho disponible.
        # alto 10 = altura de la línea.
        # ln=True = después de escribir, baja a la línea siguiente.
        # align="C" = centra el texto.

        self.set_font("Arial", "", 11)
        # "" significa texto normal, sin negrita ni cursiva.

        self.cell(0,8,"Sistema de apoyo para jubilados y pensionados",
                  ln=True,
                  align="C")

        self.ln(8)
        # ln(8) agrega espacio vertical entre el encabezado y el contenido.

    def footer(self):
        """
        footer() se ejecuta automáticamente al final de cada página.
        """

        self.set_y(-15)
        # set_y(-15) mueve el cursor a 15 mm del final de la página.

        self.set_font("Arial", "I", 8)
        # "I" = cursiva.

        self.cell(0, 10, f"Página {self.page_no()}", align="C")
        # page_no() devuelve el número de página actual.


# 5. AGREGAR RESUMEN ECONÓMICO AL PDF

def agregar_resumen_economico(pdf, resumen):
    """
    Agrega al PDF los datos económicos principales.

    pdf:
        Es el documento PDF que se está construyendo.

    resumen:
        Es el diccionario generado por analisis_gasto.py.
    """

    pdf.set_font("Arial", "B", 13)

    pdf.cell(0, 10, "1. Resumen economico", ln=True)
    # Escribe el título de la sección.

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
    # Agrega espacio antes de pasar a la siguiente sección.


# 6. AGREGAR MEDICAMENTOS SELECCIONADOS AL PDF

def agregar_medicamentos(pdf, df_medicamentos):
    """
    Agrega al PDF una tabla simple con los medicamentos seleccionados.

    df_medicamentos:
        DataFrame con los medicamentos elegidos por el usuario.
    """

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "2. Medicamentos seleccionados", ln=True)

    if df_medicamentos.empty:
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, "No se seleccionaron medicamentos.", ln=True)
        pdf.ln(6)
        return

    # Encabezado de la tabla.
    pdf.set_font("Arial", "B", 9)

    pdf.cell(45, 8, "Droga", border=1)
    # border=1 dibuja el borde de la celda.

    pdf.cell(50, 8, "Marca", border=1)
    pdf.cell(35, 8, "Cobertura", border=1)
    pdf.cell(40, 8, "A pagar", border=1, ln=True)
    # ln=True al final de la última celda baja a la siguiente fila.

    # Filas de la tabla.
    pdf.set_font("Arial", "", 8)

    for _, fila in df_medicamentos.iterrows():
        # iterrows() recorre cada fila del DataFrame.

        droga = str(fila.get("DROGA", ""))[:25]
        marca = str(fila.get("MARCA", ""))[:28]
        cobertura = str(fila.get("COBERTURA", ""))
        a_pagar = formatear_pesos(float(fila.get("A_PAGAR", 0)))

        # [:25] y [:28] recortan textos largos para que no rompan la tabla.

        pdf.cell(45, 8, droga, border=1)
        pdf.cell(50, 8, marca, border=1)
        pdf.cell(35, 8, cobertura, border=1)
        pdf.cell(40, 8, a_pagar, border=1, ln=True)

    pdf.ln(6)


# 7. AGREGAR AGENCIAS SELECCIONADAS AL PDF

def agregar_agencias(pdf, df_agencias):
    """
    Agrega al PDF las agencias PAMI seleccionadas o sugeridas.

    df_agencias:
        DataFrame con las agencias elegidas durante la consulta.
    """

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "3. Agencias PAMI seleccionadas", ln=True)

    if df_agencias.empty:
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, "No se seleccionaron agencias.", ln=True)
        pdf.ln(6)
        return

    pdf.set_font("Arial", "", 11)

    for indice, fila in df_agencias.iterrows():
        nombre = fila.get("Nombre_Agencia", "")
        domicilio = fila.get("Domicilio", "")
        localidad = fila.get("Localidad", "")
        provincia = fila.get("Provincia", "")

        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, f"Agencia {indice + 1}: {nombre}", ln=True)

        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 7, f"Domicilio: {domicilio}", ln=True)
        pdf.cell(0, 7, f"Localidad: {localidad}", ln=True)
        pdf.cell(0, 7, f"Provincia: {provincia}", ln=True)

        pdf.ln(3)


# 8. AGREGAR MENSAJE FINAL

def agregar_mensaje_final(pdf):
    """
    Agrega una aclaración final para el usuario.
    """

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "4. Información importante", ln=True)

    pdf.set_font("Arial", "", 10)

    texto = ("Este resumen es orientativo. Los valores pueden variar segun la actualizacion "
             "de precios, la cobertura vigente de PAMI y la situacion particular del afiliado. "
             "Para confirmar requisitos, cobertura o tramites, se recomienda consultar en la "
             "agencia PAMI seleccionada."
             "Y recuerde: los beneficios no son automaticos, debe acercarse a alguna de las "
             "agencias de PAMI seleccionadas para realizar el empadronamiento")

    pdf.multi_cell(0, 7, texto)
    # multi_cell() permite escribir textos largos en varias líneas.
    # A diferencia de cell(), si el texto no entra en una línea,
    # lo continúa automáticamente debajo.


# 9. GENERAR PDF FINAL

def generar_pdf_resumen(resumen,
                        df_medicamentos,
                        df_agencias,
                        nombre_archivo="resumen_pami.pdf"):
    """
    Genera el PDF final del sistema.

    resumen:
        Diccionario con ingreso, gasto, saldo y porcentaje.

    df_medicamentos:
        Tabla con medicamentos seleccionados.

    df_agencias:
        Tabla con agencias seleccionadas.

    nombre_archivo:
        Nombre del archivo PDF generado.

    Devuelve:
        Ruta completa del PDF creado.
    """

    ruta_pdf = PDF_DIR / nombre_archivo
    # Define dónde se guardará el archivo PDF.

    pdf = PDFResumenPAMI()
    # Crea un documento PDF vacío usando la clase personalizada.

    pdf.add_page()
    # Agrega una página nueva.
    # No se puede escribir contenido si no hay una página creada.

    agregar_resumen_economico(pdf, resumen)
    # Agrega la sección de resumen económico.

    agregar_medicamentos(pdf, df_medicamentos)
    # Agrega la tabla de medicamentos.

    agregar_agencias(pdf, df_agencias)
    # Agrega la información de agencias.

    agregar_mensaje_final(pdf)
    # Agrega la aclaración final.

    pdf.output(str(ruta_pdf))
    # output() guarda físicamente el PDF.
    # str(ruta_pdf) convierte la ruta Path en texto,
    # porque FPDF necesita recibir la ruta como string.

    return ruta_pdf