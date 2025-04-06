from sqlalchemy import Column, Integer, String, create_engine, Time
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from dotenv import load_dotenv
import os

path = ".env"
load_dotenv(dotenv_path=path)

engine_url = os.getenv("DATABASE_URL")
engine = create_engine(url=engine_url, echo=True)

Base = declarative_base()

class SeedTable(Base):
    __tablename__ = "week_shifts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    day_no = Column(Integer, unique=True, nullable=False)
    day = Column(Time, nullable=False)
    start_shift = Column(Time, nullable=False)
    end_shift = Column(Time, nullable=False)
    start_break = Column(Time, nullable=False)
    end_break = Column(Time, nullable=False)