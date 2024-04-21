import psycopg2
from sshtunnel import SSHTunnelForwarder

import credentials
from contextlib import contextmanager
import logging

@contextmanager
def cs_database(username, password):

    with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
         ssh_username=username,
         ssh_password=password,
         remote_bind_address=('127.0.0.1', 5432)) as server:
        server.start()

        params = {
            'database': 'p320_14',
            'user': username,
            'password': password,
            'host': '127.0.0.1',
            'port': server.local_bind_port
            }

        conn = psycopg2.connect(**params)
        yield conn

@contextmanager
def local_database():

    params = {
        'database': 'jupyter',
        'user': 'jupyter',
        'password': 'jupyter',
        'host': '127.0.0.1',
        'port': 5432
        }

    conn = psycopg2.connect(**params)
    yield conn


if __name__=='__main__':
    # Example Query
    with cs_database() as db:
        cursor = db.cursor()
        query = 'select P.username, E.email from "Player" P NATURAL JOIN "Emails" E' 

        cursor.execute(query)
        records = cursor.fetchall()

        for row in records:
            print(row)
