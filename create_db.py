import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='localhost', port='5432')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('CREATE DATABASE drngpit_db;')
    cur.close()
    conn.close()
    print("Database drngpit_db created successfully.")
except psycopg2.errors.DuplicateDatabase:
    print("Database drngpit_db already exists.")
except Exception as e:
    print(f"Error: {e}")
