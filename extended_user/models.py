from sqlalchemy import MetaData, create_engine, Column, Integer,Boolean,String
from sqlalchemy.ext.declarative import declarative_base
Base= declarative_base(metadata=MetaData())
class extended_user(Base):
    __tablename__ = 'extended_user'
    id=Column(Integer,primary_key=True)
    role=Column(String)

class practice(Base):
    __tablename__ = 'practice'
    id=Column(Integer,primary_key=True)
    name = Column(String)

DB_URL = "postgresql://postgres:Anjul123@localhost:5432/lightbulb"
engine = create_engine(DB_URL)
Base.metadata.create_all(engine)