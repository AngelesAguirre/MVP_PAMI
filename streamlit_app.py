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


# 4. CONFIGURACIÓN GENERAL DE LA PÁGINA

st.set_page_config(page_title="Consulta PAMI",
                   page_icon="💊",
                   layout="wide")
# Configura el título de la pestaña, el ícono y el ancho de la página.


# 5. ESTILO VISUAL SIMPLE

st.markdown("""
            <style>.main {font-size: 20px;}
            div.stButton > button {font-size: 20px;height: 3em;border-radius: 10px;}
            </style>
            """,
            unsafe_allow_html=True)
# Agrega un estilo básico para que botones y textos sean más grandes.


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


# 8. TÍTULO Y MENSAJE DE BIENVENIDA

st.title("💊 Sistema de consulta PAMI")

st.markdown("""
            Este sistema permite consultar medicamentos, estimar el gasto total,
            identificar posibles beneficios y seleccionar agencias PAMI de referencia.
            
            **Importante:** los resultados son orientativos. La cobertura final puede
            depender de autorizaciones, empadronamientos o trámites específicos de PAMI.
            """)


# 9. CARGAR BASES

df_medicamentos = cargar_base_medicamentos()
df_agencias = cargar_base_agencias()



# ==========================================================
# DATOS DEL USUARIO

st.header("1. Datos del afiliado")

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

st.header("2. Selección de medicamentos")

busqueda = st.text_input("Escriba el nombre, marca o droga del medicamento")
# text_input permite escribir texto libre.

if busqueda:
    resultado_busqueda = buscar_medicamento(busqueda,df_medicamentos)

    opciones = preparar_opciones_medicamentos(resultado_busqueda)

    if opciones.empty:
        st.warning("No se encontraron medicamentos con esa búsqueda.")

    else:
        opciones["Texto_Opcion"] = opciones.apply(crear_texto_opcion_medicamento,
                                                  axis=1)

        indice_medicamento = st.selectbox("Seleccione el medicamento encontrado",
                                          range(len(opciones)),
                                          format_func=lambda i: opciones.loc[i, "Texto_Opcion"])

        if st.button("Agregar medicamento"):
            medicamento = opciones.iloc[indice_medicamento].to_dict()
            st.session_state.medicamentos_seleccionados.append(medicamento)
            st.success("Medicamento agregado correctamente.")

if len(st.session_state.medicamentos_seleccionados) > 0:
    st.subheader("Medicamentos seleccionados")

    df_meds_seleccionados = pd.DataFrame(st.session_state.medicamentos_seleccionados)

    st.dataframe(df_meds_seleccionados)

    if st.button("Borrar medicamentos seleccionados"):
        st.session_state.medicamentos_seleccionados = []
        st.experimental_rerun()
else:
    df_meds_seleccionados = pd.DataFrame()




# ==========================================================
# SELECCIÓN DE AGENCIAS

st.header("3. Agencias PAMI")

provincias = obtener_provincias(df_agencias)

provincia = st.selectbox("Seleccione su provincia",
                         provincias)

ubicaciones = obtener_ubicaciones_por_provincia(df_agencias,
                                                provincia)

ubicacion = st.selectbox("Seleccione la UGL o ubicación territorial más cercana",
                         ubicaciones)

localidades = obtener_localidades_por_ubicacion(df_agencias,
                                                provincia,
                                                ubicacion)

localidad = st.selectbox("Seleccione su localidad o la más cercana",
                         localidades)

agencias_localidad = obtener_agencias_por_localidad(df_agencias,
                                                    provincia,
                                                    ubicacion,
                                                    localidad)

st.write("Agencias encontradas en la localidad seleccionada:")
st.dataframe(agencias_localidad[["Nombre_Agencia", "Domicilio", "Localidad"]])

agencias_seleccionadas = []

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
                                         localidades_alternativas)

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
            agencias_segunda_localidad["Texto_Opcion"] = (agencias_segunda_localidad.apply(crear_texto_opcion_agencia,
                                                                                           axis=1))

            indice_agencia_2 = st.selectbox("Seleccione la segunda agencia",
                                            range(len(agencias_segunda_localidad)),
                                            format_func=lambda i: agencias_segunda_localidad.loc[i,"Texto_Opcion"])

            agencia_2 = seleccionar_segunda_agencia(agencias_segunda_localidad,
                                                    indice_agencia_2)

            agencias_seleccionadas.append(agencia_2)

elif len(agencias_localidad) >= 2:
    agencias_localidad["Texto_Opcion"] = agencias_localidad.apply(crear_texto_opcion_agencia,
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
    st.dataframe(df_agencias_seleccionadas)




# ==========================================================
# GENERAR ANÁLISIS ECONOMICO FINAL

st.header("4. Resultado final")

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
        st.pyplot(resultado["grafico"])

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




