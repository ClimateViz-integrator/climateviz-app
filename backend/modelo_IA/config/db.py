from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv('.env')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

#DB_URL = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}' # Mysql

DB_URL = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}' # Postgres

Base = declarative_base()


engine = create_engine(DB_URL, echo=False, future=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()  # En caso de error, hacer rollback
        print(f"Error en la sesión de la base de datos: {e}")
        raise
    finally:
        db.close()

        