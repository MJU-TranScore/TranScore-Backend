from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from src.config import Config
from src.models import db

def create_app():
    app = Flask(__name__)

    # ✅ 전체 앱에 CORS 설정 (프리플라이트 OPTIONS 포함)
    # Origin: 프론트엔드 주소 허용
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    # ✅ Flask 설정 로드
    app.config.from_object(Config)

    # ✅ Swagger 초기화 (API 문서)
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

    # ✅ DB 초기화
    db.init_app(app)

    # ✅ 라우트/블루프린트 등록 및 Blueprint 별 CORS 허용
    from src.routes.auth_route import auth_bp
    from src.routes.user_route import user_bp
    from src.routes.score_route import score_bp
    from src.routes.transform_route import transform_bp
    from src.routes.result_route import result_bp
    from src.routes.mypage_uploadscore_route import upload_score_bp
    from src.routes.mypage_resultscore_route import result_score_bp

    # Blueprint 별 CORS 적용
    for bp in [auth_bp, user_bp, score_bp, transform_bp, result_bp, upload_score_bp, result_score_bp]:
        CORS(bp, origins="http://localhost:5173", supports_credentials=True)
        app.register_blueprint(bp)

    return app
