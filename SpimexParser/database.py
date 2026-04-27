import os

import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base

dotenv.load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)


def create_tables():
    Base.metadata.create_all(engine)
