import os
import streamlit as st
# from dotenv import load_dotenv
import pyodbc

# load_dotenv()

def connect_softland():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        f"SERVER={st.secrets['SOFTLAND_DB_SERVER']};"
        f"DATABASE={st.secrets['SOFTLAND_DB_NAME']};"
        f"UID={st.secrets['BERALDI_PYTHON_DB_USER']};"
        f"PWD={st.secrets['BERALDI_PYTHON_DB_PASSWORD']}"
    )
    cursor = conn.cursor()
    return conn, cursor
