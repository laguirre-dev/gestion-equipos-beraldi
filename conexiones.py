import os
from dotenv import load_dotenv
import pyodbc

load_dotenv()

def connect_softland():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        f"SERVER={os.getenv('SOFTLAND_DB_SERVER')};"
        f"DATABASE={os.getenv('SOFTLAND_DB_NAME')};"
        f"UID={os.getenv('BERALDI_PYTHON_DB_USER')};"
        f"PWD={os.getenv('BERALDI_PYTHON_DB_PASSWORD')}"
    )
    cursor = conn.cursor()
    return conn, cursor
