import os
from flask import send_file, jsonify
from src.models.result import Result

# 5-1: 키 변경된 악보 결과
def get_transpose_image(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'transpose' or not result.image_path:
        raise FileNotFoundError("키 변경 악보 이미지 결과를 찾을 수 없습니다")
    return send_file(result.image_path, mimetype='image/png')

# 키 변경 파일일
def download_transpose_file(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'transpose' or not result.download_path:
        raise FileNotFoundError("키 변경 악보 다운로드 파일을 찾을 수 없습니다")
    return send_file(result.download_path, as_attachment=True)

# 5-2: 가사 추출 결과
def get_lyrics_text(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'lyrics' or not result.text_content:
        raise FileNotFoundError("가사 텍스트 결과를 찾을 수 없습니다")
    return jsonify({"text": result.text_content})

# 추출된 가사 파일일
def download_lyrics_file(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'lyrics' or not result.download_path:
        raise FileNotFoundError("가사 다운로드 파일을 찾을 수 없습니다")
    return send_file(result.download_path, as_attachment=True)

# 5-3: 멜로디 추출 결과
def get_melody_meta_info(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'melody' or not result.meta_info:
        raise FileNotFoundError("멜로디 메타 정보가 없습니다")
    return jsonify({"meta_info": result.meta_info})

# 추출된 오디오 파일일
def get_melody_audio(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'melody' or not result.audio_path:
        raise FileNotFoundError("멜로디 오디오 파일을 찾을 수 없습니다")
    return send_file(result.audio_path, mimetype='audio/mpeg', as_attachment=True)
