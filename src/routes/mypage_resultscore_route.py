from flask import Blueprint, request, jsonify
from flasgger import swag_from
from src.models.result_model import Result
from src.models.db import db
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
        200: {'description': '이미 저장된 결과입니다'},
        401: {'description': '인증 실패'}
    }
})
def save_result(result_id):
    user_id, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code

    data = request.get_json(silent=True) or {}
    title = data.get("title")

    print(f"🚨 save_result() 호출됨: result_id={result_id}")
    print(f"📦 받은 데이터: {data}")
    print(f"🎯 전달받은 title: {title}")

    # 이미 저장된 경우에도 OK 반환
    if not save_result_score(user_id, result_id):
        return jsonify({"message": "이미 저장된 결과입니다"}), 200

    # 새로 저장된 경우 → title이 오면 업데이트
    if title:
        result = Result.query.get(result_id)
        if result:
            print(f"📌 커밋 전 기존 DB title: {result.title}")
            result.title = title
            db.session.add(result)  # ✅ 명시적으로 추가
            db.session.commit()
            print(f"✅ 변경 후 result.title: {result.title}")

    return jsonify({"message": "변환 결과가 저장되었습니다"}), 201


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
                            'original_filename': '파일명.mid',
                            'key': 'C Major'
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
    saved = get_saved_result_scores(user_id, result_type)

    result = []
    for s, r, score in saved:
        result.append({
            "result_id": r.id,
            "result_type": r.type,
            "saved_at": s.saved_at.isoformat(),
            "title": r.title or score.title or "제목 없음",  # ✅ Result 우선
            "original_filename": r.original_filename or score.original_filename or "없음",  # ✅ .mid 우선
            "key": r.key or "없음"
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


# ✅ 추가된 마이페이지 전용 결과 조회 API
@result_score_bp.route("/<int:result_id>/view", methods=["GET"])
def view_result_for_mypage(result_id):
    """
    마이페이지에서 결과 보기용 API
    """
    result = Result.query.get(result_id)
    if not result:
        return jsonify({"error": "Result not found"}), 404

    return jsonify({
        "result_id": result.id,
        "title": result.title,
        "image_url": result.image_url,
        "key_signature": result.key_signature,
        "created_at": result.created_at.strftime('%Y-%m-%d %H:%M'),
        "mp3_path": result.mp3_path,
        "midi_path": result.midi_path
    }), 200