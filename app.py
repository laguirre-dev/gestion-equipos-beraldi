from conexiones import connect_softland
from querys import vencimientos
import streamlit as st
import pandas as pd
import datetime
import os
# from dotenv import load_dotenv
import time

# load_dotenv()

# --- Configuración de página ---
st.set_page_config(
    page_title="Gestion VTO Equipos - Grupo Beraldi",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Usuarios para login ---
USERS = {"logistica": "1234", "admin": "1234"}

# =========================
# FUNCIONES
# =========================

def login():
    """Maneja login y session state"""
    if "logged" not in st.session_state:
        st.session_state.logged = False

    if not st.session_state.logged:
        with st.container(horizontal_alignment="center"):
            con = st.container(horizontal_alignment="center", width=500, border=True)
            # con.image(os.getenv("URL_LOGO"))
            con.image(st.secrets["URL_LOGO"])
            user = con.text_input("Usuario", key="user")
            pwd = con.text_input("Contraseña", type="password", key="pwd")
            if con.button("Ingresar", type="primary") and user and USERS.get(user) == pwd:
                with st.spinner("Validando..."):
                    time.sleep(1)
                st.session_state.logged = True
                con.success(f"Bienvenido {user}")
                time.sleep(0.5)
                st.rerun()
    return st.session_state.logged

def get_data(conn):
    """Carga la data desde la base"""
    return pd.read_sql(vencimientos(), conn)

def apply_filters(df, tipo_equipo, tipo_vencimiento, dias_vencimiento, matricula):
    """Aplica los filtros seleccionados sobre df"""
    df_f = df[
        (df["Tipo"].isin(tipo_equipo)) &
        (df["ClasVTO"].isin(tipo_vencimiento)) &
        (df["DiasVencimiento"] <= dias_vencimiento)
    ]
    if matricula:
        df_f = df_f[df_f["Patente"].str.contains(matricula, case=False)]
    return df_f

def color_vencimiento(val):
    if val < 0:
        return "background-color: #d33a3a; font-weight: bold;"
    elif val < 7:
        return "background-color: #dbae33; font-weight: bold;"
    elif val < 15:
        return "background-color: #629513; font-weight: bold;"
    else:
        return "background-color: #1274b3; font-weight: bold;"

def color_estados(val):
    if val == "Pendiente":
        return "color: #FF595E; font-weight: bold;"
    elif val == "En proceso":
        return "background-color: #FFCA3A; font-weight: bold; color: black;"
    elif val == "Programado":
        return "background-color: #8AC926; font-weight: bold; color: black;"
    elif val == "Realizado":
        return "background-color: #1982C4; font-weight: bold; color: white;"

def calculate_metrics(df_filtro):
    """Calcula totales y porcentajes"""
    totales = len(df_filtro)
    vencidos = len(df_filtro[df_filtro["ClasVTO"] == "Vencido"])
    por_vencer = len(df_filtro[df_filtro["ClasVTO"] == "Por vencer"])
    en_fecha = len(df_filtro[df_filtro["ClasVTO"] == "En fecha"])
    
    p_vencidos = round((vencidos / totales) * 100,2) if totales else 0
    p_por_vencer = round((por_vencer / totales) * 100,2) if totales else 0
    p_en_fecha = round((en_fecha / totales) * 100,2) if totales else 0
    
    return (totales, vencidos, por_vencer, en_fecha, p_vencidos, p_por_vencer, p_en_fecha)

# =========================
# INICIO APP
# =========================

if login():
    # --- Conexión a BD ---
    try:
        conn, cur = connect_softland()
    except Exception as e:
        st.error(e)
        st.stop()
    
    # --- Header ---
    st.title("Gestión de Vencimientos de Equipos - Grupo Beraldi")
    st.write(f"Fecha: {datetime.datetime.today().strftime('%Y-%m-%d')}")
    if st.button("Actualizar Informe en Softland", type="primary"):
        st.toast("Funcionalidad en desarrollo. Vuelva a intentar más tarde", icon="🚧")
    
    # --- Filtros ---
    with st.container(border=True):
        st.subheader("Filtros", divider="orange")
        col1, col2, col3, col4 = st.columns(4)
        
        tipo_equipo = col1.segmented_control(
            "Tipo de Equipo",
            ["Automovil", "Cisterna", "Tractor"],
            default=["Automovil", "Cisterna", "Tractor"],
            selection_mode="multi"
        )
        tipo_vencimiento = col2.segmented_control(
            "Tipo de Vencimiento",
            ["Vencido", "Por vencer", "En fecha"],
            default=["Vencido", "Por vencer", "En fecha"],
            selection_mode="multi"
        )
        dias_vencimiento = col4.number_input(
            "Dias de Vencimiento",
            min_value=0,
            max_value=365,
            value=15,
            step=1
        )
        matricula = col3.text_input("Patente")

    # --- Cargar DF completo si no existe ---
    if 'df_full' not in st.session_state:
        st.session_state.df_full = get_data(conn)
    df_full = st.session_state.df_full.copy()
    
    # --- Aplicar filtros ---
    df_filtro = apply_filters(df_full, tipo_equipo, tipo_vencimiento, dias_vencimiento, matricula)
    
    # --- Métricas ---
    totales, vencidos, por_vencer, en_fecha, p_vencidos, p_por_vencer, p_en_fecha = calculate_metrics(df_filtro)
    col1, col2, col3, col4 = st.columns(4, border=True)
    col1.metric("Total", totales)
    col2.metric("Vencidos", vencidos, delta=f"{p_vencidos}%", delta_color="off")
    col3.metric("Por vencer", por_vencer, delta=f"{p_por_vencer}%", delta_color="off")
    col4.metric("En fecha", en_fecha, delta=f"{p_en_fecha}%", delta_color="off")
    
    # --- Tabs: Gráficos y Detalle ---
    graficos, detalle = st.tabs(["Graficos", "Detalle"])
    
    with graficos:
        col1, col2 = st.columns(2)
        conteo_tipo_1 = df_filtro["TipoVencimiento"].value_counts().reset_index()
        conteo_tipo_1.columns = ["TipoVencimiento", "Cantidad"]
        col1.bar_chart(conteo_tipo_1, x="TipoVencimiento", y="Cantidad", color="TipoVencimiento")
        
        conteo_tipo_2 = df_filtro["ClasVTO"].value_counts().reset_index()
        conteo_tipo_2.columns = ["ClasVTO", "Cantidad"]
        col2.bar_chart(conteo_tipo_2, x="ClasVTO", y="Cantidad", color="ClasVTO")
    
    with detalle:
        df_filtro["DiasVencimiento"] = df_filtro["DiasVencimiento"].astype(int)
        estados = ["Pendiente", "En proceso", "Programado", "Realizado"]
        
        col1, col2, col3, _, _ = st.columns(5)
        patente_fil = col1.selectbox("Patente", sorted(df_filtro["Patente"].unique()))
        vto_fil = df_filtro[df_filtro["Patente"]==patente_fil]["TipoVencimiento"].unique()
        # vto_fil ordenado
        vto_new = col2.selectbox("Vencimiento", sorted(vto_fil))
        status_new = col3.selectbox("Estado", estados)
        
        if st.button("Guardar estado", type="primary"):
            mask = (st.session_state.df_full["Patente"]==patente_fil) & \
                   (st.session_state.df_full["TipoVencimiento"]==vto_new)
            st.session_state.df_full.loc[mask,"Estado"] = status_new
            st.toast(f"Estado actualizado: {patente_fil} - {vto_new} → {status_new}", icon="✅")
            st.rerun() 
        # ordenamos el df por DiasVencimiento
        df_filtro = df_filtro.sort_values("DiasVencimiento")
        df_styled = df_filtro.style\
            .map(color_vencimiento, subset=["DiasVencimiento"])\
            .map(color_estados, subset=["Estado"])
        st.dataframe(df_styled, use_container_width=True)
