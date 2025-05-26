from flask import Blueprint, jsonify
from flasgger import swag_from
from src.services.result_service import (
    get_transpose_image,
    download_transpose_file,
    get_lyrics_text,
    download_lyrics_file,
    get_melody_meta_info,
    get_melody_audio
)

result_bp = Blueprint('result', __name__, url_prefix='/result')


# 5-1. 키 변경된 악보 결과
@result_bp.route('/transpose/<int:resultId>/image', methods=['GET'])
@swag_from({
    'tags': ['Result - Transpose'],
    'parameters': [
        {
            'name': 'resultId',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '조회할 transpose 결과 ID'
        }
    ],
    'responses': {
        200: {'description': '변경된 악보 이미지 반환'},
        404: {'description': '결과 없음'}
    }
})
def transposeImage(resultId):
    try:
        return get_transpose_image(resultId)
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404


@result_bp.route('/transpose/<int:resultId>/download', methods=['GET'])
@swag_from({
    'tags': ['Result - Transpose'],
    'parameters': [
        {
            'name': 'resultId',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '다운로드할 transpose 결과 ID'
        }
    ],
    'responses': {
        200: {'description': '변경된 악보 다운로드 파일 반환'},
        404: {'description': '결과 없음'}
    }
})
def transposeDownload(resultId):
    try:
        return download_transpose_file(resultId)
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404


# 5-2. 가사 추출 결과
@result_bp.route('/lyrics/<int:resultId>/text', methods=['GET'])
@swag_from({
    'tags': ['Result - Lyrics'],
    'parameters': [
        {
            'name': 'resultId',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '조회할 lyrics 결과 ID'
        }
    ],
    'responses': {
        200: {'description': '가사 텍스트 반환'},
        404: {'description': '결과 없음'}
    }
})
def lyricsText(resultId):
    try:
        return get_lyrics_text(resultId)
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404


@result_bp.route('/lyrics/<int:resultId>/download', methods=['GET'])
@swag_from({
    'tags': ['Result - Lyrics'],
    'parameters': [
        {
            'name': 'resultId',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '다운로드할 lyrics 결과 ID'
        }
    ],
    'responses': {
        200: {'description': '가사 다운로드 파일 반환'},
        404: {'description': '결과 없음'}
    }
})
def lyricsDownload(resultId):
    try:
        return download_lyrics_file(resultId)
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404


# 5-3. 멜로디 추출 결과
@result_bp.route('/melody/<int:resultId>/info', methods=['GET'])
@swag_from({
    'tags': ['Result - Melody'],
    'parameters': [
        {
            'name': 'resultId',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '조회할 melody 결과 ID'
        }
    ],
    'responses': {
        200: {'description': '멜로디 메타 정보 반환'},
        404: {'description': '결과 없음'}
    }
})
def melodyInfo(resultId):
    try:
        return get_melody_meta_info(resultId)
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404


@result_bp.route('/melody/<int:resultId>/audio', methods=['GET'])
@swag_from({
    'tags': ['Result - Melody'],
    'parameters': [
        {
            'name': 'resultId',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '다운로드할 melody 오디오 ID'
        }
    ],
    'responses': {
        200: {'description': '오디오 파일 반환'},
        404: {'description': '결과 없음'}
    }
})
def melodyAudio(resultId):
    try:
        return get_melody_audio(resultId)
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
