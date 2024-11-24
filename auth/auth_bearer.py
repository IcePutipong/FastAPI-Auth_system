from dotenv import load_dotenv
import jwt, os
from jwt.exceptions import InvalidTokenError
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.auth_models import RefreshToken

from functools import wraps

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
ALGORITHM = os.getenv("ALGORITHM")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")

def decode_jwt(jwttoken: str):
    try:
        #Decode & Verify Token
        payload = jwt.decode(jwttoken, JWT_SECRET_KEY, ALGORITHM)
        return payload
    except InvalidTokenError:
        return None
    
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
       credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
       if credentials:
           if credentials.scheme != "Bearer":
               raise HTTPException(status_code=403, detail="Invalid authenticate schema.")
           if not self.verify_jwt(credentials.credentials):
               raise HTTPException(status_code=403, detail="Invalid token or expired token.")
           
           return credentials.credentials
       else:
           raise HTTPException(status_code=403, detail="Invalid authorization code.")
       
    def verify_jwt(self, jwtoken: str) -> bool:
        is_token_valid: bool = False

        try: 
            paylaod = decode_jwt(jwtoken)
        except Exception as e:
            paylaod = None
            print(f"Error decoding JWT: {e}")
        if paylaod:
            is_token_valid =True
        return is_token_valid
    
jwt_bearer = JWTBearer


    
            
