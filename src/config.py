import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_CLIENT_ID = os.getenv("209363296101-g39k160rq6nvpal70l0e12ptq6vj7stl.apps.googleusercontent.com")
    GOOGLE_CLIENT_SECRET = os.getenv("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")
    GOOGLE_REDIRECT_URI = os.getenv("http://localhost:5000/auth/google/callback")
    KAKAO_CLIENT_ID = os.getenv("d2c88b5c51aa0c3c287ecb0ceb0a20ec")
    KAKAO_REDIRECT_URI = os.getenv("http://localhost:5000/auth/kakao/callback")
    JWT_SECRET_KEY = os.getenv("G9eMZkD6Ah7r8x3uBvK1cQz5L9sR2xT1DfNwVqYgHtEoUpIjXyCbNkMwZp9aQjWs")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
