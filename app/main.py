from medicamentos import obtener_medicamentos_limpios

print("1. Iniciando prueba del módulo medicamentos...")

try:
    print("2. Intentando cargar base de medicamentos...")

    df_medicamentos = obtener_medicamentos_limpios()

    print("3. Base cargada correctamente.")
    print("Cantidad de registros:", len(df_medicamentos))
    print("Columnas:", df_medicamentos.columns.tolist())
    print(df_medicamentos.head())

except Exception as error:
    print("Ocurrió un error durante la prueba.")
    print(error)