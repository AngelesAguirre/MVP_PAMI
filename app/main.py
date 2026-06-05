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
from agencias import (obtener_agencias_limpias,
                      obtener_provincias,
                      obtener_ubicaciones_por_provincia,
                      obtener_localidades_por_ubicacion,
                      obtener_agencias_por_localidad)

print("1. Iniciando prueba del módulo agencias...\n")

try:
    print("2. Intentando cargar base de agencias...")

    df_agencias = obtener_agencias_limpias()

    print("3. Base de agencias cargada correctamente.")
    print("Cantidad de registros:", len(df_agencias))
    print("Columnas:", df_agencias.columns.tolist())

    provincias = obtener_provincias(df_agencias)
    print("\n4. Provincias disponibles:")
    print(provincias[:10])

    provincia_prueba = "BUENOS AIRES"
    ubicaciones = obtener_ubicaciones_por_provincia(df_agencias, provincia_prueba)

    print(f"\n5. UGL disponibles en {provincia_prueba}:")
    print(ubicaciones)

    ubicacion_prueba = ubicaciones[0]
    localidades = obtener_localidades_por_ubicacion(df_agencias,
                                                    provincia_prueba,
                                                    ubicacion_prueba)

    print(f"\n6. Localidades disponibles en {ubicacion_prueba}:")
    print(localidades[:10])

    localidad_prueba = localidades[0]
    agencias = obtener_agencias_por_localidad(df_agencias,
                                              provincia_prueba,
                                              ubicacion_prueba,
                                              localidad_prueba)

    print(f"\n7. Agencias disponibles en {localidad_prueba}:")
    print(agencias[["Nombre_Agencia", "Domicilio", "Localidad"]].head())

except Exception as error:
    print("Ocurrió un error durante la prueba.")
    print(error)