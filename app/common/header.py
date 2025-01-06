import os
from fastapi import HTTPException, Depends, Security, Response
from fastapi_jwt_auth import AuthJWT
from fastapi.security import OAuth2PasswordBearer
from configs.db import user_collection
import logging
from pydantic import BaseSettings
from dotenv import load_dotenv
from app.core.jwt_handler import decode_jwt_token
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Settings(BaseSettings):
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY")

@AuthJWT.load_config
def get_config():
    return Settings()

# All endpoints using this function require authorization
async def authorization_required(Authorize: AuthJWT = Depends(), token: str = Security(oauth2_scheme)):
    try:
        logging.info("Getting user details using JWT Token")
        decoded_token = decode_jwt_token(token)
        if not decoded_token:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        userid = decoded_token.get("sub")
        logging.info("User ID from token:", {userid})
        
        return decoded_token
    except Exception as e:
        logging.error("Error in authorization_required:", {str(e)})
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoints using this function do not require authorization
async def authorization_optional(Authorize: AuthJWT = Depends(), token: str = Security(oauth2_scheme)):
    try:
        if token:
            logging.info("Getting user details using JWT Token")
            decoded_token = decode_jwt_token(token)
            if not decoded_token:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            userid = decoded_token.get("sub")
            logging.info("User ID from token:", {userid})
            
            return decoded_token
        else:
            logging.info("No token provided, proceeding without user details")
            return None
    except Exception as e:
        logging.error("Error in authorization_optional:", {str(e)})
        raise HTTPException(status_code=401, detail="Invalid token")

class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        trace_id = str(uuid.uuid4())
        response.headers["X-Trace-Id"] = trace_id
        logging.info("Generated Trace ID:", {trace_id})
        return response