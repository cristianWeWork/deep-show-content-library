from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Date, ForeignKey, create_engine, Sequence
from sqlalchemy import String, Integer, Float, Boolean, Column
from sqlalchemy.orm import sessionmaker,relationship


Base = declarative_base()


class users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(500))
    email = Column(String(500))
    password = Column(String(500))
    name = Column(String(500))
    surname = Column(String(500))
    subscription = Column(Integer)
    created_at = Column(Date)
    
    def __init__(self, username, email, password, name, surname, subscription, created_at):
        self.username = username
        self.email = email
        self.password = password
        self.name = name
        self.surname = surname
        self.subscription = subscription
        self.created_at = created_at


class shows(Base):
    __tablename__ = 'shows'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)


class themes(Base):
    __tablename__ = 'themes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    preview = Column(String)
    music_url = Column(String)
    themes = relationship(
        "graphics", back_populates="themes"
    )
    def _init__(self, name, preview, music_url):
        self.name = name
        self.preview = preview
        self.music_url = music_url


class graphics(Base):
    __tablename__ = "graphics"
    id = Column(Integer, primary_key=True, index=True)
    theme_id = Column(Integer, ForeignKey("themes.id"))
    type = Column(String)
    url = Column(String)
    themes = relationship("themes", back_populates="graphics")
    
    def __init__(self, theme_id,url,type ):
        self.theme_id =theme_id
        self.url = url
        self.type = type