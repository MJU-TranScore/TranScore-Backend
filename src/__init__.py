# src/__init__.py
from flask import Flask
from flasgger import Swagger
from src.config import Config
from src.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Swagger 초기화
    Swagger(app)
    db.init_app(app)

    # 블루프린트 등록
    from src.routes.auth import auth_bp
    from src.routes.index import index_bp  # index_bp 추가
    app.register_blueprint(auth_bp)
    app.register_blueprint(index_bp)  # index_bp 등록

    return app
