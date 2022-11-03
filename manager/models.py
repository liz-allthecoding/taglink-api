from sqlalchemy import Column, ForeignKey, String, UniqueConstraint

from manager.database import Base


class Link(Base):
    __tablename__ = "link"

    link_id = Column(String, primary_key=True, index=True)
    account_id = Column(String, ForeignKey("account.account_id"), index=True)
    link = Column(String)


class Tag(Base):
    __tablename__ = "tag"

    tag_id = Column(String, primary_key=True, index=True)
    account_id = Column(String, ForeignKey("account.account_id"), index=True)
    tag = Column(String)


class TagLink(Base):
    __tablename__ = "taglink"

    tag_id = Column(String, ForeignKey("tag.tag_id"), primary_key=True, index=True)
    link_id = Column(String, ForeignKey("link.link_id"), primary_key=True, index=True)
    account_id = Column(String, ForeignKey("account.account_id"), index=True)


class User(Base):
    __tablename__ = "user"

    user_id = Column(String, primary_key=True, index=True)
    username = Column(String)
    hashed_password = Column(String)


class Account(Base):
    __tablename__ = "account"

    account_id = Column(String, primary_key=True, index=True)
    email = Column(String)
    hashed_password = Column(String)
    created = Column(String)


