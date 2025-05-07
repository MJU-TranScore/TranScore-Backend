from flask import Flask
from flasgger import Swagger
from src.config import Config
from src.models import db
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app) 
    
    app.config.from_object(Config)

    # Swagger 초기화
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "TranScore API",
            "description": "TranScore 백엔드 API 문서입니다. JWT 인증이 필요합니다.",
            "version": "1.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT 토큰을 입력하세요. 예: Bearer <your_token>"
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }

    Swagger(app, template=swagger_template)

    db.init_app(app)

    # 블루프린트 등록
    from src.routes.index import index_bp
    app.register_blueprint(index_bp)
    
    #transcore 블루프린트 등록
    from src.routes.auth import auth_bp
    from src.routes.user import user_bp
    from src.routes.score import score_bp  

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(score_bp)      

    return app
