from .db import db

class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score_id = db.Column(db.Integer, db.ForeignKey('scores.id'), nullable=False)

    # 결과 타입: 'transpose', 'lyrics', 'melody'
    type = db.Column(db.String(50), nullable=False)

    # transpose용
    image_path = db.Column(db.String(512))
    download_path = db.Column(db.String(512))  # transpose/lyrics 공통

    # lyrics용
    text_content = db.Column(db.Text)

    # melody용
    audio_path = db.Column(db.String(512))     # mp3/wav 파일 경로
    meta_info = db.Column(db.JSON)             # 예: {"notes": [...], "tempo": 120}

    created_at = db.Column(db.DateTime, default=db.func.now())

    # ✅ ResultScoreSave와의 관계 설정 (마이페이지 저장용)
    saved_by_users = db.relationship(
        'ResultScoreSave',
        back_populates='result',
        cascade='all, delete-orphan'
    )
