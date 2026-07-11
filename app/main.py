# ESTE MAIN.PY SE USA COMO ARCHIVO DE PRUEBA LOCAL
# Se divide por secciones para saber que se provo y se cometna la seccion que no se va a utilizar

# 1. PRUEBA DE MEDICAMENTOS.PY
#from medicamentos import obtener_medicamentos_limpios

#print("1. Iniciando prueba del módulo medicamentos...")

#try:
#    print("2. Intentando cargar base de medicamentos...")

#    df_medicamentos = obtener_medicamentos_limpios()

#    print("3. Base cargada correctamente.")
#    print("Cantidad de registros:", len(df_medicamentos))
#    print("Columnas:", df_medicamentos.columns.tolist())
#    print(df_medicamentos.head())

#except Exception as error:
#    print("Ocurrió un error durante la prueba.")
#    print(error)

#2. PRUEBA DE AGENCIAS.PY
#from agencias import (obtener_agencias_limpias,
#                      obtener_provincias,
#                      obtener_ubicaciones_por_provincia,
#                      obtener_localidades_por_ubicacion,
#                      obtener_agencias_por_localidad)

#print("1. Iniciando prueba del módulo agencias...\n")

#try:
#    print("2. Intentando cargar base de agencias...")

#    df_agencias = obtener_agencias_limpias()

#    print("3. Base de agencias cargada correctamente.")
#    print("Cantidad de registros:", len(df_agencias))
#    print("Columnas:", df_agencias.columns.tolist())

#    provincias = obtener_provincias(df_agencias)
#    print("\n4. Provincias disponibles:")
#    print(provincias[:10])

#    provincia_prueba = "BUENOS AIRES"
#    ubicaciones = obtener_ubicaciones_por_provincia(df_agencias, provincia_prueba)

#    print(f"\n5. UGL disponibles en {provincia_prueba}:")
#    print(ubicaciones)

#    ubicacion_prueba = ubicaciones[0]
#    localidades = obtener_localidades_por_ubicacion(df_agencias,
#                                                    provincia_prueba,
#                                                    ubicacion_prueba)

#    print(f"\n6. Localidades disponibles en {ubicacion_prueba}:")
#    print(localidades[:10])

#    localidad_prueba = localidades[0]
#    agencias = obtener_agencias_por_localidad(df_agencias,
#                                              provincia_prueba,
#                                              ubicacion_prueba,
#                                              localidad_prueba)

#    print(f"\n7. Agencias disponibles en {localidad_prueba}:")
#    print(agencias[["Nombre_Agencia", "Domicilio", "Localidad"]].head())

#except Exception as error:
#    print("Ocurrió un error durante la prueba.")
#    print(error)


# 3. PRUEBA DE ANÁLISIS_GASTO.PY

#import pandas as pd
#from analisis_gasto import armar_analisis_completo

#print("1. Iniciando prueba del módulo análisis de gasto...\n")

#try:
    # Simular medicamentos seleccionados
#    medicamentos_seleccionados = pd.DataFrame({"DROGA": ["AMLODIPINA", "LOSARTAN", "LEVOTIROXINA"],
#                                               "MARCA": ["MEDICAMENTO A", "MEDICAMENTO B", "MEDICAMENTO C"],
#                                               "A_PAGAR": [5000, 7500, 0]})

    # Simular ingreso jubilatorio ingresado por el usuario
#    ingreso_jubilatorio = 437000

    # Ejecutar análisis completo
#    resultado = armar_analisis_completo(ingreso_jubilatorio,
#                                        medicamentos_seleccionados)

    # Mostrar resultados
#    print("2. Análisis realizado correctamente.\n")

#    print("Resumen:")
#    print(resultado["resumen"])

#    print("\nTabla resumen:")
#    print(resultado["tabla_resumen"])

#    print("\nMensaje para el usuario:")
#    print(resultado["mensaje"])

    # Mostrar gráfico
#    resultado["grafico"].show()

#except Exception as error:
#    print("Ocurrió un error durante la prueba.")
#    print(error)


# 4. PRUEBA DEL MÓDULO PDF_GENERADO

#import pandas as pd
#from pdf_generado import generar_pdf_resumen

#print("1. Iniciando prueba del módulo PDF...\n")

#try:
    # 1. Simular resumen economico
#    resumen = {"Ingreso_Jubilatorio": 437000,
#               "Cantidad_Medicamentos": 3,
#               "Gasto_Total_Medicamentos": 12500,
#               "Saldo_Restante": 424500,
#               "Porcentaje_Gasto_Medicamentos": 2.86}

#    print("2. Resumen económico generado.")

    # 2. Simular medicamentos seleccionados
#    df_medicamentos = pd.DataFrame({"DROGA": ["AMLODIPINA","LOSARTAN","LEVOTIROXINA"],
#                                    "MARCA": ["MEDICAMENTO A","MEDICAMENTO B","MEDICAMENTO C"],
#                                    "COBERTURA": ["80%","50%","100%"],
#                                    "A_PAGAR": [5000,7500,0]})

#    print("3. Tabla de medicamentos creada.")

    # 3. Simular agencias seleccionadas
#    df_agencias = pd.DataFrame({"Nombre_Agencia": ["AGENCIA ADROGUE","AGENCIA LOMAS DE ZAMORA"],
#                                "Domicilio": ["Av. Espora 123","Hipolito Yrigoyen 456"],
#                                "Localidad": ["ADROGUE","LOMAS DE ZAMORA"],
#                                "Provincia": ["BUENOS AIRES","BUENOS AIRES"]})

#    print("4. Tabla de agencias creada.")

    # 4. Generar PDF
#    ruta_pdf = generar_pdf_resumen(resumen,df_medicamentos,df_agencias)

#    print("\n5. PDF generado correctamente.")
#    print("Ubicación del archivo:")
#    print(ruta_pdf)

#except Exception as error:

#    print("\nOcurrió un error durante la prueba.")
#    print(error)


# 5. PRUEBA DE BENEFICIOS + ANÁLISIS DE GASTO + PDF

import pandas as pd

from analisis_gasto import armar_analisis_completo
from pdf_generado import generar_pdf_resumen

print("1. Iniciando prueba de analisis_gasto.py con beneficios.py...\n")

try:

    # 1. SIMULAR MEDICAMENTOS SELECCIONADOS
    medicamentos_seleccionados = pd.DataFrame({"DROGA": ["AMLODIPINA","VALSARTAN","ROSUVASTATINA","METFORMINA","INSULINA"],
                                               "MARCA": ["MEDICAMENTO A","MEDICAMENTO B","MEDICAMENTO C","MEDICAMENTO D","MEDICAMENTO E"],
                                               "PRESENTACION": ["10 MG","80 MG","10 MG","850 MG","100 UI"],
                                               "LABORATORIO": ["LAB A","LAB B","LAB C","LAB D","LAB E"],
                                               "COBERTURA": ["50%","50%","50%","100%","100%"],
                                               "A_PAGAR": [8000,9500,6000,0,0]})

    print("2. Medicamentos simulados creados correctamente.")
    print(medicamentos_seleccionados)


    # 2. SIMULAR INGRESO DEL USUARIO
    ingreso_jubilatorio = 437000
    enfermedad_seleccionada = "Diabetes"
    incluye_bono = True

    print("\n3. Datos del usuario simulados:")
    print("Ingreso jubilatorio:", ingreso_jubilatorio)
    print("Enfermedad seleccionada:", enfermedad_seleccionada)
    print("Incluye bono:", incluye_bono)

    # 3. EJECUTAR ANÁLISIS COMPLETO
    resultado = armar_analisis_completo(ingreso_jubilatorio=ingreso_jubilatorio,
                                        df_medicamentos_seleccionados=medicamentos_seleccionados,
                                        enfermedad_seleccionada=enfermedad_seleccionada,
                                        incluye_bono=incluye_bono)

    print("\n4. Análisis ejecutado correctamente.")

    # 4. MOSTRAR RESUMEN ECONÓMICO
    print("\n5. Resumen económico:")
    print(resultado["resumen"])

    print("\n6. Tabla resumen:")
    print(resultado["tabla_resumen"])

    print("\n7. Mensaje económico:")
    print(resultado["mensaje"])

    # 5. MOSTRAR ALERTAS DE BENEFICIOS
    print("\n8. Alertas detectadas:")

    for alerta in resultado["alertas_beneficios"]:
        print("-" * 60)
        print("Tipo:", alerta["tipo"])
        print("Aplica:", alerta["aplica"])
        print("Mensaje:", alerta["mensaje"])

    print("\n9. Mensaje final de beneficios:")
    print(resultado["mensaje_beneficios"])

    # 6. SIMULAR AGENCIAS SELECCIONADAS
    df_agencias = pd.DataFrame({"Nombre_Agencia": ["AGENCIA ADROGUE","AGENCIA LOMAS DE ZAMORA"],
                                "Domicilio": ["Av. Espora 123","Hipolito Yrigoyen 456"],
                                "Localidad": ["ADROGUE","LOMAS DE ZAMORA"],
                                "Provincia": ["BUENOS AIRES","BUENOS AIRES"]})

    print("\n10. Tabla de agencias creada correctamente.")

    # 7. GENERAR PDF
    ruta_pdf = generar_pdf_resumen(resumen=resultado["resumen"],
                                   df_medicamentos=medicamentos_seleccionados,
                                   df_agencias=df_agencias,
                                   alertas_beneficios=resultado["alertas_beneficios"],
                                   mensaje_beneficios=resultado["mensaje_beneficios"],
                                   enfermedad_seleccionada=enfermedad_seleccionada,
                                   nombre_archivo="resumen_pami_prueba.pdf")

    print("\n11. PDF generado correctamente.")
    print("Ubicación:")
    print(ruta_pdf)

    # 8. MOSTRAR GRÁFICO
    resultado["grafico"].show()

except Exception as error:

    print("\nOcurrió un error durante la prueba.")
    print(error)