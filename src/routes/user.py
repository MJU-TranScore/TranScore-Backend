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
def getCurrentUser():
    authHeader = request.headers.get("Authorization")
    if not authHeader or not authHeader.startswith("Bearer "):
        return None, jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = authHeader.split(" ")[1]
    payload, error = decode_token(token)
    if error:
        return None, jsonify({"error": error}), 401

    user = User.query.get(payload["userId"])
    if not user:
        return None, jsonify({"error": "User not found"}), 404

    return user, None, None


@user_bp.route('/me', methods=['GET'])
@swag_from({
    'summary': '내 정보 조회',
    'tags': ['user'],
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': '유저 정보 조회 성공',
            'schema': {
                'type': 'object',
                'properties': {
                    'userId': {'type': 'integer'},
                    'nickname': {'type': 'string'},
                    'profileImage': {'type': 'string'}
                }
            }
        },
        401: {'description': '유효하지 않은 토큰'},
        404: {'description': 'User not found'}
    }
})
def getMyInfo():
    user, errorResp, status = getCurrentUser()
    if errorResp:
        return errorResp, status

    return jsonify({
        "userId": user.id,
        "nickname": user.nickname,
        "profileImage": user.profile_image
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
                    'userId': {'type': 'integer'},
                    'nickname': {'type': 'string'}
                }
            }
        },
        400: {'description': '잘못된 요청'},
        401: {'description': '유효하지 않은 토큰'},
        404: {'description': 'User not found'}
    }
})
def updateMyInfo():
    user, errorResp, status = getCurrentUser()
    if errorResp:
        return errorResp, status

    data = request.get_json()
    newNickname = data.get("nickname")
    if not newNickname:
        return jsonify({"error": "Nickname is required"}), 400

    user.nickname = newNickname
    db.session.commit()

    return jsonify({
        "userId": user.id,
        "nickname": user.nickname
    }), 200


@user_bp.route("/me/profile-image", methods=["PATCH"])
@swag_from({
    'summary': '프로필 이미지 업로드/변경',
    'tags': ['user'],
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'profileImage',
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
                    'userId': {'type': 'integer'},
                    'nickname': {'type': 'string'},
                    'profileImage': {'type': 'string'}
                }
            }
        },
        400: {'description': '잘못된 요청'},
        401: {'description': '유효하지 않은 토큰'}
    }
})
def updateProfileImage():
    user, errorResp, status = getCurrentUser()
    if errorResp:
        return errorResp, status

    if 'profileImage' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['profileImage']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    uniqueFilename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    filePath = os.path.join(UPLOAD_FOLDER, uniqueFilename)
    file.save(filePath)

    user.profile_image = filePath
    db.session.commit()

    return jsonify({
        "userId": user.id,
        "nickname": user.nickname,
        "profileImage": user.profile_image
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
                    'userId': {'type': 'integer'},
                    'message': {'type': 'string'}
                }
            }
        },
        401: {'description': '유효하지 않은 토큰'},
        404: {'description': '사용자 없음'}
    }
})
def deleteMyAccount():
    user, errorResp, status = getCurrentUser()
    if errorResp:
        return errorResp, status

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "userId": user.id,
        "message": "User successfully deleted"
    }), 200
