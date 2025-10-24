import os
import streamlit as st
# from dotenv import load_dotenv
# import pyodbc
# usemos otra libreria en vez de pyodbc
import sqlalchemy

# load_dotenv()

def connect_softland2():
    conn = sqlalchemy.connect(
        server=st.secrets['SOFTLAND_DB_SERVER'],
        database=st.secrets['SOFTLAND_DB_NAME'],
        user=st.secrets['BERALDI_PYTHON_DB_USER'],
        password=st.secrets['BERALDI_PYTHON_DB_PASSWORD']
    )
    cursor = conn.cursor()
    return conn, cursor


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
