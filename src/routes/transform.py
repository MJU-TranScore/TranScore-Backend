from flask import Blueprint, request, jsonify
from src.utils.transpose_helper import transpose_key
from src.models.score import Score
from src.models.result import Result
from src.services.transform_service import perform_transpose, extract_melody

transform_bp = Blueprint('transform', __name__)

@transform_bp.route('/transpose-preview', methods=['POST'])
def transpose_preview_route():
    """
    키 변경 미리보기 API
    ---
    tags:
      - transform
    summary: 현재 키와 반음 이동 수를 입력 받아 변환될 키를 미리 보여줍니다
    consumes:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            current_key:
              type: string
              example: "F"
              description: 현재 키
            shift:
              type: integer
              example: -1
              description: 변환할 반음 수
          required:
            - current_key
            - shift
    responses:
      200:
        description: 변환된 키 정보
        schema:
          type: object
          properties:
            transposed_key:
              type: string
              example: "E"
            message:
              type: string
              example: "F → E (shift -1)"
      400:
        description: 잘못된 요청
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid key: Z"
    """
    data = request.get_json()
    current_key = data.get('current_key')
    shift = data.get('shift')

    if current_key is None or shift is None:
        return jsonify({'error': 'current_key and shift are required'}), 400

    try:
        shift = int(shift)
        transposed_key = transpose_key(current_key, shift)

        return jsonify({
            'transposed_key': transposed_key,
            'message': f"{current_key.upper()} → {transposed_key} (shift {shift})"
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@transform_bp.route('/score/<int:score_id>/transpose', methods=['POST'])
def transform_transpose_route(score_id):
    """
    키 변경 수행 API
    ---
    tags:
      - transform
    summary: 업로드된 악보를 지정된 반음 수만큼 키 변경하고 결과 PDF를 생성합니다
    parameters:
      - in: path
        name: score_id
        required: true
        schema:
          type: integer
        description: 변환할 대상 악보의 ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            shift:
              type: integer
              example: -1
              description: 변경할 반음 수
          required:
            - shift
    responses:
      201:
        description: 키 변경 결과 PDF 생성 성공
        schema:
          type: object
          properties:
            result_id:
              type: integer
              example: 101
            message:
              type: string
              example: "Transpose completed successfully"
      404:
        description: 악보 ID를 찾을 수 없음
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Score not found"
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


@transform_bp.route('/score/<int:score_id>/melody', methods=['POST'])
def melody_extract_route(score_id):
    """
    멜로디 추출 API
    ---
    tags:
      - transform
    summary: 업로드된 악보에서 특정 마디 범위의 멜로디를 추출하고 MP3 파일을 생성합니다
    parameters:
      - in: path
        name: score_id
        required: true
        schema:
          type: integer
        description: 멜로디를 추출할 대상 악보의 ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            start_measure:
              type: integer
              example: 1
              description: 시작 마디
            end_measure:
              type: integer
              example: 8
              description: 종료 마디
          required:
            - start_measure
            - end_measure
    responses:
      200:
        description: 멜로디 추출 완료
        schema:
          type: object
          properties:
            result_id:
              type: integer
              example: 205
            mp3_path:
              type: string
              example: "convert_result/205.mp3"
            message:
              type: string
              example: "Melody extracted from measure 1 to 8"
      404:
        description: 악보 ID를 찾을 수 없음
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Score not found"
    """
    data = request.get_json()
    start = data.get('start_measure')
    end = data.get('end_measure')

    score = Score.query.get(score_id)
    if not score:
        return jsonify({'error': 'Score not found'}), 404

    result_id = extract_melody(score, start, end)

    result = Result.query.get(result_id)
    mp3_path = result.audio_path if result else f"convert_result/{result_id}.mp3"

    return jsonify({
        'result_id': result_id,
        'mp3_path': mp3_path,
        'message': f'Melody extracted from measure {start} to {end}'
    }), 200
