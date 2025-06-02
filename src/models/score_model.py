# models/score_model.py
from datetime import datetime
from .db import db

class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=True)  # ✅ 제목 컬럼 추가!
    original_filename = db.Column(db.String(255), nullable=False)
    xml_path = db.Column(db.String(512), nullable=True)
    pdf_path = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    key = db.Column(db.String(10), nullable=True)
    
    saved_by_users = db.relationship(
        'UploadScoreSave',
        back_populates='score',
        cascade='all, delete-orphan'
    )
