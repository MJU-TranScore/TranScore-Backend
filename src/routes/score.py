from flask import Blueprint, request, jsonify
from src.services.score_service import upload_score, get_score, delete_score

score_bp = Blueprint('score', __name__)

@score_bp.route('/score/upload', methods=['POST'])
def upload_score_route():
    
    """
    악보 이미지 업로드 API
    ---
    tags:
      - score
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: 업로드할 악보 이미지
    responses:
      201:
        description: 업로드 성공
      400:
        description: 파일 없음
    """
    
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    result = upload_score(file)
    return jsonify(result), 201

@score_bp.route('/score/<int:scoreId>', methods=['GET'])
def get_score_route(score_id):
  
    """
    악보 인식 결과 조회 API
    ---
    tags:
      - score
    security:
      - Bearer: []
    parameters:
      - name: score_id
        in: path
        type: string
        required: true
        description: 조회할 악보의 ID
    responses:
      200:
        description: 조회 성공
        examples:
          application/json:
            score_id: "abc123"
            status: "success"
            result_url: "https://example.com/score/result.png"
      404:
        description: 해당 악보 없음
    """
    
    result = get_score(score_id)
    if result:
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Score not found'}), 404

@score_bp.route('/score/<int:scoreId>', methods=['DELETE'])
def delete_score_route(score_id):
  
    """
    악보 인식 결과 삭제 API
    ---
    tags:
      - score
    security:
      - Bearer: []
    parameters:
      - name: score_id
        in: path
        type: string
        required: true
        description: 삭제할 악보의 ID
    responses:
      200:
        description: 삭제 성공
      404:
        description: 해당 악보 없음
    """
    
    success = delete_score(score_id)
    if success:
        return jsonify({'message': 'Score deleted'}), 200
    else:
        return jsonify({'error': 'Score not found'}), 404
