from flask import Blueprint, request, jsonify
from src.services.mypage_upload_score import (
    save_upload_score,
    get_saved_upload_scores,
    delete_upload_score
)
from src.utils.jwt_util import decode_token

upload_score_bp = Blueprint("upload_score_bp", __name__, url_prefix="/mypage/score")


@upload_score_bp.route("/<string:score_id>/save", methods=["POST"])
def save_score(score_id):
    """
    업로드한 악보 저장
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
        name: score_id
        required: true
        description: 저장할 악보 ID
        schema:
          type: string
    responses:
      201:
        description: 업로드한 악보가 저장되었습니다
      400:
        description: 이미 저장된 악보입니다
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
    if save_upload_score(user_id, score_id):
        return jsonify({"message": "업로드한 악보가 저장되었습니다"}), 201
    return jsonify({"message": "이미 저장된 악보입니다"}), 400


@upload_score_bp.route("", methods=["GET"])
def get_saved_scores():
    """
    저장한 업로드 악보 목록 조회
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
    responses:
      200:
        description: 저장된 악보 목록 반환
        content:
          application/json:
            example:
              - score_id: "abc123"
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
    saved = get_saved_upload_scores(user_id)
    result = [
        {
            "score_id": s.score_id,
            "saved_at": s.saved_at.isoformat()
        }
        for s in saved
    ]
    return jsonify(result), 200


@upload_score_bp.route("/<string:score_id>", methods=["DELETE"])
def delete_score(score_id):
    """
    저장한 업로드 악보 삭제
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
        name: score_id
        required: true
        description: 삭제할 악보 ID
        schema:
          type: string
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
    if delete_upload_score(user_id, score_id):
        return jsonify({"message": "저장이 해제되었습니다"}), 200
    return jsonify({"message": "저장 내역이 없습니다"}), 404
