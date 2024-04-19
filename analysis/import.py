# Import data from starbug to local db for analysis

import getpass
from functools import cmp_to_key
import csv
from itertools import islice
from database import local_database, cs_database
from psycopg2 import sql
from psycopg2.extras import execute_values
import re


def main():
    with local_database() as db:
        cursor = db.cursor()
        # delete local tables/ setup empty ones
        # reset_tables(cursor)
        # copy data from starbug
        # import_db(cursor)
        bolster_users(cursor, 2000)
        # copy in data from datasets
        import_csvs(cursor)

        db.commit()

# delete local tables/ setup empty ones
def reset_tables(cursor):
    # Delete existing tables
    query = "select table_name from information_schema.tables WHERE table_schema='public'"
    cursor.execute(query)
    tables = cursor.fetchall()
    for table in tables:
        table = table[0]
        query = sql.SQL("DROP TABLE {table} CASCADE").format(table=sql.Identifier(table))
        print("Deleting", table)
        cursor.execute(query)
        
    # Create new tables
    cursor.execute(open("table_definitions.sql", "r").read())

def import_db(cursor):
    ###Import data from the starbug server. Queries for username/password###
    query = "select t.table_name, count(*) from information_schema.tables as t JOIN information_schema.columns as c on (t.table_name=c.table_name) WHERE t.table_schema='public' GROUP BY t.table_name"
    cursor.execute(query)
    tables = cursor.fetchall()
    tables.sort(key=cmp_to_key(table_cmp))
    print(tables)
    username = getpass.getpass('Enter your username:')
    password = getpass.getpass('Enter your password:')
    with cs_database(username, password) as cs_db:
        cs_cursor = cs_db.cursor()
        for (table, col_count) in tables:
            print("Copying "+table+"...")
            # Copy the contents of each table over
            fetch_query = sql.SQL("SELECT * FROM {table}").format(table=sql.Identifier(table))
            cs_cursor.execute(fetch_query)
            data = cs_cursor.fetchall()

            # Save the data locally
            save_query = sql.SQL("INSERT INTO {table} OVERRIDING SYSTEM VALUE VALUES %s").format(table=sql.Identifier(table))
            # values = "(" + ("%s"*col_count) + ")"
            # save_query = sql.SQL("INSERT INTO {table} VALUES " + values).format(table=sql.Identifier(table))
            execute_values(cursor, save_query, data, page_size=1000)
            # cursor.execute()
    cs_db.close()


def table_cmp(table1, table2):
    index = {
        "Player": 10,
        "Game": 8,
        "Platform": 5
    }
    cmp1 = 0
    if table1[0] in index:
        cmp1 = index[table1[0]]
    cmp2 = 0
    if table2[0] in index:
        cmp2 = index[table2[0]]
    return cmp2 - cmp1
    

def import_csvs(cursor):
    print("Importing CSVs...")
    # CSVS 
    # Steam: Playtime/ownership
    # IMDB: ESRB, Genre
    # Gamespot: Aggregate Ratings (Not sure what we can do with this)

    # Steam
    print("Importing Steam data...")
    with open('datasets/steam-200k.csv', newline='') as csvfile:
        # Delete existing playtime/ownership
        cursor.execute('DELETE FROM "PlaysGame"');
        cursor.execute('DELETE FROM "OwnsGame"');
        # for each user in the csv, find a user in the db, and give that user the playtime
        cursor.execute('SELECT username FROM "Player"')
        userlist = cursor.fetchall()
        userlist = [user[0] for user in userlist]
        usermap = {}
        extra_data_count = {}
        failed_to_match = {}
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in csvreader:
            # Match to existing game
            game_name = row[1]
            cursor.execute('SELECT gameid FROM "Game" WHERE title=%s', [game_name])
            game_id = cursor.fetchone()
            
            if game_id is None:
                failed_to_match[game_name] = True
                continue
            else:
                game_id = game_id[0]
            
            # Match to existing user
            if row[0] in usermap:
                username = usermap[row[0]]
            else:
                if len(userlist) != 0:
                    username = userlist.pop()
                    usermap[row[0]] = username
                else:
                    extra_data_count[row[0]] = True
                    continue
            # print(f"mapped {row[0]} to username {username}")

            # Insert appropriate data
            action = row[2]
            hours = row[3]
            zero = row[4]
            if action == "purchase":
                cursor.execute('INSERT INTO "OwnsGame" VALUES (%s, %s, null, null)', [game_id, username])
            if action == "play":
                # Since this dataset does not have individual play sessions,
                # we will assume that all playtime happened in the preceding hours
                cursor.execute('INSERT INTO "PlaysGame" VALUES (%s, %s, now()-interval %s hour, now())', [game_id, username, hours])
            # print(row)
        if len(failed_to_match) != 0:
            print("Steam data failed to match games:", len(failed_to_match), "Failed matches!")
        if len(extra_data_count) != 0:
            print("Steam data has extra users:", len(extra_data_count), "Extra users found!")

    # IMDB: for each game in the csv, find the game in the db, and update its ESRB and Genre to match
    print("Importing IMDB data")
    with open('datasets/imdb-videogames.csv', newline='') as csvfile: 
        esrb_map = {}
        failed_to_match = {}
        updated_games = {}
        # Clear Genre information
        cursor.execute('DELETE FROM "Genre"')
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in csvreader:
            # Match to existing game
            game_name = row[1]
            cursor.execute('SELECT gameid FROM "Game" WHERE title=%s', [game_name])
            game_id = cursor.fetchone()
            
            if game_id is None:
                failed_to_match[game_name] = True
                continue
            else:
                game_id = game_id[0]
            if game_id in updated_games:
                continue
            updated_games[game_id] = True
            print(row)
            
            # Update ESRB Rating
            if row[4] in esrb_map:
                esrb_rating = esrb_map[row[4]]
                cursor.execute('UPDATE "Game" SET esrb_rating = %s WHERE gameid=%s', [esrb_rating, game_id])

            # Update Genre
            if row[8] == 'True':
                cursor.execute('INSERT INTO "Genre" VALUES (%s, \'Action\')', [game_id])
            if row[9] == 'True':
                cursor.execute('INSERT INTO "Genre" VALUES (%s, \'Adventure\')', [game_id])
            if row[10] == 'True':
                cursor.execute('INSERT INTO "Genre" VALUES (%s, \'Comedy\')', [game_id])
            if row[11] == 'True':
                cursor.execute('INSERT INTO "Genre" VALUES (%s, \'Crime\')', [game_id])
            if row[12] == 'True':
                cursor.execute('INSERT INTO "Genre" VALUES (%s, \'Family\')', [game_id])
            if row[13] == 'True':
                cursor.execute('INSERT INTO "Genre" VALUES (%s, \'Fantasy\')', [game_id])
            if row[14] == 'True':
                cursor.execute('INSERT INTO "Genre" VALUES (%s, \'Mystery\')', [game_id])
            if row[15] == 'True':
                cursor.execute('INSERT INTO "Genre" VALUES (%s, \'Sci-Fi\')', [game_id])
            if row[16] == 'True':
                cursor.execute('INSERT INTO "Genre" VALUES (%s, \'Thriller\')', [game_id])

        if len(failed_to_match) != 0:
            print("IMDB data failed to match games:", len(failed_to_match), "Failed matches!")

    
    # Gamespot
    # For each row in the csv, insert that review into the db for an existing user
    # if there are no more existing users, move on
    # cursor.execute("")
    # with open('datasets/gamespot.csv', newline='') as csvfile:
    #     spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    #     for row in islice(spamreader,0,4):
    #         print(row)
            

def bolster_users(cursor, count):
    print("Bolstering users...")
    cursor.execute('SELECT * FROM "Player"')
    users = cursor.fetchall()
    print("creating "+str(count-len(users))+" users...")
    
    user_index = {}
    for user in users:
        m = re.match("^(.*?)(\d+)$", user[0])
        if m is None:
            basename = user[0]
            index = 0
        else:
            basename = m.group(1)
            index = int(m.group(2))
        # print("basename", basename, index)
        
        if basename in user_index:
            index_user = user_index[basename]
            if index > index_user[1]:
                user_index[basename] = [basename, index, user]
        else:
            user_index[basename] = [basename, index, user]

    query = 'INSERT INTO "Player" (username, first_name, last_name, creation_date, password, salt, last_online) VALUES (%s, %s, %s, NOW(), %s, %s, NOW())'
    usercount = len(users)
    while usercount < count:
        for index_user in user_index:
            index_user = user_index[index_user]
            index_user[1] += 1
            # user_index[index_user] = (index_user[0], index_user[1]+1, index_user[2])
            new_username = index_user[0]+str(index_user[1])
            # print("Would create: "+new_username)

            # print(index_user[2])
            # print([new_username, index_user[2][1], index_user[2][2], index_user[2][5], index_user[2][6] ])
            cursor.execute(query, [new_username, index_user[2][1], index_user[2][2], index_user[2][5], index_user[2][6] ])
            usercount += 1
            if usercount > count:
                break
        

if __name__ == '__main__':
    main()
