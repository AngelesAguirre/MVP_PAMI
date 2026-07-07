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

# ==========================================================
# 5. ESTILO VISUAL INSTITUCIONAL

st.markdown(
    """
    <style>

    /* Fondo general */
    .stApp {
    background-color:#FFFFFF;
    color:#061A40;}

    /* Contenedor principal */
    .block-container{
    padding-top:2rem;
    padding-bottom:3rem;
    max-width:1250px;}

    /* Logo */
    .logo-container{
        display:flex;
        justify-content:center;
        align-items:center;
        margin-top:1rem;
        margin-bottom:1.2rem;}

    /* Título principal del sistema */
    div.titulo-sistema{
        color:#061A40 !important;
        font-size:50px !important;
        font-weight:900 !important;
        text-align:center !important;
        line-height:1.15;
        margin-top:1rem;
        margin-bottom:2rem;}

    /* Títulos propios de cada sección */
    .titulo-seccion{
        color:#061A40 !important;
        font-size:32px !important;
        font-weight:850 !important;
        line-height:1.25;
        margin-top:2.8rem;
        margin-bottom:1.2rem;}

    /* Texto general */
    p,
    label,
    span{
        font-size:20px !important;}

    /* Etiquetas */
    label{
        font-size:20px !important;
        font-weight:700 !important;
        color:#061A40 !important;
    }

    /* Inputs y selectores */
    input,
    textarea,
    select{
        font-size:18px !important;}

    /* Texto mostrado dentro de los selectbox de Streamlit */
    div[data-baseweb="select"] span{
        font-size:18px !important;
        font-weight:500 !important;}

    /* Opciones del menú desplegable */
    div[role="option"]{
        font-size:22px !important;
    }

    input[type="number"]{
        font-size:20px !important;
        font-weight:600 !important;}

    /* Botones */
    div.stButton>button{
        background:#005CA8;
        color:white;
        font-size:17px;
        font-weight:750;
        height:2.6em;
        padding:0.35rem 1.2rem;
        border:none;
        border-radius:9px;
    }

    div.stButton>button:hover{
        background:#003B73;
        color:white;
    }

    div.stDownloadButton>button{
        background:#00A6D6;
        color:white;
        font-size:17px;
        font-weight:750;
        height:2.6em;
        padding:0.35rem 1.2rem;
        border:none;
        border-radius:9px;
    }

    /* Alertas */
    div[data-testid="stAlert"]{
        font-size:16px !important;
        border-radius:8px;
        padding:0.35rem 0.75rem;
    }

    div[data-testid="stAlert"] p{
        font-size:16px !important;
        line-height:1.35 !important;
    }

    /* Tablas */
    div[data-testid="stDataFrame"]{
        font-size:20px;
    }

    /* Caja azul */
    .caja-presentacion{
        background:#005CA8;
        color:white;
        padding:2.3rem 2.5rem;
        border-radius:14px;
        margin-top:2rem;
        margin-bottom:3rem;
        text-align:center;
        line-height:1.8;
        font-size:23px;
        font-weight:500;
    }

    .caja-presentacion strong{
        color:white;
        font-size:25px;
        font-weight:900;
    }

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
        <strong>Importante:</strong> los resultados son orientativos. La cobertura final puede
        depender de autorizaciones, empadronamientos o trámites específicos de PAMI.
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

ingreso_jubilatorio = st.number_input("Ingrese el monto de su última jubilación o pensión",
                                      min_value=0.0,
                                      step=1000.0)
# number_input permite ingresar números.

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

    # hide_index=True oculta el índice interno de Pandas.
    # Así el usuario ve N° 1, 2, 3... y no el índice 0, 1, 2...
    st.dataframe(df_meds_mostrar,hide_index=True)

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

                st.dataframe(df_agencias_seleccionadas,hide_index=True)



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
        resultado = armar_analisis_completo(ingreso_jubilatorio=ingreso_jubilatorio,
                                            df_medicamentos_seleccionados=df_meds_seleccionados,
                                            enfermedad_seleccionada=enfermedad_seleccionada,
                                            incluye_bono=incluye_bono)

        st.subheader("Resumen económico")
        st.write(resultado["mensaje"])
        st.dataframe(resultado["tabla_resumen"])

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

        st.progress(
            porcentaje_gasto,
            text=f"Medicamentos ({cantidad}): ${gasto:,.2f} | Saldo restante: ${saldo:,.2f}")

        st.subheader("Posibles beneficios o trámites a consultar")
        st.write(resultado["mensaje_beneficios"])
        
        
# ==========================================================
# GENERAR PDF INFORMATIVO FINAL

        ruta_pdf = generar_pdf_resumen(resumen=resultado["resumen"],
                                       df_medicamentos=df_meds_seleccionados,
                                       df_agencias=df_agencias_seleccionadas,
                                       mensaje_beneficios=resultado["mensaje_beneficios"],
                                       enfermedad_seleccionada=enfermedad_seleccionada,
                                       nombre_archivo="resumen_pami_streamlit.pdf")

        with open(ruta_pdf, "rb") as archivo_pdf:
            st.download_button(label="Descargar PDF",
                               data=archivo_pdf,
                               file_name="resumen_pami.pdf",
                               mime="application/pdf")