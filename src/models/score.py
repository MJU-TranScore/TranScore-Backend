from datetime import datetime
from .db import db

class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.String(64), primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    xml_path = db.Column(db.String(512), nullable=False)
    pdf_path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
