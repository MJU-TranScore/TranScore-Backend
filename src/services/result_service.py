import os
from flask import send_file, jsonify
from src.models.result import Result

# 내부 경로 정리 함수
def normalizePath(path):
    return os.path.normpath(path) if path else None

# 5-1: 키 변경된 악보 결과 이미지
def getTransposeImage(resultId):
    result = Result.query.get(resultId)
    if not result or result.type != 'transpose':
        raise FileNotFoundError("키 변경 악보 이미지 결과를 찾을 수 없습니다")
    imagePath = normalizePath(result.image_path)
    if not imagePath or not os.path.exists(imagePath):
        raise FileNotFoundError("키 변경 악보 이미지 결과를 찾을 수 없습니다")
    return send_file(imagePath, mimetype='image/png')

# 키 변경된 PDF 파일 다운로드
def downloadTransposeFile(resultId):
    result = Result.query.get(resultId)
    if not result or result.type != 'transpose':
        raise FileNotFoundError("키 변경 악보 다운로드 파일을 찾을 수 없습니다")
    downloadPath = normalizePath(result.download_path)
    if not downloadPath or not os.path.exists(downloadPath):
        raise FileNotFoundError("키 변경 악보 다운로드 파일을 찾을 수 없습니다")
    return send_file(downloadPath, as_attachment=True)

# 5-2: 가사 추출 결과 텍스트
def getLyricsText(resultId):
    result = Result.query.get(resultId)
    if not result or result.type != 'lyrics' or not result.text_content:
        raise FileNotFoundError("가사 텍스트 결과를 찾을 수 없습니다")
    return jsonify({"textContent": result.text_content})

# 가사 다운로드 파일
def downloadLyricsFile(resultId):
    result = Result.query.get(resultId)
    if not result or result.type != 'lyrics':
        raise FileNotFoundError("가사 다운로드 파일을 찾을 수 없습니다")
    downloadPath = normalizePath(result.download_path)
    if not downloadPath or not os.path.exists(downloadPath):
        raise FileNotFoundError("가사 다운로드 파일을 찾을 수 없습니다")
    return send_file(downloadPath, as_attachment=True)

# 5-3: 멜로디 메타 정보
def getMelodyMetaInfo(resultId):
    result = Result.query.get(resultId)
    if not result or result.type != 'melody' or not result.meta_info:
        raise FileNotFoundError("멜로디 메타 정보가 없습니다")
    return jsonify({"metaInfo": result.meta_info})

# 멜로디 오디오 MP3
def getMelodyAudio(resultId):
    result = Result.query.get(resultId)
    if not result or result.type != 'melody':
        raise FileNotFoundError("멜로디 오디오 파일을 찾을 수 없습니다")
    audioPath = normalizePath(result.audio_path)
    if not audioPath or not os.path.exists(audioPath):
        raise FileNotFoundError("멜로디 오디오 파일을 찾을 수 없습니다")
    return send_file(audioPath, mimetype='audio/mpeg', as_attachment=True)
