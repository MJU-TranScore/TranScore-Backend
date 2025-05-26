from src.utils.jwt_util import create_access_token, create_refresh_token, decode_token
from src.models import db, User

def handle_kakao_login(kakaoId, nickname, profileImageUrl):
    # DB 컬럼에 맞춰 social_id로 조회
    user = User.query.filter_by(social_id=kakaoId).first()
    
    if not user:
        user = User(
            social_id=kakaoId,
            nickname=nickname,
            profile_image=profileImageUrl
        )
        db.session.add(user)
        db.session.commit()

    accessToken = create_access_token(user.id)
    refreshToken = create_refresh_token(user.id)

    return {
        "accessToken": accessToken,
        "refreshToken": refreshToken,
        "userId": user.id,
        "nickname": user.nickname
    }

def refresh_access_token(refreshToken):
    payload = decode_token(refreshToken)
    if not payload:
        return None, "Invalid or expired refresh token"
    
    userId = payload.get("userId")
    user = User.query.get(userId)
    if not user:
        return None, "User not found"
    
    newAccessToken = create_access_token(user.id)
    return newAccessToken, None
