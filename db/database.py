from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from decouple import config

mysql_user = config("MYSQL_USER")
mysql_password = config("MYSQL_PASSWORD")
mysql_host = config("MYSQL_HOST")
mysql_port = config("MYSQL_PORT")
mysql_db = config("MYSQL_DB")

mysql_url = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"

engine = create_engine(mysql_url, echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def create_db_and_tables():
    Base.metadata.create_all(engine)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()



    
    

