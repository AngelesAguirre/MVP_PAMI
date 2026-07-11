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

try:
    from app.scraping_valores_previsionales import obtener_valores_previsionales_actualizados
except ModuleNotFoundError:
    from scraping_valores_previsionales import obtener_valores_previsionales_actualizados
# Permite importar el scraper tanto si ejecutamos el proyecto completo
# como si probamos módulos localmente desde app/main.py.

_VALORES_PREVISIONALES = obtener_valores_previsionales_actualizados()
# Se ejecuta una sola vez, al cargar este módulo: intenta traer el haber
# mínimo y el bono actualizados desde la página de ANSES y, si falla,
# usa los valores de respaldo definidos en scraping_valores_previsionales.py.
# Así se evita repetir la solicitud web cada vez que se llama a una función.

HABER_MINIMO_REFERENCIA = _VALORES_PREVISIONALES["haber_minimo"]
# Haber mínimo previsional vigente (sin bono).
# Antes era un valor fijo cargado a mano; ahora se actualiza automáticamente.

BONO_REFERENCIA = _VALORES_PREVISIONALES["bono"]
# Bono previsional de referencia (tope). Se guarda separado del haber
# mínimo porque funciona como un "nivelador": lo cobra completo quien
# está en el mínimo, y va bajando a medida que el haber base sube, hasta
# llegar a $0 en el tope (haber mínimo + bono).

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

# Frase estándar que recuerda que el sistema es orientativo y que el
# trámite concreto debe iniciarse en la agencia PAMI seleccionada. Se
# reutiliza en todas las alertas para mantener un mismo criterio de
# redacción en Streamlit y en el PDF.
NOTA_AGENCIA = ("Recuerde que esta informacion es orientativa: no reemplaza la evaluacion que realiza PAMI. "
                "Ante cualquier duda, o para confirmar requisitos e iniciar el tramite correspondiente, "
                "acerquese a una de las agencias PAMI seleccionadas.")


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
            - titulo: título breve de la alerta (para mostrar en negrita)
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
                "titulo": "",
                "mensaje": ""}

    # d. Caso particular: diabetes
    if enfermedad.lower() == "diabetes":
        titulo = "Diabetes: posible cobertura especial"
        mensaje = ("Al declarar diabetes, es posible acceder a una cobertura especial para los medicamentos e "
                   "insumos vinculados a esta enfermedad. Este beneficio no es automático: suele requerir "
                   f"empadronamiento o certificación médica. {NOTA_AGENCIA}")

    # e. Casos generales de enfermedades con cobertura especial
    else:
        titulo = f"{enfermedad}: posible cobertura especial"
        mensaje = (f"Al declarar {enfermedad}, esta condición podría estar vinculada a coberturas especiales "
                   f"de PAMI. La cobertura efectiva depende de certificación médica, empadronamiento o "
                   f"autorización. {NOTA_AGENCIA}")

    return {"aplica": True,
            "tipo": "patologia_especial",
            "titulo": titulo,
            "mensaje": mensaje}


# 6. EVALUAR POSIBLE SUBSIDIO SOCIAL

def estimar_bono_percibido(ingreso,
                           haber_minimo=HABER_MINIMO_REFERENCIA,
                           bono_maximo=BONO_REFERENCIA,
                           margen_tolerancia=0.05):
    """
    Estima cuánto del ingreso informado corresponde al bono previsional.

    El bono funciona como un "nivelador": ANSES lo definió así (ver
    aumentos-por-movilidad-para-jubilaciones-pensiones-y-asignaciones)
    - quien cobra el haber mínimo recibe el bono completo;
    - a medida que el haber base sube, el bono baja proporcionalmente;
    - quien ya supera (haber_minimo + bono_maximo) no recibe bono.

    Por eso no siempre corresponde restar el bono completo: si se
    hiciera así con alguien que ya está por encima de ese tope, se le
    restaría un bono que en realidad no cobró.

    Parámetros:
        ingreso:
            Monto total informado por el usuario (asumiendo que incluye bono).

        haber_minimo:
            Haber mínimo previsional vigente (sin bono).

        bono_maximo:
            Bono previsional de referencia (tope).

        margen_tolerancia:
            Margen para contemplar descuentos propios del recibo (obra
            social, etc.) que hacen que el "Total a cobrar" sea un poco
            menor a (haber_minimo + bono_maximo), aunque la persona esté
            en ese rango nivelado.

    Devuelve:
        El monto estimado de bono, entre 0 y bono_maximo.

    Importante:
        Es una estimación orientativa. Dentro del rango nivelado,
        distintos haberes base terminan cobrando el mismo total, por lo
        que no es posible reconstruir el haber base exacto únicamente a
        partir del ingreso total informado. Fuera de ese rango (ingresos
        claramente mayores), se asume bono $0 en lugar de descontar el
        bono máximo por defecto.
    """

    tope_con_bono = haber_minimo + bono_maximo
    tope_con_margen = tope_con_bono * (1 + margen_tolerancia)

    # a. Si el ingreso está claramente por encima del tope nivelado,
    # se asume que no corresponde bono.
    if ingreso > tope_con_margen:
        return 0

    # b. Si el ingreso está dentro (o cerca) del rango nivelado, se
    # estima el bono como la diferencia entre el ingreso y el haber
    # mínimo, sin superar el bono máximo ni bajar de 0.
    bono_estimado = ingreso - haber_minimo
    bono_estimado = max(0, min(bono_estimado, bono_maximo))

    return bono_estimado


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

    # b. Si el ingreso informado incluye bono, se estima cuánto de ese ingreso
    # corresponde al bono (que funciona como nivelador) y se descuenta,
    # en lugar de restar siempre el bono completo. Esto evita restarle bono
    # a quienes ya cobran un haber por encima del rango nivelado.
    if incluye_bono:
        bono_estimado = estimar_bono_percibido(ingreso,
                                               haber_minimo=haber_minimo,
                                               bono_maximo=bono)
        ingreso_considerado = ingreso - bono_estimado
    else:
        bono_estimado = 0
        ingreso_considerado = ingreso

    # c. Evitar valores negativos si el usuario ingresó un monto menor al bono
    if ingreso_considerado < 0:
        ingreso_considerado = 0

    # d. Calcular límite de 1,5 haberes mínimos
    limite_subsidio = haber_minimo * MULTIPLICADOR_SUBSIDIO_SOCIAL

    # e. Evaluar si el ingreso considerado queda dentro del límite
    cumple_criterio_ingresos = ingreso_considerado <= limite_subsidio

    titulo = "Posible Subsidio Social de Medicamentos"

    if cumple_criterio_ingresos:
        mensaje = ("Según el ingreso informado, usted podría cumplir el criterio económico general para "
            "consultar por el Subsidio Social de Medicamentos de PAMI. Este resultado no implica aprobación "
            f"automática: existen otros requisitos patrimoniales y administrativos que deben ser evaluados por "
            f"PAMI. {NOTA_AGENCIA}")
    else:
        mensaje = ("Según el ingreso informado, no se detecta automáticamente cumplimiento del criterio "
            "general de ingresos para el Subsidio Social de Medicamentos. De todos modos, si su gasto en salud "
            f"es elevado o su situación particular cambió, puede consultarlo igualmente. {NOTA_AGENCIA}")

    return {"aplica": cumple_criterio_ingresos,
            "tipo": "subsidio_social",
            "titulo": titulo,
            "ingreso_informado": ingreso,
            "bono_estimado": bono_estimado,
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

    titulo = "Gasto elevado en medicamentos (15% o más del ingreso)"

    if supera_umbral:
        mensaje = (f"El gasto estimado en medicamentos representa el {porcentaje:.2f}% del ingreso informado. "
            "Como supera o iguala el 15%, podría corresponder solicitar una evaluación especial de cobertura "
            f"en PAMI. La aprobación no es automática y debe ser evaluada por el organismo. {NOTA_AGENCIA}")
    else:
        mensaje = (f"El gasto estimado en medicamentos representa el {porcentaje:.2f}% del ingreso informado. "
            "No supera el umbral del 15% utilizado como referencia para solicitar una evaluación excepcional "
            "por gasto elevado.")

    return {"aplica": supera_umbral,
            "tipo": "umbral_15",
            "titulo": titulo,
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
        titulo = "Cantidad de medicamentos dentro de un rango habitual"
        mensaje = ("La cantidad de medicamentos seleccionados se encuentra dentro de un rango bajo o moderado. "
            "En principio, podría corresponder un circuito de validación simple, aunque siempre depende de la "
            "situación particular del afiliado.")

    elif 5 <= cantidad <= 6:
        nivel = "evaluacion_ugl"
        aplica = True
        titulo = "Posible evaluación por la UGL (5 a 6 medicamentos)"
        mensaje = (f"Se seleccionaron {cantidad} medicamentos. Esta cantidad podría requerir evaluación de la "
            "UGL o agencia PAMI correspondiente, especialmente si se solicita cobertura total para varios de "
            f"ellos. {NOTA_AGENCIA}")

    else:
        nivel = "polimedicacion"
        aplica = True
        titulo = "Polimedicación (más de 6 medicamentos)"
        mensaje = (f"Se seleccionaron {cantidad} medicamentos. Este caso podría considerarse una situación de "
            f"polimedicación y requerir una evaluación adicional por parte de PAMI. {NOTA_AGENCIA}")

    return {"aplica": aplica,
            "tipo": "polimedicacion",
            "titulo": titulo,
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
                "titulo": "",
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
                "titulo": "",
                "palabras_detectadas": [],
                "mensaje": ""}

    titulo = "Afecciones frecuentes en personas mayores"

    mensaje = ("Algunos medicamentos seleccionados podrían estar vinculados a afecciones frecuentes en "
        "personas mayores, como problemas cardiovasculares, tensión arterial, colesterol, artrosis u otros "
        f"tratamientos crónicos. En algunos casos pueden existir coberturas o autorizaciones especiales. "
        f"{NOTA_AGENCIA}")

    return {"aplica": True,
            "tipo": "afecciones_frecuentes",
            "titulo": titulo,
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
            f"autorizaciones vigentes de PAMI. {NOTA_AGENCIA}")

    # Cada alerta se muestra como un ítem independiente: título en
    # markdown (negrita, "**Título**") seguido del desarrollo breve.
    # Esta misma estructura la reutilizan streamlit_app.py (que ya
    # interpreta "**...**" como negrita) y pdf_generado.py (que separa
    # título y mensaje para darle su propio estilo en el PDF).
    mensajes = []

    for alerta in alertas:
        titulo = alerta.get("titulo", "")

        if titulo:
            mensajes.append(f"**{titulo}**: {alerta['mensaje']}")
        else:
            mensajes.append(alerta["mensaje"])

    mensaje_final = "\n\n".join(mensajes)

    return mensaje_final