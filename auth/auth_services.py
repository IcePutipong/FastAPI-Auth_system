import os, jwt, datetime
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

import auth.auth_models as auth_models, auth.auth_schemas as auth_schemas

from db import db_models
from db.db_models import User
from db.database import Base, engine, SessionLocal, get_session

from auth.auth_utils import create_access_token, create_refresh_token, verify_password, get_hashed_password, token_required
from .auth_bearer import JWTBearer
from .auth_models import RefreshToken

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
ALGORITHM = os.getenv("ALGORITHM")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")

def generate_emp_id(session: Session) -> str:
    emp_count = session.query(db_models.User).count()
    return f"2024000{emp_count +1:03d}"

#### wait for conflict the dtabase "email". && Add error when user doesn't input email or password.
def register_user(user: auth_schemas.UserCreate, session: Session = Depends(get_session)):

    if not user.email or not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email and Password cannot be Null.")

    existing_email = session.query(db_models.Email).filter_by(email=user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.")
    emp_id = generate_emp_id(session)

    encrypted_password = get_hashed_password(user.password)

    new_user = db_models.User(
        employment_id = emp_id,
        username=user.username, 
        password=encrypted_password)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    primary_email = db_models.Email(email=user.email, employment_id =new_user.id)
    session.add(primary_email)
    session.commit()

    return {"message": "User created successfully."}

#### wait for add can used multi email that in user database to login. && Add error when user doesn't input email or password.
def login_user(request: auth_schemas.UserLogin, db: Session = Depends(get_session)):

    user = db.query(User).filter(User.emails.any(email=request.emails)).first()
    if user is None: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email."
        )
    hashed_pass = user.password
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Password."
        )
    
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    
    token_db = auth_models.RefreshToken(employment_id=user.id,access_token=access, refresh_token=refresh, status=True)
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
    }

def getusers(limit: int=10, skip: int=0, dependencies=Depends(JWTBearer()), session:Session = Depends(get_session)):
    try:
        user = session.query(db_models.User).offset(skip).limit(limit).all() 
        return {"users:": user}
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database error occurred: {str(e)}")

def change_password(request: auth_schemas.ChangePassword, db: Session = Depends(get_session)): ##&& Add error when user doesn't password or new password.
    user = db.query(db_models.User).filter(db_models.User.emails == request.emails).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User not Found.")
    
    if not verify_password(request.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid old Password.")
    
    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    db.commit()

    return {"Message": "Password change Successfully."}

def logout(dependencies=Depends(JWTBearer()), db:Session=Depends(get_session)):
    token = dependencies
    try: 
        payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, 
            detail="Token has Expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401, 
            detail="Invalid Token.")
    
    employment_id = payload['sub']
    token_record = (db.query(RefreshToken)
                    .filter(
                        RefreshToken.employment_id == employment_id,
                        RefreshToken.access_token == token,
                    ).first()
                    )
    
    if token_record:
        token_record.status = False
        db.add(token_record)
        db.commit()
        db.refresh(token_record)

    return {"message": "LogOut Successfully."}

