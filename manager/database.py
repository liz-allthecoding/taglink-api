from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from manager import CONFIG

database_config = CONFIG['database']
username = database_config['username']
password = database_config['password']
host = database_config['host']
name = database_config['name']
port = database_config['port']

SQLALCHEMY_DATABASE_URL = f"mariadb+mariadbconnector://{username}:{password}@{host}:{port}/{name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recyle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
    finally:
        db.close()
