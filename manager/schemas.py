from typing import Optional, Union, List
from enum import Enum

from pydantic import BaseModel, Field

from fastapi import HTTPException


class PostLink(BaseModel):
    link: str = Field(..., description="The link URL")
    tag: Optional[str] = Field(None,
                               description="Tag name to associate with the link (will be created if it doesn't exist)")
    tag_id: Optional[str] = Field(None, description="Tag ID to associate with the link (must already exist)")
    account_id: Optional[str] = Field(
        None,
        description="The account ID. Not required for account scope. Required for admin scope.")


class PostTag(BaseModel):
    tag: str = Field(..., description="Tag name")
    account_id: Optional[str] = Field(
        None,
        description="The account ID. Not required for account scope. Required for admin scope.")


class PostTagLink(BaseModel):
    tag_id: str = Field(..., description="Tag ID (must already exist)")
    link_id: str = Field(..., description="Link ID (must already exist)")
    account_id: Optional[str] = Field(
        None,
        description="The account ID. Not required for account scope. Required for admin scope.")


class PostAccount(BaseModel):
    email: str = Field(..., description="Email Address for the new account")
    password: str = Field(..., description="Password for the new account")


class Token(BaseModel):
    access_token: str
    token_type: str
    expires: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = []
    account_id: Union[str, None] = None


class User(BaseModel):
    user_id: str
    username: str

    class Config:
        orm_mode = True


class EntityType(str, Enum):
    USER = 'user'
    ACCOUNT = 'account'


class AuthEntity(BaseModel):
    entity_type: EntityType
    entity_id: str
    entity_identifier: str
    hashed_password: str

    def get_account_id(self):
        # Get the account id if scope is account, otherwise None
        if self.entity_type == EntityType.ACCOUNT:
            return self.entity_id
        return None

    def assert_account_id(self, required: bool = True, account_id: Optional[str] = None, code: Optional[int] = 422):
        # Check if a provided account_id matches the AuthEntity account id, if scope account
        valid = True
        msg_422 = "Invalid account_id"
        if account_id is not None and self.entity_type == EntityType.ACCOUNT:
            if account_id != self.entity_id:
                msg_422 = "The account_id field should not be provided for account scope"
                valid = False
        # If account_id is required and this is scope user, check we have an account_id
        if self.entity_type == EntityType.USER and required and account_id is None:
            valid = False
            msg_422 = "The account_id field is required for the admin scope"

        if not valid:
            if code == 422:
                raise HTTPException(status_code=422, detail=msg_422)
            elif code == 404:
                raise HTTPException(status_code=404, detail=f"Account with account_id '{account_id}' not found")
            else:
                raise HTTPException(status_code=code, detail="Invalid account_id")

        return account_id if account_id is not None else self.get_account_id()
