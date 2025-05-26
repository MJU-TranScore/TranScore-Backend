from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import cv2
import subprocess
import platform  # 운영체제 확인용

from ML.src.makexml.MakeScore import MakeScore
from src.services.score_service import save_score_to_db, get_score, delete_score

score_bp = Blueprint('score', __name__)

@score_bp.route('/score/upload', methods=['POST'])
def upload_score_route():
    """
    악보 이미지 업로드 API
    ---
    tags:
      - score
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
        description: 업로드 및 인식 성공
        examples:
          application/json:
            score_id: 1
            message: Score uploaded and recognized successfully
      400:
        description: 파일 없음
      500:
        description: 내부 서버 오류
    """
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    try:
        upload_dir = 'uploaded_scores'
        os.makedirs(upload_dir, exist_ok=True)

        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        img = cv2.imread(file_path, cv2.IMREAD_COLOR)
        img_list = [img]
        score = MakeScore.make_score(img_list)

        convert_dir = 'convert_result'
        os.makedirs(convert_dir, exist_ok=True)

        temp_id = os.urandom(4).hex()
        xml_path = os.path.join(convert_dir, temp_id + '.xml')
        pdf_path = os.path.join(convert_dir, temp_id + '.pdf')
        MakeScore.score_to_xml(score, temp_id)

        if platform.system() == "Windows":
            mscore_path = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
        else:
            mscore_path = os.path.join("squashfs-root", "mscore4portable")

        print("실행 명령어 확인:", [mscore_path, xml_path, "-o", pdf_path])
        subprocess.run([mscore_path, xml_path, "-o", pdf_path], check=True)

        score_id = save_score_to_db(filename, xml_path, pdf_path)

        return jsonify({
            'score_id': score_id,
            'message': 'Score uploaded and recognized successfully'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@score_bp.route('/score/<int:score_id>', methods=['GET'])
def get_score_route(score_id):
    """
    악보 정보 조회 API
    ---
    tags:
      - score
    parameters:
      - name: score_id
        in: path
        type: integer
        required: true
        description: 조회할 악보 ID
    responses:
      200:
        description: 조회 성공
        examples:
          application/json:
            score_id: 1
            original_filename: gomsong.png
            xml_path: convert_result/1.xml
            pdf_path: convert_result/1.pdf
            created_at: 2025-05-11T13:00:00
      404:
        description: 악보를 찾을 수 없음
    """
    result = get_score(score_id)
    if result:
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Score not found'}), 404


@score_bp.route('/score/<int:score_id>', methods=['DELETE'])
def delete_score_route(score_id):
    """
    악보 삭제 API
    ---
    tags:
      - score
    parameters:
      - name: score_id
        in: path
        type: integer
        required: true
        description: 삭제할 악보 ID
    responses:
      200:
        description: 삭제 성공
        examples:
          application/json:
            message: Score deleted
      404:
        description: 악보를 찾을 수 없음
    """
    success = delete_score(score_id)
    if success:
        return jsonify({'message': 'Score deleted'}), 200
    else:
        return jsonify({'error': 'Score not found'}), 404
