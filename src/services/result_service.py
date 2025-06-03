import os
from flask import send_file, jsonify
from src.models.result_model import Result

def normalize_path(path):
    return os.path.normpath(path) if path else None

# 키 변경된 이미지
def get_transpose_image(result_id):
    result = Result.query.get(result_id)

    if not result or result.type != 'transpose':
        raise FileNotFoundError("키 변경 악보 이미지 결과를 찾을 수 없습니다")

    if not result.image_path:
        raise FileNotFoundError("이미지 경로 정보가 DB에 없습니다")

    image_path = normalize_path(result.image_path)
    abs_image_path = os.path.abspath(image_path)

    if not os.path.exists(abs_image_path):
        raise FileNotFoundError(f"이미지 파일이 존재하지 않음: {abs_image_path}")

    return send_file(abs_image_path, mimetype='image/png')


def download_transpose_file(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'transpose':
        raise FileNotFoundError("키 변경 악보 다운로드 파일을 찾을 수 없습니다")

    download_path = normalize_path(result.download_path)
    abs_download_path = os.path.join(os.getcwd(), download_path) if download_path else None

    if not abs_download_path or not os.path.exists(abs_download_path):
        raise FileNotFoundError("키 변경 악보 다운로드 파일을 찾을 수 없습니다")

    return send_file(abs_download_path, as_attachment=True)


def get_lyrics_text(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'lyrics' or not result.text_content:
        raise FileNotFoundError("가사 텍스트 결과를 찾을 수 없습니다")
    return jsonify({"text_content": result.text_content})


def download_lyrics_file(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'lyrics':
        raise FileNotFoundError("가사 다운로드 파일을 찾을 수 없습니다")

    download_path = normalize_path(result.download_path)
    abs_download_path = os.path.join(os.getcwd(), download_path) if download_path else None

    if not abs_download_path or not os.path.exists(abs_download_path):
        raise FileNotFoundError("가사 다운로드 파일을 찾을 수 없습니다")

    return send_file(abs_download_path, as_attachment=True)


def get_melody_meta_info(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'melody' or not result.meta_info:
        raise FileNotFoundError("멜로디 메타 정보가 없습니다")
    return jsonify({"meta_info": result.meta_info})


def get_melody_audio(result_id):
    result = Result.query.get(result_id)
    if not result or result.type != 'melody':
        raise FileNotFoundError("멜로디 오디오 파일을 찾을 수 없습니다")

    audio_path = normalize_path(result.audio_path)
    abs_audio_path = os.path.join(os.getcwd(), audio_path) if audio_path else None

    if not abs_audio_path or not os.path.exists(abs_audio_path):
        raise FileNotFoundError("멜로디 오디오 파일을 찾을 수 없습니다")

    return send_file(abs_audio_path, mimetype='audio/mpeg', as_attachment=True)
