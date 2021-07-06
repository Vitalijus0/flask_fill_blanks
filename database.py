from flask import g
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
"""

def connect_db():
    sql = sqlite3.connect('/home/vitalijus/Desktop/flask_app/lecture23/23/questions.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
    """


def connect_db():
    conn = psycopg2.connect('postgres://ymqyxqhwnoojlv:cd9240186a3287b43f7632c4ba12f40f32b4994228ad049b35dfe4abaefbe030@ec2-54-227-246-76.compute-1.amazonaws.com:5432/dfjjjf4hg2bau4', cursor_factory=DictCursor)
    conn.autocommit = True
    sql = conn.cursor()
    return conn, sql

def get_db():
    db = connect_db()

    if not hasattr(g, 'postgres_db_conn'):
        g.postgres_db_conn = db[0]

    if not hasattr(g, 'postgres_db_cur'):
        g.postgres_db_cur = db[1]

    return g.postgres_db_cur

def init_db():
    db = connect_db()

    db[1].execute(open('schema.sql', 'r').read())
    db[1].close()

    db[0].close()

def init_admin():
    db = connect_db()

    db[1].execute('update users set admin = True where name = %s', ('admin', ))

    db[1].close()
    db[0].close()
