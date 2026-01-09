import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv
from pwdlib import PasswordHash
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from database import admin_collection

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "7"))

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
password_hash = PasswordHash.recommended()


class Token(BaseModel):
    access_token: str
    token_type: str


class Admin(BaseModel):
    id: str = Field(alias="_id")
    admin_id: int
    username: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime
    photo: Optional[str] = None
    description: Optional[str] = None
    contact: str

    class Config:
        populate_by_name = True


class AdminInDB(Admin):
    hashed_password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


async def get_admin(username: str) -> Optional[AdminInDB]:
    admin_dict = await admin_collection.find_one({"username": username})
    if not admin_dict:
        return None
    admin_dict["_id"] = str(admin_dict["_id"])
    return AdminInDB(**admin_dict)


async def authenticate_admin(username: str, password: str):
    admin = await get_admin(username)
    if not admin:
        return False
    if not verify_password(password, admin.hashed_password):
        return False
    return admin


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_admin(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> AdminInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    admin = await get_admin(username)
    if admin is None:
        raise credentials_exception
    return admin


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    admin = await authenticate_admin(form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": admin.username},
        expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/admins/me/", response_model=Admin)
async def read_admin_me(
    current_admin: Annotated[Admin, Depends(get_current_admin)],
):
    return current_admin


@router.put("/admins/me/password")
async def change_own_password(
    password_data: PasswordChange,
    current_admin: Annotated[AdminInDB, Depends(get_current_admin)],
):
    if not verify_password(
        password_data.current_password,
        current_admin.hashed_password,
    ):
        raise HTTPException(status_code=400, detail="wrong password")

    new_hashed = get_password_hash(password_data.new_password)

    await admin_collection.update_one(
        {"username": current_admin.username},
        {
            "$set": {
                "hashed_password": new_hashed,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    return {"message": "Admin updated successfully"}
