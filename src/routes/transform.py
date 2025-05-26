from flask import Blueprint, request, jsonify
from src.utils.transpose_helper import transpose_key
from src.models.score import Score
from src.models.result import Result
from src.services.transform_service import perform_transpose, extract_melody, extract_lyrics

transform_bp = Blueprint('transform', __name__)


@transform_bp.route('/transpose-preview', methods=['POST'])
def transposePreviewRoute():
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
            currentKey:
              type: string
              example: "F"
              description: 현재 키
            shift:
              type: integer
              example: -1
              description: 변환할 반음 수
          required:
            - currentKey
            - shift
    responses:
      200:
        description: 변환된 키 정보
        schema:
          type: object
          properties:
            transposedKey:
              type: string
              example: "E"
            message:
              type: string
              example: "F → E (shift -1)"
      400:
        description: 잘못된 요청
    """
    data = request.get_json()
    currentKey = data.get('currentKey')
    shift = data.get('shift')

    if currentKey is None or shift is None:
        return jsonify({'error': 'currentKey and shift are required'}), 400

    try:
        shift = int(shift)
        transposedKey = transpose_key(currentKey, shift)
        return jsonify({
            'transposedKey': transposedKey,
            'message': f"{currentKey.upper()} → {transposedKey} (shift {shift})"
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@transform_bp.route('/score/<int:scoreId>/transpose', methods=['POST'])
def transformTransposeRoute(scoreId):
    """
    키 변경 수행 API
    ---
    tags:
      - transform
    summary: 업로드된 악보를 지정된 반음 수만큼 키 변경하고 결과 PDF를 생성합니다
    parameters:
      - in: path
        name: scoreId
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
            resultId:
              type: integer
              example: 101
            message:
              type: string
              example: "Transpose completed successfully"
      404:
        description: 악보 ID를 찾을 수 없음
    """
    score = Score.query.get(scoreId)
    if not score:
        return jsonify({'error': 'Score not found'}), 404

    data = request.get_json()
    shift = data.get('shift')
    if shift is None:
        return jsonify({'error': 'shift is required'}), 400

    resultId = perform_transpose(score, int(shift))

    return jsonify({
        'resultId': resultId,
        'message': 'Transpose completed successfully'
    }), 201


@transform_bp.route('/score/<int:scoreId>/lyrics', methods=['POST'])
def lyricsExtractRoute(scoreId):
    """
    가사 추출 API
    ---
    tags:
      - transform
    summary: 업로드된 악보에서 가사를 추출하여 텍스트 파일로 저장하고 결과 ID를 반환합니다
    parameters:
      - in: path
        name: scoreId
        required: true
        schema:
          type: integer
        description: 가사를 추출할 대상 악보의 ID
    responses:
      200:
        description: 가사 추출 완료
        schema:
          type: object
          properties:
            resultId:
              type: integer
              example: 301
            textPath:
              type: string
              example: "convert_result/301.txt"
            message:
              type: string
              example: "Lyrics extracted successfully"
      404:
        description: 악보 ID를 찾을 수 없음
    """
    score = Score.query.get(scoreId)
    if not score:
        return jsonify({'error': 'Score not found'}), 404

    resultId = extract_lyrics(score)
    result = Result.query.get(resultId)
    if not result:
        return jsonify({"error": "Result not found"}), 500

    return jsonify({
        'resultId': resultId,
        'textPath': result.download_path,
        'message': 'Lyrics extracted successfully'
    }), 200


@transform_bp.route('/score/<int:scoreId>/melody', methods=['POST'])
def melodyExtractRoute(scoreId):
    """
    멜로디 추출 API
    ---
    tags:
      - transform
    summary: 업로드된 악보에서 특정 마디 범위의 멜로디를 추출하고 MP3 파일을 생성합니다
    parameters:
      - in: path
        name: scoreId
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
            startMeasure:
              type: integer
              example: 1
              description: 시작 마디
            endMeasure:
              type: integer
              example: 8
              description: 종료 마디
          required:
            - startMeasure
            - endMeasure
    responses:
      200:
        description: 멜로디 추출 완료
        schema:
          type: object
          properties:
            resultId:
              type: integer
              example: 205
            mp3Path:
              type: string
              example: "convert_result/205.mp3"
            message:
              type: string
              example: "Melody extracted from measure 1 to 8"
      404:
        description: 악보 ID를 찾을 수 없음
    """
    data = request.get_json()
    start = data.get('startMeasure')
    end = data.get('endMeasure')

    score = Score.query.get(scoreId)
    if not score:
        return jsonify({'error': 'Score not found'}), 404

    resultId = extract_melody(score, start, end)
    result = Result.query.get(resultId)
    if not result:
        return jsonify({"error": "Result not found"}), 500

    return jsonify({
        'resultId': resultId,
        'mp3Path': result.audio_path,
        'message': f'Melody extracted from measure {start} to {end}'
    }), 200
