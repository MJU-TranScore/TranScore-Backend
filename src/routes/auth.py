import requests
from flask import Blueprint, redirect, request, jsonify, url_for
from src.config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 카카오 로그인 요청
@auth_bp.route('/kakao')
def kakao_login():
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={Config.KAKAO_CLIENT_ID}&redirect_uri={Config.KAKAO_REDIRECT_URI}&response_type=code"
    return redirect(kakao_auth_url)

# 카카오 로그인 콜백
@auth_bp.route('/kakao/callback')
def kakao_callback():
    # 카카오에서 받은 인증 코드
    code = request.args.get('code')

    # 카카오 API로 액세스 토큰 요청
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': Config.KAKAO_CLIENT_ID,
        'redirect_uri': Config.KAKAO_REDIRECT_URI,
        'code': code,
    }
    
    # 액세스 토큰 요청
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    
    access_token = token_json.get('access_token')

    # 사용자 정보 요청
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()
    
    # 사용자 정보 반환
    return jsonify(user_info)
