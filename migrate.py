from database import cs_database
from backend.player import HASH_ITERATIONS, SALT_LENGTH
from hashlib import pbkdf2_hmac
from secrets import token_bytes

def main():
    """
    Migrates the passwords in the database from the password column
    to a hashed_password column, and adds a salt value to a salt column
    """
    # try to get each player, calculate a hash for them, save the hashes
    with cs_database() as db:
        cur = db.cursor()
        # Get the player data
        query = 'SELECT username, password FROM "Player" WHERE hashed_password is NULL'
        cur.execute(query)
        
        inner_cur = db.cursor()
        for (username, password) in cur.fetchall():
            salt = token_bytes(SALT_LENGTH)
            hashed = pbkdf2_hmac('sha256', password.encode('utf-8'), salt, HASH_ITERATIONS)
            
            query = 'UPDATE "Player" SET hashed_password=%s, salt=%s WHERE username=%s'
            cur.execute(query, (hashed, salt, username))
            db.commit()
            print("Migrated " + username)

if __name__ == "__main__":
    main()
