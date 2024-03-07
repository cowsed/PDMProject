import psycopg2
from sshtunnel import SSHTunnelForwarder

import credentials
from contextlib import contextmanager

@contextmanager
def cs_database():
    with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
         ssh_username=credentials.ssh_username,
         ssh_password=credentials.ssh_password,
         remote_bind_address=('127.0.0.1', 5432)) as server:
        server.start()
        print("server connected")

        params = {
            'database': 'p320_14',
            'user': credentials.cs_username,
            'password': credentials.cs_password,
            'host': '127.0.0.1',
            'port': server.local_bind_port
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
