import jwt # type: ignore
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv # type: ignore

# Load environment variables from .env file
load_dotenv()

PRIVATE_KEY = os.getenv("JWT_SECRET_KEY")

def generate_jwt_token(userid: str, user_type: str) -> str:
    try:
        payload = {
            "sub": userid,
            "user_type": user_type,
            "exp": datetime.utcnow() + timedelta(days=365),  # Token expiration time set to 1 year
            "iat": datetime.utcnow()  # Token issued at time
        }

        token = jwt.encode(payload, PRIVATE_KEY, algorithm="HS256")
        return token
    except Exception as e:
        print(e)
        raise Exception(f"Error generating JWT token: {str(e)}")
    
def decode_jwt_token(token: str):
    try:
        decoded_token = jwt.decode(token, PRIVATE_KEY, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None