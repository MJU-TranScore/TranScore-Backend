import os
import requests
from flask import Blueprint, redirect, request, jsonify
from src.config import Config
from src.services.auth_service import handle_kakao_login, refresh_access_token 
from flasgger import swag_from

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/kakao')
def kakao_login():
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={Config.KAKAO_CLIENT_ID}"
        f"&redirect_uri={Config.KAKAO_REDIRECT_URI}"
        f"&response_type=code"
    )
    return redirect(kakao_auth_url)


@auth_bp.route('/kakao/callback')
def kakao_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400

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

    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    kakao_id = user_info.get("id")
    nickname = user_info.get("properties", {}).get("nickname", "")
    profile_image = user_info.get("properties", {}).get("profile_image", "")

    result = handle_kakao_login(kakao_id, nickname, profile_image)
    return jsonify(result), 200


@auth_bp.route('/kakao/token', methods=['POST'])
@swag_from({
    'summary': '카카오 인가 코드(code)를 받아 JWT를 발급 (OAuth 처리 + JWT 발급)',
    'tags': ['auth'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['code'],
                'properties': {
                    'code': {
                        'type': 'string',
                        'example': '6aeakys-XXX'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': '로그인 성공 및 JWT 발급',
            'schema': {
                'type': 'object',
                'properties': {
                    'access_token': {'type': 'string'},
                    'refresh_token': {'type': 'string'}
                }
            }
        },
        400: {
            'description': '인증 코드 누락 또는 실패'
        }
    }
})

def kakao_token():
    try:
        # 요청 내용 디버깅 로그
        print("🔥 /auth/kakao/token 요청 도착")
        print("🔥 REQUEST HEADERS:", dict(request.headers))
        print("🔥 RAW BODY:", request.get_data(as_text=True))
        
        # JSON이든 form이든 유연하게 처리
        data = request.get_json(silent=True) or request.form or request.values
        code = data.get('code') if data else None

        if not code:
            print("❌ No code provided")
            return jsonify({'error': 'No code provided'}), 400

        # 카카오 토큰 요청
        token_url = "https://kauth.kakao.com/oauth/token"
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': Config.KAKAO_CLIENT_ID,
            'redirect_uri': Config.KAKAO_REDIRECT_URI,
            'code': code,
        }
        token_response = requests.post(token_url, data=token_data)
        print("🔐 Kakao token response:", token_response.status_code, token_response.text)

        token_json = token_response.json()
        access_token = token_json.get('access_token')
        if not access_token:
            print("❌ Failed to get access token")
            return jsonify({'error': 'Failed to get Kakao access token'}), 400

        # 유저 정보 요청
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(user_info_url, headers=headers)
        user_info = user_info_response.json()

        kakao_id = user_info.get("id")
        nickname = user_info.get("properties", {}).get("nickname", "")
        profile_image = user_info.get("properties", {}).get("profile_image", "")

        result = handle_kakao_login(kakao_id, nickname, profile_image)
        return jsonify(result), 200

    except Exception as e:
        print("❌ Unexpected error in kakao_token:", str(e))
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500




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
  
@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    로그아웃 처리 (클라이언트 토큰 삭제 방식)
    ---
    tags:
      - auth
    summary: 로그아웃
    description: 클라이언트가 저장한 access_token 및 refresh_token을 삭제하면 로그아웃이 완료됩니다. 서버에서는 별도 처리를 하지 않습니다.
    responses:
      200:
        description: 로그아웃 성공
        schema:
          type: object
          properties:
            message:
              type: string
              example: "로그아웃 완료"
    """
    return jsonify({"message": "로그아웃 완료"}), 200
