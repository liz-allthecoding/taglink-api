from typing import Optional
from datetime import datetime

from uuid import uuid4

from sqlalchemy.orm import Session

from fastapi import HTTPException

from manager import models, schemas, authentication


def get_link(db: Session, link_id: str, account_id: Optional[str] = None):
    filters = [models.Link.link_id == link_id]
    if account_id is not None:
        filters.append(models.Link.account_id == account_id)
    return db.query(models.Link).filter(*filters).first()


def get_tag(db: Session, tag_id: str, account_id: Optional[str] = None):
    filters = [models.Tag.tag_id == tag_id]
    if account_id is not None:
        filters.append(models.Tag.account_id == account_id)
    return db.query(models.Tag).filter(*filters).first()


def get_tag_by_tag_name(db: Session, tag: str, account_id: Optional[str]):
    filters = [models.Tag.tag == tag]
    if account_id is not None:
        filters.append(models.Tag.account_id == account_id)
    return db.query(models.Tag).filter(*filters).first()


def get_links(db: Session, tag_id: Optional[str] = None, tag: Optional[str] = None, account_id: Optional[str] = None):
    filters = []
    filter_tags = []
    if tag is None and tag_id is None and account_id is None:
        # TODO: Implement offset and limit
        return db.query(models.Link).all()
    if tag is not None:
        # tag_record = get_tag_by_tag_name(db, tag, account_id)
        tag_records = get_tags(db, tag, account_id)
        if len(tag_records) == 0:
            return []
        for tag_record in tag_records:
            filter_tags.append(tag_record.tag_id)
    if account_id is not None:
        filters.append(models.Link.account_id == account_id)
    if tag_id is not None:
        filter_tags.append(tag_id)
    if len(filter_tags) > 0:
        filters.append(models.TagLink.tag_id.in_(filter_tags))
        return db.query(models.Link).join(models.TagLink).filter(*filters).all()

    return db.query(models.Link).filter(*filters).all()


def get_tags(db: Session, tag: Optional[str] = None, account_id: Optional[str] = None):
    filters = []
    if tag is None and account_id is None:
        # TODO: Implement offset and limit
        return db.query(models.Tag).all()
    if tag is not None:
        filters.append(models.Tag.tag == tag)
    if account_id is not None:
        filters.append(models.Tag.account_id == account_id)
    return db.query(models.Tag).filter(*filters).all()


def get_taglinks(db: Session, tag_id: Optional[str] = None, link_id: Optional[str] = None,
                 account_id: Optional[str] = None):
    filters = []
    if tag_id is None and link_id is None and account_id is None:
        # TODO: Implement offset and limit
        return db.query(models.TagLink).all()
    if tag_id is not None:
        filters.append(models.TagLink.tag_id == tag_id)
    if link_id is not None:
        filters.append(models.TagLink.link_id == link_id)
    if account_id is not None:
        filters.append(models.TagLink.account_id == account_id)

    return db.query(models.TagLink).filter(*filters).all()


def get_accounts(db: Session, email: Optional[str] = None, account_id: Optional[str] = None):
    filters = []
    if email is None and account_id is None:
        # TODO: Implement offset and limit
        return db.query(models.Account).all()
    if email is not None:
        filters.append(models.Account.email == email)
    if account_id is not None:
        filters.append(models.Account.account_id == account_id)
    return db.query(models.Account).filter(*filters).all()


def get_account(db: Session, account_id: str):
    filters = [models.Account.account_id == account_id]
    return db.query(models.Account).filter(*filters).first()


def create_link(db: Session, link: schemas.PostLink):
    db_link = models.Link(link_id=str(uuid4()), link=link.link, account_id=link.account_id)
    db.add(db_link)
    tag_id = link.tag_id
    link_id = db_link.link_id

    if link.tag is not None:
        db_tag = get_tag_by_tag_name(db, link.tag, link.account_id)
        if db_tag is None:
            db_tag = models.Tag(tag_id=str(uuid4()), tag=link.tag, account_id=link.account_id)
            db.add(db_tag)
            tag_id = db_tag.tag_id
        else:
            tag_id = db_tag.tag_id
    elif tag_id is not None:
        db_tag = get_tag(db, tag_id, link.account_id)
        if db_tag is None:
            raise HTTPException(status_code=404,
                                detail=f"Tag with tag_id {tag_id} not found for account_id {link.account_id}")

    db_taglink = models.TagLink(link_id=link_id, tag_id=tag_id, account_id=link.account_id)
    db.add(db_taglink)

    db.commit()
    db.refresh(db_link)
    return db_link


def create_tag(db: Session, tag: schemas.PostTag):
    db_tag = models.Tag(tag_id=str(uuid4()), tag=tag.tag, account_id=tag.account_id)
    db_tag_existing = get_tags(db, tag=tag.tag, account_id=tag.account_id)
    if len(db_tag_existing) > 0:
        raise HTTPException(status_code=409, detail=f"Tag with name {tag.tag} exists for account {tag.account_id}")
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def create_taglink(db: Session, taglink: schemas.PostTagLink):
    tag_id = taglink.tag_id
    link_id = taglink.link_id
    account_id = taglink.account_id
    db_taglink = models.TagLink(tag_id=tag_id, link_id=link_id, account_id=account_id)
    db_tag_id_existing = get_tag(db, tag_id, account_id)
    if db_tag_id_existing is None:
        raise HTTPException(status_code=422, detail=f"Tag with tag_id {tag_id} not found for account_id {account_id}")
    db_link_id_existing = get_link(db, link_id, account_id)
    if db_link_id_existing is None:
        raise HTTPException(status_code=422, detail=f"Link with link_id {link_id} not found for account_id {account_id}")
    db_taglink_existing = get_taglinks(db, tag_id=tag_id, link_id=link_id, account_id=account_id)
    if len(db_taglink_existing) > 0:
        raise HTTPException(status_code=409, detail=f"TagLink with tag_id {tag_id} and link_id {link_id} exists")
    db.add(db_taglink)
    db.commit()
    db.refresh(db_taglink)
    return db_taglink


def delete_link(db: Session, link_id: str, account_id: Optional[str] = None):
    db_link = get_link(db, link_id=link_id, account_id=account_id)
    if not db_link:
        raise HTTPException(status_code=404, detail=f"Link with link_id {link_id} not found")
    delete_taglinks(db, link_id=link_id)
    db.delete(db_link)
    db.commit()
    return "OK"


def delete_tag(db: Session, tag_id: str, account_id: Optional[str] = None):
    db_tag = get_tag(db, tag_id=tag_id, account_id=account_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail=f"Tag with tag_id {tag_id} not found")
    delete_taglinks(db, tag_id=tag_id)
    db.delete(db_tag)
    db.commit()
    return "OK"


def delete_taglinks(db: Session, tag_id: Optional[str] = None, link_id: Optional[str] = None,
                    account_id: Optional[str] = None):
    db_taglinks = get_taglinks(db, tag_id=tag_id, link_id=link_id, account_id=account_id)
    for db_taglink in db_taglinks:
        db.delete(db_taglink)
    db.commit()
    return "OK"


def get_account_from_email(db: Session, email: str):
    return db.query(models.Account).filter(models.Account.email == email).first()


def create_account(db: Session, account: schemas.PostAccount):
    hashed_password = authentication.get_password_hash(account.password)
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    db_account = models.Account(account_id=str(uuid4()), email=account.email, hashed_password=hashed_password,
                                created=now)
    db_account_existing = get_account_from_email(db, email=account.email)
    if db_account_existing is not None:
        raise HTTPException(status_code=409, detail=f"Account with email {account.email} exists")
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def delete_account(db: Session, account_id: str):
    db_account = get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail=f"Account id {account_id} not found")
    delete_taglinks(db, account_id=account_id)
    tags = get_tags(db, account_id=account_id)
    for db_tag in tags:
        db.delete(db_tag)
        db.commit()
    links = get_links(db, account_id=account_id)
    for db_link in links:
        print(db_link)
        db.delete(db_link)
        db.commit()
    db.delete(db_account)
    db.commit()
    return "OK"
