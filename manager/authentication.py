from datetime import datetime, timedelta
from typing import Union, Optional, List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext

from sqlalchemy.orm import Session

from manager import CONFIG, schemas, models
from manager.database import get_db
from manager.schemas import EntityType, AuthEntity


AUTH_CONFIG = CONFIG['authentication']

SECRET_KEY = AUTH_CONFIG['secret_key']
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SCOPE_ACCOUNT = 'account'
SCOPE_ADMIN = 'admin'
SCOPES = {SCOPE_ACCOUNT: 'API actions for a specific account', SCOPE_ADMIN: 'All API actions'}


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes=SCOPES)

app = FastAPI()


class AuthenticationException(Exception):
    def __init__(self, msg: str, *args):
        super().__init__(self, msg, *args)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_account(db: Session, email: Optional[str] = None, account_id: Optional[str] = None):
    if email is not None:
        return db.query(models.Account).filter(models.Account.email == email).first()
    elif account_id is not None:
        return db.query(models.Account).filter(models.Account.account_id == account_id).first()
    return None


def get_auth_entity(db: Session, identifier: str, security_scopes: List[str], entity_id: Optional[str] = None):
    auth_entity = None
    if SCOPE_ADMIN in security_scopes:
        user = get_user(db, identifier)
        if user:
            auth_entity = AuthEntity(entity_type=EntityType.USER, entity_id=user.user_id, entity_identifier=identifier,
                                     hashed_password=user.hashed_password)
    elif SCOPE_ACCOUNT in security_scopes:
        account = get_account(db, email=identifier, account_id=entity_id)
        if account:
            auth_entity = AuthEntity(entity_type=EntityType.ACCOUNT, entity_id=account.account_id,
                                     entity_identifier=identifier, hashed_password=account.hashed_password)

    if not auth_entity:
        scopes = ", ".join(security_scopes)
        msg = f"Cannot get AuthEntity for scopes {scopes} with identifier {identifier}"
        raise AuthenticationException(msg)
    return auth_entity


def authenticate(db: Session, identifier: str, password: str, security_scopes: List[str]):
    # Only one scope should be set
    if len(security_scopes) != 1:
        print("Too many security scopes set")
        return False
    try:
        auth_entity = get_auth_entity(db, identifier=identifier, security_scopes=security_scopes)
    except AuthenticationException as ex:
        print('Caught AuthenticationException' + str(ex))
        return False
    if not auth_entity:
        print("No auth_entity found")
        return False
    if not verify_password(password, auth_entity.hashed_password):
        print("Password not verified")
        return False
    return auth_entity


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_auth_entity(security_scopes: SecurityScopes, db: Session = Depends(get_db),
                                  token: str = Depends(oauth2_scheme)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f'Bearer'
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        account_id = payload.get("account_id", None)
        token_data = schemas.TokenData(username=username, scopes=token_scopes, account_id=account_id)
    except JWTError:
        raise credentials_exception
    # Only one scope should be set
    if len(token_scopes) != 1:
        raise credentials_exception

    try:
        auth_entity = get_auth_entity(db, identifier=token_data.username, security_scopes=token_data.scopes,
                                      entity_id=token_data.account_id)
    except RuntimeError:
        raise credentials_exception

    if auth_entity is None:
        raise credentials_exception
    print(security_scopes.scopes)
    print(token_data.scopes)
    token_scope = token_scopes[0]
    if token_scope not in security_scopes.scopes:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )
    return auth_entity


async def get_current_active_auth_entity(current_auth_entity: schemas.AuthEntity = Depends(get_current_auth_entity)):
    return current_auth_entity
