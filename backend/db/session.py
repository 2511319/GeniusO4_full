from sqlmodel import SQLModel, create_engine, Session
import os

# Для локальной разработки используем SQLite в памяти
# В продакшене будет использоваться Firestore для подписок
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
