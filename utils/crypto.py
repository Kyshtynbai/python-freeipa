import random
import string
import secrets

def generate_password(chars):
    password = ''
    special = '!@#$%^&*'
    alphabet = string.digits + string.ascii_letters + special
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(chars))
        if (any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3):
            break
    shift = random.randrange(1,23)
    password = password[:shift] + secrets.choice(special) + password[shift:]
    return password
