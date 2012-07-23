from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    ForeignKey,
    Table,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

import tw2.sqla as tws

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
# We need this for tws
Base.query = DBSession.query_property()


user_role = Table('user_role', 
                  Base.metadata,
                  Column('iduser', Integer, ForeignKey('user.iduser')),
                  Column('idrole', Integer, ForeignKey('role.idrole')),
            )

user_group = Table('user_group', 
                  Base.metadata,
                  Column('iduser', Integer, ForeignKey('user.iduser')),
                  Column('idgroup', Integer, ForeignKey('groups.idgroup')),
            )

class Group(Base):
    __tablename__ = 'groups'

    idgroup = Column(
                Integer, 
                nullable=False, 
                autoincrement=True, 
                primary_key=True)
    name = Column(String(255), nullable=False)

class Role(Base):
    __tablename__ = 'role'

    idrole = Column(
                Integer, 
                nullable=False, 
                autoincrement=True, 
                primary_key=True)
    name = Column(String(255), nullable=False)

class User(Base):
    __tablename__ = 'user'

    iduser = Column(
                Integer, 
                nullable=False, 
                autoincrement=True, 
                primary_key=True)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)

    roles = relationship(
                'Role',
                secondary=user_role,
                backref='users')
    groups = relationship(
                'Group',
                secondary=user_group,
                backref='users')


class Page(Base):
    __tablename__ = 'page'

    idpage = Column(Integer, 
                    nullable=False,
                    autoincrement=True,
                    primary_key=True)
    parent_id = Column(Integer,
                       ForeignKey('page.idpage'),
                       nullable=True,
                       default=None)
    page_type = Column(String(128), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    parent = relationship('Page', 
                          primaryjoin="Page.idpage==Page.parent_id", 
                          remote_side=[idpage], 
                          backref = 'children')

    __mapper_args__ = ({'polymorphic_on': page_type, 'polymorphic_identity': 'page'})

    _pk_name = 'idpage'

    def __unicode__(self):
        return self.name

    @property
    def id(self):
        # Need for tws
        return self.idpage

    @classmethod
    def getAdminForm(cls):
        return type('%sAutoTableForm' % cls.__name__, 
                    (tws.AutoTableForm,),
                    {'entity': cls})

