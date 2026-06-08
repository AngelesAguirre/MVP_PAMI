# SELECCIÓN DE LAS AGENCIAS

Mediante una búsqueda se ofrecerá al usuario dos opciones de agencias cercanas a su dirección declarada. De esta forma se le proveerá la información para que pueda acercarse a alguna de las agencias a realizar el trámite que le corresponda.

## 1. CARGA DE LA BASE DE AGENCIAS PAMI

### OPCIÓN 1
Se utiliza la URL del dataset de PAMI, que permite obtener la base actualizada de las agencias disponibles de manera automática.

### Opción 2
En el caso de que no corra la URL del dataset de PAMI (puede deberse a que la página no esté funcionando por problemas técnicos) se sube el último dataset descargado desde dicho link.

### Aclaración
El código va a ejecutar la opción 1 a menos que la web de PAMI no responda, en cuyo caso se ejecutará la opción 2. Esta última es básicamente un archivo de respaldo declarado en el código. 
El archivo de respaldo se sube al código una vez que se descargó desde el link del archivo que no se pudo ejecutar, es decir, que trae exactamente la misma data (columnas) pero sin asegurar que esté actualizada en tiempo real. Debido a esto, se dejará un mensaje aclaratorio con esta información (en caso de que se ejecute la opción 2).

## 2. CARGA Y LIMPIEZA DE LA BASE DE AGENCIAS

Consiste en la carga de la base de agencias de PAMI para utilizar en la búsqueda. 
Primero se creará una copia para no modificar el dataset inicial, y en esta copia se corregirá el encabezado en caso de que el Excel traiga filas iniciales innecesarias. 
Luego se limpiarán los nombres de las columnas y se eliminarán aquellas que no serán utilizadas. Las columnas serán renombradas para facilitar su comprensión.
En el paso siguiente se limitarán los espacios en las columnas de texto, y se pasarán las columnas clave a mayúsculas. 
Posteriormente, se creará la columna "Provincias". Debido a que la provincia de Buenos Aires y la CABA no tienen sus agencias agrupadas a nivel provincial, se reagruparán las UGL (Unidades de Gestión Local) de ambas en una misma categoría que corresponda a la provincia de Buenos Aires. 
También se agruparán otros casos casos especiales, como los de Córdoba y Entre Ríos, que tienen agencias en municipios registrados por fuera de la categoría de sus respectivas provincias.

## 3. OPCIONES PARA LISTAS DESPLEGABLES

El desplegable devolverá las provincias disponibles para el primer selector, las UGL/ubicaciones territoriales de una provincia, y las localidades disponibles dentro de una ULG.

## 4. FILTRAR AGENCIAS SEGÚN LA SELECCIÓN DEL USUARIO

Se le solicita al usuario que indique su provincia y localidad (la ubicación disponible más cercana).
En base a lo que el usuario ingresó, la búsqueda devolverá las agencias disponibles según provincia, UGL y localidad.
En caso de que la localidad indicada cuente con una sola agencia, la búsqueda devolverá otras localidades dentro de la misma UGL para poder ofrecerle al usuario una segunda localidad cercana.

## 5. TEXTO PARA MOSTRAR EN LAS LISTAS DESPLEGABLES

Se creará un texto claro para mostrar cada agencia en Streamlit.

## 6. LÓGICA DE SELECCIÓN DE AGENCIAS

La búsqueda evaluará cuántas agencias tiene una localidad.
- Si no hay agencias en dicha localidad, devolverá 'sin_agencias'.
- Si hay una única agencia devolverá 'una_agencia'.
- Si existen múltiples agencias devolverá 'varias_agencias'.

En el segundo caso (una agencia), la búsqueda devolverá la única agencia existente automáticamente.
En el tercer caso, se le pedirá al usuario que seleccione dos agencias dentro de su misma localidad. En Streamlit los índices serán visualizados en listas desplegables.

## 7.ARMADO DE RESUMEN FINAL DE AGENCIAS

Se convertirán las agencias seleccionadas en una tabla final. Esta tabla será mostrada al usuario y luego podrá incluirse en un PDF descargable.