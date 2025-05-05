from flask import Blueprint, jsonify, g
from utils.jwt_util import token_required
from models import db, User

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/me", methods=["GET"])
@token_required
def get_my_info():
    
    """
    내 정보 조회 (JWT 필요)
    ---
    tags:
      - user
    security:
      - Bearer: []
    responses:
      200:
        description: 사용자 정보 반환
        schema:
          type: object
          properties:
            user_id:
              type: integer
            nickname:
              type: string
            profile_image_url:
              type: string
      401:
        description: JWT 누락 또는 유효하지 않음
    """
    
    user = User.query.get(g.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id": user.id,
        "nickname": user.nickname,
        "profile_image_url": user.profile_image_url
    }), 200
