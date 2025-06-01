from src.utils.jwt_util import create_access_token, create_refresh_token, decode_token
from src.models import db, User

def handle_kakao_login(kakao_id, nickname, profile_image_url):
    # DB 컬럼에 맞춰 social_id로 조회
    user = User.query.filter_by(social_id=kakao_id).first()

    if not user:
        user = User(
            social_id=kakao_id,
            nickname=nickname,
            profile_image=profile_image_url
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
    # decode_token이 (payload, error) 형태로 반환됨
    payload, error = decode_token(refresh_token)
    if error:
        return None, error

    user_id = payload.get("user_id")
    if not user_id:
        return None, "유효하지 않은 토큰입니다."

    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    new_access_token = create_access_token(user.id)
    return new_access_token, None
