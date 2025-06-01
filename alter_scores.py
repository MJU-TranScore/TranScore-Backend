# alter_scores.py
from sqlalchemy import text
from src import create_app
from src.models.db import db

app = create_app()

with app.app_context():
    db.session.execute(text("ALTER TABLE scores MODIFY xml_path VARCHAR(512) NULL;"))
    db.session.execute(text("ALTER TABLE scores MODIFY pdf_path VARCHAR(512) NULL;"))
    db.session.commit()
    print("✅ DB 컬럼을 NULL 허용으로 변경 완료!")
