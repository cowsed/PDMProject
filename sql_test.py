import psycopg2
from sshtunnel import SSHTunnelForwarder

import credentials

try:

    with SSHTunnelForwarder(
         ('starbug.cs.rit.edu', 22),
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
        curs = conn.cursor()
        print("database connected")
        try:
            cursor = conn.cursor()
            postgreSQL_select_Query = 'select U.username, E.email from "User" U NATURAL JOIN "Emails" E' 

            cursor.execute(postgreSQL_select_Query)
            mobile_records = cursor.fetchall()

            print("Print each row and it's columns values")
            for row in mobile_records:
                print(row)
            	# print(row[0], row[1])
        except Exception as e:
            print("query failed:",e)
except Exception as e:
    print("Connection Failed:", e)
