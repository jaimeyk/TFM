import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt

st.set_page_config(layout="wide")

microdata = pd.read_csv('cbecs2018_final_public.csv')
microdatasi = microdata.copy()

# Conversión de BTU a MJ y pies cuadrados a metros cuadrados
btucolumns = ['MFBTU', 'ELBTU', 'NGBTU', 'FKBTU','DHBTU', 'MFHTBTU', 'MFCLBTU', 'MFVNBTU', 'MFWTBTU','MFLTBTU', 'MFCKBTU', 'MFRFBTU', 'MFOFBTU', 'MFPCBTU', 'MFOTBTU', 'ELHTBTU', 'ELCLBTU', 'ELVNBTU', 'ELWTBTU', 'ELLTBTU',
              'ELCKBTU', 'ELRFBTU', 'ELOFBTU', 'ELPCBTU', 'ELOTBTU', 'NGHTBTU', 'NGCLBTU', 'NGWTBTU', 'NGCKBTU', 'NGOTBTU', 'FKHTBTU', 'FKCLBTU', 'FKWTBTU', 'FKCKBTU', 'FKOTBTU', 'DHHTBTU', 'DHCLBTU', 'DHWTBTU', 'DHCKBTU', 'DHOTBTU']  

btu2kWh = 1.055060/3600  # Conversión de miles de BTU a MJ
kWh2Mtoe = 8.6e-8
btu2Mtoe = btu2kWh*kWh2Mtoe #2.52e-11
sq2m = 0.092903  # Conversión de pies cuadrados a metros cuadrados

microdatasi[btucolumns] *= btu2Mtoe
microdatasi['SQFT'] *= sq2m

# Crear categorías por año de construcción
microdatasi.loc[(microdatasi['YRCONC'] == 2) | (microdatasi['YRCONC'] == 3), 'YRCONCN'] = 1
microdatasi.loc[(microdatasi['YRCONC'] == 4) | (microdatasi['YRCONC'] == 5), 'YRCONCN'] = 2
microdatasi.loc[(microdatasi['YRCONC'] == 6) | (microdatasi['YRCONC'] == 7), 'YRCONCN'] = 3
microdatasi.loc[microdatasi['YRCONC'] > 7, 'YRCONCN'] = 4

# Convertir la columna 'YRCONCN' a enteros
microdatasi['YRCONCN'] = microdatasi['YRCONCN'].astype(int)

# Reemplazos en la columna PBAPLUS
cambios = {
    3: 2, 4: 2, 5: 2, 6: 2, 7: 2,  # Oficinas
    43: 42, 51: 50,  # Comercios
    23: 22, 24: 22, 25: 22, 26: 22,  # Edificios públicos
    17: 16, 52: 16,  # Orden público
    14: 12, 15: 12,  # Tiendas/Venta de alimentos
    33: 32, 34: 32,  # Restaurantes
    46: 44, 47: 44, 48: 44,  # Servicios
    19: 18  # Ambulatorios
}

# Aplicar los cambios a PBAPLUS
microdatasi['PBAPLUS'] = microdatasi['PBAPLUS'].replace(cambios)

# Aplicar las reglas de clasificación a la columna PBAN
microdatasi.loc[microdatasi['PBAPLUS'] == 1, 'PBAN'] = 1  # Vacíos
microdatasi.loc[microdatasi['PBAPLUS'] == 2, 'PBAN'] = 2  # Oficinas
microdatasi.loc[microdatasi['PBAPLUS'].isin([9, 10, 11, 20]), 'PBAN'] = 3  # Almacenes
microdatasi.loc[microdatasi['PBAPLUS'].isin([12, 32]), 'PBAN'] = 4  # Alimentación
microdatasi.loc[microdatasi['PBAPLUS'] == 44, 'PBAN'] = 5  # Servicios
microdatasi.loc[microdatasi['PBAPLUS'].isin([18, 35]), 'PBAN'] = 6  # Servicios sanitarios
microdatasi.loc[microdatasi['PBAPLUS'].isin([22, 21, 16]), 'PBAN'] = 7  # Edificios públicos
microdatasi.loc[microdatasi['PBAPLUS'].isin([27, 28, 29, 30, 54]), 'PBAN'] = 8  # Educación
microdatasi.loc[microdatasi['PBAPLUS'].isin([36, 37, 38, 39, 40]), 'PBAN'] = 9  # Alojamiento
microdatasi.loc[microdatasi['PBAPLUS'].isin([42, 50]), 'PBAN'] = 10  # Comercio
microdatasi.loc[microdatasi['PBAPLUS'].isin([8, 49]), 'PBAN'] = 11  # Otros

# Verificar valores de NaN en PBAN y reemplazarlos
microdatasi['PBAN'].fillna(99, inplace=True)  # Asignar un valor específico para casos sin asignación
microdatasi['PBAN'] = microdatasi['PBAN'].astype(int)

# Sumar categorías de calefacción y aire acondicionado
microdatasi['CLIMAF'] = microdatasi['MFHTBTU'] + microdatasi['MFCLBTU'] + microdatasi['MFVNBTU']
microdatasi['CLIMAE'] = microdatasi['ELHTBTU'] + microdatasi['ELCLBTU'] + microdatasi['ELVNBTU']

 # Definir tipos de edificios
tipo_edificio = ["Vacíos", "Oficina", "Almacenes","Alimentación", 
                 "Edificio público", "Sanitario", "Educación", 
                 "Alojamiento","Comercio", "Servicios", "Otros"]


st.title("Datos Energéticos de Edificios")

# PESTAÑAS SUPERIORES - Tipos de edificio
col1, col2, col3, col4, col5, col6 = st.columns([1.3,1.3,1.3,1.3,1.3,1.3])

with col1:
    tipo = st.selectbox("Seleccione tipo de edificio:",
        tipo_edificio,
        key="tipo_edificio",
        format_func=lambda x: f"🏢 {x}"
    )

st.markdown("---")

tipo_edificio_PBAN = {
    "Vacíos": 1,
    "Oficina": 2,
    "Almacenes": 3,
    "Alimentación": 4,
    "Servicios": 5,
    "Sanitario": 6,
    "Edificio público": 7,
    "Educación": 8,
    "Alojamiento": 9,
    "Comercio": 10,
    "Otros": 11
}

# FILTRO TIPO
PBAN_tipo = tipo_edificio_PBAN[tipo]
microdatasi = microdatasi[microdatasi["PBAN"] == PBAN_tipo]

#FILTRO SUBTIPO
# subtipo_prueba = [[None],
#                     ['Oficina'],
#                     ['Centro de distribución','Almacén sin refrigeración','Alquiler de almacenes públicos','Almacén con refrigeración'],
#                     ['Venta de alimentos','Restauración'],
#                     ['Orden público','Religión','Servicio público'],
#                     ['Hospital','Ambulatorio'],
#                     ['Infantil/Guardería','Escuela primaria','Escuela secundaria','Bachillerato','Universidad'],
#                     ['Residencia de ancianos','Residencia universitaria','Hotel','Motel/B&B','Otro hospedaje'],
#                     ['Centro comercial','Tiendas'],
#                     ['Servicios'], 
#                     ['Laboratorio']]

subtipos_por_tipo = {
    "Vacíos": [None],
    "Oficina": ['Oficina'],
    "Almacenes": ['Centro de distribución', 'Almacén sin refrigeración', 'Alquiler de almacenes públicos', 'Almacén con refrigeración'],
    "Alimentación": ['Venta de alimentos', 'Restauración'],
    "Edificio público": ['Orden público', 'Religión', 'Servicio público'],
    "Sanitario": ['Hospital', 'Ambulatorio'],
    "Educación": ['Infantil/Guardería', 'Escuela primaria', 'Escuela secundaria', 'Bachillerato', 'Universidad'],
    "Alojamiento": ['Residencia de ancianos', 'Residencia universitaria', 'Hotel', 'Motel/B&B', 'Otro hospedaje'],
    "Comercio": ['Centro comercial', 'Tiendas'],
    "Servicios": ['Servicios'],
    "Otros": ['Laboratorio']
}

subtipo_edificio_PBAPLUS = {
  'Oficina': [2, 3, 4, 5, 6, 7],
  'Laboratorio': [8],
  'Centro de distribución': [9],
  'Almacén sin refrigeración': [10],
  'Alquiler de almacenes públicos': [11],
  'Almacén con refrigeración': [20],
  'Venta de alimentos': [12, 14, 15],
  'Restauración': [32, 33, 34],
  'Orden público': [16, 17, 52],
  'Religión': [21],
  'Servicio público': [22, 23, 24, 25, 26],
  'Hospital': [35],
  'Ambulatorio': [18, 19],
  'Infantil/Guardería': [30],
  'Escuela primaria': [28],
  'Escuela secundaria': [54],
  'Bachillerato': [29],
  'Universidad': [27],
  'Residencia de ancianos': [36],
  'Residencia universitaria': [37],
  'Hotel': [38],
  'Motel/B&B': [39],
  'Otro hospedaje': [40],
  'Centro comercial': [50, 51],
  'Tiendas': [42, 43],
  'Servicios': [44, 46, 47, 48],
  'Otros': [49]
}

    # Seleccionar subtipo
with col2:
    subtipo = st.selectbox("Seleccione subtipo de edificio:", 
                           subtipos_por_tipo[tipo],
                           index=None, placeholder="Todos")

if subtipo is not None:
    PBAPLUS_values = subtipo_edificio_PBAPLUS.get(subtipo.strip(), [])
    if PBAPLUS_values:
        microdatasi = microdatasi[microdatasi["PBAPLUS"].isin(PBAPLUS_values)]

if microdatasi.empty:
    st.warning("No hay datos disponibles para la combinación de tipo y subtipo seleccionada.")
    st.stop()

#FILTRO TAMAÑO
    #TENGO QUE RECLASIFICAR ESTE FILTRO SEGÚN EL TIPO DE EDIFICIO...
if tipo == "Alojamiento":
    tamaño_edificio = ['S', 'M', 'L']
    # AQUÍ AJUSTO EL TAMAÑO PARA ESTE TIPO DE EDIF.
    microdatasi.loc[microdatasi['SQFT'] < 10000, 'SQFTCM'] = 1 #S
    microdatasi.loc[(microdatasi['SQFT'] >= 10000) & (microdatasi['SQFT'] < 20000), 'SQFTCM'] = 2 #M
    microdatasi.loc[microdatasi['SQFT'] >= 20000, 'SQFTCM'] = 3 #L
    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].astype(int)

    tamaño_edificio_SQFTC1 = [1, 2, 3]
    with col3:
        tamaño = st.selectbox("Seleccione tamaño del edificio:",tamaño_edificio, index=None
                                ,placeholder="Todos")
    if tamaño is not None:
        SQFTC1 = tamaño_edificio_SQFTC1[tamaño_edificio.index(tamaño)]
        microdatasi = microdatasi[microdatasi["SQFTCM"] == SQFTC1]

elif tipo == "Oficina":
    tamaño_edificio = ['XS', 'S', 'M', 'L', 'XL']
    microdatasi.loc[(microdatasi['SQFT']) <= 500, 'SQFTCM'] = 1 #XS
    microdatasi.loc[((microdatasi['SQFT']) > 500) & ((microdatasi['SQFT']) <= 5000), 'SQFTCM'] = 2 #S
    microdatasi.loc[((microdatasi['SQFT']) > 5000) & ((microdatasi['SQFT']) <= 15000), 'SQFTCM'] = 3 #M
    microdatasi.loc[((microdatasi['SQFT']) > 15000) & ((microdatasi['SQFT']) < 30000), 'SQFTCM'] = 4 #L
    microdatasi.loc[(microdatasi['SQFT']) >= 30000, 'SQFTCM'] = 5 #XL

    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].fillna(0).astype(int)

    tamaño_edificio_SQFTC1 = [1, 2, 3, 4, 5]
    with col3:
        tamaño = st.selectbox("Seleccione tamaño del edificio:",tamaño_edificio
                                ,index=None ,placeholder="Todos")
    if tamaño is not None:
        SQFTC1 = tamaño_edificio_SQFTC1[tamaño_edificio.index(tamaño)]
        microdatasi = microdatasi[microdatasi["SQFTCM"] == SQFTC1]
        
elif tipo == "Almacenes":
    tamaño_edificio = ['S', 'M', 'L']
    microdatasi.loc[(microdatasi['SQFT']) <= 2500, 'SQFTCM'] = 1
    microdatasi.loc[((microdatasi['SQFT']) > 2500) & ((microdatasi['SQFT']) < 15000), 'SQFTCM'] = 2 
    microdatasi.loc[(microdatasi['SQFT']) >= 15000, 'SQFTCM'] = 3

    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].fillna(0).astype(int)

    tamaño_edificio_SQFTC1 = [1, 2, 3]
    with col3:
        tamaño = st.selectbox("Seleccione tamaño del edificio:",tamaño_edificio
                                ,index=None ,placeholder="Todos")
    if tamaño is not None:
        SQFTC1 = tamaño_edificio_SQFTC1[tamaño_edificio.index(tamaño)]
        microdatasi = microdatasi[microdatasi["SQFTCM"] == SQFTC1]

elif tipo == "Educación":
    tamaño_edificio = ['XS', 'S', 'M', 'L']
    microdatasi.loc[(microdatasi['SQFT']) <= 5000, 'SQFTCM'] = 1
    microdatasi.loc[((microdatasi['SQFT']) > 5000) & ((microdatasi['SQFT']) <= 10000), 'SQFTCM'] = 2 
    microdatasi.loc[((microdatasi['SQFT']) > 10000) & ((microdatasi['SQFT']) < 20000), 'SQFTCM'] = 3 
    microdatasi.loc[(microdatasi['SQFT']) >= 20000, 'SQFTCM'] = 4

    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].fillna(0).astype(int)

    tamaño_edificio_SQFTC1 = [1, 2, 3, 4]
    with col3:
        tamaño = st.selectbox("Seleccione tamaño del edificio:",tamaño_edificio
                                ,index=None ,placeholder="Todos")
    if tamaño is not None:
        SQFTC1 = tamaño_edificio_SQFTC1[tamaño_edificio.index(tamaño)]
        microdatasi = microdatasi[microdatasi["SQFTCM"] == SQFTC1]

elif tipo == "Alimentación":
    tamaño_edificio = ['S', 'M', 'L']
    microdatasi.loc[(microdatasi['SQFT']) <= 250, 'SQFTCM'] = 1
    microdatasi.loc[((microdatasi['SQFT']) > 250) & ((microdatasi['SQFT']) < 500), 'SQFTCM'] = 2 
    microdatasi.loc[(microdatasi['SQFT']) >= 500, 'SQFTCM'] = 3

    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].fillna(0).astype(int)

    tamaño_edificio_SQFTC1 = [1, 2, 3]
    with col3:
        tamaño = st.selectbox("Seleccione tamaño del edificio:",tamaño_edificio
                                ,index=None ,placeholder="Todos")
    if tamaño is not None:
        SQFTC1 = tamaño_edificio_SQFTC1[tamaño_edificio.index(tamaño)]
        microdatasi = microdatasi[microdatasi["SQFTCM"] == SQFTC1]
            
elif tipo == "Edificio público":
    tamaño_edificio = ['S', 'M', 'L']
    microdatasi.loc[(microdatasi['SQFT']) <= 1000, 'SQFTCM'] = 1
    microdatasi.loc[((microdatasi['SQFT']) > 1000) & ((microdatasi['SQFT']) < 5000), 'SQFTCM'] = 2 
    microdatasi.loc[(microdatasi['SQFT']) >= 5000, 'SQFTCM'] = 3

    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].fillna(0).astype(int)

    tamaño_edificio_SQFTC1 = [1, 2, 3]
    with col3:
        tamaño = st.selectbox("Seleccione tamaño del edificio:",tamaño_edificio
                                ,index=None ,placeholder="Todos")
    if tamaño is not None:
        SQFTC1 = tamaño_edificio_SQFTC1[tamaño_edificio.index(tamaño)]
        microdatasi = microdatasi[microdatasi["SQFTCM"] == SQFTC1]
        
elif tipo == "Sanitario":
    tamaño_edificio = ['S', 'M', 'L']
    microdatasi.loc[(microdatasi['SQFT']) <= 10000, 'SQFTCM'] = 1
    microdatasi.loc[((microdatasi['SQFT']) > 10000) & ((microdatasi['SQFT']) < 30000), 'SQFTCM'] = 2 
    microdatasi.loc[(microdatasi['SQFT']) >= 30000, 'SQFTCM'] = 3

    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].fillna(0).astype(int)

    tamaño_edificio_SQFTC1 = [1, 2, 3]
    with col3:
        tamaño = st.selectbox("Seleccione tamaño del edificio:",tamaño_edificio
                                ,index=None ,placeholder="Todos")
    if tamaño is not None:
        SQFTC1 = tamaño_edificio_SQFTC1[tamaño_edificio.index(tamaño)]
        microdatasi = microdatasi[microdatasi["SQFTCM"] == SQFTC1]
        
elif tipo == "Servicios":
    tamaño_edificio = ['S', 'M', 'L']
    microdatasi.loc[(microdatasi['SQFT']) <= 500, 'SQFTCM'] = 1
    microdatasi.loc[((microdatasi['SQFT']) > 500) & ((microdatasi['SQFT']) < 2000), 'SQFTCM'] = 2 
    microdatasi.loc[(microdatasi['SQFT']) >= 2000, 'SQFTCM'] = 3

    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].fillna(0).astype(int)

    tamaño_edificio_SQFTC1 = [1, 2, 3]
    with col3:
        tamaño = st.selectbox("Seleccione tamaño del edificio:",tamaño_edificio
                                ,index=None ,placeholder="Todos")
    if tamaño is not None:
        SQFTC1 = tamaño_edificio_SQFTC1[tamaño_edificio.index(tamaño)]
        microdatasi = microdatasi[microdatasi["SQFTCM"] == SQFTC1]
        
elif tipo == "Comercio":
    tamaño_edificio = ['XS', 'S', 'M', 'L']
    microdatasi.loc[(microdatasi['SQFT']) <= 2000, 'SQFTCM'] = 1
    microdatasi.loc[((microdatasi['SQFT']) > 2000) & ((microdatasi['SQFT']) <= 5000), 'SQFTCM'] = 2 
    microdatasi.loc[((microdatasi['SQFT']) > 5000) & ((microdatasi['SQFT']) < 15000), 'SQFTCM'] = 3 
    microdatasi.loc[(microdatasi['SQFT']) >= 15000, 'SQFTCM'] = 4

    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].fillna(0).astype(int)

    tamaño_edificio_SQFTC1 = [1, 2, 3, 4]
    with col3:
        tamaño = st.selectbox("Seleccione tamaño del edificio:",tamaño_edificio
                                ,index=None ,placeholder="Todos")
    if tamaño is not None:
        SQFTC1 = tamaño_edificio_SQFTC1[tamaño_edificio.index(tamaño)]
        microdatasi = microdatasi[microdatasi["SQFTCM"] == SQFTC1]

elif tipo == "Vacíos":
    tamaño_edificio = ['XS', 'S', 'M', 'L']
    microdatasi.loc[(microdatasi['SQFT']) <= 500, 'SQFTCM'] = 1
    microdatasi.loc[((microdatasi['SQFT']) > 500) & ((microdatasi['SQFT']) <= 5000), 'SQFTCM'] = 2 
    microdatasi.loc[((microdatasi['SQFT']) > 5000) & ((microdatasi['SQFT']) < 10000), 'SQFTCM'] = 3 
    microdatasi.loc[(microdatasi['SQFT']) >= 10000, 'SQFTCM'] = 4

    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].fillna(0).astype(int)

    tamaño_edificio_SQFTC1 = [1, 2, 3, 4]
    with col3:
        tamaño = st.selectbox("Seleccione tamaño del edificio:",tamaño_edificio
                                ,index=None ,placeholder="Todos")
    if tamaño is not None:
        SQFTC1 = tamaño_edificio_SQFTC1[tamaño_edificio.index(tamaño)]
        microdatasi = microdatasi[microdatasi["SQFTCM"] == SQFTC1]

elif tipo == "Otros":
    tamaño_edificio = ['XS', 'S', 'M', 'L', 'XL']
    microdatasi.loc[(microdatasi['SQFT']) <= 1000, 'SQFTCM'] = 1
    microdatasi.loc[((microdatasi['SQFT']) > 1000) & ((microdatasi['SQFT']) <= 2500), 'SQFTCM'] = 2 
    microdatasi.loc[((microdatasi['SQFT']) > 2500) & ((microdatasi['SQFT']) <= 5000), 'SQFTCM'] = 3 
    microdatasi.loc[((microdatasi['SQFT']) > 5000) & ((microdatasi['SQFT']) < 20000), 'SQFTCM'] = 4
    microdatasi.loc[(microdatasi['SQFT']) >= 20000, 'SQFTCM'] = 5

    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].fillna(0).astype(int)

    tamaño_edificio_SQFTC1 = [1, 2, 3, 4, 5]
    with col3:
        tamaño = st.selectbox("Seleccione tamaño del edificio:",tamaño_edificio
                                ,index=None ,placeholder="Todos")
    if tamaño is not None:
        SQFTC1 = tamaño_edificio_SQFTC1[tamaño_edificio.index(tamaño)]
        microdatasi = microdatasi[microdatasi["SQFTCM"] == SQFTC1]


clasif_tipo_grafica={"Distribución":[
            "Distribución de superficie por año de construcción",
            "Distribución de Superficies por Categoría Climática",
            "Distribución del consumo por tamaño",
            "Distribución del consumo por Usos Finales y Tipo de Energía"],
        "Estructura":[
            "Estructura del área por tamaños",
            "Estructura del consumo por usos",
            "Estructura del consumo por fuentes"],
        "Análisis": [
            "Análisis del Consumo por Clima y Usos Finales",
            "Análisis del Consumo por año y Usos Finales",
            "Análisis del Consumo por tamaño y Usos Finales"],
        "Consumo": [
            "Consumo de Energía por Clima y Tipo de Energía",
            "Consumo de Energía por Tamaño y Tipo de Energía",
            "Consumo de Energía por Edad y Tipo de Energía"],
        "Actividad":[]}

tipo_grafica = ["Distribución", "Estructura", "Análisis", "Consumo", "Actividad"]

# PESTAÑAS IZQUIERDA - Gráficas según el tipo de edificio seleccionado

with st.sidebar:
    st.subheader("Gráficas disponibles")
    #grafica_idx=st.radio
    grafica_tipo = st.selectbox(
        "Seleccione tipo de gráfica:",
        tipo_grafica,
        key="grafica_seleccionada"
    )
graficas = clasif_tipo_grafica[grafica_tipo]

if tamaño is not None and grafica_tipo == "Estructura":
    graficas = [
        g for g in graficas
        if g != "Estructura del área por tamaños"
    ]
elif tamaño is not None and grafica_tipo == "Distribución":
    graficas = [
        g for g in graficas
        if g != "Distribución del consumo por tamaño"
    ]
elif tamaño is not None and grafica_tipo == "Análisis":
    graficas = [
        g for g in graficas
        if g != "Análisis del Consumo por tamaño y Usos Finales"
    ]

with st.sidebar:
    grafica_idx = st.radio("Seleccione la gráfica:", graficas)

st.markdown(
    f"<div style='text-align: center; font-size:2.0em; font-weight:600;'>{grafica_tipo} - {tipo}</div>",
    unsafe_allow_html=True
)
st.markdown(
    f"<div style='text-align: center; font-size:2.0em; font-weight:600;'>{grafica_idx} - {tipo}</div>",
    unsafe_allow_html=True
)
x = np.arange(1990, 2023)

#FILTRO NUMERO DE PLANTAS
plantas_edificio = ['1','2','3','4','5','6','7','8','9','10-14','15 o más']

plantas_edificio_NFLOOR1 = [1,2,3,4,5,6,7,8,9,994,995]
with col4:
    plantas = st.selectbox("Seleccione las plantas del edificio:",plantas_edificio,
                                index=None, placeholder="Todos") 

if plantas is not None:
    NFLOOR1 = plantas_edificio_NFLOOR1[plantas_edificio.index(plantas)]
    microdatasi = microdatasi[microdatasi["NFLOOR"] == NFLOOR1]

#FILTRO CLIMA
clima_edificio = ['Frío o muy frío','Frío','Templado','Cálido','Muy cálido']

clima_edificio_PUBCLIM1 = [1,2,3,4,5]
with col5:
    clima = st.selectbox("Seleccione el clima del edificio:",clima_edificio,index=None, placeholder="Todos")
    
if clima is not None:
    PUBCLIM1 = clima_edificio_PUBCLIM1[clima_edificio.index(clima)]
    microdatasi = microdatasi[microdatasi["PUBCLIM"]==PUBCLIM1]

    #AQUI ELIMINO LAS GRÁFICAS QUE TIENEN QUE VER CON LOS TAMAÑOS, QUE SE VEN ALTERADAS POR ESTE FILTRO
    graficas.remove("Distribución de Superficies por Categoría Climática")
    graficas.remove("Análisis del Consumo por Clima y Usos Finales")

#FILTRO EDAD
edad_edificio = ['Antes de 1960', '1960-1979', '1980-1999', '2000-2018']

microdatasi.loc[(microdatasi['YRCONC'] == 2) | (microdatasi['YRCONC'] == 3), 'YRCONC'] = 1 #Antes de 1960
microdatasi.loc[(microdatasi['YRCONC'] == 4) | (microdatasi['YRCONC'] == 5), 'YRCONC'] = 2 #1960-1979
microdatasi.loc[(microdatasi['YRCONC'] == 6) | (microdatasi['YRCONC'] == 7), 'YRCONC'] = 3 #1980-1999
microdatasi.loc[microdatasi['YRCONC'] > 7, 'YRCONC'] = 4 #2000-2018

microdatasi['YRCONC'] = microdatasi['YRCONC'].fillna(0).astype(int)

edad_edificio_YRCONC1 = [1, 2, 3, 4]
with col6:
    edad = st.selectbox("Seleccione la edad del edificio:",edad_edificio,
                         index=None, placeholder="Todos")
    
if edad is not None:    
    YRCONC1 = edad_edificio_YRCONC1[edad_edificio.index(edad)]
    microdatasi = microdatasi[microdatasi["YRCONC"]==YRCONC1]

    #AQUI ELIMINO LAS GRÁFICAS QUE TIENEN QUE VER CON LOS TAMAÑOS, QUE SE VEN ALTERADAS POR ESTE FILTRO
    graficas.remove("Distribución de superficie por año de construcción")
    graficas.remove("Análisis del Consumo por año y Usos Finales")

    st.markdown("---")


#AQUÍ VOY A DESARROLLAR CADA TIPOLOGÍA, DETALLANDO LAS DISTINTAS GRÁFICAS, SUS NOMBRES Y LOS TAMAÑOS (m2) DE CADA TIPO
if tipo == "Alojamiento":
    # pban = 9
    # AQUÍ AJUSTO EL TAMAÑO PARA ESTE TIPO DE EDIF.
    microdatasi.loc[microdatasi['SQFT'] <= 10000, 'SQFTCM'] = 1
    microdatasi.loc[(microdatasi['SQFT'] > 10000) & (microdatasi['SQFT'] < 20000), 'SQFTCM'] = 2
    microdatasi.loc[microdatasi['SQFT'] >= 20000, 'SQFTCM'] = 3
    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].astype(int)

    nombres = ['S <= 10000', 'M 10000 - 20000', 'L >= 20000']
    nombres_simples = ['S', 'M', 'L']

elif tipo == "Almacenes":
    pban = 3
    # AQUÍ AJUSTO EL TAMAÑO PARA ESTE TIPO DE EDIF.
    microdatasi.loc[microdatasi['SQFT'] <= 2500, 'SQFTCM'] = 1
    microdatasi.loc[(microdatasi['SQFT'] > 2500) & (microdatasi['SQFT'] < 15000), 'SQFTCM'] = 2
    microdatasi.loc[microdatasi['SQFT'] >= 15000, 'SQFTCM'] = 3
    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].astype(int)

    nombres = ['S <= 2500', 'M 2500 - 15000', 'L >= 15000']
    nombres_simples = ['S', 'M', 'L']

elif tipo == "Educación":
    # pban = 8
    # AQUÍ AJUSTO EL TAMAÑO PARA ESTE TIPO DE EDIF.
    microdatasi.loc[microdatasi['SQFT'] <= 5000, 'SQFTCM'] = 1
    microdatasi.loc[(microdatasi['SQFT'] > 5000) & (microdatasi['SQFT'] <= 10000), 'SQFTCM'] = 2
    microdatasi.loc[(microdatasi['SQFT'] >= 10000) & (microdatasi['SQFT'] < 20000), 'SQFTCM'] = 3
    microdatasi.loc[microdatasi['SQFT'] >= 20000, 'SQFTCM'] = 4
    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].astype(int)

    nombres = ['XS <= 5000', 'S 5000 - 10000', 'M 10000 - 20000', 'L >= 20000']
    nombres_simples = ['XS', 'S', 'M', 'L']

elif tipo == "Oficina":
    # pban = 2
    # AQUÍ AJUSTO EL TAMAÑO PARA ESTE TIPO DE EDIF.
    microdatasi.loc[microdatasi['SQFT'] <= 500, 'SQFTCM'] = 1
    microdatasi.loc[(microdatasi['SQFT'] > 500) & (microdatasi['SQFT'] <= 5000), 'SQFTCM'] = 2
    microdatasi.loc[(microdatasi['SQFT'] >= 5000) & (microdatasi['SQFT'] <= 15000), 'SQFTCM'] = 3
    microdatasi.loc[(microdatasi['SQFT'] >= 15000) & (microdatasi['SQFT'] < 30000), 'SQFTCM'] = 4
    microdatasi.loc[microdatasi['SQFT'] >= 30000, 'SQFTCM'] = 5
    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].astype(int)

    nombres = ['XS <= 500', 'S 500 - 5000', 'M 5000 - 15000', 'L 15000 - 30000', 'XL >= 30000']
    nombres_simples = ['XS', 'S', 'M', 'L', 'XL']

elif tipo == "Alimentación":
    # pban = 4
    # AQUÍ AJUSTO EL TAMAÑO PARA ESTE TIPO DE EDIF.
    microdatasi.loc[microdatasi['SQFT'] <= 250, 'SQFTCM'] = 1
    microdatasi.loc[(microdatasi['SQFT'] > 250) & (microdatasi['SQFT'] < 500), 'SQFTCM'] = 2
    microdatasi.loc[microdatasi['SQFT'] >= 500, 'SQFTCM'] = 3
    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].astype(int)

    nombres = ['S <= 250', 'M 250 - 500', 'L >= 500']
    nombres_simples = ['S', 'M', 'L']

elif tipo == "Edificio público":
    # pban = 7
    # AQUÍ AJUSTO EL TAMAÑO PARA ESTE TIPO DE EDIF.
    microdatasi.loc[microdatasi['SQFT'] <= 1000, 'SQFTCM'] = 1
    microdatasi.loc[(microdatasi['SQFT'] > 1000) & (microdatasi['SQFT'] < 5000), 'SQFTCM'] = 2
    microdatasi.loc[microdatasi['SQFT'] >= 5000, 'SQFTCM'] = 3
    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].astype(int)

    nombres = ['S <= 1000', 'M 1000 - 5000', 'L >= 5000']
    nombres_simples = ['S', 'M', 'L']

elif tipo == "Sanitario":
    # pban = 6
    # AQUÍ AJUSTO EL TAMAÑO PARA ESTE TIPO DE EDIF.
    microdatasi.loc[microdatasi['SQFT'] <= 10000, 'SQFTCM'] = 1
    microdatasi.loc[(microdatasi['SQFT'] > 10000) & (microdatasi['SQFT'] < 30000), 'SQFTCM'] = 2
    microdatasi.loc[microdatasi['SQFT'] >= 30000, 'SQFTCM'] = 3
    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].astype(int)

    nombres = ['S <= 10000', 'M 10000 - 30000', 'L >= 30000']
    nombres_simples = ['S', 'M', 'L']

elif tipo == "Servicios":
    # pban = 5
    # AQUÍ AJUSTO EL TAMAÑO PARA ESTE TIPO DE EDIF.
    microdatasi.loc[microdatasi['SQFT'] <= 500, 'SQFTCM'] = 1
    microdatasi.loc[(microdatasi['SQFT'] > 500) & (microdatasi['SQFT'] < 2000), 'SQFTCM'] = 2
    microdatasi.loc[microdatasi['SQFT'] >= 2000, 'SQFTCM'] = 3
    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].astype(int)

    nombres = ['S <= 500', 'M 500 - 2000', 'L >= 2000']
    nombres_simples = ['S', 'M', 'L']

elif tipo == "Comercio":
    # pban = 10
    # AQUÍ AJUSTO EL TAMAÑO PARA ESTE TIPO DE EDIF.
    microdatasi.loc[(microdatasi['SQFT']) <= 2000, 'SQFTCM'] = 1
    microdatasi.loc[((microdatasi['SQFT']) > 2000) & ((microdatasi['SQFT']) <= 5000), 'SQFTCM'] = 2 
    microdatasi.loc[((microdatasi['SQFT']) > 5000) & ((microdatasi['SQFT']) <= 15000), 'SQFTCM'] = 3 
    microdatasi.loc[(microdatasi['SQFT']) >= 15000, 'SQFTCM'] = 4
    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].astype(int)

    nombres = ['XS <= 2000', 'S 2000 - 5000', 'M 5000 - 15000', 'L >= 15000']
    nombres_simples = ['XS', 'S', 'M', 'L']

elif tipo == "Vacíos":
    # pban = 1
    # AQUÍ AJUSTO EL TAMAÑO PARA ESTE TIPO DE EDIF.
    microdatasi.loc[(microdatasi['SQFT']) <= 500, 'SQFTCM'] = 1
    microdatasi.loc[((microdatasi['SQFT']) > 500) & ((microdatasi['SQFT']) <= 5000), 'SQFTCM'] = 2 
    microdatasi.loc[((microdatasi['SQFT']) > 5000) & ((microdatasi['SQFT']) <= 10000), 'SQFTCM'] = 3 
    microdatasi.loc[(microdatasi['SQFT']) >= 10000, 'SQFTCM'] = 4
    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].astype(int)

    nombres = ['XS <= 500', 'S 500 - 5000', 'M 5000 - 10000', 'L >= 10000']
    nombres_simples = ['XS', 'S', 'M', 'L']

elif tipo == "Otros":
    # pban = 11
    # AQUÍ AJUSTO EL TAMAÑO PARA ESTE TIPO DE EDIF.
    microdatasi.loc[(microdatasi['SQFT']) <= 1000, 'SQFTCM'] = 1
    microdatasi.loc[((microdatasi['SQFT']) > 1000) & ((microdatasi['SQFT']) <= 2500), 'SQFTCM'] = 2 
    microdatasi.loc[((microdatasi['SQFT']) > 2500) & ((microdatasi['SQFT']) <= 5000), 'SQFTCM'] = 3
    microdatasi.loc[((microdatasi['SQFT']) > 5000) & ((microdatasi['SQFT']) < 20000), 'SQFTCM'] = 4
    microdatasi.loc[(microdatasi['SQFT']) >= 20000, 'SQFTCM'] = 5
    microdatasi['SQFTCM'] = microdatasi['SQFTCM'].astype(int)

    nombres = ['XS <= 1000', 'S 1000 - 2500', 'M 2500 - 5000', 'L 5000 - 20000', 'XL >= 20000']
    nombres_simples = ['XS', 'S', 'M', 'L', 'XL']

#AQUI APARECE EL CÓDIGO DE CADA GRÁFICA, QUE VARÍA SEGÚN EL TIPO DE EDIFICIO
espacio1, contenido, espacio2 = st.columns([1,3,1])

if grafica_idx == "Estructura del área por tamaños":
    # Inicializar listas
    etiquetas = []
    valores = []
    medias = []
    # Bucle para calcular los valores y medias para cada 'SQFTCM'
    n = len(nombres_simples)+1
    for i in range(1, n):
        Edi = microdatasi.query(f'SQFTCM=={i}')
        SQEdi = Edi['SQFT'] * Edi['FINALWT']
        TotalEdi = SQEdi.sum()
        TotalWTEdi = Edi['FINALWT'].sum()
        MediaEdi = TotalEdi / TotalWTEdi if TotalWTEdi > 0 else 0
        valores.append(TotalEdi)
        medias.append(MediaEdi)
        etiquetas.append(f'{nombres_simples[i-1]}')

    # Crear gráfico circular
    fig, ax = plt.subplots(figsize=(8, 10))
    wedges, texts, autotexts = ax.pie(
        valores,
        labels=etiquetas,
        autopct='%0.0f%%',
        startangle=90,
        colors=plt.cm.Paired.colors,
        textprops={'fontsize': 14, 'weight': 'bold'}
    )
    ax.axis('equal')

    # Crear la leyenda con nombre y promedio
    leyenda = [f"{nombres[i]} - Promedio:{medias[i]:.2f} m²/Edif" for i in range(n-1)]
    ax.legend(leyenda, title="Tamaños Promedio", loc="upper left", bbox_to_anchor=(1, 1), fontsize=12)

    with contenido:
        st.pyplot(fig, use_container_width=True)

        # Crear DataFrame con resultados
        df_resultados = pd.DataFrame({
            "Categoría": etiquetas,
            "Total (m²)": valores,
            "Promedio (m²/Edif)": medias
        })
        # Mostrar tabla en Streamlit
        col1, col2, col3 = st.columns([1, 8, 1])  # Columna central más ancha
        with col2:
            st.subheader("Tabla Resultados")
            # st.dataframe(df_resultados, use_container_width=True, hide_index=True)
            st.dataframe(
                df_resultados.style.format({
                    "Total (m²)": "{:.0f}",
                    "Promedio (m²/Edif)": "{:.0f}"
                }),
                use_container_width=True,
                hide_index=True
            )

elif grafica_idx == "Distribución de superficie por año de construcción":

    # Función para calcular la superficie total y media por rango de años
    def calcular_superficie(rango_yrconcn, microdatasi):
        edi = microdatasi.query(f'YRCONCN == {rango_yrconcn}')
        sq_edi = edi['SQFT'] * edi['FINALWT']
        total_edi = sq_edi.sum()  # Superficie total de ese rango de años
        total_wt_edi = edi['FINALWT'].sum()  # Número de edificios
        media_edi = total_edi / total_wt_edi if total_wt_edi > 0 else 0  # Área media de ese rango de años
        return total_edi, media_edi

    # Lista de rangos de años (1: antes 1960, 2: 1960-1980, 3: 1980-2000, 4: 2000-2018)
    rangos_yrconcn = [1, 2, 3, 4]
    nombres_rangos = ['Antes 1960', '1960-1980', '1980-2000', '2000-2018']

    # Inicializar listas para los totales y las medias
    totales = []
    medias = []
    labels = []

    # Calcular los valores para cada rango de años
    for i, rango in enumerate(rangos_yrconcn):
        total, media = calcular_superficie(rango, microdatasi)
        totales.append(total)
        medias.append(media)
        labels.append(nombres_rangos[i])

    # Crear gráfico circular
    plt.figure(figsize=(10, 8))  # Aumentamos el tamaño de la figura
    plt.pie(totales, labels=labels, autopct='%1.0f%%', startangle=90, textprops={'fontsize': 14, 'weight': 'bold'})
    plt.axis('equal')  # Asegura que el gráfico sea circular

    # Agregar una leyenda con la información completa
    leyenda = [f'{nombres_rangos[i]}: {medias[i]:.0f} m2/Edif' for i in range(4)]
    plt.legend(leyenda, title="Período y Media de Superficie", loc="upper left", bbox_to_anchor=(1, 1), fontsize=12)

    # Ajustar el diseño para evitar que se corten las etiquetas
    plt.tight_layout()

    with contenido:
        st.pyplot(plt)

        # Crear DataFrame con resultados
        df_resultados = pd.DataFrame({
            "Categoría": labels,
            "Total (m²)": totales,
            "Media (m²/Edif)": medias
        })
        # Mostrar tabla en Streamlit
        col1, col2, col3 = st.columns([1, 8, 1])  # Columna central más ancha
        with col2:
            st.subheader("Tabla Resultados")
            # st.dataframe(df_resultados, use_container_width=True, hide_index=True)
            st.dataframe(
                df_resultados.style.format({
                    "Total (m²)": "{:.0f}",
                    "Media (m²/Edif)": "{:.0f}"
                }),
                use_container_width=True,
                hide_index=True
            )

elif grafica_idx == "Distribución de Superficies por Categoría Climática":
    # Definir las categorías climáticas y su respectivo PUBCLIM
    climate_categories = {
        'Frío o muy frío': 1,
        'Frío': 2,
        'Templado': 3,
        'Cálido': 4,
        'Muy cálido': 5
    }

    # Inicializar listas para los cálculos
    totales = []
    medias = []

    # Calcular TotalEdi y MediaEdi para cada categoría
    for category, pubclim in climate_categories.items():
        # Filtrar el DataFrame
        Edi = microdatasi.query(f'PUBCLIM=={pubclim}') #El tipo se cambia aquí

        # Calcular la superficie total y media
        SQEdi = Edi['SQFT'] * Edi['FINALWT']
        TotalEdi = SQEdi.sum()
        TotalWTEdi = Edi['FINALWT'].sum()

        # Evitar división por cero
        if TotalWTEdi > 0:
            MediaEdi = TotalEdi / TotalWTEdi
        else:
            MediaEdi = 0

        # Guardar los resultados
        totales.append(TotalEdi)
        medias.append(MediaEdi)

        # # Mostrar resultados
        # print(f'{category} - Superficie Total: {TotalEdi:.2f}, Superficie Media: {MediaEdi:.2f}')

    # Crear el gráfico circular
    plt.figure(figsize=(10, 8))
    plt.pie(totales, labels=[f'{category}' for category, media in zip(climate_categories.keys(), medias)], autopct='%1.0f%%', startangle=90,
             textprops={'fontsize': 14, 'weight': 'bold'})
    plt.axis('equal')  # Para que el gráfico sea un círculo

    # Crear leyenda aparte (sólo el nombre y la media)
    leyenda = [f"{category}: {media:.2f} m²/Edif" for category, media in zip(climate_categories.keys(), medias)]
    plt.legend(leyenda, title="Clima y Superficie Media", loc="upper left", bbox_to_anchor=(1, 1), fontsize=12)

    plt.tight_layout()
    with contenido:
        st.pyplot(plt)

elif grafica_idx == "Distribución del consumo por tamaño":

    st.title("DEJO LAS UNIDADES KTOE ASI?")

    sqftcm_ranges = [1, 2, 3]
    labels = ['S', 'M', 'L']
    total_consumption_values = []
    media_consumo_por_edificio = []

    # Cálculo de los consumos totales y medios por categoría
    for sqftcm in sqftcm_ranges:
        edi = microdatasi.query(f'SQFTCM == {sqftcm}')
        # Consumo total ponderado
        total_consumption = (edi['MFBTU'] * edi['FINALWT']).sum()
        total_consumption_values.append(total_consumption)
        # Consumo medio ponderado
        total_wt = edi['FINALWT'].sum()
        if total_wt > 0:
            media_consumo = (total_consumption / total_wt) * 1000 #para pasar de Mtoe a ktoe
        else:
            media_consumo = 0
        media_consumo_por_edificio.append(media_consumo)

    # Suma total de consumos convertida a Mtoe
    ConsTotal = sum(total_consumption_values)

    # Crear gráfico circular con etiquetas personalizadas
    plt.figure(figsize=(10, 8))
    plt.pie(
        total_consumption_values, 
        labels=labels, 
        autopct='%1.1f%%', 
        startangle=90,
        textprops={'fontsize': 14, 'weight': 'bold'}
    )
    plt.axis('equal')  # Para que el gráfico sea un círculo

    # Crear leyenda aparte (nombre y consumo medio)
    leyenda = [f"{nombre}: {media_consumo:.4f} ktoe/Edif" for nombre, media_consumo in zip(labels, media_consumo_por_edificio)]
    plt.legend(leyenda, title="Tamaño y Consumo Medio", loc="upper left", bbox_to_anchor=(1, 1), fontsize=12)

    plt.tight_layout()
    with contenido:
        st.pyplot(plt)

elif grafica_idx == "Estructura del consumo por usos":
    # Datos de la columna que representan los diferentes usos energéticos
    usos = ['MFHTBTU', 'MFCLBTU', 'MFVNBTU', 'MFWTBTU', 'MFLTBTU', 'MFCKBTU', 'MFRFBTU', 'MFOFBTU', 'MFPCBTU', 'MFOTBTU']
    usos_labels = ['Calefacción', 'Aire acondicionado', 'Ventilación', 'ACS', 'Iluminación', 'Cocina', 'Refrigeración', 'Equipos Oficina', 'Computación', 'Otros']

    Edi = microdatasi.copy()
    if Edi.empty:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
        st.stop()
    # Cálculo de los consumos totales por uso
    total_consumos = []

    # for uso in usos:
    #     consumo = (Edi[uso] * Edi['FINALWT']).sum()
    #     total_consumos.append(consumo)

    # ----------------------------
    # CÁLCULO DE CONSUMOS
    # ----------------------------

    for uso in usos:
        consumo = (Edi[uso] * Edi['FINALWT']).sum()
        total_consumos.append(consumo)

    df_usos = pd.DataFrame({
        "Uso": usos_labels,
        "Consumo (Mtoe)": total_consumos
    })

    df_usos = df_usos[df_usos["Consumo (Mtoe)"] > 0]

    if df_usos.empty:
        st.warning("Todos los consumos son cero para los filtros seleccionados.")
        st.stop()

    df_usos["Porcentaje (%)"] = (
        df_usos["Consumo (Mtoe)"] /
        df_usos["Consumo (Mtoe)"].sum()
    ) * 100

    # Ordenar para mejor visualización en barras
    # df_usos = df_usos.sort_values("Porcentaje (%)", ascending=True)

    st.subheader("1 Pie chart - MatPlotly")
    # PIE CHART MATPLOTLIB
    plt.figure(figsize=(10, 8))
    plt.pie(df_usos["Consumo (Mtoe)"], labels=df_usos["Uso"], autopct='%1.f%%', startangle=90, textprops={'weight':'bold'}, pctdistance=0.9)
    with contenido:
        st.pyplot(plt)
    
    # PIE CHART PLOTLY
    st.subheader("2️ Pie chart - Plotly")

    fig_pie = px.pie(
        df_usos,
        names="Uso",
        values="Consumo (Mtoe)",
        hole=0.45
    )

    fig_pie.update_traces(
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>" +
                      "Consumo: %{value:.2f} Mtoe<br>" +
                      "Porcentaje: %{percent}"
    )

    fig_pie.update_layout(
        margin=dict(t=40, b=20, l=20, r=20)
    )
    with contenido:
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("3️ Barras horizontales relativas")

    fig_bar = px.bar(
        df_usos,
        x="Porcentaje (%)",
        y="Uso",
        orientation="h",
        text=df_usos["Porcentaje (%)"].round(1).astype(str) + "%"
    )

    fig_bar.update_layout(
        xaxis_title="Porcentaje del consumo total (%)",
        yaxis_title="",
        margin=dict(t=40, b=20, l=20, r=20)
    )

    fig_bar.update_traces(
        hovertemplate="<b>%{y}</b><br>" +
                      "Porcentaje: %{x:.2f}%"
    )
    with contenido:
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("4 Barras horizontales relativas - Plotly")

    fig_bar = px.bar(
        df_usos,
        x="Porcentaje (%)",
        y="Uso",
        orientation="h",
        text=df_usos["Porcentaje (%)"].round(1).astype(str) + "%",
        color="Uso",                     
        color_discrete_sequence=px.colors.qualitative.Set1  # COLORES
    )

    fig_bar.update_layout(
        xaxis_title="Porcentaje del consumo total (%)",
        yaxis_title="",
        showlegend=False, 
        margin=dict(t=40, b=20, l=20, r=20)
    )

    fig_bar.update_traces(
        hovertemplate="<b>%{y}</b><br>" +
                      "Porcentaje: %{x:.2f}%"
    )
    with contenido:
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("5 Pie chart - Altair")

    # Pie chart con Altair
    pie_altair = (
        alt.Chart(df_usos)
        .mark_arc(innerRadius=60)  # donut
        .encode(
            theta=alt.Theta(field="Consumo (Mtoe)", type="quantitative"),
            color=alt.Color(field="Uso", type="nominal"),
            tooltip=[
                alt.Tooltip("Uso:N"),
                alt.Tooltip("Consumo (Mtoe):Q", format=".2f"),
                alt.Tooltip("Porcentaje (%):Q", format=".2f")
            ]
        )
        .properties(
            width=500,
            height=400,
            title="Estructura porcentual del consumo energético"
        )
    )
    with contenido:
        st.altair_chart(pie_altair, use_container_width=True)

    st.subheader("6 Barras horizontales - Altair")

    bar_altair = (
        alt.Chart(df_usos)
        .mark_bar()
        .encode(
            x=alt.X(
                "Porcentaje (%):Q",
                title="Porcentaje del consumo total (%)"
            ),
            y=alt.Y(
                "Uso:N",
                sort="-x",
                title=None
            ),
            color=alt.Color(
                "Uso:N",
                legend=None
            ),
            tooltip=[
                alt.Tooltip("Uso:N"),
                alt.Tooltip("Porcentaje (%):Q", format=".2f"),
                alt.Tooltip("Consumo (Mtoe):Q", format=".2f")
            ]
        )
        .properties(
            width=600,
            height=400,
            title="Distribución relativa del consumo energético por usos"
        )
    )
    with contenido:
        st.altair_chart(bar_altair, use_container_width=True)


elif grafica_idx == "Análisis del Consumo por Clima y Usos Finales":
    # Definición de los usos energéticos y sus etiquetas
    usos = ['MFHTBTU', 'MFCLBTU', 'MFVNBTU', 'MFWTBTU', 'MFLTBTU', 'MFCKBTU', 'MFRFBTU', 'MFOFBTU', 'MFPCBTU', 'MFOTBTU']
    usos_labels = ['Calefacción', 'Aire Acondicionado', 'Ventilación', 'ACS', 'Iluminación', 'Cocina', 'Refrigeración', 'Equipos Oficina', 'Computación', 'Otros']

    # Colores para los usos energéticos
    colors = ['red', 'deepskyblue', 'violet', 'orange', 'yellow', 'purple', 'blue', 'green', 'lightgreen', 'gray']

    # Inicialización de los datos por clima
    climates = ['Muy Frío', 'Frío', 'Templado', 'Cálido', 'Muy Cálido']
    climate_consumptions = []

    # Selección de edificios comerciales por cada zona climática
    for pubclim in range(1, 6):
        Edi = microdatasi.query(f'PUBCLIM == {pubclim}')
        consumos = []
        total_consumo = (Edi[usos] * Edi['FINALWT'].values.reshape(-1, 1)).sum()  # Suma de todos los consumos para el clima actual

        # Normalización para obtener porcentajes
        for uso in usos:
            consumo = (Edi[uso] * Edi['FINALWT']).sum()
            consumos.append(consumo / total_consumo.sum() * 100)  # Normalización a porcentaje

        climate_consumptions.append(consumos)

    # Crear el gráfico de barras apiladas
    fig, ax = plt.subplots(figsize=(8, 12))  # Ajuste de la figura: más alta (12) y más estrecha (8)

    # Crear las barras apiladas por cada clima
    for i, consumo_por_clima in enumerate(zip(*climate_consumptions)):
            ax.bar(climates, consumo_por_clima, bottom=[sum(consumo[:i]) for consumo in climate_consumptions], color=colors[i], label=usos_labels[i])

    # Agregar líneas horizontales para mejorar la visualización de los porcentajes
    ax.set_yticks(range(0, 110, 10))
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5, color='black', alpha=0.7)

    # Etiquetas y leyenda
    ax.set_ylabel('Porcentaje de Consumo (%)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=5)
    with contenido:
        # Mostrar el gráfico
        st.pyplot(plt)

elif grafica_idx == "Análisis del Consumo por año y Usos Finales":
    # Definición de los usos energéticos y sus etiquetas
    usos = ['MFHTBTU', 'MFCLBTU', 'MFVNBTU', 'MFWTBTU', 'MFLTBTU', 'MFCKBTU', 'MFRFBTU', 'MFOFBTU', 'MFPCBTU', 'MFOTBTU']
    usos_labels = ['Calefacción', 'Aire Acondicionado', 'Ventilación', 'ACS', 'Iluminación', 'Cocina', 'Refrigeración', 'Equipos Oficina', 'Computación', 'Otros']

    # Colores para los usos energéticos
    colors = ['red', 'deepskyblue', 'violet', 'orange', 'yellow', 'purple', 'blue', 'green', 'lightgreen', 'gray']

    # Inicialización de los datos por clima
    climates = ['Antes 1960', '1960-1980', '1980-2000', '2000-2018']
    climate_consumptions = []

    # Selección de edificios comerciales por cada zona climática
    for YRCONCN in range(1, 5):
        Edi = microdatasi.query(f'YRCONCN == {YRCONCN}') 
        consumos = []
        total_consumo = (Edi[usos] * Edi['FINALWT'].values.reshape(-1, 1)).sum()  # Suma de todos los consumos para el año actual

        # Normalización para obtener porcentajes
        for uso in usos:
            consumo = (Edi[uso] * Edi['FINALWT']).sum()
            consumos.append(consumo / total_consumo.sum() * 100)  # Normalización a porcentaje

        climate_consumptions.append(consumos)

    # Crear el gráfico de barras apiladas
    fig, ax = plt.subplots(figsize=(8, 12))

    # Crear las barras apiladas por cada clima
    for i, consumo_por_clima in enumerate(zip(*climate_consumptions)):
        ax.bar(climates, consumo_por_clima, bottom=[sum(consumo[:i]) for consumo in climate_consumptions], color=colors[i], label=usos_labels[i])

    # Agregar líneas horizontales para mejorar la visualización de los porcentajes
    ax.set_yticks(range(0, 110, 10))
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5, color='black', alpha=0.7)

    # Etiquetas y leyenda
    ax.set_ylabel('Porcentaje de Consumo (%)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4)
    with contenido:
        # Mostrar el gráfico
        st.pyplot(plt)

elif grafica_idx == "Análisis del Consumo por tamaño y Usos Finales":
    # Definición de los usos energéticos y sus etiquetas
    usos = ['MFHTBTU', 'MFCLBTU', 'MFVNBTU', 'MFWTBTU', 'MFLTBTU', 'MFCKBTU', 'MFRFBTU', 'MFOFBTU', 'MFPCBTU', 'MFOTBTU']
    usos_labels = ['Calefacción', 'Aire Acondicionado', 'Ventilación', 'ACS', 'Iluminación', 'Cocina', 'Refrigeración', 'Equipos Oficina', 'Computación', 'Otros']

    # Colores para los usos energéticos
    colors = ['red', 'deepskyblue', 'violet', 'orange', 'yellow', 'purple', 'blue', 'green', 'lightgreen', 'gray']

    # Inicialización de los datos por clima
    climates = ['S', 'M', 'L']
    climate_consumptions = []

    # Selección de edificios comerciales por cada zona climática
    for SQFTCM in range(1, 4):
        Edi = microdatasi.query(f'SQFTCM == {SQFTCM}')
        consumos = []
        total_consumo = (Edi[usos] * Edi['FINALWT'].values.reshape(-1, 1)).sum()  # Suma de todos los consumos para el tamaño actual

        # Normalización para obtener porcentajes
        for uso in usos:
            consumo = (Edi[uso] * Edi['FINALWT']).sum()
            consumos.append(consumo / total_consumo.sum() * 100)  # Normalización a porcentaje

        climate_consumptions.append(consumos)

    # Crear el gráfico de barras apiladas
    fig, ax = plt.subplots(figsize=(8, 12))  # Ajuste de la figura: más alta (12) y más estrecha (8)

    # Crear las barras apiladas por cada clima
    for i, consumo_por_clima in enumerate(zip(*climate_consumptions)):
        ax.bar(climates, consumo_por_clima, bottom=[sum(consumo[:i]) for consumo in climate_consumptions], color=colors[i], label=usos_labels[i])

    # Agregar líneas horizontales para mejorar la visualización de los porcentajes
    ax.set_yticks(range(0, 110, 10))
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5, color='black', alpha=0.7)

    # Etiquetas y leyenda
    ax.set_ylabel('Porcentaje de Consumo (%)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=5)
    with contenido:
        st.pyplot(fig)

elif grafica_idx == "Estructura del consumo por fuentes":
    fuentes = ['ELBTU', 'NGBTU', 'FKBTU', 'DHBTU']
    fuentes_labels = ['Electricidad', 'Gas Natural', 'Fuel oil', 'Vapor de distrito']

    # Colores personalizados (puedes usar los que desees)
    colores = ['purple', 'yellow', 'brown', 'deepskyblue']

    # Selección de edificios comerciales 
    Edi = microdatasi.copy()

    # Cálculo de los consumos totales por uso
    total_consumos = []

    for fuente in fuentes:
        consumo = (Edi[fuente] * Edi['FINALWT']).sum()
        total_consumos.append(consumo)

    # Crear gráfico circular
    plt.figure(figsize=(8, 8))
    # plt.pie(total_consumos, labels=fuentes_labels, autopct='%1.1f%%', startangle=90, pctdistance=0.9, colors=colores, labeldistance=1.1)

    # st.pyplot(plt)
    explode = [0, 0, 0.2, 0.2]  # Separa Gasoil y Vapor de distrito
    wedges, texts, autotexts = plt.pie(
        total_consumos,
        autopct='%1.1f%%',
        startangle=90,
        colors=colores,
        pctdistance=1.1,
        textprops={'weight':'bold'},
        explode=explode
    )
    plt.legend(wedges, fuentes_labels, title="Fuente", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.tight_layout()

    with contenido:
        st.pyplot(plt)

elif grafica_idx == "Distribución del consumo por Usos Finales y Tipo de Energía":
    # Selección de edificios comerciales 
    Edi = microdatasi.copy()

    # Definir los tipos de energía y sus columnas correspondientes
    tipos_energia = {
        'Electricidad': {
            'Calefacción': 'ELHTBTU', 'Aire Acondicionado': 'ELCLBTU', 'ACS': 'ELWTBTU',
            'Cocina': 'ELCKBTU', 'Otros Usos': 'ELOTBTU', 'Ventilación': 'ELVNBTU',
            'Iluminación': 'ELLTBTU', 'Refrigeración': 'ELRFBTU', 'Equipos Oficina': 'ELOFBTU', 'Computación': 'ELPCBTU'
        },
        'Gas Natural': {
            'Calefacción': 'NGHTBTU', 'Aire Acondicionado': 'NGCLBTU', 'ACS': 'NGWTBTU',
            'Cocina': 'NGCKBTU', 'Otros Usos': 'NGOTBTU'
        },
        'Fuel oil': {
            'Calefacción': 'FKHTBTU', 'Aire Acondicionado': 'FKCLBTU', 'ACS': 'FKWTBTU',
            'Cocina': 'FKCKBTU', 'Otros Usos': 'FKOTBTU'
        },
        'Vapor de Distrito': {
            'Calefacción': 'DHHTBTU', 'Aire Acondicionado': 'DHCLBTU', 'ACS': 'DHWTBTU',
            'Cocina': 'DHCKBTU', 'Otros Usos': 'DHOTBTU'
        }
    }

    # Inicializar diccionario para almacenar los totales de energía por tipo y uso final
    totales_energia = {energia: {uso: 0 for uso in tipos_energia['Electricidad']} for energia in tipos_energia}

    # Calcular los totales de energía por tipo y uso final
    for energia, usos in tipos_energia.items():
        for uso, columna in usos.items():
            totales_energia[energia][uso] = (Edi[columna] * Edi['FINALWT']).sum()

    # Crear lista de usos finales y tipos de energía
    usos_finales = list(totales_energia['Electricidad'].keys())
    tipos_energia_lista = list(totales_energia.keys())

    # Crear una lista de totales por tipo de energía para cada uso final
    data_por_uso = {uso: [totales_energia[energia][uso] for energia in tipos_energia_lista] for uso in usos_finales}

    # Calcular totales por uso final para normalización
    totales_por_uso = [sum(data_por_uso[uso]) for uso in usos_finales]

    # Calcular porcentajes para cada tipo de energía
    porcentajes_por_uso = {uso: [(valor / total) * 100 if total != 0 else 0 for valor in data_por_uso[uso]]
                           for uso, total in zip(usos_finales, totales_por_uso)}
    
    # Crear el gráfico apilado con mejor resolución
    fig, ax = plt.subplots(figsize=(12, 7), dpi=120)

    # Colores (puedes cambiarlos si quieres)
    colores = ['purple', 'gold', 'brown', 'deepskyblue']

    # Crear las barras apiladas
    bottom = [0] * len(usos_finales)

    for i, energia in enumerate(tipos_energia_lista):
        valores = [porcentajes_por_uso[uso][i] for uso in usos_finales]
        ax.bar(
            usos_finales,
            valores,
            bottom=bottom,
            label=energia,
            color=colores[i]
        )
        bottom = [x + y for x, y in zip(bottom, valores)]

    # Etiquetas y título (más grandes)
    ax.set_xlabel('Usos Finales', fontsize=14)
    ax.set_ylabel('Porcentaje de Consumo (%)', fontsize=14)
    ax.set_title(
        f'Distribución del Consumo de Energía por Usos Finales y Tipo de Energía\n',
        fontsize=16
    )

    # Ajustar tamaño de ticks
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    plt.xticks(rotation=45, ha='right')

    # Leyenda a la derecha pero dentro del área visible
    ax.legend(
        loc='center left',
        bbox_to_anchor=(1.02, 0.5),
        title="Tipo de Energía",
        fontsize=12,
        title_fontsize=13
    )

    # Ajuste para que no se corte nada
    plt.tight_layout(rect=[0, 0, 0.82, 1])
    with contenido:
        # Mostrar en Streamlit
        st.pyplot(fig, use_container_width=True)

elif grafica_idx == "Consumo de Energía por Clima y Tipo de Energía":
    consumos = {
        'Clima': ['Muy frío', 'Frío', 'Templado', 'Cálido', 'Muy cálido'],
        'Eléctrico': [],
        'Gas natural': [],
        'Fuel Oil': [],
        'Vapor de distrito': []
    }

    climas = [1, 2, 3, 4, 5]
    energias = ['ELBTU', 'NGBTU', 'FKBTU', 'DHBTU']
    nombres_energias = ['Eléctrico', 'Gas natural', 'Fuel Oil', 'Vapor de distrito']

    colores = ['purple', 'gold', 'brown', 'deepskyblue']

    for clima in climas:
        EdiClima = microdatasi.query(f'PUBCLIM=={clima}')

        for idx, energia in enumerate(energias):
            consumo = (EdiClima[energia] * EdiClima['FINALWT']).sum()
            consumos[nombres_energias[idx]].append(consumo)

    # Convertir a DataFrame
    df_consumos = pd.DataFrame(consumos)

    # Calcular porcentajes
    df_consumos_pct = (
        df_consumos
        .set_index('Clima')
        .apply(lambda x: x / x.sum(), axis=1) * 100
    )

    fig, ax = plt.subplots(figsize=(12, 7), dpi=120)

    df_consumos_pct.plot(
        kind='bar',
        stacked=True,
        ax=ax,
        color=colores
    )

    # Títulos y etiquetas
    ax.set_title(
        f'Consumo de Energía por Clima (%)\n',
        fontsize=16
    )

    ax.set_ylabel('Porcentaje (%)', fontsize=14)
    ax.set_xlabel('Clima', fontsize=14)

    # Tamaño de ticks
    ax.tick_params(axis='x', labelsize=12, rotation=0)
    ax.tick_params(axis='y', labelsize=12)

    # Leyenda fuera pero sin cortar
    ax.legend(
        title='Tipo de Energía',
        bbox_to_anchor=(1.02, 1),
        loc='upper left',
        fontsize=12,
        title_fontsize=13
    )

    plt.tight_layout(rect=[0, 0, 0.82, 1])
    with contenido:
        # Mostrar en Streamlit
        st.pyplot(fig, use_container_width=True)

elif grafica_idx == "Consumo de Energía por Tamaño y Tipo de Energía":
    consumos = {
        'Tamaño': ['S', 'M', 'L'],
        'Eléctrico': [],
        'Gas natural': [],
        'Fuel Oil': [],
        'Vapor de distrito': []
    }

    tamanos = [1, 2, 3]
    energias = ['ELBTU', 'NGBTU', 'FKBTU', 'DHBTU']
    nombres_energias = ['Eléctrico', 'Gas natural', 'Fuel Oil', 'Vapor de distrito']

    colores = ['purple', 'gold', 'brown', 'deepskyblue']

    for tamano in tamanos:
        EdiTamano = microdatasi.query(f'SQFTCM=={tamano}')

        for idx, energia in enumerate(energias):
            consumo = (EdiTamano[energia] * EdiTamano['FINALWT']).sum()
            consumos[nombres_energias[idx]].append(consumo)

    df_consumos = pd.DataFrame(consumos)

    df_consumos_pct = (
        df_consumos
        .set_index('Tamaño')
        .apply(lambda x: x / x.sum(), axis=1) * 100
    )

    fig, ax = plt.subplots(figsize=(12, 7), dpi=120)

    df_consumos_pct.plot(
        kind='bar',
        stacked=True,
        ax=ax,
        color=colores
    )

    # Título y etiquetas
    ax.set_title(
        f'Consumo de Energía por Tamaño de Edificio (%)\n',
        fontsize=16
    )

    ax.set_ylabel('Porcentaje (%)', fontsize=14)
    ax.set_xlabel('Tamaño de Edificio', fontsize=14)

    # Ticks más grandes
    ax.tick_params(axis='x', labelsize=12, rotation=0)
    ax.tick_params(axis='y', labelsize=12)

    # Leyenda alineada a la derecha sin recorte
    ax.legend(
        title='Tipo de Energía',
        bbox_to_anchor=(1.02, 1),
        loc='upper left',
        fontsize=12,
        title_fontsize=13
    )

    # Ajuste para reservar espacio a la leyenda
    plt.tight_layout(rect=[0, 0, 0.82, 1])
    with contenido:
        # Mostrar en Streamlit
        st.pyplot(fig, use_container_width=True)

elif grafica_idx == "Consumo de Energía por Edad y Tipo de Energía":
    consumos = {
        'Edad': ['Antes 1960', '1960-1980', '1980-2000', '2000-2018'],
        'Eléctrico': [],
        'Gas natural': [],
        'Fuel Oil': [],
        'Vapor de distrito': []
    }

    edades = [1, 2, 3, 4]
    energias = ['ELBTU', 'NGBTU', 'FKBTU', 'DHBTU']
    nombres_energias = ['Eléctrico', 'Gas natural', 'Fuel Oil', 'Vapor de distrito']

    colores = ['purple', 'gold', 'brown', 'deepskyblue']

    for edad in edades:
        EdiEdad = microdatasi.query(f'YRCONCN=={edad}')

        for idx, energia in enumerate(energias):
            consumo = (EdiEdad[energia] * EdiEdad['FINALWT']).sum()
            consumos[nombres_energias[idx]].append(consumo)

    df_consumos = pd.DataFrame(consumos)

    df_consumos_pct = (
        df_consumos
        .set_index('Edad')
        .apply(lambda x: x / x.sum(), axis=1) * 100
    )

    fig, ax = plt.subplots(figsize=(12, 7), dpi=120)

    df_consumos_pct.plot(
        kind='bar',
        stacked=True,
        ax=ax,
        color=colores
    )

    # Título y etiquetas
    ax.set_title(
        f'Consumo de Energía por Edad de Edificio (%)\n',
        fontsize=16
    )

    ax.set_ylabel('Porcentaje (%)', fontsize=14)
    ax.set_xlabel('Edad del Edificio', fontsize=14)

    # Mejorar legibilidad de ejes
    ax.tick_params(axis='x', labelsize=12, rotation=0)
    ax.tick_params(axis='y', labelsize=12)

    # Leyenda alineada fuera sin cortar
    ax.legend(
        title='Tipo de Energía',
        bbox_to_anchor=(1.02, 1),
        loc='upper left',
        fontsize=12,
        title_fontsize=13
    )

    # Reservar espacio para la leyenda
    plt.tight_layout(rect=[0, 0, 0.82, 1])
    with contenido:
        # Mostrar en Streamlit
        st.pyplot(fig, use_container_width=True)

st.markdown("---")
st.caption("Desarrollado por JYK - Fuente: U.S. Energy Information Administration (eia)")