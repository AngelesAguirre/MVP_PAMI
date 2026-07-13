# Sistema de Consulta PAMI

## Proyecto Final - Ciencia de Datos para Politólogos/as

### Asistente de orientación sobre cobertura de medicamentos PAMI

Este proyecto desarrolla una aplicación destinada a asistir a jubilados y pensionados afiliados al Instituto Nacional de Servicios Sociales para Jubilados y Pensionados (PAMI), permitiéndoles estimar el costo de sus medicamentos, identificar posibles beneficios vigentes y localizar agencias PAMI cercanas donde realizar consultas o iniciar trámites.

La aplicación se encuentra desarrollada en Python y actualmente cuenta con una interfaz web construida mediante Streamlit.

---

# Información general

| Sección | Detalle |
|----------|----------|
| **Autor** | Ángeles Aguirre |
| **Problema** | Los afiliados de PAMI muchas veces desconocen cuánto deberán pagar realmente por sus medicamentos, ya que la cobertura final depende de múltiples factores (porcentaje de cobertura, enfermedades especiales, subsidios, autorizaciones administrativas, entre otros). |
| **Usuarios** | Jubilados, pensionados, familiares, cuidadores, trabajadores sociales, organizaciones civiles y cualquier persona que necesite estimar gastos en medicamentos PAMI. |
| **Objetivo** | Brindar una herramienta sencilla que permita estimar el gasto mensual en medicamentos, identificar posibles beneficios disponibles y orientar al afiliado hacia la agencia PAMI correspondiente. |

---

# Funcionalidades actuales

Actualmente el sistema permite:

- Buscar medicamentos del vademécum oficial de PAMI.
- Agregar múltiples medicamentos a una consulta.
- Calcular automáticamente el gasto total mensual en base a los precios actualizados del mercado.
- Calcular el porcentaje del ingreso destinado a medicamentos.
- Seleccionar enfermedades con posible cobertura especial.
- Detectar posibles beneficios de PAMI según la situación del afiliado.
- Buscar agencias PAMI por provincia, UGL y localidad.
- Seleccionar automáticamente agencias cuando corresponde.
- Generar un informe completo en formato PDF.
- En etapa preliminar, ejecutar todo el sistema desde una aplicación web desarrollada con Streamlit.

---

# Módulos desarrollados

El proyecto se encuentra organizado de manera modular.

| Archivo | Función |
|----------|----------|
| `medicamentos.py` | Limpieza, búsqueda y selección de medicamentos. |
| `agencias.py` | Selección de agencias PAMI por provincia, UGL y localidad. |
| `beneficios.py` | Evaluación de posibles beneficios y cobertura especial. |
| `analisis_gasto.py` | Cálculo económico y generación de indicadores. |
| `pdf_generado.py` | Construcción del informe PDF para el usuario. |
| `streamlit_app.py` | Interfaz gráfica del sistema. |
| `cargar_datos.py` | Carga y administración de datasets. |
| `scraping_precios_actualizados.py` | Comparacion de precios de medicamentos entre el dataset oficial de Pami y el de mercado. |
| `scraping_valores_previsionales.py` | Extracción de valores de jubilación mínima y bono previsional. |

---

# Origen de los datos

La aplicación utiliza información proveniente de organismos oficiales.

- Dataset oficial de medicamentos para afiliados PAMI.
- Dataset oficial de Agencias PAMI.
- Dataset de Centros de Jubilados.
- Índice de Precios al Consumidor (INDEC).
- Dataset propio de actualización jubilatoria.
- Scraping de jubilación mínima desde fuentes oficiales.
---

# Tecnologías utilizadas

- Python
- Pandas
- Streamlit
- FPDF
- Git
- GitHub
- Open Data PAMI
- INDEC
- Scraping

---

# Estado del proyecto

| Módulo | Estado |
|---------|---------|
| Medicamentos | Finalizado |
| Agencias PAMI | Finalizado |
| Beneficios | Finalizado |
| Análisis económico | Finalizado |
| Generación de PDF | Finalizado |
| Aplicación Streamlit | En proceso avanzado |
| Scraping de jubilación mínima | Finalizado |
| Scraping de precios de medicamentos | Finalizado |

---

# Próximas mejoras

Entre las funcionalidades previstas para futuras versiones se encuentran:

- Publicación online mediante Streamlit Cloud.

---

# Observaciones

Los resultados obtenidos por la aplicación tienen carácter orientativo.

La cobertura efectiva de un medicamento puede depender de:
- Empadronamientos específicos
- Autorizaciones médicas
- Subsidios sociales
- Programas especiales de cobertura
- Normativa vigente de PAMI

Por este motivo, el sistema recomienda siempre consultar la información con la agencia PAMI correspondiente antes de tomar decisiones.

---

## Licencia

Proyecto académico desarrollado como Trabajo Final Integrador para la asignatura **Ciencia de Datos para Politólogos/as**.# Proyecto-Final-MVP
