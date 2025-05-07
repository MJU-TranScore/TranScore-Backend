import datetime
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"

# 액세스 토큰 생성 (1시간 유효)
def create_access_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

# 리프레시 토큰 생성 (7일 유효)
def create_refresh_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

# 토큰 디코딩 + 오류 메시지 리턴
def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload, None
    except jwt.ExpiredSignatureError:
        print("JWT 디코딩 실패: 토큰 만료됨")
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        print("JWT 디코딩 실패: 유효하지 않은 토큰")
        return None, "Invalid token"

