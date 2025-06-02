from flask import Blueprint, request, jsonify
from flasgger import swag_from
from src.services.mypage_uploadscore_service import (
    save_upload_score,
    get_saved_upload_scores,
    delete_upload_score
)
from src.utils.jwt_util import decode_token

upload_score_bp = Blueprint("upload_score_bp", __name__, url_prefix="/mypage/score")


# ✅ JWT 토큰에서 user_id 파싱 (KeyError 방지)
def get_user_id_from_token():
    auth_header = request.headers.get("Authorization", None)
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, jsonify({"message": "토큰이 필요합니다"}), 401

    token = auth_header.split(" ")[1]
    payload, error = decode_token(token)
    if error or not payload:
        return None, jsonify({"message": error or "유효하지 않은 토큰입니다"}), 401

    user_id = payload.get("user_id") or payload.get("userId")
    if not user_id:
        return None, jsonify({"message": "토큰에 user_id가 없습니다"}), 401

    return user_id, None, None


# ✅ 업로드 악보 저장
@upload_score_bp.route("/<string:score_id>/save", methods=["POST"])
@swag_from({
    'tags': ['Mypage'],
    'summary': '업로드한 악보 저장',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'required': True, 'schema': {'type': 'string'}},
        {'name': 'score_id', 'in': 'path', 'required': True, 'schema': {'type': 'string'}}
    ],
    'responses': {
        201: {'description': '업로드한 악보가 저장되었습니다'},
        400: {'description': '이미 저장된 악보입니다'},
        401: {'description': '인증 실패'}
    }
})
def save_score(score_id):
    user_id, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code

    if save_upload_score(user_id, score_id):
        return jsonify({"message": "업로드한 악보가 저장되었습니다"}), 201
    return jsonify({"message": "이미 저장된 악보입니다"}), 400


# ✅ 저장된 업로드 악보 목록 조회 (제목 등 함께 반환)
@upload_score_bp.route("", methods=["GET"])
@swag_from({
    'tags': ['Mypage'],
    'summary': '저장한 업로드 악보 목록 조회',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'required': True, 'schema': {'type': 'string'}}
    ],
    'responses': {
        200: {
            'description': '저장된 악보 목록 반환',
            'content': {
                'application/json': {
                    'example': [
                        {
                            'score_id': "abc123",
                            'title': "제목",
                            'saved_at': "2025-05-18T12:34:56",
                            'original_filename': "file.pdf",
                            'key': "C"
                        }
                    ]
                }
            }
        },
        401: {'description': '인증 실패'}
    }
})
def get_saved_scores():
    user_id, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code

    saved = get_saved_upload_scores(user_id)
    result = [
        {
            "score_id": save.score_id,
            "saved_at": save.saved_at.isoformat(),
            "title": score.title or "제목 없음",
            "original_filename": score.original_filename,
            "key": score.key or "N/A"
        }
        for save, score in saved
    ]
    return jsonify(result), 200


# ✅ 저장된 업로드 악보 삭제
@upload_score_bp.route("/<string:score_id>", methods=["DELETE"])
@swag_from({
    'tags': ['Mypage'],
    'summary': '저장한 업로드 악보 삭제',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'required': True, 'schema': {'type': 'string'}},
        {'name': 'score_id', 'in': 'path', 'required': True, 'schema': {'type': 'string'}}
    ],
    'responses': {
        200: {'description': '저장이 해제되었습니다'},
        404: {'description': '저장 내역이 없습니다'},
        401: {'description': '인증 실패'}
    }
})
def delete_score(score_id):
    user_id, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code

    if delete_upload_score(user_id, score_id):
        return jsonify({"message": "저장이 해제되었습니다"}), 200
    return jsonify({"message": "저장 내역이 없습니다"}), 404
