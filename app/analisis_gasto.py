# 1. IMPORTACIÓN DE LIBRERÍAS

import pandas as pd
# Para trabajar con tablas de datos.
# Para ordenar la información del resumen económico.

import matplotlib.pyplot as plt
# Para generar el gráfico de barra horizontal apilada.


# 2. CÁLCULO DEL RESUMEN ECONÓMICO

def calcular_resumen_gasto(ingreso_jubilatorio, df_medicamentos_seleccionados):
    """
    Calcula cuánto representa el gasto en medicamentos sobre el ingreso jubilatorio.

    Recibe:
        - ingreso_jubilatorio: monto de la última jubilación ingresada por el usuario.
        - df_medicamentos_seleccionados: tabla con los medicamentos elegidos.

    Devuelve:
        - ingreso jubilatorio total.
        - cantidad de medicamentos seleccionados.
        - gasto total en medicamentos.
        - saldo restante.
        - porcentaje del ingreso destinado a medicamentos.
    """

    # a. Convertir el ingreso jubilatorio a número
    ingreso_jubilatorio = float(ingreso_jubilatorio)

    # b. Si no hay medicamentos seleccionados, el gasto total es 0
    if df_medicamentos_seleccionados.empty:
        gasto_total = 0
        cantidad_medicamentos = 0

    # c. Si hay medicamentos seleccionados, se suma la columna A_PAGAR
    else:
        cantidad_medicamentos = len(df_medicamentos_seleccionados)
        if "A_PAGAR" in df_medicamentos_seleccionados.columns:
            gasto_total = df_medicamentos_seleccionados["A_PAGAR"].sum()
        else:
            gasto_total = 0

    # d. Calcular saldo restante luego de pagar medicamentos
    saldo_restante = ingreso_jubilatorio - gasto_total

    # e. Calcular porcentaje del ingreso destinado a medicamentos
    if ingreso_jubilatorio > 0:
        porcentaje_gasto = (gasto_total / ingreso_jubilatorio) * 100
    else:
        porcentaje_gasto = 0

    # f. Guardar los resultados en un diccionario
    resumen = {"Ingreso_Jubilatorio": ingreso_jubilatorio,
               "Cantidad_Medicamentos": cantidad_medicamentos,
               "Gasto_Total_Medicamentos": gasto_total,
               "Saldo_Restante": saldo_restante,
               "Porcentaje_Gasto_Medicamentos": porcentaje_gasto}

    return resumen


# 3. CONVERTIR RESUMEN EN TABLA

def crear_tabla_resumen_gasto(resumen):
    """
    Convierte el resumen económico en una tabla.

    Esta tabla se podrá mostrar en Streamlit y también incluir en el PDF final.
    """

    # a. Crear tabla con conceptos y valores
    df_resumen = pd.DataFrame({"Concepto": ["Ingreso jubilatorio",
                                            "Gasto total en medicamentos",
                                            "Saldo restante",
                                            "Porcentaje destinado a medicamentos",
                                            "Cantidad de medicamentos"],
        "Valor": [resumen["Ingreso_Jubilatorio"],
                  resumen["Gasto_Total_Medicamentos"],
                  resumen["Saldo_Restante"],
                  resumen["Porcentaje_Gasto_Medicamentos"],
                  resumen["Cantidad_Medicamentos"]]})

    return df_resumen


# 4. FORMATEAR VALORES EN PESOS

def formatear_pesos(valor):
    """
    Convierte un número en texto con formato de pesos argentinos.
    """

    return f"${valor:,.2f}"


# 5. CREAR MENSAJE EXPLICATIVO PARA EL USUARIO

def crear_mensaje_resumen(resumen):
    """
    Crea un mensaje simple para explicar el resultado al usuario.
    """

    ingreso = formatear_pesos(resumen["Ingreso_Jubilatorio"])
    gasto = formatear_pesos(resumen["Gasto_Total_Medicamentos"])
    saldo = formatear_pesos(resumen["Saldo_Restante"])
    porcentaje = resumen["Porcentaje_Gasto_Medicamentos"]
    cantidad = resumen["Cantidad_Medicamentos"]

    mensaje = (f"Su ingreso jubilatorio informado es de {ingreso}. "
               f"El gasto total estimado en {cantidad} medicamento/s es de {gasto}. "
               f"Después de pagar esos medicamentos, le quedarían aproximadamente {saldo}. "
               f"Los medicamentos representan el {porcentaje:.2f}% de su ingreso.")

    return mensaje


# 6. GENERAR GRÁFICO DE BARRA HORIZONTAL APILADA

def generar_grafico_gasto(resumen):
    """
    Genera un gráfico horizontal apilado.

    El gráfico muestra:
        - una parte del ingreso destinada a medicamentos;
        - una parte del ingreso que queda como saldo restante.

    La suma de ambas partes representa el ingreso jubilatorio total.
    """

    # a. Tomar valores desde el resumen
    gasto_total = resumen["Gasto_Total_Medicamentos"]
    saldo_restante = resumen["Saldo_Restante"]
    cantidad_medicamentos = resumen["Cantidad_Medicamentos"]

    # b. Crear figura
    fig, ax = plt.subplots(figsize=(10, 2.5))

    # c. Graficar el gasto en medicamentos
    ax.barh(y=["Ingreso jubilatorio"],
            width=[gasto_total],
            label=f"Medicamentos ({cantidad_medicamentos})")

    # d. Graficar el saldo restante al lado del gasto en medicamentos
    ax.barh(y=["Ingreso jubilatorio"],
            width=[saldo_restante],
            left=[gasto_total],
            label="Saldo restante")

    # e. Agregar título y etiquetas
    ax.set_title("Distribución del ingreso jubilatorio")
    ax.set_xlabel("Monto en pesos")

    # f. Agregar leyenda
    ax.legend()

    # g. Ajustar diseño
    plt.tight_layout()

    return fig


# 7. ARMAR RESULTADO FINAL DEL ANÁLISIS

def armar_analisis_completo(ingreso_jubilatorio, df_medicamentos_seleccionados):
    """
    Ejecuta todo el análisis de gasto en medicamentos.

    Esta función integra:
        - cálculo del resumen económico;
        - creación de tabla;
        - creación del mensaje explicativo;
        - generación del gráfico.

    Es la función principal que luego usará Streamlit.
    """

    # a. Calcular resumen económico
    resumen = calcular_resumen_gasto(ingreso_jubilatorio,
                                     df_medicamentos_seleccionados)

    # b. Crear tabla resumen
    tabla_resumen = crear_tabla_resumen_gasto(resumen)

    # c. Crear mensaje explicativo
    mensaje = crear_mensaje_resumen(resumen)

    # d. Crear gráfico
    grafico = generar_grafico_gasto(resumen)

    # e. Devolver todos los resultados juntos
    resultado = {"resumen": resumen,
                 "tabla_resumen": tabla_resumen,
                 "mensaje": mensaje,
                 "grafico": grafico}

    return resultado