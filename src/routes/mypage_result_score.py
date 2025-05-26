from flask import Blueprint, request, jsonify
from src.services.mypage_result_score import (
    save_result_score,
    get_saved_result_scores,
    delete_result_score
)
from src.utils.jwt_util import decode_token
from flasgger import swag_from

result_score_bp = Blueprint("result_score_bp", __name__, url_prefix="/mypage/result")


# ✅ 공통 JWT 인증 함수
def getUserIdFromToken():
    authHeader = request.headers.get("Authorization", None)
    if not authHeader or not authHeader.startswith("Bearer "):
        return None, jsonify({"message": "토큰이 필요합니다"}), 401

    token = authHeader.split(" ")[1]
    payload, error = decode_token(token)
    if error:
        return None, jsonify({"message": error}), 401

    return payload["userId"], None, None


@result_score_bp.route("/<int:resultId>/save", methods=["POST"])
@swag_from({
    'tags': ['Mypage'],
    'summary': '변환 결과 저장 (키 변경, 가사, 멜로디)',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'required': True,
            'description': 'Bearer 액세스 토큰',
            'schema': {'type': 'string'}
        },
        {
            'name': 'resultId',
            'in': 'path',
            'required': True,
            'description': '저장할 결과 ID',
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        201: {'description': '변환 결과가 저장되었습니다'},
        400: {'description': '이미 저장된 결과입니다'},
        401: {'description': '인증 실패'}
    }
})
def saveResult(resultId):
    userId, errorResponse, statusCode = getUserIdFromToken()
    if errorResponse:
        return errorResponse, statusCode

    if save_result_score(userId, resultId):
        return jsonify({"message": "변환 결과가 저장되었습니다"}), 201
    return jsonify({"message": "이미 저장된 결과입니다"}), 400


@result_score_bp.route("", methods=["GET"])
@swag_from({
    'tags': ['Mypage'],
    'summary': '저장한 변환 결과 목록 조회',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'required': True,
            'description': 'Bearer 액세스 토큰',
            'schema': {'type': 'string'}
        },
        {
            'name': 'type',
            'in': 'query',
            'required': False,
            'description': '결과 타입 필터 (transpose, lyrics, melody)',
            'schema': {
                'type': 'string',
                'enum': ['transpose', 'lyrics', 'melody']
            }
        }
    ],
    'responses': {
        200: {
            'description': '저장된 변환 결과 목록 반환',
            'content': {
                'application/json': {
                    'example': [
                        {
                            'resultId': 1,
                            'resultType': 'transpose',
                            'savedAt': '2025-05-18T12:34:56'
                        }
                    ]
                }
            }
        },
        401: {'description': '인증 실패'}
    }
})
def getSavedResults():
    userId, errorResponse, statusCode = getUserIdFromToken()
    if errorResponse:
        return errorResponse, statusCode

    resultType = request.args.get("type")
    saved = get_saved_result_scores(userId, resultType)
    result = [
        {
            "resultId": s.result_id,
            "resultType": s.result.type,
            "savedAt": s.saved_at.isoformat()
        }
        for s in saved
    ]
    return jsonify(result), 200


@result_score_bp.route("/<int:resultId>", methods=["DELETE"])
@swag_from({
    'tags': ['Mypage'],
    'summary': '저장한 변환 결과 삭제',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'required': True,
            'description': 'Bearer 액세스 토큰',
            'schema': {'type': 'string'}
        },
        {
            'name': 'resultId',
            'in': 'path',
            'required': True,
            'description': '삭제할 변환 결과 ID',
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {'description': '저장이 해제되었습니다'},
        404: {'description': '저장 내역이 없습니다'},
        401: {'description': '인증 실패'}
    }
})
def deleteResult(resultId):
    userId, errorResponse, statusCode = getUserIdFromToken()
    if errorResponse:
        return errorResponse, statusCode

    if delete_result_score(userId, resultId):
        return jsonify({"message": "저장이 해제되었습니다"}), 200
    return jsonify({"message": "저장 내역이 없습니다"}), 404
