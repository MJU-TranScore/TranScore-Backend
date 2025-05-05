import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    
    KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
    KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
    
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCORE_UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads', 'scores')

# 폴더 없으면 생성
os.makedirs(SCORE_UPLOAD_DIR, exist_ok=True)
