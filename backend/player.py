from typing import Optional
import datetime
from typing import List
from database import cs_database
import psycopg2


class Player:
    """Class for keeping important details of a user"""
    username: str
    first_name: str
    last_name: str
    creation_date: datetime.date
    password: str

    def __init__(self, username: str, first_name: str, last_name: str, creation_date: datetime.date, password: str):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.creation_date = creation_date
        self.password = password

    def __repr__(self):
        return "Player (%s, %s, %s, %s, %s)" % (self.username, self.first_name, self.last_name, self.creation_date, self.password)

    def get_platforms_owned(self):
        raise NotImplementedError

    def get_emails(self) -> List[str]:
        with cs_database() as db:
            cur = db.cursor()
            query = 'select email from "Emails" where username = %s'
            cur.execute(query, [self.username])
            res = list(map(lambda t: t[0], cur.fetchall()))

            return res


def get_player(username: str) -> Optional[Player]:
    try:
        with cs_database() as db:
            cursor = db.cursor()
            query = 'select first_name, last_name, creation_date, password from "Player" where username=%s'
            cursor.execute(query, [username])
            result = cursor.fetchone()

            # no username found
            if result == None:
                return None

            return Player(username, result[0], result[1], result[2], result[3])
    except Exception as e:
        print(e)
        # No such user found (or database down)
        return None


def follow_player(follower: str, followed: str):
    query = 'insert into "Friends" (username, friend) VALUES (%s, %s)'
    try:
        with cs_database() as db:
            cursor = db.cursor()
            cursor.execute(query, [follower, followed])
            db.commit()

    except Exception as e:
        print("follow player err", e)
        raise e


def unfollow_player(follower: str, followed: str):
    query = 'delete from "Friends" where username = %s and friend = %s'
    try:
        with cs_database() as db:
            cursor = db.cursor()
            cursor.execute(query, [follower, followed])
            db.commit()

    except Exception as e:
        print("unfollow player err", e)
        raise e


def player_follows_player(follower: str, followed: str) -> bool:
    query = 'select * from "Friends" F where F.username = %s and F.friend  = %s'
    try:
        with cs_database() as db:
            cursor = db.cursor()
            cursor.execute(query, [follower, followed])
            res = cursor.fetchone()
            if res == None:
                return False
            else:
                return True

    except Exception as e:
        print("player follows player err", e)
        raise e


class DuplicateNameException(Exception):
    def __init__(self):
        pass


def change_names(username: str, firstname: str, lastname: str):
    query = 'update "Player" set first_name = %s, last_name = %s where username = %s'
    with cs_database() as db:
        cur = db.cursor()
        cur.execute(query, (firstname, lastname, username))
        db.commit()


def search_player_by_email(email: str, username: str) -> List[str]:
    query = 'select DISTINCT P.username from "Player" P natural join "Emails" E where P.username = E.username and UPPER(E.email) like upper(%s) and E.username != %s'
    with cs_database() as db:
        try:
            cur = db.cursor()
            cur.execute(query, ['%'+email+'%', username])
            res = cur.fetchall()
            return [val[0] for val in res]

        except Exception as e:
            print("email lookup failed", e)
            raise e


def add_player(username: str, first_name: str, last_name: str, password: str, emails: List[str]):

    query = 'insert into "Player" (username, first_name, last_name, creation_date, password) values (%s, %s, %s, NOW(), %s)'
    email_query = 'insert into "Emails" (username, email) values (%s, %s)'

    with cs_database() as db:
        try:
            cur = db.cursor()
            cur.execute(query, [username, first_name, last_name, password])
            for email in emails:
                cur.execute(email_query, [username, email])

            db.commit()
        except psycopg2.errors.UniqueViolation:
            raise DuplicateNameException

        # loop through emails, adding them
