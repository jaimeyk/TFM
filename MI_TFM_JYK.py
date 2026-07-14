import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt

st.set_page_config(layout="wide")

# =========================================================
# CONSTANTES Y CONFIGURACIÓN
# =========================================================
DATA_FILE = 'cbecs2018_final_public.csv'

BTU_COLUMNS = [
    'MFBTU', 'ELBTU', 'NGBTU', 'FKBTU', 'DHBTU',
    'MFHTBTU', 'MFCLBTU', 'MFVNBTU', 'MFWTBTU', 'MFLTBTU', 'MFCKBTU', 'MFRFBTU', 'MFOFBTU', 'MFPCBTU', 'MFOTBTU',
    'ELHTBTU', 'ELCLBTU', 'ELVNBTU', 'ELWTBTU', 'ELLTBTU', 'ELCKBTU', 'ELRFBTU', 'ELOFBTU', 'ELPCBTU', 'ELOTBTU',
    'NGHTBTU', 'NGCLBTU', 'NGWTBTU', 'NGCKBTU', 'NGOTBTU',
    'FKHTBTU', 'FKCLBTU', 'FKWTBTU', 'FKCKBTU', 'FKOTBTU',
    'DHHTBTU', 'DHCLBTU', 'DHWTBTU', 'DHCKBTU', 'DHOTBTU'
]

BTU_TO_KWH = 1.055060 / 3600
KWH_TO_MTOE = 8.6e-8
BTU_TO_MTOE = BTU_TO_KWH * KWH_TO_MTOE
SQFT_TO_M2 = 0.092903

TIPOS_EDIFICIO = [
    "Vacíos", "Oficina", "Almacenes", "Alimentación", "Edificio público",
    "Sanitario", "Educación", "Alojamiento", "Comercio", "Servicios", "Otros"
]

TIPO_EDIFICIO_PBAN = {
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
    "Otros": 11,
}

CAMBIOS_PBAPLUS = {
    3: 2, 4: 2, 5: 2, 6: 2, 7: 2,
    43: 42, 51: 50,
    23: 22, 24: 22, 25: 22, 26: 22,
    17: 16, 52: 16,
    14: 12, 15: 12,
    33: 32, 34: 32,
    46: 44, 47: 44, 48: 44,
    19: 18,
}

SUBTIPOS_POR_TIPO = {
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
    "Otros": ['Laboratorio'],
}

SUBTIPO_EDIFICIO_PBAPLUS = {
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
    'Otros': [49],
}

SIZE_CONFIG = {
    "Alojamiento": {
        "labels": ['S', 'M', 'L'],
        "limits": [(-np.inf, 10000, 1), (10000, 20000, 2), (20000, np.inf, 3)],
    },
    "Oficina": {
        "labels": ['XS', 'S', 'M', 'L', 'XL'],
        "limits": [(-np.inf, 500, 1), (500, 5000, 2), (5000, 15000, 3), (15000, 30000, 4), (30000, np.inf, 5)],
    },
    "Almacenes": {
        "labels": ['S', 'M', 'L'],
        "limits": [(-np.inf, 2500, 1), (2500, 15000, 2), (15000, np.inf, 3)],
    },
    "Educación": {
        "labels": ['XS', 'S', 'M', 'L'],
        "limits": [(-np.inf, 5000, 1), (5000, 10000, 2), (10000, 20000, 3), (20000, np.inf, 4)],
    },
    "Alimentación": {
        "labels": ['S', 'M', 'L'],
        "limits": [(-np.inf, 250, 1), (250, 500, 2), (500, np.inf, 3)],
    },
    "Edificio público": {
        "labels": ['S', 'M', 'L'],
        "limits": [(-np.inf, 1000, 1), (1000, 5000, 2), (5000, np.inf, 3)],
    },
    "Sanitario": {
        "labels": ['S', 'M', 'L'],
        "limits": [(-np.inf, 10000, 1), (10000, 30000, 2), (30000, np.inf, 3)],
    },
    "Servicios": {
        "labels": ['S', 'M', 'L'],
        "limits": [(-np.inf, 500, 1), (500, 2000, 2), (2000, np.inf, 3)],
    },
    "Comercio": {
        "labels": ['XS', 'S', 'M', 'L'],
        "limits": [(-np.inf, 2000, 1), (2000, 5000, 2), (5000, 15000, 3), (15000, np.inf, 4)],
    },
    "Vacíos": {
        "labels": ['XS', 'S', 'M', 'L'],
        "limits": [(-np.inf, 500, 1), (500, 5000, 2), (5000, 10000, 3), (10000, np.inf, 4)],
    },
    "Otros": {
        "labels": ['XS', 'S', 'M', 'L', 'XL'],
        "limits": [(-np.inf, 1000, 1), (1000, 2500, 2), (2500, 5000, 3), (5000, 20000, 4), (20000, np.inf, 5)],
    },
}

CLASIF_TIPO_GRAFICA = {
    "Stock": [
        "Distribución de Superficies por Categoría Climática",
        "Estructura del área por tamaños",
        "Distribución de superficie por edad",
    ],
    "Consumo": [
        "Distribución del consumo por tamaño",
        "Estructura del consumo por usos",
        "Estructura del consumo por fuentes",
        "Distribución del consumo por Usos Finales y Tipo de Energía",
    ],
    "Consumo por Usos Finales": [
        "Análisis del Consumo por Clima y Usos Finales",
        "Análisis del Consumo por tamaño y Usos Finales",
        "Análisis del Consumo por Edad y Usos Finales",
    ],
    "Consumo por Tipo de Energía": [
        "Consumo de Energía por Clima y Tipo de Energía",
        "Consumo de Energía por Tamaño y Tipo de Energía",
        "Consumo de Energía por Edad y Tipo de Energía",
    ],
}

TIPOS_GRAFICA = list(CLASIF_TIPO_GRAFICA.keys())
BOTONES = ["Indicadores Clave"] + TIPOS_GRAFICA
CLIMA_EDIFICIO = ['Frío o muy frío', 'Frío', 'Templado', 'Cálido', 'Muy cálido']
CLIMA_EDIFICIO_PUBCLIM1 = [1, 2, 3, 4, 5]
EDAD_EDIFICIO = ['Antes de 1960', '1960-1979', '1980-1999', '2000-2018']
EDAD_EDIFICIO_YRCONC1 = [1, 2, 3, 4]
USOS_LABELS = ['Calefacción', 'Aire Acondicionado', 'Ventilación', 'ACS', 'Iluminación', 'Cocina', 'Refrigeración', 'Equipos Oficina', 'Computación', 'Otros']
COLORES_USOS = ['red', 'deepskyblue', 'lightblue', 'orange', 'yellow', '#A65E2E', '#00A6A6', 'green', 'lightgreen', 'gray']
FUENTES_LABELS = ['Electricidad', 'Gas Natural', 'Fuel Oil', 'Vapor de distrito']
COLORES_FUENTES = ['skyblue', 'yellow', '#005F6B', 'lightgreen']

# =========================================================
# FUNCIONES DE PREPARACIÓN Y FILTROS
# =========================================================
def load_and_prepare_data(path: str) -> pd.DataFrame:
    """Carga el CSV y aplica las mismas transformaciones iniciales del código original."""
    df = pd.read_csv(path).copy()

    df[BTU_COLUMNS] *= BTU_TO_MTOE
    df['SQFT'] *= SQFT_TO_M2

    df.loc[(df['YRCONC'] == 2) | (df['YRCONC'] == 3), 'YRCONCN'] = 1
    df.loc[(df['YRCONC'] == 4) | (df['YRCONC'] == 5), 'YRCONCN'] = 2
    df.loc[(df['YRCONC'] == 6) | (df['YRCONC'] == 7), 'YRCONCN'] = 3
    df.loc[df['YRCONC'] > 7, 'YRCONCN'] = 4
    df['YRCONCN'] = df['YRCONCN'].astype(int)

    df['PBAPLUS'] = df['PBAPLUS'].replace(CAMBIOS_PBAPLUS)

    df.loc[df['PBAPLUS'] == 1, 'PBAN'] = 1
    df.loc[df['PBAPLUS'] == 2, 'PBAN'] = 2
    df.loc[df['PBAPLUS'].isin([9, 10, 11, 20]), 'PBAN'] = 3
    df.loc[df['PBAPLUS'].isin([12, 32]), 'PBAN'] = 4
    df.loc[df['PBAPLUS'] == 44, 'PBAN'] = 5
    df.loc[df['PBAPLUS'].isin([18, 35]), 'PBAN'] = 6
    df.loc[df['PBAPLUS'].isin([22, 21, 16]), 'PBAN'] = 7
    df.loc[df['PBAPLUS'].isin([27, 28, 29, 30, 54]), 'PBAN'] = 8
    df.loc[df['PBAPLUS'].isin([36, 37, 38, 39, 40]), 'PBAN'] = 9
    df.loc[df['PBAPLUS'].isin([42, 50]), 'PBAN'] = 10
    df.loc[df['PBAPLUS'].isin([8, 49]), 'PBAN'] = 11

    df['PBAN'] = pd.to_numeric(df['PBAN'], errors='coerce')
    df = df.dropna(subset=['PBAN'])
    df['PBAN'] = df['PBAN'].astype(int)

    df['CLIMAF'] = df['MFHTBTU'] + df['MFCLBTU'] + df['MFVNBTU']
    df['CLIMAE'] = df['ELHTBTU'] + df['ELCLBTU'] + df['ELVNBTU']

    return df


def classify_size(df: pd.DataFrame, tipo: str) -> pd.DataFrame:
    """Crea SQFTCM según el tipo de edificio, con los mismos cortes del código original."""
    df = df.copy()
    df['SQFTCM'] = np.nan

    if tipo == "Alojamiento":
        df.loc[df['SQFT'] < 10000, 'SQFTCM'] = 1
        df.loc[(df['SQFT'] >= 10000) & (df['SQFT'] < 20000), 'SQFTCM'] = 2
        df.loc[df['SQFT'] >= 20000, 'SQFTCM'] = 3

    elif tipo == "Oficina":
        df.loc[df['SQFT'] <= 500, 'SQFTCM'] = 1
        df.loc[(df['SQFT'] > 500) & (df['SQFT'] <= 5000), 'SQFTCM'] = 2
        df.loc[(df['SQFT'] > 5000) & (df['SQFT'] <= 15000), 'SQFTCM'] = 3
        df.loc[(df['SQFT'] > 15000) & (df['SQFT'] < 30000), 'SQFTCM'] = 4
        df.loc[df['SQFT'] >= 30000, 'SQFTCM'] = 5

    elif tipo == "Almacenes":
        df.loc[df['SQFT'] <= 2500, 'SQFTCM'] = 1
        df.loc[(df['SQFT'] > 2500) & (df['SQFT'] < 15000), 'SQFTCM'] = 2
        df.loc[df['SQFT'] >= 15000, 'SQFTCM'] = 3

    elif tipo == "Educación":
        df.loc[df['SQFT'] <= 5000, 'SQFTCM'] = 1
        df.loc[(df['SQFT'] > 5000) & (df['SQFT'] <= 10000), 'SQFTCM'] = 2
        df.loc[(df['SQFT'] > 10000) & (df['SQFT'] < 20000), 'SQFTCM'] = 3
        df.loc[df['SQFT'] >= 20000, 'SQFTCM'] = 4

    elif tipo == "Alimentación":
        df.loc[df['SQFT'] <= 250, 'SQFTCM'] = 1
        df.loc[(df['SQFT'] > 250) & (df['SQFT'] < 500), 'SQFTCM'] = 2
        df.loc[df['SQFT'] >= 500, 'SQFTCM'] = 3

    elif tipo == "Edificio público":
        df.loc[df['SQFT'] <= 1000, 'SQFTCM'] = 1
        df.loc[(df['SQFT'] > 1000) & (df['SQFT'] < 5000), 'SQFTCM'] = 2
        df.loc[df['SQFT'] >= 5000, 'SQFTCM'] = 3

    elif tipo == "Sanitario":
        df.loc[df['SQFT'] <= 10000, 'SQFTCM'] = 1
        df.loc[(df['SQFT'] > 10000) & (df['SQFT'] < 30000), 'SQFTCM'] = 2
        df.loc[df['SQFT'] >= 30000, 'SQFTCM'] = 3

    elif tipo == "Servicios":
        df.loc[df['SQFT'] <= 500, 'SQFTCM'] = 1
        df.loc[(df['SQFT'] > 500) & (df['SQFT'] < 2000), 'SQFTCM'] = 2
        df.loc[df['SQFT'] >= 2000, 'SQFTCM'] = 3

    elif tipo == "Comercio":
        df.loc[df['SQFT'] <= 2000, 'SQFTCM'] = 1
        df.loc[(df['SQFT'] > 2000) & (df['SQFT'] <= 5000), 'SQFTCM'] = 2
        df.loc[(df['SQFT'] > 5000) & (df['SQFT'] < 15000), 'SQFTCM'] = 3
        df.loc[df['SQFT'] >= 15000, 'SQFTCM'] = 4

    elif tipo == "Vacíos":
        df.loc[df['SQFT'] <= 500, 'SQFTCM'] = 1
        df.loc[(df['SQFT'] > 500) & (df['SQFT'] <= 5000), 'SQFTCM'] = 2
        df.loc[(df['SQFT'] > 5000) & (df['SQFT'] < 10000), 'SQFTCM'] = 3
        df.loc[df['SQFT'] >= 10000, 'SQFTCM'] = 4

    elif tipo == "Otros":
        df.loc[df['SQFT'] <= 1000, 'SQFTCM'] = 1
        df.loc[(df['SQFT'] > 1000) & (df['SQFT'] <= 2500), 'SQFTCM'] = 2
        df.loc[(df['SQFT'] > 2500) & (df['SQFT'] <= 5000), 'SQFTCM'] = 3
        df.loc[(df['SQFT'] > 5000) & (df['SQFT'] < 20000), 'SQFTCM'] = 4
        df.loc[df['SQFT'] >= 20000, 'SQFTCM'] = 5

    df['SQFTCM'] = df['SQFTCM'].fillna(0).astype(int)
    return df

def filter_by_subtype(df: pd.DataFrame, subtipo: str | None) -> pd.DataFrame:
    if subtipo is None:
        return df

    pbaplus_values = SUBTIPO_EDIFICIO_PBAPLUS.get(subtipo.strip(), [])
    if not pbaplus_values:
        return df

    return df[df['PBAPLUS'].isin(pbaplus_values)]


def recode_age_filter_column(df: pd.DataFrame) -> pd.DataFrame:
    """Reproduce la recodificación de YRCONC usada para el filtro de edad."""
    df = df.copy()
    df.loc[(df['YRCONC'] == 2) | (df['YRCONC'] == 3), 'YRCONC'] = 1
    df.loc[(df['YRCONC'] == 4) | (df['YRCONC'] == 5), 'YRCONC'] = 2
    df.loc[(df['YRCONC'] == 6) | (df['YRCONC'] == 7), 'YRCONC'] = 3
    df.loc[df['YRCONC'] > 7, 'YRCONC'] = 4
    df['YRCONC'] = df['YRCONC'].fillna(0).astype(int)
    return df


def remove_graph_option(graficas: list[str], opcion: str) -> list[str]:
    return [grafica for grafica in graficas if grafica != opcion]


def stop_if_empty(df: pd.DataFrame) -> None:
    """Detiene la app si no quedan edificios tras aplicar los filtros."""
    if df.empty:
        st.warning("No existe ningún edificio que cumpla con esas características.")
        st.stop()


def add_percentage_column(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Añade una columna de porcentaje sobre el total de value_col."""
    df = df.copy()
    total = df[value_col].sum()
    if total > 0:
        df["Porcentaje (%)"] = df[value_col] / total * 100
    else:
        df["Porcentaje (%)"] = 0
    return df


def render_horizontal_percentage_bar(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
    xaxis_title: str,
    hover_category_name: str,
) -> None:
    """Representa una gráfica de barras horizontales en Plotly con el estilo común elegido."""
    df_plot = add_percentage_column(df, value_col)
    df_plot = df_plot[df_plot[value_col] > 0]

    if df_plot.empty:
        st.warning("No hay datos suficientes para generar esta gráfica.")
        st.stop()

    fig_bar = px.bar(
        df_plot,
        x="Porcentaje (%)",
        y=category_col,
        orientation="h",
        text=df_plot["Porcentaje (%)"].round(1).astype(str) + "%",
        color=category_col,
        color_discrete_sequence=px.colors.qualitative.Set1,
    )

    fig_bar.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title="",
        showlegend=False,
        margin=dict(t=40, b=20, l=20, r=20),
    )

    fig_bar.update_traces(
        hovertemplate=(
            f"<b>{hover_category_name}: %{{y}}</b><br>"
            "Porcentaje: %{x:.2f}%<extra></extra>"
        )
    )

    with contenido:
        st.plotly_chart(fig_bar, use_container_width=True)


def render_results_table(df: pd.DataFrame, format_dict: dict | None = None) -> None:
    """Muestra una tabla de resultados debajo de cada gráfica."""
    with contenido:
        st.subheader("Tabla Resultados")
        if format_dict:
            st.dataframe(
                df.style.format(format_dict),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )


# =========================================================
# CARGA DE DATOS E INTERFAZ DE FILTROS

microdatasi = load_and_prepare_data(DATA_FILE)

st.title("Datos Energéticos de Edificios")

if "grafica_tipo_superior" not in st.session_state:
    st.session_state.grafica_tipo_superior = "Indicadores Clave"

cols_botones = st.columns(5)

for i, tipo_grafica in enumerate(BOTONES):
    with cols_botones[i]:
        if st.button(tipo_grafica, use_container_width=True):
            st.session_state.grafica_tipo_superior = tipo_grafica

grafica_tipo = st.session_state.grafica_tipo_superior

if grafica_tipo != "Indicadores Clave":
    graficas = CLASIF_TIPO_GRAFICA[grafica_tipo].copy()
else:
    graficas = []

st.markdown("---")

col1, col2, col5, col3, col6 = st.columns([1.3, 1.3, 1.3, 1.3, 1.3])

with col1:
    tipo = st.selectbox(
        "Tipo de edificio:",
        TIPOS_EDIFICIO,
        key="tipo_edificio",
        format_func=lambda x: f"{x}",
    )

st.markdown("---")

# Filtro por tipo
microdatasi = microdatasi[microdatasi['PBAN'] == TIPO_EDIFICIO_PBAN[tipo]]
stop_if_empty(microdatasi)

# Filtro por subtipo
with col2:
    subtipo = st.selectbox(
        "Subtipo de edificio:",
        SUBTIPOS_POR_TIPO[tipo],
        index=None,
        placeholder="Todos",
    )

microdatasi = filter_by_subtype(microdatasi, subtipo)

stop_if_empty(microdatasi)

# Filtro por tamaño
microdatasi = classify_size(microdatasi, tipo)
tamaño_edificio = SIZE_CONFIG[tipo]['labels']
tamaño_edificio_SQFTC1 = list(range(1, len(tamaño_edificio) + 1))

with col3:
    tamaño = st.selectbox(
        "Tamaño del edificio:",
        tamaño_edificio,
        index=None,
        placeholder="Todos",
    )

if tamaño is not None:
    SQFTC1 = tamaño_edificio_SQFTC1[tamaño_edificio.index(tamaño)]
    microdatasi = microdatasi[microdatasi['SQFTCM'] == SQFTC1]
    stop_if_empty(microdatasi)

    if tamaño is not None and grafica_tipo == "Stock":
        graficas = remove_graph_option(graficas, "Estructura del área por tamaños")
    elif tamaño is not None and grafica_tipo == "Consumo":
        graficas = remove_graph_option(graficas, "Distribución del consumo por tamaño")
    elif tamaño is not None and grafica_tipo == "Consumo por Usos Finales":
        graficas = remove_graph_option(graficas, "Análisis del Consumo por tamaño y Usos Finales")
    elif tamaño is not None and grafica_tipo == "Consumo por Tipo de Energía":
        graficas = remove_graph_option(graficas, "Consumo de Energía por Tamaño y Tipo de Energía")

# Filtro por clima
with col5:
    clima = st.selectbox(
        "Clima del edificio:",
        CLIMA_EDIFICIO,
        index=None,
        placeholder="Todos",
    )

if clima is not None:
    PUBCLIM1 = CLIMA_EDIFICIO_PUBCLIM1[CLIMA_EDIFICIO.index(clima)]
    microdatasi = microdatasi[microdatasi['PUBCLIM'] == PUBCLIM1]
    stop_if_empty(microdatasi)

    if grafica_tipo == "Stock":
        graficas = remove_graph_option(graficas, "Distribución de Superficies por Categoría Climática")
    elif grafica_tipo == "Consumo por Usos Finales":
        graficas = remove_graph_option(graficas, "Análisis del Consumo por Clima y Usos Finales")
    elif grafica_tipo == "Consumo por Tipo de Energía":
        graficas = remove_graph_option(graficas, "Consumo de Energía por Clima y Tipo de Energía")

# Filtro por edad
microdatasi = recode_age_filter_column(microdatasi)

with col6:
    edad = st.selectbox(
        "Edad del edificio:",
        EDAD_EDIFICIO,
        index=None,
        placeholder="Todos",
    )

if edad is not None:
    YRCONC1 = EDAD_EDIFICIO_YRCONC1[EDAD_EDIFICIO.index(edad)]
    microdatasi = microdatasi[microdatasi['YRCONC'] == YRCONC1]
    stop_if_empty(microdatasi)

    if grafica_tipo == "Stock":
        graficas = remove_graph_option(graficas, "Distribución de superficie por edad")
    elif grafica_tipo == "Consumo por Usos Finales":
        graficas = remove_graph_option(graficas, "Análisis del Consumo por Edad y Usos Finales")
    elif grafica_tipo == "Consumo por Tipo de Energía":
        graficas = remove_graph_option(graficas, "Consumo de Energía por Edad y Tipo de Energía")

if grafica_tipo == "Indicadores Clave":

    if tipo == "Vacíos":
        Unidad_Servicio = "No aplica"
    elif tipo == "Oficina":
        Unidad_Servicio = sum(microdatasi["NWKER"])

    Consumo = sum((microdatasi["MFBTU"]*microdatasi["FINALWT"]) + (microdatasi["ELBTU"]*microdatasi["FINALWT"]))

    df_indicadores = pd.DataFrame([{
        "Población [Millones]":"8.3",
        "Superficie [Mm2]":sum(microdatasi["SQFT"])/1000000,
        "Número de edificios":sum(microdatasi["FINALWT"]),
        "Service Unit": Unidad_Servicio,
        "Consumo": Consumo,
        }])

    st.subheader("Indicadores Clave")
    st.dataframe(
        df_indicadores.style.format({
        "Superficie [Mm2]": "{:.0f}",
        "Número de edificios": "{:.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.caption("Desarrollado por JYK - Fuente: U.S. Energy Information Administration (eia)")
    st.stop()

# Elección de gráfica concreta
with st.sidebar:
    grafica_idx = st.radio("Gráficas:", graficas)

st.markdown(
    f"<div style='text-align: center; font-size:2.0em; font-weight:600;'>{grafica_tipo} - {tipo}</div>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<div style='text-align: center; font-size:2.0em; font-weight:600;'>{grafica_idx} - {tipo}</div>",
    unsafe_allow_html=True,
)

x = np.arange(1990, 2023)

st.markdown("---")

# Etiquetas de tamaño usadas por las gráficas que agrupan por SQFTCM
nombres_simples = SIZE_CONFIG[tipo]["labels"]
nombres = []
for i, etiqueta in enumerate(nombres_simples, start=1):
    edificios_tamano = microdatasi[microdatasi["SQFTCM"] == i]
    if not edificios_tamano.empty:
        min_m2 = edificios_tamano["SQFT"].min()
        max_m2 = edificios_tamano["SQFT"].max()
        nombres.append(f"{etiqueta} {min_m2:.0f} - {max_m2:.0f}")
    else:
        nombres.append(etiqueta)

espacio1, contenido, espacio2 = st.columns([1, 3, 1])

#AQUI APARECE EL CÓDIGO DE CADA GRÁFICA, QUE VARÍA SEGÚN EL TIPO DE EDIFICIO

if grafica_idx == "Estructura del área por tamaños":
    etiquetas = []
    valores = []
    medias = []

    n = len(nombres_simples) + 1
    for i in range(1, n):
        Edi = microdatasi.query(f'SQFTCM=={i}')
        SQEdi = Edi['SQFT'] * Edi['FINALWT']
        TotalEdi = SQEdi.sum()
        TotalWTEdi = Edi['FINALWT'].sum()
        MediaEdi = TotalEdi / TotalWTEdi if TotalWTEdi > 0 else 0

        valores.append(TotalEdi)
        medias.append(MediaEdi)
        etiquetas.append(nombres_simples[i - 1])

    df_resultados = pd.DataFrame({
        "Categoría": etiquetas,
        "Total (m²)": valores,
        "Promedio (m²/Edif)": medias,
    })

    render_horizontal_percentage_bar(
        df_resultados,
        category_col="Categoría",
        value_col="Total (m²)",
        xaxis_title="Porcentaje de superficie total (%)",
        hover_category_name="Tamaño",
    )

    df_resultados = add_percentage_column(df_resultados, "Total (m²)")

    render_results_table(
        df_resultados,
        {
            "Total (m²)": "{:.0f}",
            "Promedio (m²/Edif)": "{:.0f}",
            "Porcentaje (%)": "{:.2f}",
        },
    )

elif grafica_idx == "Distribución de superficie por edad":

    def calcular_superficie(rango_yrconcn, microdatasi):
        edi = microdatasi.query(f'YRCONCN == {rango_yrconcn}')
        sq_edi = edi['SQFT'] * edi['FINALWT']
        total_edi = sq_edi.sum()
        total_wt_edi = edi['FINALWT'].sum()
        media_edi = total_edi / total_wt_edi if total_wt_edi > 0 else 0
        return total_edi, media_edi

    rangos_yrconcn = [1, 2, 3, 4]
    nombres_rangos = ['Antes 1960', '1960-1980', '1980-2000', '2000-2018']

    totales = []
    medias = []
    labels = []

    for i, rango in enumerate(rangos_yrconcn):
        total, media = calcular_superficie(rango, microdatasi)
        totales.append(total)
        medias.append(media)
        labels.append(nombres_rangos[i])

    df_resultados = pd.DataFrame({
        "Categoría": labels,
        "Total (m²)": totales,
        "Media (m²/Edif)": medias,
    })

    render_horizontal_percentage_bar(
        df_resultados,
        category_col="Categoría",
        value_col="Total (m²)",
        xaxis_title="Porcentaje de superficie total (%)",
        hover_category_name="Edad",
    )

    df_resultados = add_percentage_column(df_resultados, "Total (m²)")

    render_results_table(
        df_resultados,
        {
            "Total (m²)": "{:.0f}",
            "Media (m²/Edif)": "{:.0f}",
            "Porcentaje (%)": "{:.2f}",
        },
    )

elif grafica_idx == "Distribución de Superficies por Categoría Climática":
    climate_categories = {
        'Frío o muy frío': 1,
        'Frío': 2,
        'Templado': 3,
        'Cálido': 4,
        'Muy cálido': 5,
    }

    categorias = []
    totales = []
    medias = []

    for category, pubclim in climate_categories.items():
        Edi = microdatasi.query(f'PUBCLIM=={pubclim}')
        SQEdi = Edi['SQFT'] * Edi['FINALWT']
        TotalEdi = SQEdi.sum()
        TotalWTEdi = Edi['FINALWT'].sum()
        MediaEdi = TotalEdi / TotalWTEdi if TotalWTEdi > 0 else 0

        categorias.append(category)
        totales.append(TotalEdi)
        medias.append(MediaEdi)

    df_clima = pd.DataFrame({
        "Categoría climática": categorias,
        "Total (m²)": totales,
        "Media (m²/Edif)": medias,
    })

    render_horizontal_percentage_bar(
        df_clima,
        category_col="Categoría climática",
        value_col="Total (m²)",
        xaxis_title="Porcentaje de superficie total (%)",
        hover_category_name="Clima",
    )

    df_clima = add_percentage_column(df_clima, "Total (m²)")

    render_results_table(
        df_clima,
        {
            "Total (m²)": "{:.0f}",
            "Media (m²/Edif)": "{:.0f}",
            "Porcentaje (%)": "{:.2f}",
        },
    )

elif grafica_idx == "Distribución del consumo por tamaño":

    st.title("ESTAN MAL LAS UNIDADES KTOE ASI?")

    sqftcm_ranges = [1, 2, 3]
    labels = ['S', 'M', 'L']
    total_consumption_values = []
    media_consumo_por_edificio = []

    for sqftcm in sqftcm_ranges:
        edi = microdatasi.query(f'SQFTCM == {sqftcm}')
        total_consumption = (edi['MFBTU'] * edi['FINALWT']).sum()
        total_consumption_values.append(total_consumption)

        total_wt = edi['FINALWT'].sum()
        if total_wt > 0:
            media_consumo = (total_consumption / total_wt) * 1000
        else:
            media_consumo = 0
        media_consumo_por_edificio.append(media_consumo)

    df_consumo_tamano = pd.DataFrame({
        "Tamaño": labels,
        "Consumo (Mtoe)": total_consumption_values,
        "Consumo medio (ktoe/Edif)": media_consumo_por_edificio,
    })

    render_horizontal_percentage_bar(
        df_consumo_tamano,
        category_col="Tamaño",
        value_col="Consumo (Mtoe)",
        xaxis_title="Porcentaje del consumo total (%)",
        hover_category_name="Tamaño",
    )

    df_consumo_tamano = add_percentage_column(df_consumo_tamano, "Consumo (Mtoe)")

    render_results_table(
        df_consumo_tamano,
        {
            "Consumo (Mtoe)": "{:.4f}",
            "Consumo medio (ktoe/Edif)": "{:.4f}",
            "Porcentaje (%)": "{:.2f}",
        },
    )

elif grafica_idx == "Estructura del consumo por usos":
    usos = ['MFHTBTU', 'MFCLBTU', 'MFVNBTU', 'MFWTBTU', 'MFLTBTU', 'MFCKBTU', 'MFRFBTU', 'MFOFBTU', 'MFPCBTU', 'MFOTBTU']
    usos_labels = ['Calefacción', 'Aire acondicionado', 'Ventilación', 'ACS', 'Iluminación', 'Cocina', 'Refrigeración', 'Equipos Oficina', 'Computación', 'Otros']

    Edi = microdatasi.copy()
    if Edi.empty:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
        st.stop()

    total_consumos = []
    for uso in usos:
        consumo = (Edi[uso] * Edi['FINALWT']).sum()
        total_consumos.append(consumo)

    df_usos = pd.DataFrame({
        "Uso": usos_labels,
        "Consumo (Mtoe)": total_consumos,
    })

    df_usos = df_usos[df_usos["Consumo (Mtoe)"] > 0]

    if df_usos.empty:
        st.warning("Todos los consumos son cero para los filtros seleccionados.")
        st.stop()

    df_plot = add_percentage_column(df_usos, "Consumo (Mtoe)")
    df_plot = df_plot[df_plot["Consumo (Mtoe)"] > 0]

    fig_bar = px.bar(
        df_plot,
        x="Porcentaje (%)",
        y="Uso",
        orientation="h",
        text=df_plot["Porcentaje (%)"].round(1).astype(str) + "%",
        color="Uso",
        color_discrete_map={
            uso: color for uso, color in zip(USOS_LABELS, COLORES_USOS)
        },
    )

    fig_bar.update_layout(
        xaxis_title="Porcentaje del consumo total (%)",
        yaxis_title="",
        showlegend=False,
        margin=dict(t=40, b=20, l=20, r=20),
    )

    fig_bar.update_traces(
        hovertemplate=(
            "<b>Uso: %{y}</b><br>"
            "Porcentaje: %{x:.2f}%<extra></extra>"
        )
    )

    with contenido:
        st.plotly_chart(fig_bar, use_container_width=True)

    df_usos = add_percentage_column(df_usos, "Consumo (Mtoe)")

    render_results_table(
        df_usos,
        {
            "Consumo (Mtoe)": "{:.4f}",
            "Porcentaje (%)": "{:.2f}",
        },
    )

elif grafica_idx == "Análisis del Consumo por Clima y Usos Finales":
    # Definición de los usos energéticos y sus etiquetas
    usos = ['MFHTBTU', 'MFCLBTU', 'MFVNBTU', 'MFWTBTU', 'MFLTBTU', 'MFCKBTU', 'MFRFBTU', 'MFOFBTU', 'MFPCBTU', 'MFOTBTU']

    usos_labels = USOS_LABELS
    colors = COLORES_USOS

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

    df_resultados = pd.DataFrame(
        climate_consumptions,
        columns=[f"{uso} (%)" for uso in usos_labels],
    )
    df_resultados.insert(0, "Clima", climates)

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

    render_results_table(
        df_resultados,
        {col: "{:.2f}" for col in df_resultados.columns if col != "Clima"},
    )

elif grafica_idx == "Análisis del Consumo por Edad y Usos Finales":
    # Definición de los usos energéticos y sus etiquetas
    usos = ['MFHTBTU', 'MFCLBTU', 'MFVNBTU', 'MFWTBTU', 'MFLTBTU', 'MFCKBTU', 'MFRFBTU', 'MFOFBTU', 'MFPCBTU', 'MFOTBTU']
    usos_labels = USOS_LABELS
    colors = COLORES_USOS

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

    df_resultados = pd.DataFrame(
        climate_consumptions,
        columns=[f"{uso} (%)" for uso in usos_labels],
    )
    df_resultados.insert(0, "Edad", climates)

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

    render_results_table(
        df_resultados,
        {col: "{:.2f}" for col in df_resultados.columns if col != "Edad"},
    )

elif grafica_idx == "Análisis del Consumo por tamaño y Usos Finales":
    # Definición de los usos energéticos y sus etiquetas
    usos = ['MFHTBTU', 'MFCLBTU', 'MFVNBTU', 'MFWTBTU', 'MFLTBTU', 'MFCKBTU', 'MFRFBTU', 'MFOFBTU', 'MFPCBTU', 'MFOTBTU']
    usos_labels = USOS_LABELS
    colors = COLORES_USOS

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

    df_resultados = pd.DataFrame(
        climate_consumptions,
        columns=[f"{uso} (%)" for uso in usos_labels],
    )
    df_resultados.insert(0, "Tamaño", climates)

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

    render_results_table(
        df_resultados,
        {col: "{:.2f}" for col in df_resultados.columns if col != "Tamaño"},
    )

elif grafica_idx == "Estructura del consumo por fuentes":
    fuentes = ['ELBTU', 'NGBTU', 'FKBTU', 'DHBTU']
    fuentes_labels = FUENTES_LABELS

    Edi = microdatasi.copy()

    total_consumos = []
    for fuente in fuentes:
        consumo = (Edi[fuente] * Edi['FINALWT']).sum()
        total_consumos.append(consumo)

    df_fuentes = pd.DataFrame({
        "Fuente": fuentes_labels,
        "Consumo (Mtoe)": total_consumos,
    })

    df_plot = add_percentage_column(df_fuentes, "Consumo (Mtoe)")
    df_plot = df_plot[df_plot["Consumo (Mtoe)"] > 0]

    fig_bar = px.bar(
        df_plot,
        x="Porcentaje (%)",
        y="Fuente",
        orientation="h",
        text=df_plot["Porcentaje (%)"].round(1).astype(str) + "%",
        color="Fuente",
        color_discrete_map={
            fuente: color for fuente, color in zip(FUENTES_LABELS, COLORES_FUENTES)
        },
    )

    fig_bar.update_layout(
        xaxis_title="Porcentaje del consumo total (%)",
        yaxis_title="",
        showlegend=False,
        margin=dict(t=40, b=20, l=20, r=20),
    )

    fig_bar.update_traces(
        hovertemplate=(
            "<b>Fuente: %{y}</b><br>"
            "Porcentaje: %{x:.2f}%<extra></extra>"
        )
    )

    with contenido:
        st.plotly_chart(fig_bar, use_container_width=True)

    df_fuentes = add_percentage_column(df_fuentes, "Consumo (Mtoe)")

    render_results_table(
        df_fuentes,
        {
            "Consumo (Mtoe)": "{:.4f}",
            "Porcentaje (%)": "{:.2f}",
        },
    )

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
    
    df_resultados = pd.DataFrame({
        "Uso final": usos_finales,
        **{
            f"{energia} (%)": [porcentajes_por_uso[uso][i] for uso in usos_finales]
            for i, energia in enumerate(tipos_energia_lista)
        },
    })

    # Crear el gráfico apilado con mejor resolución
    fig, ax = plt.subplots(figsize=(12, 7), dpi=120)

    colores = ['skyblue', 'yellow', '#005F6B', 'lightgreen']

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

    render_results_table(
        df_resultados,
        {col: "{:.2f}" for col in df_resultados.columns if col != "Uso final"},
    )

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

    colores = ['skyblue', 'yellow', '#005F6B', 'lightgreen']

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

    df_resultados = df_consumos_pct.reset_index()
    df_resultados.columns = [
        "Clima",
        "Eléctrico (%)",
        "Gas natural (%)",
        "Fuel Oil (%)",
        "Vapor de distrito (%)",
    ]

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

    render_results_table(
        df_resultados,
        {col: "{:.2f}" for col in df_resultados.columns if col != "Clima"},
    )

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

    colores = ['skyblue', 'yellow', '#005F6B', 'lightgreen']

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

    df_resultados = df_consumos_pct.reset_index()
    df_resultados.columns = [
        "Tamaño",
        "Eléctrico (%)",
        "Gas natural (%)",
        "Fuel Oil (%)",
        "Vapor de distrito (%)",
    ]

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

    render_results_table(
        df_resultados,
        {col: "{:.2f}" for col in df_resultados.columns if col != "Tamaño"},
    )

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

    colores = ['skyblue', 'yellow', '#005F6B', 'lightgreen']

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

    df_resultados = df_consumos_pct.reset_index()
    df_resultados.columns = [
        "Edad",
        "Eléctrico (%)",
        "Gas natural (%)",
        "Fuel Oil (%)",
        "Vapor de distrito (%)",
    ]

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

    render_results_table(
        df_resultados,
        {col: "{:.2f}" for col in df_resultados.columns if col != "Edad"},
    )

st.markdown("---")
st.caption("Desarrollado por JYK - Fuente: U.S. Energy Information Administration (eia)")

