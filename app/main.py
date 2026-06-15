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

import pandas as pd
from pdf_generado import generar_pdf_resumen

print("1. Iniciando prueba del módulo PDF...\n")

try:
    # 1. Simular resumen economico
    resumen = {"Ingreso_Jubilatorio": 437000,
               "Cantidad_Medicamentos": 3,
               "Gasto_Total_Medicamentos": 12500,
               "Saldo_Restante": 424500,
               "Porcentaje_Gasto_Medicamentos": 2.86}

    print("2. Resumen económico generado.")

    # 2. Simular medicamentos seleccionados
    df_medicamentos = pd.DataFrame({"DROGA": ["AMLODIPINA","LOSARTAN","LEVOTIROXINA"],
                                    "MARCA": ["MEDICAMENTO A","MEDICAMENTO B","MEDICAMENTO C"],
                                    "COBERTURA": ["80%","50%","100%"],
                                    "A_PAGAR": [5000,7500,0]})

    print("3. Tabla de medicamentos creada.")

    # 3. Simular agencias seleccionadas
    df_agencias = pd.DataFrame({"Nombre_Agencia": ["AGENCIA ADROGUE","AGENCIA LOMAS DE ZAMORA"],
                                "Domicilio": ["Av. Espora 123","Hipolito Yrigoyen 456"],
                                "Localidad": ["ADROGUE","LOMAS DE ZAMORA"],
                                "Provincia": ["BUENOS AIRES","BUENOS AIRES"]})

    print("4. Tabla de agencias creada.")

    # 4. Generar PDF
    ruta_pdf = generar_pdf_resumen(resumen,df_medicamentos,df_agencias)

    print("\n5. PDF generado correctamente.")
    print("Ubicación del archivo:")
    print(ruta_pdf)

except Exception as error:

    print("\nOcurrió un error durante la prueba.")
    print(error)