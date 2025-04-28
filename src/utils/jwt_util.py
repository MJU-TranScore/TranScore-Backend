import jwt
import os
from datetime import datetime, timedelta

def generate_jwt(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")
    return token
