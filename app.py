from conexiones import connect_softland
from querys import vencimientos
import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
import os
import json
import time

st.set_page_config(
    page_title="Gestion VTO Equipos - Grupo Beraldi",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

USERS = {"logistica": "logistica", "admin": "admin"}


def login():
    if "logged" not in st.session_state:
        st.session_state.logged = False

    if not st.session_state.logged:
        # Mientras no exista una sesion logueada, va a mostrar el login
        with st.container(horizontal_alignment="center"):
            # definimos un contenedor para el login
            con = st.container(horizontal_alignment="center", width=500, border=True)
            # logo, usuario y contraseña
            con.image(os.getenv("URL_LOGO"))
            user = con.text_input("Usuario")
            pwd = con.text_input("Contraseña", type="password")
            # boton para login
            if con.button("Ingresar") and user and USERS[user] == pwd:
                # hagamos un spinner de carga para simular una espera
                with st.spinner("Validando..."):
                    time.sleep(1)
                st.session_state.logged = True
                con.success(f"Bienvenido {user}")
                time.sleep(1)
                st.rerun()
    return st.session_state.logged

def get_data(conn, dias_vencimiento):
    df = pd.read_sql(vencimientos(dias_vencimiento), conn)
    return df


status = login()
if status:
    # ---
    # Conexiones
    # ---
    try:
        conn, cur = connect_softland()
    except Exception as e:
        st.error(e)
        st.stop()
    # ---
    # Header
    # ---
    st.title("Gestion de Vencimientos Equipos - Grupo Beraldi")
    hoy = datetime.datetime.today().strftime("%Y-%m-%d")
    f"Fecha: {hoy}"
    # ---
    # Filtros
    # ---
    with st.container(border=True):
        st.subheader("Filtros", divider="orange")
        with st.popover("Mostrar ayuda"):
            st.info("__Vencidos__: con fecha menor a hoy")
            st.info("__Por vencer__: con fecha dentro de los 15 proximos dias")
            st.info("__En fecha__: con fecha mayor a los proximos 15 dias")
        col1, col2, col3, col4 = st.columns(4)
        # Tipo de equipos (Automovil, Cisterna, Tractor)
        tipo_equipo = col1.segmented_control(
            "Tipo de Equipo",
            ["Automovil", "Cisterna", "Tractor"],
            selection_mode="multi",
            default=["Automovil", "Cisterna", "Tractor"],
            key="tipo_equipo",
        )
        if len(tipo_equipo) == 0:
            col1.error("Seleccione al menos un tipo de equipo")
        # Tipo de vencimiento (Vencido, Por vencer, En fecha)
        tipo_vencimiento = col2.segmented_control(
            "Tipo de Vencimiento",
            ["Vencido", "Por vencer", "En fecha"],
            selection_mode="multi",
            default=["Vencido", "Por vencer", "En fecha"],
            key="tipo_vencimiento",
        )
        if len(tipo_vencimiento) == 0:
            col2.error("Seleccione al menos un tipo de vencimiento")
        # Filtro Dias de vencimiento
        dias_vencimiento = col3.number_input(
            "Dias de Vencimiento",
            min_value=0,
            max_value=365,
            value=15,
            step=1,
            key="dias_vencimiento",
        )
        # Filtro Matricula
        matricula = col4.text_input("Patente", key="patente")
    # ---
    # Datos
    # ---
    df = get_data(conn, dias_vencimiento)
    # Aplicado de Filtros
    if matricula == "":
        df_filtro = df[
            (df["Tipo"].isin(tipo_equipo)) & (df["ClasVTO"].isin(tipo_vencimiento))
        ]
    else:
        df_filtro = df[
            (df["Tipo"].isin(tipo_equipo))
            & (df["ClasVTO"].isin(tipo_vencimiento))
            & (df["Patente"].str.contains(matricula, case=False))
        ]
    with st.container(border=True):
        st.subheader("Resultados", divider="orange")
        "Recordar que los datos mostrados provienen de Softland. Si algun dato es incorrecto, se debe realizar la corrección dentro de Softland en el Módulo: __Gestión de vencimientos de Equipos__"
        # ---
        # Calculos
        # ---
        totales = len(df_filtro)
        vencidos = len(df_filtro[df_filtro["ClasVTO"] == "Vencido"])
        por_vencer = len(df_filtro[df_filtro["ClasVTO"] == "Por vencer"])
        en_fecha = len(df_filtro[df_filtro["ClasVTO"] == "En fecha"])
        # ---
        # Porcentajes
        # ---
        p_vencidos = 0
        p_por_vencer = 0
        p_en_fecha = 0
        if totales != 0:
            p_vencidos = round((vencidos / totales) * 100, 2)
            p_por_vencer = round((por_vencer / totales) * 100, 2)
            p_en_fecha = round((en_fecha / totales) * 100, 2)
        # ---
        # Metricas
        # ---
        col1, col2, col3, col4 = st.columns(4, border=True)
        col1.metric("Total", totales, delta="100%", delta_color="off")
        col2.metric("Vencidos", vencidos, delta=f"{p_vencidos}%", delta_color="off")
        col3.metric("Por vencer", por_vencer, delta=f"{p_por_vencer}%", delta_color="off")
        col4.metric("En fecha", en_fecha, delta=f"{p_en_fecha}%", delta_color="off")
        # ---
        # Armado de Graficos
        # ---
        # Grafico 1
        conteo_tipo = df_filtro['TipoVencimiento'].value_counts().reset_index()
        conteo_tipo.columns = ['TipoVencimiento', 'Cantidad']
        fig1 = px.bar(
            conteo_tipo,
            x='TipoVencimiento',
            y='Cantidad',
            color='TipoVencimiento',
            title='Conteo por Tipo de Vencimiento',
            labels={'TipoVencimiento': 'Tipo', 'Cantidad': 'Cantidad'}
        )
        # Grafico 2
        conteo_tipo = df_filtro['ClasVTO'].value_counts().reset_index()
        conteo_tipo.columns = ['ClasVTO', 'Cantidad']
        fig2 = px.bar(
            conteo_tipo,
            x='ClasVTO',
            y='Cantidad',
            color='ClasVTO',
            title='Conteo por Clasificacion de VTO',
            labels={'ClasVTO': 'Clasificacion', 'Cantidad': 'Cantidad'}
        )
        # Creamos 2 tabs
        graficos, detalle = st.tabs(["Graficos", "Detalle"])
        with graficos:
            col1, col2 = st.columns(2)
            # ---
            # Grafico por Tipo Vencimiento
            # ---
            col1.plotly_chart(fig1, use_container_width=True)
            # ---
            # Grafico por Tipo de VTO
            # ---
            col2.plotly_chart(fig2, use_container_width=True)
        with detalle:
            df_filtro
        
