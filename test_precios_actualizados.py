# ==========================================================
# 1. IMPORTACIÓN DE FUNCIONES NECESARIAS
# ==========================================================

from app.medicamentos import (
    obtener_medicamentos_limpios,
    buscar_medicamento
)

from app.scraping_precios_actualizados import (
    armar_termino_busqueda,
    buscar_link_medicamento,
    buscar_precio_actualizado_medicamento,
    actualizar_precio_con_web
)


# ==========================================================
# 2. CARGAR BASE DE MEDICAMENTOS PAMI
# ==========================================================

print("==========================================")
print("Cargando base de medicamentos PAMI...")
print("==========================================")

df_medicamentos = obtener_medicamentos_limpios()

print("Base cargada correctamente.")
print("Cantidad de medicamentos:", len(df_medicamentos))


# ==========================================================
# 3. BUSCAR MEDICAMENTO DE PRUEBA
# ==========================================================

busqueda = "atorvastatin richet"
# Podés cambiar esta búsqueda para probar otros medicamentos.

print("\n==========================================")
print("Buscando medicamento en dataset PAMI")
print("==========================================")
print(busqueda)

resultado = buscar_medicamento(busqueda, df_medicamentos)

if resultado.empty:
    print("\nNo se encontró el medicamento en la base PAMI.")
    exit()


# ==========================================================
# 4. MOSTRAR PRIMEROS RESULTADOS ENCONTRADOS
# ==========================================================

print("\n==========================================")
print("Primeros resultados encontrados")
print("==========================================")

columnas_mostrar = ["MARCA", "DROGA", "PRESENTACION", "LABORATORIO", "A_PAGAR"]

print(resultado[columnas_mostrar].head(10))


# ==========================================================
# 5. SELECCIONAR MEDICAMENTO PARA LA PRUEBA
# ==========================================================

medicamento = resultado.iloc[0]

print("\n==========================================")
print("MEDICAMENTO SELECCIONADO PARA LA PRUEBA")
print("==========================================")

print("Marca:", medicamento.get("MARCA", ""))
print("Droga:", medicamento.get("DROGA", ""))
print("Presentación:", medicamento.get("PRESENTACION", ""))
print("Laboratorio:", medicamento.get("LABORATORIO", ""))
print("Precio PAMI dataset:", medicamento.get("A_PAGAR", ""))


# ==========================================================
# 6. DEBUG: TÉRMINO DE BÚSQUEDA Y LINK ENCONTRADO
# ==========================================================
# Este paso es nuevo: muestra exactamente qué término arma el scraper
# a partir de la columna DROGA, y qué URL de ficha de medicamento
# encontró como resultado. Sirve para diagnosticar rápido si el
# problema es la búsqueda o la extracción del precio.

print("\n==========================================")
print("DEBUG: TÉRMINO DE BÚSQUEDA Y LINK ENCONTRADO")
print("==========================================")

termino_busqueda = armar_termino_busqueda(medicamento)
print("Término de búsqueda armado a partir de DROGA:", termino_busqueda)

url_medicamento_encontrado = buscar_link_medicamento(medicamento)
print("URL de ficha encontrada:", url_medicamento_encontrado)

if url_medicamento_encontrado is None:
    print(
        "\nNo se encontró ningún link de ficha. Revisar si la columna "
        "DROGA está bien cargada en el dataset para este medicamento."
    )


# ==========================================================
# 7. CONSULTAR PRECIO ACTUALIZADO EN LA WEB
# ==========================================================

print("\n==========================================")
print("CONSULTANDO PRECIO ACTUALIZADO WEB")
print("==========================================")

precio_web = buscar_precio_actualizado_medicamento(medicamento)

print("Precio encontrado en la web:")
print(precio_web)


# ==========================================================
# 8. COMPARAR PRECIO DATASET VS PRECIO WEB
# ==========================================================

print("\n==========================================")
print("COMPARANDO PRECIOS")
print("==========================================")

medicamento_actualizado = actualizar_precio_con_web(medicamento)

print("Precio original dataset PAMI:")
print(medicamento.get("A_PAGAR", ""))

print("\nPrecio final utilizado por el sistema:")
print(medicamento_actualizado.get("A_PAGAR", ""))


# ==========================================================
# 9. RESULTADO FINAL
# ==========================================================

print("\n==========================================")
print("PRUEBA FINALIZADA")
print("==========================================")