import os
from database import admin_collection
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, Field
from typing import Annotated, Optional

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "7"))

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


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



password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)


async def get_admin(username: str):
    admin_dict = await admin_collection.find_one({"username": username})
    if admin_dict:
        admin_dict["_id"] = str(admin_dict["_id"])
        return AdminInDB(**admin_dict)
    return None

async def authenticate_admin(username: str, password: str):
    admin = await get_admin(username)
    if not admin:
        return False
    if not verify_password(password, admin.hashed_password):
        return False
    return admin


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_admin(token: Annotated[str, Depends(oauth2_scheme)]):
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
    admin = await get_admin(username=username)
    if admin is None:
        raise credentials_exception
    return admin


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    admin = await authenticate_admin(form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.put("/admins/me/password")
async def change_own_password(
    password_data: PasswordChange,
    current_admin: Annotated[AdminInDB, Depends(get_current_admin)]
):
    if not verify_password(password_data.current_password, current_admin.hashed_password):
        raise HTTPException(status_code=400, detail="wrong password")

    new_hashed = get_password_hash(password_data.new_password)

    try: await admin_collection.update_one(
        {"username": current_admin.username},
        {"$set": {
            "hashed_password": new_hashed,
            "updated_at": datetime.utcnow()
        }}
    )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server error")

    return {"message": "Admin updated successfully"}

@app.get("/admins/me/", response_model=Admin)
async def read_users_me(
    current_admin: Annotated[Admin, Depends(get_current_admin)],
):
    return current_admin
