import psycopg2
from os import getenv
def get_db_connection():
    return psycopg2.connect(getenv('DATABASE_URL'))