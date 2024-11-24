from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import auth_services
from auth.auth_schemas import UserCreate, UserLogin, ChangePassword
from db.database import get_session
from auth.auth_bearer import JWTBearer

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register")
def register_user(user: UserCreate, session: Session=Depends(get_session)):
    return auth_services.register_user(user, session)

@router.post("/login")
def login_user(request: UserLogin, session: Session=Depends(get_session)):
    return auth_services.login_user(request, session)

@router.put("/change-password")
def change_password(request: ChangePassword, session: Session=Depends(get_session)):
    return auth_services.change_password(request, session)

@router.get("/users")
def get_users(
    limit: int =10,
    skip: int =0,
    dependencies=Depends(JWTBearer()),
    session: Session =Depends(get_session),
):
    return auth_services.getusers(limit, skip, dependencies, session)

@router.post("/logout")
def logout_user(dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)):
    return auth_services.logout(dependencies, session)