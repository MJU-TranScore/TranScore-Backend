import os
import requests
from flask import Blueprint, redirect, request, jsonify
from src.config import Config
from src.services.auth_service import handle_kakao_login, refresh_access_token 

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 카카오 로그인 페이지 리다이렉트
@auth_bp.route('/kakao')
def kakao_login():
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={Config.KAKAO_CLIENT_ID}"
        f"&redirect_uri={Config.KAKAO_REDIRECT_URI}"
        f"&response_type=code"
    )
    return redirect(kakao_auth_url)

# 카카오 콜백 + JWT 발급 처리
@auth_bp.route('/kakao/callback')
def kakao_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    # 1. access token 요청
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': Config.KAKAO_CLIENT_ID,
        'redirect_uri': Config.KAKAO_REDIRECT_URI,
        'code': code,
    }
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    if not access_token:
        return jsonify({'error': 'Failed to get Kakao access token'}), 400

    # 2. 사용자 정보 요청
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    kakao_id = user_info.get("id")
    nickname = user_info.get("properties", {}).get("nickname", "")
    profile_image = user_info.get("properties", {}).get("profile_image", "")

    # 3. JWT 발급 및 DB 처리
    result = handle_kakao_login(kakao_id, nickname, profile_image)

    return jsonify(result), 200

@auth_bp.route('/kakao/token', methods=['POST'])
def kakao_token():
    
    """
    카카오 액세스 토큰 요청 및 JWT 발급
    ---
    tags:
      - auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              code:
                type: string
                example: "kakao_auth_code"
    responses:
      200:
        description: 로그인 성공 및 JWT 발급
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
      400:
        description: 인증 코드 누락 또는 실패
    """
    
    code = request.json.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    # 1. 카카오 access_token 요청
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': Config.KAKAO_CLIENT_ID,
        'redirect_uri': Config.KAKAO_REDIRECT_URI,
        'code': code,
    }
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    if not access_token:
        return jsonify({'error': 'Failed to get Kakao access token'}), 400

    # 2. 카카오 유저 정보 요청
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    kakao_id = user_info.get("id")
    nickname = user_info.get("properties", {}).get("nickname", "")
    profile_image = user_info.get("properties", {}).get("profile_image", "")

    # 3. 서비스로 넘기기
    result = handle_kakao_login(kakao_id, nickname, profile_image)

    return jsonify(result), 200

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    
    """
    JWT 리프레시 토큰을 이용해 액세스 토큰 재발급
    ---
    tags:
      - auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              refresh_token:
                type: string
                example: "abc.def.ghi"
    responses:
      200:
        description: 액세스 토큰 재발급 성공
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: 토큰 만료 또는 유효하지 않음
    """
    
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({"error": "No refresh token provided"}), 400

    new_access_token, error = refresh_access_token(refresh_token)
    if error:
        return jsonify({"error": error}), 401

    return jsonify({"access_token": new_access_token}), 200

@auth_bp.route("/test-token", methods=["POST"])
def issue_test_token():
    """
    테스트용 JWT 토큰 발급 API
    ---
    tags:
      - auth
    summary: 테스트용 JWT 토큰 발급
    description: 테스트용 유저 정보를 기반으로 accessToken, refreshToken을 발급합니다.
    responses:
      200:
        description: 토큰 발급 성공
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: "Access Token"
            refresh_token:
              type: string
              description: "Refresh Token"
    """
    # 테스트용 고정 유저 정보
    kakao_id = "test_kakao_12345"
    nickname = "테스트유저"
    profile_image = ""

    result = handle_kakao_login(kakao_id, nickname, profile_image)
    return jsonify(result), 200