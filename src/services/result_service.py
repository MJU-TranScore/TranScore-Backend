import os
from flask import send_file, jsonify
from src.models.result_model import Result

# 내부 경로 정리 함수
def normalize_path(path):
    return os.path.normpath(path) if path else None

# 5-1: 키 변경된 악보 결과 이미지
def get_transpose_image(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'transpose':
        raise FileNotFoundError("키 변경 악보 이미지 결과를 찾을 수 없습니다")
    
    # ✅ 절대 경로로 변환
    image_path = normalize_path(result.image_path)
    abs_image_path = os.path.join(os.getcwd(), image_path) if image_path else None

    if not abs_image_path or not os.path.exists(abs_image_path):
        raise FileNotFoundError(f"키 변경 악보 이미지 결과를 찾을 수 없습니다: {abs_image_path}")

    # ✅ 이미지 반환
    return send_file(abs_image_path, mimetype='image/png')

# 5-1: 키 변경된 PDF 파일 다운로드
def download_transpose_file(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'transpose':
        raise FileNotFoundError("키 변경 악보 다운로드 파일을 찾을 수 없습니다")
    
    download_path = normalize_path(result.download_path)
    abs_download_path = os.path.join(os.getcwd(), download_path) if download_path else None

    if not abs_download_path or not os.path.exists(abs_download_path):
        raise FileNotFoundError("키 변경 악보 다운로드 파일을 찾을 수 없습니다")
    
    return send_file(abs_download_path, as_attachment=True)

# 5-2: 가사 추출 결과 텍스트
def get_lyrics_text(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'lyrics' or not result.text_content:
        raise FileNotFoundError("가사 텍스트 결과를 찾을 수 없습니다")
    return jsonify({"text_content": result.text_content})

# 가사 다운로드 파일
def download_lyrics_file(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'lyrics':
        raise FileNotFoundError("가사 다운로드 파일을 찾을 수 없습니다")
    
    download_path = normalize_path(result.download_path)
    abs_download_path = os.path.join(os.getcwd(), download_path) if download_path else None

    if not abs_download_path or not os.path.exists(abs_download_path):
        raise FileNotFoundError("가사 다운로드 파일을 찾을 수 없습니다")
    
    return send_file(abs_download_path, as_attachment=True)

# 5-3: 멜로디 메타 정보
def get_melody_meta_info(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'melody' or not result.meta_info:
        raise FileNotFoundError("멜로디 메타 정보가 없습니다")
    return jsonify({"meta_info": result.meta_info})

# 멜로디 오디오 MP3
def get_melody_audio(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'melody':
        raise FileNotFoundError("멜로디 오디오 파일을 찾을 수 없습니다")
    
    audio_path = normalize_path(result.audio_path)
    abs_audio_path = os.path.join(os.getcwd(), audio_path) if audio_path else None

    if not abs_audio_path or not os.path.exists(abs_audio_path):
        raise FileNotFoundError("멜로디 오디오 파일을 찾을 수 없습니다")
    
    return send_file(abs_audio_path, mimetype='audio/mpeg', as_attachment=True)
