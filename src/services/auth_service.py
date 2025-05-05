from src.utils.jwt_util import create_access_token, create_refresh_token, decode_token
from src.models import db, User

def handle_kakao_login(kakao_id, nickname, profile_image_url):
    # DB 컬럼에 맞춰 social_id로 조회
    user = User.query.filter_by(social_id=kakao_id).first()
    
    if not user:
        user = User(
            social_id=kakao_id,  # 컬럼명 맞게 수정
            nickname=nickname,
            profile_image=profile_image_url  # 모델 정의에 맞게 이름 일치시킴
        )
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "nickname": user.nickname
    }

def refresh_access_token(refresh_token):
    payload = decode_token(refresh_token)
    if not payload:
        return None, "Invalid or expired refresh token"
    
    user_id = payload.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"
    
    new_access_token = create_access_token(user.id)
    return new_access_token, None
