from datetime import datetime
from .db import db

class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    original_filename = db.Column(db.String(255), nullable=False)
    xml_path = db.Column(db.String(512), nullable=False)
    pdf_path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    saved_by_users = db.relationship(
        'UploadScoreSave',
        back_populates='score',
        cascade='all, delete-orphan'
    )
