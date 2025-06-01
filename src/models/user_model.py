from datetime import datetime
from .db import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(100), unique=True, nullable=False)  # 고유한 사용자 식별자
    nickname = db.Column(db.String(100))
    profile_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 업로드된 악보를 저장한 관계
    saved_upload_scores = db.relationship(
        'UploadScoreSave',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    # 결과 악보를 저장한 관계
    saved_result_scores = db.relationship(
        'ResultScoreSave',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<User {self.social_id}>"
