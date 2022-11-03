from typing import Optional
from datetime import timedelta, datetime

from sqlalchemy.orm import Session

from fastapi import FastAPI, HTTPException, Depends, status, Security

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes

from fastapi.middleware.cors import CORSMiddleware

from manager import manager, schemas, authentication, CONFIG

from manager.database import get_db

from manager.authentication import SCOPE_ACCOUNT

from manager.schemas import EntityType


app = FastAPI()

origins = [origin for origin in CONFIG['origins']]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Get link by link_id
@app.get("/link/{link_id}")
async def get_link(link_id: str, db: Session = Depends(get_db),
                   current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                      scopes=["admin", "account"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    # If account scope, additionally filter by account_id
    db_link = manager.get_link(db, link_id, account_id=current_auth_entity.get_account_id())
    if db_link is None:
        raise HTTPException(status_code=404, detail=f"Link with link_id {link_id} not found")
    return db_link


# Get links by query params
@app.get("/link/")
async def get_links(tag_id: Optional[str] = None, tag: Optional[str] = None, account_id: Optional[str] = None,
                    db: Session = Depends(get_db),
                    current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                       scopes=["admin", "account"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    filter_account_id = current_auth_entity.assert_account_id(required=False, account_id=account_id)
    return manager.get_links(db, tag_id, tag, account_id=filter_account_id)


# Get tag by tag_id
@app.get("/tag/{tag_id}")
async def get_tag(tag_id: str, db: Session = Depends(get_db),
                  current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                     scopes=["admin", "account"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    db_tag = manager.get_tag(db, tag_id, account_id=current_auth_entity.get_account_id())
    if db_tag is None:
        raise HTTPException(status_code=404, detail=f"Tag with tag_id {tag_id} not found")
    return db_tag


# Get tags by query params
@app.get("/tag/")
async def get_tags(tag: Optional[str] = None, account_id: Optional[str] = None, db: Session = Depends(get_db),
                   current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                      scopes=["admin", "account"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    filter_account_id = current_auth_entity.assert_account_id(required=False, account_id=account_id)
    return manager.get_tags(db, tag, account_id=filter_account_id)


# Get taglinks by query params
@app.get("/taglink/")
async def get_taglinks(link_id: Optional[str] = None, tag_id: Optional[str] = None, account_id: Optional[str] = None,
                       db: Session = Depends(get_db),
                       current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                          scopes=["admin", "account"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    filter_account_id = current_auth_entity.assert_account_id(required=False, account_id=account_id)
    return manager.get_taglinks(db, tag_id, link_id, account_id=filter_account_id)


# Post a link
@app.post("/link/")
async def post_link(link: schemas.PostLink, db: Session = Depends(get_db),
                    current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                       scopes=["admin", "account"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    current_auth_entity.assert_account_id(required=True, account_id=link.account_id)
    if current_auth_entity.entity_type == EntityType.ACCOUNT:
        link.account_id = current_auth_entity.get_account_id()

    if link.tag is None and link.tag_id is None:
        raise HTTPException(status_code=422, detail="One of tag_id or tag must be specified")

    if link.tag is not None and link.tag_id is not None:
        raise HTTPException(status_code=422, detail="Only one of tag_id or tag must be specified")

    db_link = manager.create_link(db, link)

    return db_link


# Post a tag
@app.post("/tag/")
async def post_tag(tag: schemas.PostTag, db: Session = Depends(get_db),
                   current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                      scopes=["admin", "account"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    current_auth_entity.assert_account_id(required=True, account_id=tag.account_id)
    if current_auth_entity.entity_type == EntityType.ACCOUNT:
        tag.account_id = current_auth_entity.get_account_id()
    db_tag = manager.create_tag(db, tag)

    return db_tag


# Post a taglink
@app.post("/taglink/")
async def post_taglink(taglink: schemas.PostTagLink, db: Session = Depends(get_db),
                       current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                          scopes=["admin", "account"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    current_auth_entity.assert_account_id(required=True, account_id=taglink.account_id)
    if current_auth_entity.entity_type == EntityType.ACCOUNT:
        taglink.account_id = current_auth_entity.get_account_id()
    db_tag = manager.create_taglink(db, taglink)

    return db_tag


# Delete link by link_id
@app.delete("/link/{link_id}")
async def delete_link(link_id: str, db: Session = Depends(get_db),
                      current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                         scopes=["admin", "account"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    return manager.delete_link(db, link_id, account_id=current_auth_entity.get_account_id())


# Delete tag by tag_id
@app.delete("/tag/{tag_id}")
async def delete_tag(tag_id: str, db: Session = Depends(get_db),
                     current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                        scopes=["admin", "account"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    return manager.delete_tag(db, tag_id, account_id=current_auth_entity.get_account_id())


# Delete taglinks by query params
@app.delete("/taglink/")
async def delete_taglinks(link_id: Optional[str] = None, tag_id: Optional[str] = None,  db: Session = Depends(get_db),
                          current_auth_entity: schemas.AuthEntity = Security(
                              authentication.get_current_active_auth_entity, scopes=["admin", "account"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    if link_id is None and tag_id is None:
        raise HTTPException(status_code=422, detail="One or both of tag_id and link_id must be specified")
    return manager.delete_taglinks(db, tag_id, link_id, account_id=current_auth_entity.get_account_id())


@app.post("/token/", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    auth_entity = authentication.authenticate(db, form_data.username, form_data.password, form_data.scopes)
    if not auth_entity:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password or invalid scopes",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": auth_entity.entity_identifier, "scopes": form_data.scopes, "account_id": None}
    if SCOPE_ACCOUNT in form_data.scopes:
        token_data['account_id'] = auth_entity.entity_id

    access_token = authentication.create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    expires = datetime.utcnow() + access_token_expires
    return {"access_token": access_token, "token_type": "bearer", "expires": expires.isoformat()}


# Create a new account
@app.post("/account/")
async def post_account(account: schemas.PostAccount, db: Session = Depends(get_db),
                       current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                          scopes=["admin"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    db_account = manager.create_account(db, account)

    return db_account


# Get accounts by query params
@app.get("/account/")
async def get_accounts(email: Optional[str] = None, db: Session = Depends(get_db),
                       current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                          scopes=["admin", "account"])):
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    # Allow account scope to retrieve own account only. Return empty list if email and account_id do not match.
    return manager.get_accounts(db, email, account_id=current_auth_entity.get_account_id())


# Get account by account_id
@app.get("/account/{account_id}")
async def get_account(account_id: str, db: Session = Depends(get_db),
                      current_auth_entity: schemas.AuthEntity = Security(authentication.get_current_active_auth_entity,
                                                                         scopes=["admin", "account"])):
    # Allow account scope to get own account only
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    current_auth_entity.assert_account_id(required=True, account_id=account_id, code=404)
    db_account = manager.get_account(db, account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail=f"Account with account_id '{account_id}' not found")
    return db_account


# Delete account by account_id
@app.delete("/account/{account_id}")
async def delete_account(account_id: str, db: Session = Depends(get_db),
                         current_auth_entity: schemas.AuthEntity = Security(
                             authentication.get_current_active_auth_entity, scopes=["admin", "account"])):
    # Allow account scope to delete own account only. Return 404 for other accounts.
    print(f"authenticated as {current_auth_entity.entity_identifier}")
    current_auth_entity.assert_account_id(required=True, account_id=account_id, code=404)
    return manager.delete_account(db, account_id)

