import os
import cv2
import subprocess
import platform
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from flasgger import swag_from

from ML.src.makexml.MakeScore import MakeScore
from src.services.score_service import (
    save_score_file_to_db,
    update_score_with_recognized_data,
    get_score,
    delete_score
)
from src.models.score_model import Score
from src.models.db import db

from music21 import converter  # 🎵 키 분석을 위해 추가

score_bp = Blueprint('score', __name__)

# ✅ 1. 파일 업로드
@score_bp.route('/score/upload', methods=['POST'])
@swag_from({
    'tags': ['score'],
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': '업로드할 악보 이미지'
        }
    ],
    'responses': {
        201: {'description': '업로드 성공'},
        400: {'description': '파일 없음'},
        500: {'description': '내부 서버 오류'}
    }
})
def upload_score_file():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    try:
        upload_dir = 'uploaded_scores'
        os.makedirs(upload_dir, exist_ok=True)

        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # DB에 업로드 정보 저장
        score_id = save_score_file_to_db(filename)

        return jsonify({
            'score_id': score_id,
            'message': 'Score file uploaded successfully'
        }), 201

    except Exception as e:
        print('🔥 upload_score_file 에러:', e)
        return jsonify({'error': str(e)}), 500

# ✅ 2. 인식 및 변환 (key도 함께 반환)
@score_bp.route('/score/recognize', methods=['POST'])
@swag_from({
    'tags': ['score'],
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'score_id': {
                        'type': 'integer',
                        'description': '인식할 score_id'
                    }
                },
                'required': ['score_id']
            }
        }
    ],
    'responses': {
        200: {'description': '인식 및 변환 성공'},
        400: {'description': '잘못된 요청'},
        404: {'description': '악보를 찾을 수 없음'},
        500: {'description': '내부 서버 오류'}
    }
})
def recognize_score():
    data = request.get_json()
    score_id = data.get('score_id')
    if not score_id:
        return jsonify({'error': 'score_id is required'}), 400

    try:
        score = Score.query.get(score_id)
        if not score:
            return jsonify({'error': 'Score not found'}), 404

        file_path = os.path.join('uploaded_scores', score.original_filename)

        img = cv2.imread(file_path, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({'error': 'Failed to load image'}), 500

        img_list = [img]

        # 🎯 MakeScore가 tuple로 결과를 반환하는 경우 첫 번째 요소만 사용!
        result = MakeScore.make_score(img_list)
        if isinstance(result, tuple):
            score_obj = result[0]
        else:
            score_obj = result

        convert_dir = 'convert_result'
        os.makedirs(convert_dir, exist_ok=True)

        temp_id = os.urandom(4).hex()
        xml_path = os.path.join(convert_dir, f'{temp_id}.xml')
        pdf_path = os.path.join(convert_dir, f'{temp_id}.pdf')
        MakeScore.score_to_xml(score_obj, temp_id)

        # MuseScore로 PDF 변환
        if platform.system() == "Windows":
            mscore_path = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
        else:
            mscore_path = os.path.join("squashfs-root", "mscore4portable")
        subprocess.run([mscore_path, xml_path, "-o", pdf_path], check=True)

        # 🎯 music21로 XML 파싱 & 키 분석
        parsed_score = converter.parse(xml_path)
        key_analysis = parsed_score.analyze('key')
        detected_key = key_analysis.tonic.name if key_analysis else 'Unknown'

        # DB에 결과 업데이트 (key도 함께)
        score.xml_path = xml_path
        score.pdf_path = pdf_path
        score.key = detected_key
        db.session.commit()

        return jsonify({
            'score_id': score_id,
            'xml_path': xml_path,
            'pdf_path': pdf_path,
            'key': detected_key,  # 🎯 추가됨
            'message': 'Score recognized and XML/PDF generated successfully'
        }), 200

    except Exception as e:
        print('🔥 recognize_score 에러:', e)
        return jsonify({'error': str(e)}), 500

# ✅ 3. 조회
@score_bp.route('/score/<int:score_id>', methods=['GET'])
@swag_from({
    'tags': ['score'],
    'parameters': [
        {
            'name': 'score_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '조회할 악보 ID'
        }
    ],
    'responses': {
        200: {'description': '조회 성공'},
        404: {'description': '악보를 찾을 수 없음'}
    }
})
def get_score_info(score_id):
    result = get_score(score_id)
    if result:
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Score not found'}), 404

# ✅ 4. 삭제
@score_bp.route('/score/<int:score_id>', methods=['DELETE'])
@swag_from({
    'tags': ['score'],
    'parameters': [
        {
            'name': 'score_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '삭제할 악보 ID'
        }
    ],
    'responses': {
        200: {'description': '삭제 성공'},
        404: {'description': '악보를 찾을 수 없음'}
    }
})
def delete_score_info(score_id):
    success = delete_score(score_id)
    if success:
        return jsonify({'message': 'Score deleted'}), 200
    else:
        return jsonify({'error': 'Score not found'}), 404
