from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Date, ForeignKey, create_engine, Sequence
from sqlalchemy import String, Integer, Float, Boolean, Column
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class users(Base):
    __tablename__= 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(500))
    email = Column(String(500))
    password = Column(String(500))
    name = Column(String(500))
    surname = Column(String(500))
    subscription = Column(Integer)
    created_at = Column(Date)
    
    def __init__(self, username,email,password,name,surname,subscription,created_at):
        self.username = username
        self.email = email
        self.password = password
        self.name = name
        self.surname = surname
        self.subscription = subscription
        self.created_at = created_at
        

class shows(Base):
    __tablename__='shows'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False )
    
