from flask import Blueprint, request, jsonify
from src.services.mypage_result_score import (
    save_result_score,
    get_saved_result_scores,
    delete_result_score
)
from src.utils.jwt_util import decode_token

result_score_bp = Blueprint("result_score_bp", __name__, url_prefix="/mypage/result")


@result_score_bp.route("/<int:result_id>/save", methods=["POST"])
def save_result(result_id):
    """
    변환 결과 저장 (키 변경, 가사, 멜로디)
    ---
    tags:
      - Mypage
    parameters:
      - in: header
        name: Authorization
        required: true
        description: Bearer 액세스 토큰
        schema:
          type: string
      - in: path
        name: result_id
        required: true
        description: 저장할 결과 ID
        schema:
          type: integer
    responses:
      201:
        description: 변환 결과가 저장되었습니다
      400:
        description: 이미 저장된 결과입니다
      401:
        description: 인증 실패
    """
    auth_header = request.headers.get("Authorization", None)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "토큰이 필요합니다"}), 401

    token = auth_header.split(" ")[1]
    payload, error = decode_token(token)
    if error:
        return jsonify({"message": error}), 401

    user_id = payload["user_id"]
    if save_result_score(user_id, result_id):
        return jsonify({"message": "변환 결과가 저장되었습니다"}), 201
    return jsonify({"message": "이미 저장된 결과입니다"}), 400


@result_score_bp.route("", methods=["GET"])
def get_saved_results():
    """
    저장한 변환 결과 목록 조회
    ---
    tags:
      - Mypage
    parameters:
      - in: header
        name: Authorization
        required: true
        description: Bearer 액세스 토큰
        schema:
          type: string
      - in: query
        name: type
        required: false
        description: 결과 타입 필터 (transpose, lyrics, melody)
        schema:
          type: string
    responses:
      200:
        description: 저장된 변환 결과 목록 반환
        content:
          application/json:
            example:
              - result_id: 1
                result_type: "transpose"
                saved_at: "2025-05-18T12:34:56"
      401:
        description: 인증 실패
    """
    auth_header = request.headers.get("Authorization", None)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "토큰이 필요합니다"}), 401

    token = auth_header.split(" ")[1]
    payload, error = decode_token(token)
    if error:
        return jsonify({"message": error}), 401

    user_id = payload["user_id"]
    result_type = request.args.get("type")
    saved = get_saved_result_scores(user_id, result_type)
    result = [
        {
            "result_id": s.result_id,
            "result_type": s.result.type,
            "saved_at": s.saved_at.isoformat()
        }
        for s in saved
    ]
    return jsonify(result), 200


@result_score_bp.route("/<int:result_id>", methods=["DELETE"])
def delete_result(result_id):
    """
    저장한 변환 결과 삭제
    ---
    tags:
      - Mypage
    parameters:
      - in: header
        name: Authorization
        required: true
        description: Bearer 액세스 토큰
        schema:
          type: string
      - in: path
        name: result_id
        required: true
        description: 삭제할 변환 결과 ID
        schema:
          type: integer
    responses:
      200:
        description: 저장이 해제되었습니다
      404:
        description: 저장 내역이 없습니다
      401:
        description: 인증 실패
    """
    auth_header = request.headers.get("Authorization", None)
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "토큰이 필요합니다"}), 401

    token = auth_header.split(" ")[1]
    payload, error = decode_token(token)
    if error:
        return jsonify({"message": error}), 401

    user_id = payload["user_id"]
    if delete_result_score(user_id, result_id):
        return jsonify({"message": "저장이 해제되었습니다"}), 200
    return jsonify({"message": "저장 내역이 없습니다"}), 404
