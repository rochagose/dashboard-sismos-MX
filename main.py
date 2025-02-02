import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

#Configuracion general del dashboard
st.set_page_config(page_title = "Dashboard", 
                   page_icon = "💥", 
                   layout = "wide",
                   initial_sidebar_state = 'collapsed', 
                   menu_items = {
                        'About': "Dashboard sobre sismos registrados en México"
                   })                  
st.title("🌐 Sismos: México (1925 - 2025)")

@st.cache_data
def load_data():
    data = pd.read_csv('data/processed_data.csv', low_memory = False)
    return data

#FUNCIONES

#Darle formato a los numeros, ej. 140,022 -> 140k
def formatear(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'


#Cargar datos
df = load_data()


#ESTADISTICAS GENERALES
TOTAL_SISMOS = df.shape[0]
TOTAL_VERIFICADOS = df['Estatus'].value_counts().get('VERIFICADO')
TOTAL_REVISADOS = df['Estatus'].value_counts().get('REVISADO')
MAYOR_NUM_ESTADO = df['Estado'].mode().iloc[0]
MAYOR_NUM_LOCALIDAD = df['Localidad'].mode().iloc[0]

df['Magnitud'] = pd.to_numeric(df['Magnitud'], errors='coerce') 
MAYOR_MAGNITUD = df['Magnitud'].max()
MAYOR_MAGNITUD_ESTADO = df.loc[df['Magnitud'].idxmax(), 'Estado']
MAYOR_MAGNITUD_LOCALIDAD = df.loc[df['Magnitud'].idxmax(), 'Localidad']
MAYOR_MAGNITUD_FECHA = df.loc[df['Magnitud'].idxmax(), 'Fecha']
MAYOR_NUM_DIA = df['Dia Semana'].mode().iloc[0]
MAYOR_ACT_ANIO = df['Año'].mode().iloc[0]



st.markdown("#### 📰 Estadísticas Generales (1925 - 2025)")
col_row_1 = st.columns(4, gap = "small")
with col_row_1[0]:
    with st.container(border = True):
        st.info("📌 No. Total de Sismos")
        st.metric(label = "Sismos" ,value = formatear(TOTAL_SISMOS))
        frecuencia_por_anio = df['Año'].value_counts().sort_index().reset_index()
        frecuencia_por_anio.columns = ['Año', 'Frecuencia']
        st.area_chart(frecuencia_por_anio.set_index('Año'), height = 158, color = ["#bd4a4a"])

with col_row_1[1]:
    with st.container(border = True):
        st.info("✅ Sismos Verificados")
        st.metric(label = "Verificados" ,value = formatear(TOTAL_VERIFICADOS))
        fig, ax = plt.subplots(figsize = (4, 4))
        fig.patch.set_alpha(0) 
        ax.set_facecolor((0, 0, 0, 0))
        ax.pie(df['Estatus'].value_counts(), labels = df['Estatus'].unique() , colors = ['#bd4a4a', '#295f8c'],
                textprops={'color': 'white'}, explode = [0.2, 0])
        st.pyplot(fig)

with col_row_1[2]:
    with st.container(border = True):
        st.info("🌎 Mayor Cantidad de Sismos")
        st.metric(label = "Estado" , value = MAYOR_NUM_ESTADO)
        df_oax = df[df['Estado'] == 'OAX']
        df_oax['Fecha'] = pd.to_datetime(df_oax['Fecha'])
        sismos_por_anio = df_oax.groupby(df_oax['Fecha'].dt.year).size().reset_index(name='Cantidad de Sismos')
        sismos_por_anio.set_index('Fecha', inplace=True)
        st.area_chart(sismos_por_anio['Cantidad de Sismos'], height = 158, color = ["#5c2250"])

with col_row_1[3]:
    with st.container(border = True):
        st.write("###### 🌎 Top Estados")
        estados = df['Estado'].value_counts().reset_index().head(7)
        estados.columns = ['Estado', 'No. Sismos']
        st.dataframe(estados,
                    use_container_width = True,
                    hide_index = True,
                    )

col_row_2 = st.columns(2, gap = "small")
with col_row_2[0]:
    with st.container(border = True):
        st.info("📅 Año Mayor Actividad")
        st.metric(label = "Año", value = f"{MAYOR_ACT_ANIO}")
        df_anio = df[df['Año'] == 2024]
        df_anio['Fecha'] = pd.to_datetime(df_anio['Fecha']) 
        sismos = df_anio.groupby(df_anio['Fecha'].dt.month).size().reset_index(name='Cantidad de Sismos')
        sismos.set_index('Fecha', inplace=True)
        st.area_chart(sismos['Cantidad de Sismos'], height=176, color=["#3b705e"])

with col_row_2[1]:
    with st.container(border = True):
        st.info("🌎 Mayor Cantidad de Sismos")
        st.metric(label = "Localidad", value = MAYOR_NUM_LOCALIDAD)
        # Contar las localidades y obtener las 10 principales
        frecuencia = df['Localidad'].value_counts().reset_index().head()
        frecuencia.columns = ['Localidad', 'Frecuencia']

        st.bar_chart(frecuencia, x = 'Localidad', y = 'Frecuencia', horizontal = True, color = ["#374182"])


st.markdown("#### 🗺️ Mapa: Actividad Sismologica (Ultimos 50k Eventos)")
col_row_0 = st.columns(1)
with col_row_0[0]:
    with st.container(border = True):
        df_map = df[['Latitud', 'Longitud']]
        df_map.rename(columns={'Latitud': 'lat', 'Longitud': 'lon'}, inplace=True)
        df_map = df_map.tail(50000)
        st.map(df_map, height = 450, color = "#871020", zoom = 4)


st.markdown(f"#### 🗻 Registro Histórico de Sismos")
#Mostrar dataframe
with st.expander("Visualizar: Registro de Sismos (1925 - 2025)", expanded = True):
    st.dataframe(df[['Fecha', 'Estado', 'Localidad', 'Distancia KM', 'Direccion Cardinal', 'Magnitud', 'Profundidad', 'Estatus']],
                 use_container_width = True,
                 hide_index = True,
                 on_select = "ignore")
    