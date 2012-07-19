from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


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

    def __unicode__(self):
        return self.name
