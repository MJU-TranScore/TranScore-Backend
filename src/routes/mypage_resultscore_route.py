# src/routes/mypage_resultscore_route.py

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from src.services.mypage_resultscore_service import (
    save_result_score,
    get_saved_result_scores,
    delete_result_score
)
from src.utils.jwt_util import decode_token

result_score_bp = Blueprint("result_score_bp", __name__, url_prefix="/mypage/result")

# ✅ 공통 JWT 인증 함수
def get_user_id_from_token():
    auth_header = request.headers.get("Authorization", None)
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, jsonify({"message": "토큰이 필요합니다"}), 401

    token = auth_header.split(" ")[1]
    payload, error = decode_token(token)
    if error or not payload:
        return None, jsonify({"message": error or "유효하지 않은 토큰"}), 401

    user_id = payload.get("user_id") or payload.get("userId")
    if not user_id:
        return None, jsonify({"message": "토큰에 user_id가 없습니다"}), 401

    return user_id, None, None

@result_score_bp.route("/<int:result_id>/save", methods=["POST"])
@swag_from({
    'tags': ['Mypage'],
    'summary': '변환 결과 저장 (키 변경, 가사, 멜로디)',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'required': True, 'schema': {'type': 'string'}},
        {'name': 'result_id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}
    ],
    'responses': {
        201: {'description': '변환 결과가 저장되었습니다'},
        400: {'description': '이미 저장된 결과입니다'},
        401: {'description': '인증 실패'}
    }
})
def save_result(result_id):
    user_id, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code

    if save_result_score(user_id, result_id):
        return jsonify({"message": "변환 결과가 저장되었습니다"}), 201
    return jsonify({"message": "이미 저장된 결과입니다"}), 400

@result_score_bp.route("", methods=["GET"])
@swag_from({
    'tags': ['Mypage'],
    'summary': '저장한 변환 결과 목록 조회',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'required': True, 'schema': {'type': 'string'}},
        {'name': 'type', 'in': 'query', 'required': False, 'schema': {'type': 'string', 'enum': ['transpose', 'lyrics', 'melody']}}
    ],
    'responses': {
        200: {
            'description': '저장된 변환 결과 목록 반환',
            'content': {
                'application/json': {
                    'example': [
                        {
                            'result_id': 1,
                            'result_type': 'transpose',
                            'saved_at': '2025-05-18T12:34:56',
                            'title': '제목',
                            'original_filename': '파일명.png',
                            'key': 'C'
                        }
                    ]
                }
            }
        },
        401: {'description': '인증 실패'}
    }
})
def get_saved_results():
    user_id, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code

    result_type = request.args.get("type")
    # ✅ services에서 명확한 JOIN으로 처리하여 score 정보까지 가져옴
    saved = get_saved_result_scores(user_id, result_type)

    result = []
    for s, r, score in saved:
        result.append({
            "result_id": r.id,
            "result_type": r.type,
            "saved_at": s.saved_at.isoformat(),
            "title": score.title or "제목 없음",
            "original_filename": score.original_filename or "없음",
            "key": score.key or "없음"
        })

    return jsonify(result), 200

@result_score_bp.route("/<int:result_id>", methods=["DELETE"])
@swag_from({
    'tags': ['Mypage'],
    'summary': '저장한 변환 결과 삭제',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'required': True, 'schema': {'type': 'string'}},
        {'name': 'result_id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}
    ],
    'responses': {
        200: {'description': '저장이 해제되었습니다'},
        404: {'description': '저장 내역이 없습니다'},
        401: {'description': '인증 실패'}
    }
})
def delete_result(result_id):
    user_id, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code

    if delete_result_score(user_id, result_id):
        return jsonify({"message": "저장이 해제되었습니다"}), 200
    return jsonify({"message": "저장 내역이 없습니다"}), 404
