from datetime import datetime
from .db import db

class TransformTranspose(db.Model):
    __tablename__ = 'transform_transpose'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score_id = db.Column(db.Integer, db.ForeignKey('scores.id'), nullable=False)
    pdf_path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class TransformLyrics(db.Model):
    __tablename__ = 'transform_lyrics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score_id = db.Column(db.Integer, db.ForeignKey('scores.id'), nullable=False)
    lyrics_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class TransformMelody(db.Model):
    __tablename__ = 'transform_melody'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score_id = db.Column(db.Integer, db.ForeignKey('scores.id'), nullable=False)
    mp3_path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
