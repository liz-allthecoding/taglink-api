#!/home/osboxes/.venv-fastapi/bin/python

import os

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = os.environ.get('PASSWORD')


def get_password_hash(password):
    return pwd_context.hash(password)


if __name__ == "__main__":

    hashed_password = get_password_hash(password)
    print(hashed_password)
