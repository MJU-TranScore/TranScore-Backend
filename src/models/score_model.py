# models/score_model.py
from datetime import datetime
from .db import db

class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=True)
    original_filename = db.Column(db.String(255), nullable=False)
    xml_path = db.Column(db.String(512), nullable=True)
    pdf_path = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    key = db.Column(db.String(10), nullable=True)

    # ✅ 업로드한 악보 저장한 유저 정보
    saved_by_users = db.relationship(
        'UploadScoreSave',
        back_populates='score',
        cascade='all, delete-orphan'
    )

    # ✅ 변환 결과들 (Result와 연결)
    results = db.relationship(
        "Result",
        back_populates="score",
        cascade="all, delete-orphan"
    )
