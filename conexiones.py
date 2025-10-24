import os
import streamlit as st
# from dotenv import load_dotenv
# import pyodbc
import pymssql

# load_dotenv()

def connect_softland():
    server = st.secrets["DB_SERVER"]
    user = st.secrets["DB_USER"]
    password = st.secrets["DB_PASSWORD"]
    database = st.secrets["DB_NAME"]

    conn = pymssql.connect(
        server=server,
        user=user,
        password=password,
        database=database,
        login_timeout=10,
        charset='UTF-8'
    )
    return conn, conn.cursor()

# def connect_softland():
#     conn = pyodbc.connect(
#         "DRIVER={SQL Server};"
#         f"SERVER={st.secrets['SOFTLAND_DB_SERVER']};"
#         f"DATABASE={st.secrets['SOFTLAND_DB_NAME']};"
#         f"UID={st.secrets['BERALDI_PYTHON_DB_USER']};"
#         f"PWD={st.secrets['BERALDI_PYTHON_DB_PASSWORD']}"
#     )
#     cursor = conn.cursor()
#     return conn, cursor
