from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
import os

from src.utils.transpose_helper import transpose_key
from src.models.score_model import Score
from src.models.result_model import Result
from src.services.score_service import (
    save_score_file_to_db,
    get_latest_score_info
)
from src.services.transform_service import (
    perform_transpose,
    extract_melody,
    extract_lyrics
)

transform_bp = Blueprint('transform', __name__)

# ============================================================
# ✅ 1. transform 흐름 - 업로드 및 악보 정보 조회
# ============================================================

@transform_bp.route('/score/upload', methods=['POST', 'OPTIONS'])
@cross_origin(origins="http://localhost:5173", supports_credentials=True)
def upload_score_for_transform():
    """
    악보 이미지 업로드 API (transform 기능용)
    ---
    tags:
      - transform
    summary: 악보 업로드 (멜로디 추출 / 키변경 / 가사 추출 등 transform 기능 전용)
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: 업로드할 악보 이미지
      - name: title
        in: formData
        type: string
        required: false
        description: 악보 제목 (선택)
    responses:
      201:
        description: 업로드 성공
      400:
        description: 파일 없음
      500:
        description: 내부 서버 오류
    """
    if request.method == 'OPTIONS':
        return '', 200

    file = request.files.get('file')
    title = request.form.get('title')

    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    try:
        upload_dir = 'uploaded_scores'
        os.makedirs(upload_dir, exist_ok=True)

        # ✅ UUID 기반 고유 파일명 생성
        from uuid import uuid4
        unique_id = uuid4().hex
        original_name = secure_filename(file.filename)
        filename = f"{unique_id}_{original_name}"

        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # ✅ title이 없으면 원본 파일명에서 확장자 제거한 걸로 설정
        if not title:
            title = os.path.splitext(original_name)[0]

        score_id = save_score_file_to_db(filename, title)

        return jsonify({
            'score_id': score_id,
            'message': 'Score uploaded for transform successfully'
        }), 201

    except Exception as e:
        print("🔥 /transform/score/upload 에러:", e)
        return jsonify({'error': str(e)}), 500


@transform_bp.route('/score/info', methods=['GET'])
def get_score_info():
    """
    최신 업로드된 악보 정보 조회
    ---
    tags:
      - transform
    summary: 최신 업로드된 악보 ID 및 이미지 정보 반환
    responses:
      200:
        description: 최신 악보 정보 반환
        schema:
          type: object
          properties:
            score_id: {type: integer}
            title: {type: string}
            imageUrl: {type: string}
            totalMeasures: {type: integer}
            imageWidth: {type: integer}
            imageHeight: {type: integer}
      404:
        description: 악보가 존재하지 않음
    """
    info = get_latest_score_info()
    return jsonify(info) if info else (jsonify({'error': 'No score found'}), 404)

# ============================================================
# ✅ 2. 키 관련 기능: 미리보기 / 실제 변경
# ============================================================

def clean_key(key: str) -> str:
    return key.replace("-", "b").strip()  # ✅ E- → Eb, A- → Ab

@transform_bp.route('/transpose-preview', methods=['POST'])
@cross_origin(origins="http://localhost:5173", supports_credentials=True)
def transpose_preview():
    """
    키 변경 미리보기 API
    ---
    tags:
      - transform
    summary: 현재 키와 이동 수를 받아 변환될 키 정보 반환
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            current_key: {type: string}
            shift: {type: integer}
          required: [current_key, shift]
    responses:
      200:
        description: 변환된 키 반환
        schema:
          type: object
          properties:
            transposed_key: {type: string}
            message: {type: string}
      400:
        description: 잘못된 요청
    """
    # ✅ OPTIONS 프리플라이트 응답 처리
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    current_key = clean_key(data.get('current_key', ''))  # ✅ 변환 적용
    shift = data.get('shift')

    if not current_key or shift is None:
        return jsonify({'error': 'current_key and shift are required'}), 400

    try:
        transposed_key = transpose_key(current_key, int(shift))
        return jsonify({
            'transposed_key': transposed_key,
            'message': f"{current_key.upper()} → {transposed_key} (shift {shift})"
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@transform_bp.route('/score/<int:score_id>/transpose', methods=['POST'])
def transform_transpose(score_id):
    """
    키 변경 실행 API
    ---
    tags:
      - transform
    summary: 업로드된 악보를 지정된 반음 수만큼 키 변경 후 결과 PDF 생성
    parameters:
      - in: path
        name: score_id
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            shift: {type: integer}
    responses:
      201:
        description: 키 변경 완료
        schema:
          type: object
          properties:
            result_id: {type: integer}
            message: {type: string}
      404:
        description: 악보를 찾을 수 없음
    """
    score = Score.query.get(score_id)
    if not score:
        return jsonify({'error': 'Score not found'}), 404

    data = request.get_json()
    shift = data.get('shift')
    if shift is None:
        return jsonify({'error': 'shift is required'}), 400

    result_id = perform_transpose(score, int(shift))
    return jsonify({
        'result_id': result_id,
        'message': 'Transpose completed successfully'
    }), 201

# ============================================================
# ✅ 3. 가사 및 멜로디 추출
# ============================================================

@transform_bp.route('/score/<int:score_id>/lyrics', methods=['POST'])
def extract_lyrics_route(score_id):
    """
    가사 추출 API
    ---
    tags:
      - transform
    summary: 업로드된 악보에서 가사 텍스트 추출
    parameters:
      - in: path
        name: score_id
        required: true
        type: integer
    responses:
      200:
        description: 가사 추출 성공
        schema:
          type: object
          properties:
            result_id: {type: integer}
            text_path: {type: string}
            message: {type: string}
      404:
        description: 악보 또는 결과를 찾을 수 없음
    """
    score = Score.query.get(score_id)
    if not score:
        return jsonify({'error': 'Score not found'}), 404

    result_id = extract_lyrics(score)
    result = Result.query.get(result_id)
    if not result:
        return jsonify({'error': 'Result not found'}), 500

    return jsonify({
        'result_id': result_id,
        'text_path': result.download_path,
        'message': 'Lyrics extracted successfully'
    }), 200


@transform_bp.route('/score/<int:score_id>/melody', methods=['POST', 'OPTIONS'])
@cross_origin(origins="http://localhost:5173", supports_credentials=True)
def extract_melody_route(score_id):
    """
    멜로디 추출 API
    ---
    tags:
      - transform
    summary: 업로드된 악보에서 멜로디를 추출하여 MP3로 생성
    parameters:
      - in: path
        name: score_id
        required: true
        type: integer
    responses:
      200:
        description: 멜로디 추출 성공
        schema:
          type: object
          properties:
            result_id: {type: integer}
            mp3_path: {type: string}
            midi_path: {type: string}
            title: {type: string}
            key_signature: {type: string}
      404:
        description: 악보 또는 결과를 찾을 수 없음
    """
    score = Score.query.get(score_id)
    if not score:
        return jsonify({'error': 'Score not found'}), 404

    try:
        start, end = 1, 9999
        result_info = extract_melody(score, start, end)  # ✅ dict 반환

        return jsonify(result_info), 200  # ✅ 그대로 반환

    except Exception as e:
        print("🔥 Melody 추출 중 서버 에러:", e)
        return jsonify({'error': str(e)}), 500
