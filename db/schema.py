from sqlalchemy import (
    Column, ForeignKey, Integer,
    String, MetaData, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import pg_conf

engine = create_engine(pg_conf.SQLALCHEMY_DATABASE_URI)
meta = MetaData()
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class UserRequest(Base):
    __tablename__ = 'user_requests'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    user = relationship("User", back_populates="user_requests")


def fill_db():
    User.user_requests = relationship("UserRequest", order_by=UserRequest.id, back_populates="user")
    Base.metadata.create_all(engine)

    ex = User(name='Dimary')
    ex.user_requests = [UserRequest(name='Ex1'), UserRequest(name='Ex2')]

    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(ex)
    session.commit()
