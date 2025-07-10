import bcrypt


#hasing the password using bcrypt
#salt is added to randomise and prevent the same password having the same hashing

def hash_pasword(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'),salt)
    return hashed.decode('utf-8')

# Verify a password on login
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
