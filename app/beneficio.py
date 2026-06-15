# 1. CONFIGURACIÓN GENERAL DEL MÓDULO

"""
Este archivo concentra la lógica vinculada a posibles beneficios, 
alertas y trámites que el usuario podría consultar en PAMI.

La idea central es NO modificar automáticamente el copago del dataset,
este ya trae una cobertura base.

Este módulo sólo agrega mensajes orientativos cuando el caso del usuario
podría requerir una evaluación adicional, por ejemplo:
- Posible subsidio social;
- Gasto en medicamentos igual o mayor al 15% del ingreso;
- Enfermedades con cobertura especial;
- Polimedicación;
- Medicamentos vinculados a afecciones frecuentes en adultos mayores.
"""

# 2. VALORES DE REFERENCIA

HABER_MINIMO_REFERENCIA = 304723.93
# Valor de referencia del haber mínimo previsional.
# Por ahora se coloca como valor fijo para poder desarrollar y probar la lógica del sistema.
# Más adelante este valor puede reemplazarse por scraping, API o carga manual actualizada desde una fuente oficial.

BONO_REFERENCIA = 70000
# Bono previsional de referencia.
# Se lo guarda separado porque puede ser importante diferenciar entre haber mensual y bono extraordinario.

MULTIPLICADOR_SUBSIDIO_SOCIAL = 1.5
# El subsidio social suele tomar como referencia ingresos menores a 1,5 haberes mínimos previsionales.

UMBRAL_GASTO_MEDICAMENTOS = 15
# Umbral porcentual de referencia.
# Si el gasto en medicamentos representa el 15% o más del ingreso, 
# el usuario puede consultar por una evaluación excepcional.


# 3. LISTAS DE ENFERMEDADES Y TRATAMIENTOS ESPECIALES

ENFERMEDADES_COBERTURA_ESPECIAL = ["Ninguna",
                                   "Diabetes",
                                   "Oncología",
                                   "Oncohematología",
                                   "VIH",
                                   "Hepatitis B",
                                   "Hepatitis C",
                                   "Hemofilia",
                                   "Trasplantes",
                                   "Artritis reumatoidea",
                                   "Osteoartritis",
                                   "Insuficiencia renal crónica",
                                   "Enfermedades fibroquísticas",
                                   "Tratamientos oftalmológicos especiales",
                                   "Otra enfermedad con cobertura especial"]
# Esta lista se usará luego en Streamlit como lista desplegable.
# La opción "Ninguna" permite que el usuario indique que no posee 
# una enfermedad especial o que no desea declarar ninguna.

AFECCIONES_FRECUENTES_ADULTOS_MAYORES = ["hipertensión",
                                         "presión arterial",
                                         "tensión",
                                         "corazón",
                                         "cardiovascular",
                                         "colesterol",
                                         "artrosis",
                                         "osteoporosis",
                                         "calcio",
                                         "diabetes"]
# Esta lista no modifica precios ni copagos.
# Sirve para generar una advertencia general: algunas afecciones frecuentes en personas mayores pueden 
# tener coberturas, programas o autorizaciones especiales que deben consultarse en PAMI.


# 4. FUNCIÓN PARA OBTENER ENFERMEDADES DISPONIBLES

def obtener_enfermedades_cobertura_especial():
    """
    Devuelve la lista de enfermedades/tratamientos con posible cobertura especial.

    Esta función será utilizada por la interfaz Streamlit para mostrar
    un selector al usuario.

    Ejemplo futuro:
        enfermedad = st.selectbox("¿Posee alguna enfermedad con cobertura especial?",
        obtener_enfermedades_cobertura_especial())
    """

    return ENFERMEDADES_COBERTURA_ESPECIAL


# 5. EVALUAR PATOLOGÍA ESPECIAL

def evaluar_patologia_especial(enfermedad_seleccionada):
    """
    Evalúa si el usuario indicó una enfermedad o tratamiento especial.

    Parámetro:
        enfermedad_seleccionada:
            Texto elegido por el usuario.
            Puede ser "Ninguna", "Diabetes", "Oncología", etc.

    Devuelve:
        Un diccionario con:
            - aplica: True/False
            - tipo: categoría de alerta
            - mensaje: texto orientativo para mostrar al usuario

    Importante:
        Esta función NO cambia automáticamente el valor de los medicamentos.
        Sólo genera una advertencia para consultar en PAMI.
    """

    # a. Si no se recibió ningún valor, se asume que no aplica
    if enfermedad_seleccionada is None:
        enfermedad_seleccionada = "Ninguna"

    # b. Normalizar el texto para evitar errores por espacios
    enfermedad = str(enfermedad_seleccionada).strip()

    # c. Si el usuario eligió "Ninguna", no se genera alerta
    if enfermedad.lower() == "ninguna":
        return {"aplica": False,
                "tipo": "patologia_especial",
                "mensaje": ""}

    # d. Caso particular: diabetes
    if enfermedad.lower() == "diabetes":
        mensaje = ("Usted indicó diabetes. PAMI cuenta con cobertura especial para medicamentos e insumos "
                   "vinculados a esta enfermedad, pero suele requerir empadronamiento o certificación médica. "
                   "Consulte en la PAMI seleccionada si corresponde realizar o actualizar el trámite.")

    # e. Casos generales de enfermedades con cobertura especial
    else:
        mensaje = (f"Usted indicó {enfermedad}. Esta condición podría estar vinculada a coberturas especiales "
                   "de PAMI. La cobertura efectiva puede depender de certificación médica, empadronamiento o "
                   "autorización. Consulte en la agencia PAMI seleccionada.")

    return {"aplica": True,
            "tipo": "patologia_especial",
            "mensaje": mensaje}


# 6. EVALUAR POSIBLE SUBSIDIO SOCIAL

def evaluar_subsidio_social(ingreso_jubilatorio,
                            haber_minimo=HABER_MINIMO_REFERENCIA,
                            incluye_bono=True,
                            bono=BONO_REFERENCIA):
    """
    Evalúa si el ingreso informado podría estar por debajo de 1,5 haberes mínimos.

    Parámetros:
        ingreso_jubilatorio: 
            Monto informado por el usuario.

        haber_minimo:
            Haber mínimo previsional usado como referencia.

        incluye_bono:
            Indica si el ingreso informado incluye bono.
            Por defecto se asume True porque muchos usuarios informan
            el total efectivamente cobrado.

        bono:
            Monto del bono de referencia.

    Devuelve:
        Diccionario con:
            - aplica: True/False
            - ingreso_considerado
            - limite_subsidio
            - mensaje

    Importante:
        Esta función NO confirma que el usuario accede al subsidio.
        Sólo indica que podría cumplir el criterio de ingresos.
    """

    # a. Convertir ingreso a número
    ingreso = float(ingreso_jubilatorio)

    # b. Si el ingreso informado incluye bono, se descuenta para estimar el haber previsional base.
    # Esto responde a la decisión metodológica de diferenciar ingreso total
    # cobrado de haber jubilatorio propiamente dicho.
    if incluye_bono:
        ingreso_considerado = ingreso - bono
    else:
        ingreso_considerado = ingreso

    # c. Evitar valores negativos si el usuario ingresó un monto menor al bono
    if ingreso_considerado < 0:
        ingreso_considerado = 0

    # d. Calcular límite de 1,5 haberes mínimos
    limite_subsidio = haber_minimo * MULTIPLICADOR_SUBSIDIO_SOCIAL

    # e. Evaluar si el ingreso considerado queda dentro del límite
    cumple_criterio_ingresos = ingreso_considerado <= limite_subsidio

    if cumple_criterio_ingresos:
        mensaje = ("Según el ingreso informado, usted podría cumplir el criterio económico general para "
            "consultar por el Subsidio Social de Medicamentos de PAMI. Este resultado no implica aprobación "
            "automática: existen otros requisitos patrimoniales y administrativos que deben ser evaluados por "
            "PAMI.")
    else:
        mensaje = ("Según el ingreso informado, no se detecta automáticamente cumplimiento del criterio "
            "general de ingresos para el Subsidio Social de Medicamentos. De todos modos, si su gasto en salud "
            "es elevado o su situación particular cambió, puede consultar en PAMI.")

    return {"aplica": cumple_criterio_ingresos,
            "tipo": "subsidio_social",
            "ingreso_informado": ingreso,
            "ingreso_considerado": ingreso_considerado,
            "haber_minimo_referencia": haber_minimo,
            "limite_subsidio": limite_subsidio,
            "mensaje": mensaje}


# 7. EVALUAR UMBRAL DEL 15%

def evaluar_umbral_15(porcentaje_gasto_medicamentos):
    """
    Evalúa si el gasto en medicamentos representa el 15% o más del ingreso.

    Parámetro:
        porcentaje_gasto_medicamentos:
            Porcentaje calculado en analisis_gasto.py.

    Devuelve:
        Diccionario con:
            - aplica: True/False
            - porcentaje
            - mensaje

    Importante:
        Superar el 15% no implica cobertura automática.
        Sólo habilita una posible consulta o reconsideración.
    """

    porcentaje = float(porcentaje_gasto_medicamentos)

    supera_umbral = porcentaje >= UMBRAL_GASTO_MEDICAMENTOS

    if supera_umbral:
        mensaje = (f"El gasto estimado en medicamentos representa el {porcentaje:.2f}% del ingreso informado. "
            "Como supera o iguala el 15%, podría corresponder solicitar una evaluación especial de cobertura "
            "en PAMI. La aprobación no es automática y debe ser evaluada por el organismo.")
    else:
        mensaje = (f"El gasto estimado en medicamentos representa el {porcentaje:.2f}% del ingreso informado. "
            "No supera el umbral del 15% utilizado como referencia para solicitar una evaluación excepcional "
            "por gasto elevado.")

    return {"aplica": supera_umbral,
            "tipo": "umbral_15",
            "porcentaje": porcentaje,
            "mensaje": mensaje}


# 8. EVALUAR POLIMEDICACIÓN

def evaluar_polimedicacion(cantidad_medicamentos):
    """
    Evalúa el circuito probable según cantidad de medicamentos.

    Parámetro:
        cantidad_medicamentos:
            Cantidad de medicamentos seleccionados por el usuario.

    Devuelve:
        Diccionario con:
            - aplica: True/False
            - nivel
            - mensaje

    Criterio orientativo:
        Hasta 4 medicamentos:
            validación simple.

        5 a 6 medicamentos:
            puede requerir evaluación UGL.

        Más de 6 medicamentos:
            puede requerir evaluación adicional por polimedicación.
    """

    cantidad = int(cantidad_medicamentos)

    if cantidad <= 4:
        nivel = "validacion_simple"
        aplica = False
        mensaje = ("La cantidad de medicamentos seleccionados se encuentra dentro de un rango bajo o moderado. "
            "En principio, podría corresponder un circuito de validación simple, aunque siempre depende de la "
            "situación particular del afiliado.")

    elif 5 <= cantidad <= 6:
        nivel = "evaluacion_ugl"
        aplica = True
        mensaje = (f"Se seleccionaron {cantidad} medicamentos. Esta cantidad podría requerir evaluación de la "
            "UGL o agencia PAMI correspondiente, especialmente si se solicita cobertura total para varios de "
            "ellos.")

    else:
        nivel = "polimedicacion"
        aplica = True
        mensaje = (f"Se seleccionaron {cantidad} medicamentos. Este caso podría considerarse una situación de "
            "polimedicación y requerir una evaluación adicional por parte de PAMI.")

    return {"aplica": aplica,
            "tipo": "polimedicacion",
            "cantidad_medicamentos": cantidad,
            "nivel": nivel,
            "mensaje": mensaje}


# 9. DETECTAR AFECCIONES FRECUENTES EN MEDICAMENTOS

def detectar_afecciones_frecuentes(df_medicamentos_seleccionados):
    """
    Busca palabras clave asociadas a afecciones frecuentes en adultos mayores.

    Parámetro:
        df_medicamentos_seleccionados:
            DataFrame con medicamentos elegidos por el usuario.

    Devuelve:
        Diccionario con:
            - aplica: True/False
            - palabras_detectadas
            - mensaje

    Importante:
        Esta función no diagnostica enfermedades.
        Sólo identifica posibles temas a consultar según los medicamentos
        seleccionados o sus descripciones.
    """

    # a. Si no hay medicamentos, no se evalúa nada
    if df_medicamentos_seleccionados.empty:
        return {"aplica": False,
                "tipo": "afecciones_frecuentes",
                "palabras_detectadas": [],
                "mensaje": ""}

    # b. Unir columnas relevantes en un único texto
    columnas_posibles = ["DROGA",
                         "MARCA",
                         "PRESENTACION",
                         "LABORATORIO"]

    columnas_existentes = [columna for columna in columnas_posibles
                           if columna in df_medicamentos_seleccionados.columns]

    texto_medicamentos = (df_medicamentos_seleccionados[columnas_existentes]
                          .astype(str)
                          .agg(" ".join, axis=1)
                          .str.lower()
                          .str.cat(sep=" "))

    # c. Buscar palabras clave dentro del texto de medicamentos
    palabras_detectadas = [palabra for palabra in AFECCIONES_FRECUENTES_ADULTOS_MAYORES
                           if palabra in texto_medicamentos]

    # d. Si no encuentra palabras, no genera alerta
    if len(palabras_detectadas) == 0:
        return {"aplica": False,
                "tipo": "afecciones_frecuentes",
                "palabras_detectadas": [],
                "mensaje": ""}

    mensaje = ("Algunos medicamentos seleccionados podrían estar vinculados a afecciones frecuentes en "
        "personas mayores, como problemas cardiovasculares, tensión arterial, colesterol, artrosis u otros "
        "tratamientos crónicos. En algunos casos pueden existir coberturas o autorizaciones especiales. "
        "Consulte en la agencia PAMI seleccionada si corresponde iniciar un trámite adicional.")

    return {"aplica": True,
            "tipo": "afecciones_frecuentes",
            "palabras_detectadas": palabras_detectadas,
            "mensaje": mensaje}


# 10. GENERAR ALERTAS INTEGRALES DE BENEFICIOS

def generar_alertas_beneficios(ingreso_jubilatorio,
                               resumen_gasto,
                               df_medicamentos_seleccionados,
                               enfermedad_seleccionada="Ninguna",
                               incluye_bono=True,
                               haber_minimo=HABER_MINIMO_REFERENCIA,
                               bono=BONO_REFERENCIA):
    """
    Ejecuta todas las evaluaciones de beneficios y alertas.

    Parámetros:
        ingreso_jubilatorio:
            Monto ingresado por el usuario.

        resumen_gasto:
            Diccionario generado por analisis_gasto.py.
            Debe contener:
                - Cantidad_Medicamentos
                - Porcentaje_Gasto_Medicamentos

        df_medicamentos_seleccionados:
            Tabla con medicamentos seleccionados.

        enfermedad_seleccionada:
            Enfermedad indicada por el usuario.

        incluye_bono:
            Indica si el ingreso informado incluye bono.

        haber_minimo:
            Haber mínimo de referencia.

        bono:
            Bono previsional de referencia.

    Devuelve:
        Una lista de diccionarios.
        Cada diccionario representa una alerta o evaluación.
    """

    alertas = []
    # Se crea una lista vacía.
    # Luego se agregará cada evaluación realizada.

    # a. Evaluar patología especial
    alerta_patologia = evaluar_patologia_especial(enfermedad_seleccionada)

    if alerta_patologia["aplica"]:
        alertas.append(alerta_patologia)

    # b. Evaluar subsidio social por ingresos
    alerta_subsidio = evaluar_subsidio_social(ingreso_jubilatorio=ingreso_jubilatorio,
                                              haber_minimo=haber_minimo,
                                              incluye_bono=incluye_bono,
                                              bono=bono)

    if alerta_subsidio["aplica"]:
        alertas.append(alerta_subsidio)

    # c. Evaluar umbral del 15%
    alerta_umbral = evaluar_umbral_15(resumen_gasto["Porcentaje_Gasto_Medicamentos"])

    if alerta_umbral["aplica"]:
        alertas.append(alerta_umbral)

    # d. Evaluar polimedicación
    alerta_polimedicacion = evaluar_polimedicacion(resumen_gasto["Cantidad_Medicamentos"])

    if alerta_polimedicacion["aplica"]:
        alertas.append(alerta_polimedicacion)

    # e. Detectar afecciones frecuentes según medicamentos
    alerta_afecciones = detectar_afecciones_frecuentes(df_medicamentos_seleccionados)

    if alerta_afecciones["aplica"]:
        alertas.append(alerta_afecciones)

    return alertas


# 11. CONVERTIR ALERTAS EN MENSAJE FINAL

def crear_mensaje_alertas(alertas):
    """
    Convierte la lista de alertas en un único texto.

    Este texto podrá mostrarse en Streamlit y también incluirse en el PDF.
    """

    if len(alertas) == 0:
        return ("No se detectaron alertas automáticas de beneficios adicionales según los datos ingresados. "
            "De todos modos, la cobertura real puede variar según la situación particular del afiliado y las "
            "autorizaciones vigentes de PAMI.")

    mensajes = []

    for alerta in alertas:
        mensajes.append(alerta["mensaje"])

    mensaje_final = "\n\n".join(mensajes)

    return mensaje_final