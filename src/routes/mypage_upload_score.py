from flask import Blueprint, request, jsonify
from src.services.mypage_upload_score import (
    save_upload_score,
    get_saved_upload_scores,
    delete_upload_score
)
from src.utils.jwt_util import decode_token
from flasgger import swag_from

upload_score_bp = Blueprint("upload_score_bp", __name__, url_prefix="/mypage/score")


# ✅ JWT 인증 공통 함수
def getUserIdFromToken():
    authHeader = request.headers.get("Authorization", None)
    if not authHeader or not authHeader.startswith("Bearer "):
        return None, jsonify({"message": "토큰이 필요합니다"}), 401
    token = authHeader.split(" ")[1]
    payload, error = decode_token(token)
    if error:
        return None, jsonify({"message": error}), 401
    return payload["userId"], None, None


@upload_score_bp.route("/<string:scoreId>/save", methods=["POST"])
@swag_from({
    'tags': ['Mypage'],
    'summary': '업로드한 악보 저장',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'required': True,
            'description': 'Bearer 액세스 토큰',
            'schema': {'type': 'string'}
        },
        {
            'name': 'scoreId',
            'in': 'path',
            'required': True,
            'description': '저장할 악보 ID',
            'schema': {'type': 'string'}
        }
    ],
    'responses': {
        201: {'description': '업로드한 악보가 저장되었습니다'},
        400: {'description': '이미 저장된 악보입니다'},
        401: {'description': '인증 실패'}
    }
})
def saveScore(scoreId):
    userId, errorResponse, statusCode = getUserIdFromToken()
    if errorResponse:
        return errorResponse, statusCode
    if save_upload_score(userId, scoreId):
        return jsonify({"message": "업로드한 악보가 저장되었습니다"}), 201
    return jsonify({"message": "이미 저장된 악보입니다"}), 400


@upload_score_bp.route("", methods=["GET"])
@swag_from({
    'tags': ['Mypage'],
    'summary': '저장한 업로드 악보 목록 조회',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'required': True,
            'description': 'Bearer 액세스 토큰',
            'schema': {'type': 'string'}
        }
    ],
    'responses': {
        200: {
            'description': '저장된 악보 목록 반환',
            'content': {
                'application/json': {
                    'example': [
                        {
                            'scoreId': "abc123",
                            'savedAt': "2025-05-18T12:34:56"
                        }
                    ]
                }
            }
        },
        401: {'description': '인증 실패'}
    }
})
def getSavedScores():
    userId, errorResponse, statusCode = getUserIdFromToken()
    if errorResponse:
        return errorResponse, statusCode

    saved = get_saved_upload_scores(userId)
    result = [
        {
            "scoreId": s.score_id,
            "savedAt": s.saved_at.isoformat()
        }
        for s in saved
    ]
    return jsonify(result), 200


@upload_score_bp.route("/<string:scoreId>", methods=["DELETE"])
@swag_from({
    'tags': ['Mypage'],
    'summary': '저장한 업로드 악보 삭제',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'required': True,
            'description': 'Bearer 액세스 토큰',
            'schema': {'type': 'string'}
        },
        {
            'name': 'scoreId',
            'in': 'path',
            'required': True,
            'description': '삭제할 악보 ID',
            'schema': {'type': 'string'}
        }
    ],
    'responses': {
        200: {'description': '저장이 해제되었습니다'},
        404: {'description': '저장 내역이 없습니다'},
        401: {'description': '인증 실패'}
    }
})
def deleteScore(scoreId):
    userId, errorResponse, statusCode = getUserIdFromToken()
    if errorResponse:
        return errorResponse, statusCode

    if delete_upload_score(userId, scoreId):
        return jsonify({"message": "저장이 해제되었습니다"}), 200
    return jsonify({"message": "저장 내역이 없습니다"}), 404
