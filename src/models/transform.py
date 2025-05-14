from datetime import datetime
from .db import db


class TransformTranspose(db.Model):
    __tablename__ = 'transform_transpose'

    id = db.Column(db.String(64), primary_key=True)  # 변환 결과 고유 ID (UUID)
    score_id = db.Column(db.String(64), db.ForeignKey('scores.id'), nullable=False)
    pdf_path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
class TransformMelody(db.Model):
    __tablename__ = 'transform_melody'

    id = db.Column(db.String(64), primary_key=True)
    score_id = db.Column(db.String(64), db.ForeignKey('scores.id'), nullable=False)
    mp3_path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

