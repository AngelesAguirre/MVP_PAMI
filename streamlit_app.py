# ==========================================================
# CONFIGURACION GENERAL 

# 1. IMPORTACIÓN DE LIBRERÍAS

import streamlit as st
# Streamlit permite crear la interfaz web del sistema.

import pandas as pd
# Se usa para trabajar con tablas de medicamentos y agencias.

import sys
from pathlib import Path
# Se usan para manejar rutas y permitir importar los módulos de la carpeta app/.

import base64
# Permite convertir el logo en formato legible para mostrarlo centrado con HTML.

# 2. CONFIGURACIÓN DE RUTAS

BASE_DIR = Path(__file__).resolve().parent
# Carpeta principal del proyecto.

APP_DIR = BASE_DIR / "app"
# Carpeta donde están los módulos del sistema.

sys.path.append(str(APP_DIR))
# Permite importar archivos como medicamentos.py, agencias.py, etc.


# 3. IMPORTACIÓN DE MÓDULOS DEL PROYECTO

from medicamentos import (obtener_medicamentos_limpios,
                          buscar_medicamento,
                          preparar_opciones_medicamentos,
                          crear_texto_opcion_medicamento)

from agencias import (obtener_agencias_limpias,
                      obtener_provincias,
                      obtener_ubicaciones_por_provincia,
                      obtener_localidades_por_ubicacion,
                      obtener_agencias_por_localidad,
                      obtener_localidades_alternativas,
                      crear_texto_opcion_agencia,
                      seleccionar_unica_agencia,
                      seleccionar_dos_agencias_misma_localidad,
                      seleccionar_segunda_agencia,
                      armar_resumen_agencias)

from beneficios import obtener_enfermedades_cobertura_especial

from analisis_gasto import armar_analisis_completo

from pdf_generado import generar_pdf_resumen

from scraping_precios_actualizados import actualizar_precio_con_web
# actualizar_precio_con_web compara, para UN medicamento, el precio PAMI
# del dataset contra el precio PAMI actualizado en
# preciosdemedicamentos.com.ar, y deja en A_PAGAR el valor más alto.
# Se aplica en el momento en que el usuario agrega el medicamento,
# para que la tabla de "Medicamentos seleccionados" ya muestre
# directamente el precio final (no hace falta una segunda tabla
# comparativa más adelante).


# ==========================================================
# 3.1. PALETA DE COLORES INSTITUCIONAL PAMI
# Estos son los únicos colores que se usan en todo el sistema, tomados
# directamente del sitio oficial de PAMI. Se dejan como variables para
# no repetir códigos hexadecimales sueltos a lo largo del archivo.

COLOR_NAVY = "#0B2344"     # Azul oscuro institucional
COLOR_SLATE = "#45658D"    # Azul grisáceo
COLOR_ORANGE = "#F8951D"   # Naranja
COLOR_TEAL = "#50B8B1"     # Verde azulado
COLOR_PURPLE = "#916EAF"   # Violeta
COLOR_WHITE = "#FFFFFF"


# ==========================================================
# 4. CONFIGURACIÓN GENERAL DE LA PÁGINA

BASE_DIR = Path(__file__).resolve().parent
LOGO_PAMI = BASE_DIR / "assets" / "logo_pami.png"

st.set_page_config(
    page_title="Consulta tus medicamentos",
    page_icon=str(LOGO_PAMI),
    layout="wide"
)
# page_title cambia el nombre de la pestaña del navegador.
# page_icon coloca el logo de PAMI en la pestaña.
# layout="wide" usa el ancho completo de la pantalla.


# 4.1. LOGO INSTITUCIONAL CENTRADO

def mostrar_logo_centrado(ruta_logo, ancho=240):
    """
    Muestra el logo centrado en la parte superior de la aplicación.
    """

    with open(ruta_logo, "rb") as archivo:
        logo_base64 = base64.b64encode(archivo.read()).decode()

    st.markdown(
        f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" width="{ancho}">
        </div>
        """,
        unsafe_allow_html=True
    )

mostrar_logo_centrado(LOGO_PAMI)


# 4.2. TABLAS HTML DESTACADAS (Medicamentos seleccionados / Agencias seleccionadas / Resumen económico)

def formatear_numeros_tabla(df):
    """
    Da formato a los valores numéricos de una tabla antes de mostrarla:
    - Si el número es entero (por ejemplo 3.0 o 373000.0), se muestra sin decimales.
    - Si el número tiene parte decimal, se muestra con exactamente 2 decimales.
    Los valores que no son numéricos (texto) se dejan tal cual.
    """

    df_formateado = df.copy()

    def formatear_valor(valor):
        if pd.isna(valor):
            return valor
        try:
            valor_float = float(valor)
        except (TypeError, ValueError):
            return valor

        if valor_float == int(valor_float):
            return f"{int(valor_float)}"
        else:
            return f"{valor_float:.2f}"

    for columna in df_formateado.columns:
        if pd.api.types.is_numeric_dtype(df_formateado[columna]):
            df_formateado[columna] = df_formateado[columna].apply(formatear_valor)

    return df_formateado


def mostrar_tabla_destacada(df):
    """
    Muestra un DataFrame como tabla HTML con el encabezado (primera fila)
    destacado: fondo de color institucional, texto en negrita y en
    mayúscula. Se usa para las tablas de "Medicamentos seleccionados",
    "Agencias seleccionadas" y "Resumen económico", que son las que el
    usuario necesita leer con más claridad.
    """

    df_formateado = formatear_numeros_tabla(df)

    html_tabla = df_formateado.to_html(index=False, classes="tabla-destacada", border=0, escape=True)

    st.markdown(
        f'<div class="tabla-destacada-wrapper">{html_tabla}</div>',
        unsafe_allow_html=True
    )


# ==========================================================
# 5. ESTILO VISUAL INSTITUCIONAL

st.markdown(
    f"""
    <style>

    /* Fondo general */
    .stApp {{
    background-color:{COLOR_WHITE};
    color:{COLOR_NAVY};}}

    /* Contenedor principal */
    .block-container{{
    padding-top:2rem;
    padding-bottom:3rem;
    max-width:1250px;}}

    /* Logo */
    .logo-container{{
        display:flex;
        justify-content:center;
        align-items:center;
        margin-top:1rem;
        margin-bottom:1.2rem;}}

    /* Título principal del sistema */
    div.titulo-sistema{{
        color:{COLOR_NAVY} !important;
        font-size:50px !important;
        font-weight:900 !important;
        text-align:center !important;
        line-height:1.15;
        margin-top:1rem;
        margin-bottom:2rem;}}

    /* Títulos propios de cada sección */
    .titulo-seccion{{
        color:{COLOR_NAVY} !important;
        font-size:32px !important;
        font-weight:850 !important;
        line-height:1.25;
        margin-top:2.8rem;
        margin-bottom:1.2rem;}}

    /* Texto general */
    p,
    label,
    span{{
        font-size:20px !important;}}

    /* Etiquetas */
    label{{
        font-size:20px !important;
        font-weight:700 !important;
        color:{COLOR_NAVY} !important;
    }}

    /* Inputs y selectores */
    input,
    textarea,
    select{{
        font-size:18px !important;}}

    /* Texto mostrado dentro de los selectbox de Streamlit */
    div[data-baseweb="select"] span{{
        font-size:18px !important;
        font-weight:500 !important;}}

    /* Opciones del menú desplegable */
    div[role="option"]{{
        font-size:22px !important;
    }}

    input[type="number"]{{
        font-size:20px !important;
        font-weight:600 !important;}}

    /* Botones */
    div.stButton>button{{
        background:{COLOR_SLATE};
        color:{COLOR_WHITE};
        font-size:17px;
        font-weight:750;
        height:2.6em;
        padding:0.35rem 1.2rem;
        border:none;
        border-radius:9px;
    }}

    div.stButton>button:hover{{
        background:{COLOR_NAVY};
        color:{COLOR_WHITE};
    }}

    div.stDownloadButton>button{{
        background:{COLOR_TEAL};
        color:{COLOR_WHITE};
        font-size:17px;
        font-weight:750;
        height:2.6em;
        padding:0.35rem 1.2rem;
        border:none;
        border-radius:9px;
    }}

    div.stDownloadButton>button:hover{{
        background:{COLOR_NAVY};
        color:{COLOR_WHITE};
    }}

    /* Alertas */
    div[data-testid="stAlert"]{{
        font-size:16px !important;
        border-radius:8px;
        padding:0.35rem 0.75rem;
    }}

    div[data-testid="stAlert"] p{{
        font-size:16px !important;
        line-height:1.35 !important;
    }}

    /* Tablas nativas de Streamlit (st.dataframe) */
    div[data-testid="stDataFrame"]{{
        font-size:21px;
    }}

    /* Caja azul */
    .caja-presentacion{{
        background:{COLOR_NAVY};
        color:{COLOR_WHITE};
        padding:2.3rem 2.5rem;
        border-radius:14px;
        margin-top:2rem;
        margin-bottom:3rem;
        text-align:center;
        line-height:1.8;
        font-size:23px;
        font-weight:500;
    }}

    .caja-presentacion strong{{
        color:{COLOR_WHITE};
        font-size:25px;
        font-weight:900;
    }}

    /* ================================================== */
    /* Tablas HTML destacadas: Medicamentos seleccionados  */
    /* y Agencias seleccionadas.                           */
    /* ================================================== */

    .tabla-destacada-wrapper{{
        overflow-x:auto;
        margin-top:0.4rem;
        margin-bottom:1.4rem;
    }}

    table.tabla-destacada{{
        width:auto;
        border-collapse:collapse;
        font-size:16px !important;
        line-height:1.1 !important;
    }}

    table.tabla-destacada thead th{{
        background-color:{COLOR_NAVY};
        color:{COLOR_WHITE};
        text-transform:uppercase;
        font-weight:800;
        text-align:center;
        white-space:nowrap;
        padding:5px 10px !important;
        line-height:1.1 !important;
        border:1px solid {COLOR_NAVY};
    }}

    table.tabla-destacada tbody td{{
        white-space:nowrap;
        padding:3px 10px !important;
        line-height:1.1 !important;
        border:1px solid #d9d9d9;
        color:{COLOR_NAVY};
        text-align:center;
        background-color:{COLOR_WHITE};
    }}

    table.tabla-destacada tbody tr{{
        height:auto !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# 6. CARGA DE DATOS CON CACHE

@st.cache_data
def cargar_base_medicamentos():
    """
    Carga la base de medicamentos una sola vez.

    @st.cache_data evita que Streamlit vuelva a descargar y limpiar
    la base cada vez que el usuario toca un botón.
    """
    return obtener_medicamentos_limpios()


@st.cache_data
def cargar_base_agencias():
    """
    Carga la base de agencias una sola vez.
    """
    return obtener_agencias_limpias()


# 7. INICIALIZAR VARIABLES DE SESIÓN

if "medicamentos_seleccionados" not in st.session_state:
    st.session_state.medicamentos_seleccionados = []

if "agencias_seleccionadas" not in st.session_state:
    st.session_state.agencias_seleccionadas = []
# session_state guarda información aunque la página se recargue.


# ==========================================================
# 8. TÍTULO Y MENSAJE DE BIENVENIDA

st.markdown(
    """
    <div class="titulo-sistema">
        Sistema de orientación sobre medicamentos
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="caja-presentacion">
        Este sistema permite consultar medicamentos, estimar el gasto total,
        identificar posibles beneficios y seleccionar agencias PAMI de referencia.
        <br><br>
        <strong>Importante:</strong> todos los resultados de este sistema son orientativos y no reemplazan
        la evaluación oficial de PAMI. La cobertura final puede depender de autorizaciones, empadronamientos
        o trámites específicos. Ante cualquier duda, o para confirmar e iniciar los trámites correspondientes,
        acérquese a una de las agencias PAMI que seleccione más abajo.
    </div>
    """,
    unsafe_allow_html=True
)


# 9. CARGAR BASES

df_medicamentos = cargar_base_medicamentos()
df_agencias = cargar_base_agencias()


# ==========================================================
# DATOS DEL USUARIO

st.markdown(
    """
    <div class="titulo-seccion">
        Datos del afiliado
    </div>
    """,
    unsafe_allow_html=True
)

mes_aguinaldo = st.checkbox("El monto que voy a ingresar corresponde a Junio o Diciembre (mes con aguinaldo)")
# En junio y diciembre los jubilados y pensionados cobran el aguinaldo (SAC),
# que aparece en el recibo como "PRESTACION ANUAL COMPLEMENTARIA LEY 24241".
# Ese monto extra no forma parte del ingreso mensual habitual y, si se lo
# tiene en cuenta, distorsiona el cálculo del porcentaje de gasto en
# medicamentos y las alertas de beneficios (por ejemplo, el umbral del 15%
# o el Subsidio Social).

if mes_aguinaldo:
    st.warning(
        "Junio y diciembre incluyen el aguinaldo (SAC), lo que aumenta el ingreso informado y puede "
        "distorsionar el cálculo del gasto en medicamentos y las alertas de beneficios. "
        "Para que el análisis sea preciso, ingrese en el campo de abajo el monto correspondiente al "
        "mes anterior (Mayo o Noviembre, según corresponda), ya que ese recibo no incluye aguinaldo."
    )
# Se avisa al usuario antes de que cargue el monto, para que no ingrese
# el total de junio/diciembre por error.

ingreso_jubilatorio = st.number_input("Ingrese el monto de su última jubilación o pensión",
                                      min_value=0.0,
                                      step=1000.0)
# number_input permite ingresar números.
# Si mes_aguinaldo está tildado, este valor debería corresponder al mes
# anterior (Mayo o Noviembre), no al mes con aguinaldo.

enfermedad_seleccionada = st.selectbox("¿Posee alguna enfermedad o tratamiento con posible cobertura especial?",
                                       obtener_enfermedades_cobertura_especial())
# selectbox crea una lista desplegable.

incluye_bono = st.checkbox("El monto ingresado incluye bono previsional",
                           value=True)
# checkbox permite responder Sí/No.


# ==========================================================
# SELECCIÓN DE MEDICAMENTOS
st.markdown(
    """
    <div class="titulo-seccion">
        Selección de medicamentos
    </div>
    """,
    unsafe_allow_html=True
)

busqueda = st.text_input("Escriba el nombre, marca o droga del medicamento")
# text_input permite escribir texto libre.

if busqueda:
    resultado_busqueda = buscar_medicamento(busqueda, df_medicamentos)

    opciones = preparar_opciones_medicamentos(resultado_busqueda)

    if opciones.empty:
        st.warning("No se encontraron medicamentos con esa búsqueda.")

    else:
        opciones["Texto_Opcion"] = opciones.apply(crear_texto_opcion_medicamento,axis=1)

        indice_medicamento = st.selectbox("Seleccione el medicamento encontrado",
                                          range(len(opciones)),
                                          format_func=lambda i: opciones.iloc[i]["Texto_Opcion"])

        if st.button("Agregar medicamento"):
            medicamento = opciones.iloc[indice_medicamento].to_dict()

            with st.spinner("Consultando precio actualizado en la web..."):
                medicamento = actualizar_precio_con_web(medicamento)
            # Desde acá en adelante, A_PAGAR ya es el mayor entre el
            # precio del dataset PAMI y el precio actualizado de la web.

            st.session_state.medicamentos_seleccionados.append(medicamento)
            st.success("Medicamento agregado correctamente.")

if len(st.session_state.medicamentos_seleccionados) > 0:
    st.subheader("Medicamentos seleccionados")

    df_meds_seleccionados = pd.DataFrame(st.session_state.medicamentos_seleccionados)

    # Crear una copia solo para mostrar en pantalla.
    # No modifica la tabla original que después se usa para cálculos.
    df_meds_mostrar = df_meds_seleccionados.copy()

    # Agrega una columna visual llamada N°.
    # Empieza en 1 para evitar confusión en usuarios con muchos medicamentos.
    df_meds_mostrar.insert(0,"N°",range(1, len(df_meds_mostrar) + 1))

    # Tabla HTML con encabezado destacado (fondo de color, negrita, mayúscula).
    mostrar_tabla_destacada(df_meds_mostrar)

    if st.button("Borrar medicamentos seleccionados"):
        st.session_state.medicamentos_seleccionados = []
        st.rerun()

else:
    df_meds_seleccionados = pd.DataFrame()

# ==========================================================
# SELECCIÓN DE AGENCIAS

st.markdown(
    """
    <div class="titulo-seccion">
        Agencias PAMI
    </div>
    """,
    unsafe_allow_html=True
)

agencias_seleccionadas = []
# Se crea una lista vacía donde luego se guardarán las agencias elegidas.

provincias = obtener_provincias(df_agencias)

provincia = st.selectbox("Seleccione su provincia",
                         ["Seleccione..."] + provincias)
# Se agrega "Seleccione..." como primera opción para evitar
# que Streamlit elija automáticamente la primera provincia.

if provincia == "Seleccione...":
    st.info("Seleccione una provincia para continuar.")
    df_agencias_seleccionadas = pd.DataFrame()

else:
    ubicaciones = obtener_ubicaciones_por_provincia(df_agencias,
                                                    provincia)

    ubicacion = st.selectbox("Seleccione la UGL o ubicación territorial más cercana",
                             ["Seleccione..."] + ubicaciones)

    if ubicacion == "Seleccione...":
        st.info("Seleccione una UGL o ubicación territorial para continuar.")
        df_agencias_seleccionadas = pd.DataFrame()

    else:
        localidades = obtener_localidades_por_ubicacion(df_agencias,
                                                        provincia,
                                                        ubicacion)

        localidad = st.selectbox(
            "Seleccione su localidad o la más cercana",
            ["Seleccione..."] + localidades)

        if localidad == "Seleccione...":
            st.info("Seleccione una localidad para continuar.")
            df_agencias_seleccionadas = pd.DataFrame()

        else:
            agencias_localidad = obtener_agencias_por_localidad(df_agencias,
                                                                provincia,
                                                                ubicacion,
                                                                localidad)

            st.write("Agencias encontradas en la localidad seleccionada:")

            st.dataframe(agencias_localidad[["Nombre_Agencia", "Domicilio", "Localidad"]],
                         hide_index=True)

            if len(agencias_localidad) == 1:
                agencia_1 = seleccionar_unica_agencia(agencias_localidad)
                agencias_seleccionadas.append(agencia_1)

                st.info("Esta localidad tiene una sola agencia. "
                        "Se seleccionó automáticamente como primera agencia.")

                localidades_alternativas = obtener_localidades_alternativas(df_agencias,
                                                                            provincia,
                                                                            ubicacion,
                                                                            localidad)

                if len(localidades_alternativas) > 0:
                    segunda_localidad = st.selectbox("Seleccione una segunda localidad cercana",
                                                     ["Seleccione..."] + localidades_alternativas)

                    if segunda_localidad != "Seleccione...":
                        agencias_segunda_localidad = obtener_agencias_por_localidad(df_agencias,
                                                                                    provincia,
                                                                                    ubicacion,
                                                                                    segunda_localidad)

                        if len(agencias_segunda_localidad) == 1:
                            agencia_2 = seleccionar_segunda_agencia(agencias_segunda_localidad)
                            agencias_seleccionadas.append(agencia_2)

                            st.info("La segunda localidad también tiene una sola agencia. "
                                    "Se seleccionó automáticamente.")

                        elif len(agencias_segunda_localidad) > 1:
                            agencias_segunda_localidad["Texto_Opcion"] = (
                                agencias_segunda_localidad.apply(
                                    crear_texto_opcion_agencia,
                                    axis=1))

                            indice_agencia_2 = st.selectbox(
                                "Seleccione la segunda agencia",
                                range(len(agencias_segunda_localidad)),
                                format_func=lambda i: agencias_segunda_localidad.loc[
                                    i,
                                    "Texto_Opcion"])

                            agencia_2 = seleccionar_segunda_agencia(
                                agencias_segunda_localidad,
                                indice_agencia_2)

                            agencias_seleccionadas.append(agencia_2)

            elif len(agencias_localidad) >= 2:
                agencias_localidad["Texto_Opcion"] = agencias_localidad.apply(
                    crear_texto_opcion_agencia,
                    axis=1)

                indice_1 = st.selectbox("Seleccione la primera agencia",
                                        range(len(agencias_localidad)),
                                        format_func=lambda i: agencias_localidad.loc[i, "Texto_Opcion"])

                indice_2 = st.selectbox("Seleccione la segunda agencia",
                                        range(len(agencias_localidad)),
                                        format_func=lambda i: agencias_localidad.loc[i, "Texto_Opcion"])

                if indice_1 != indice_2:
                    agencias_seleccionadas = seleccionar_dos_agencias_misma_localidad(agencias_localidad,
                                                                                      indice_1,
                                                                                      indice_2)
                else:
                    st.warning("Seleccione dos agencias distintas.")

            df_agencias_seleccionadas = armar_resumen_agencias(agencias_seleccionadas)

            if not df_agencias_seleccionadas.empty:
                st.subheader("Agencias seleccionadas")

                # Tabla HTML con encabezado destacado (fondo de color, negrita, mayúscula).
                mostrar_tabla_destacada(df_agencias_seleccionadas)



# ==========================================================
# GENERAR ANÁLISIS ECONOMICO FINAL

st.markdown(
    """
    <div class="titulo-seccion">
        Resultado final
    </div>
    """,
    unsafe_allow_html=True)

if st.button("Generar análisis"):

    if ingreso_jubilatorio <= 0:
        st.error("Debe ingresar un monto jubilatorio válido.")

    elif df_meds_seleccionados.empty:
        st.error("Debe seleccionar al menos un medicamento.")

    elif df_agencias_seleccionadas.empty:
        st.error("Debe seleccionar agencias PAMI.")

    else:

        # df_meds_seleccionados ya tiene el precio final en A_PAGAR
        # (el mayor entre dataset PAMI y web), porque esa comparación
        # se hace al momento de apretar "Agregar medicamento".

        resultado = armar_analisis_completo(ingreso_jubilatorio=ingreso_jubilatorio,
                                            df_medicamentos_seleccionados=df_meds_seleccionados,
                                            enfermedad_seleccionada=enfermedad_seleccionada,
                                            incluye_bono=incluye_bono)

        st.subheader("Resumen económico")
        st.write(resultado["mensaje"])
        mostrar_tabla_destacada(resultado["tabla_resumen"])

        st.subheader("Gráfico del ingreso")

        resumen_grafico = resultado["resumen"]

        ingreso = resumen_grafico["Ingreso_Jubilatorio"]
        gasto = resumen_grafico["Gasto_Total_Medicamentos"]
        saldo = resumen_grafico["Saldo_Restante"]
        cantidad = resumen_grafico["Cantidad_Medicamentos"]

        if ingreso > 0:
            porcentaje_gasto = gasto / ingreso
        else:
            porcentaje_gasto = 0

        # Se limita entre 0 y 1 para que la barra no se rompa visualmente
        # si el gasto llegara a superar el ingreso informado.
        porcentaje_gasto_barra = max(0, min(porcentaje_gasto, 1))

        st.markdown(
            f"""
            <div style="
                background-color:{COLOR_ORANGE};
                border-radius:10px;
                height:38px;
                width:100%;
                overflow:hidden;
                margin-top:0.4rem;
                margin-bottom:0.6rem;">
                <div style="
                    background-color:{COLOR_NAVY};
                    height:100%;
                    width:{porcentaje_gasto_barra * 100}%;
                    border-radius:10px 0 0 10px;">
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write(
            f"Medicamentos ({cantidad}): ${gasto:,.2f}  |  "
            f"Saldo restante: ${saldo:,.2f}  |  "
            f"{porcentaje_gasto * 100:.2f}% del ingreso"
        )

        st.subheader("Posibles beneficios o trámites a consultar")

        st.caption(
            "Estas alertas son orientativas y no implican aprobación automática de ningún beneficio. "
            "Para confirmar requisitos e iniciar los trámites, acérquese a una de las agencias PAMI "
            "seleccionadas."
        )

        alertas_beneficios = resultado["alertas_beneficios"]

        if len(alertas_beneficios) == 0:
            st.info(
                "No se detectaron alertas automáticas de beneficios adicionales según los datos ingresados. "
                "De todos modos, la cobertura real puede variar según la situación particular del afiliado "
                "y las autorizaciones vigentes de PAMI."
            )
        else:
            # Cada alerta se muestra como un ítem propio: título en
            # negrita y, debajo, el desarrollo breve.
            for alerta in alertas_beneficios:
                st.markdown(f"**{alerta['titulo']}**")
                st.write(alerta["mensaje"])
                st.markdown("---")


# ==========================================================
# GENERAR PDF INFORMATIVO FINAL

        ruta_pdf = generar_pdf_resumen(resumen=resultado["resumen"],
                                       df_medicamentos=df_meds_seleccionados,
                                       df_agencias=df_agencias_seleccionadas,
                                       alertas_beneficios=resultado["alertas_beneficios"],
                                       mensaje_beneficios=resultado["mensaje_beneficios"],
                                       enfermedad_seleccionada=enfermedad_seleccionada,
                                       mes_aguinaldo=mes_aguinaldo,
                                       nombre_archivo="resumen_pami_streamlit.pdf")

        with open(ruta_pdf, "rb") as archivo_pdf:
            st.download_button(label="Descargar PDF",
                               data=archivo_pdf,
                               file_name="resumen_pami.pdf",
                               mime="application/pdf")