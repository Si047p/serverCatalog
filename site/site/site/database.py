from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

db_loc = "postgres://catalog:password@localhost/catalog"
engine = create_engine(db_loc)

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'picture': self.picture,
            'email': self.email,
        }


class Recipe(Base):
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    instructions = Column(String(500), nullable=False)
    type = Column(String(10), nullable=False)
    picture = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'instructions': self.instructions,
            'id': self.id,
            'type': self.type,
            'user_id': self.user_id,
        }


engine = create_engine(db_loc)


Base.metadata.create_all(engine)
