from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from src.models import db, User
from src.utils.jwt_util import decode_token
from flasgger import swag_from
import os
import uuid

user_bp = Blueprint('user', __name__, url_prefix='/user')

UPLOAD_FOLDER = 'static/profile_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ 공통 인증 함수
def get_current_user():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.split(" ")[1]
    payload, error = decode_token(token)
    if error:
        return None, jsonify({"error": error}), 401

    user = User.query.get(payload["user_id"])
    if not user:
        return None, jsonify({"error": "User not found"}), 404

    return user, None, None


@user_bp.route('/me', methods=['GET'])
@swag_from({
    'summary' : '내 정보 조회',
    'tags': ['user'],
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': '유저 정보 조회 성공',
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer'},
                    'nickname': {'type': 'string'},
                    'profile_image': {'type': 'string'}
                }
            }
        },
        401: {
            'description': '유효하지 않은 토큰'
        },
        404: {
            'description': 'User not found'
        }
    }
})
def get_my_info():
    user, error_resp, status = get_current_user()
    if error_resp:
        return error_resp, status

    return jsonify({
        "user_id": user.id,
        "nickname": user.nickname,
        "profile_image": user.profile_image
    }), 200


@user_bp.route('/me', methods=['PATCH'])
@swag_from({
    'summary': '기본 정보 수정(우선 닉네임만 수정하도록 구현)',
    'tags': ['user'],
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nickname': {
                        'type': 'string',
                        'example': '새로운닉네임'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': '닉네임 수정 성공',
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer'},
                    'nickname': {'type': 'string'}
                }
            }
        },
        400: {'description': '잘못된 요청'},
        401: {'description': '유효하지 않은 토큰'},
        404: {'description': 'User not found'}
    }
})
def update_my_info():
    user, error_resp, status = get_current_user()
    if error_resp:
        return error_resp, status

    data = request.get_json()
    new_nickname = data.get("nickname")
    if not new_nickname:
        return jsonify({"error": "Nickname is required"}), 400

    user.nickname = new_nickname
    db.session.commit()

    return jsonify({
        "user_id": user.id,
        "nickname": user.nickname
    }), 200


@user_bp.route("/me/profile-image", methods=["PATCH"])
@swag_from({
    'summary' : '프로필 이미지 업로드/변경',
    'tags': ['user'],
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'profile_image',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': '새 프로필 이미지 파일'
        }
    ],
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': '프로필 이미지 변경 성공',
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer'},
                    'nickname': {'type': 'string'},
                    'profile_image': {'type': 'string'}
                }
            }
        },
        400: {'description': '잘못된 요청'},
        401: {'description': '유효하지 않은 토큰'}
    }
})
def update_profile_image():
    user, error_resp, status = get_current_user()
    if error_resp:
        return error_resp, status

    if 'profile_image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['profile_image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)

    user.profile_image = file_path
    db.session.commit()

    return jsonify({
        "user_id": user.id,
        "nickname": user.nickname,
        "profile_image": user.profile_image
    }), 200


@user_bp.route("/me", methods=["DELETE"])
@swag_from({
    'summary': '회원 탈퇴',
    'tags': ['user'],
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': '회원 탈퇴 성공',
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer'},
                    'message': {'type': 'string'}
                }
            }
        },
        401: {'description': '유효하지 않은 토큰'},
        404: {'description': '사용자 없음'}
    }
})
def delete_my_account():
    user, error_resp, status = get_current_user()
    if error_resp:
        return error_resp, status

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "user_id": user.id,
        "message": "User successfully deleted"
    }), 200
