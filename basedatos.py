from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

URL_BASE_DE_DATOS = "postgresql+psycopg://postgres:estacion934@localhost:5432/inadaptados"

motor = create_engine(URL_BASE_DE_DATOS)
Sesion = sessionmaker(bind=motor)

class Base(DeclarativeBase):
    pass

