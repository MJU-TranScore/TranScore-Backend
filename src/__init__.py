from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from flask_migrate import Migrate
from src.config import Config
from src.models import db

def create_app():
    app = Flask(__name__)

    # ✅ 전체 앱에 CORS 설정 (OPTIONS preflight 포함)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    # ✅ Flask 설정 로드
    app.config.from_object(Config)

    # ✅ Swagger 초기화
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

    # ✅ Flask-Migrate 초기화
    Migrate(app, db)

    # ✅ 라우트 등록
    from src.routes.auth_route import auth_bp
    from src.routes.user_route import user_bp
    from src.routes.score_route import score_bp
    from src.routes.transform_route import transform_bp
    from src.routes.result_route import result_bp
    from src.routes.mypage_uploadscore_route import upload_score_bp
    from src.routes.mypage_resultscore_route import result_score_bp

    # ✅ Blueprint 등록 (transform만 /transform prefix 부여)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(score_bp)
    app.register_blueprint(transform_bp, url_prefix='/transform')  # 🔥 핵심 수정
    app.register_blueprint(result_bp)
    app.register_blueprint(upload_score_bp)
    app.register_blueprint(result_score_bp)

    return app
