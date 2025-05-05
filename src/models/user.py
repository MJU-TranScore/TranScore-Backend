from datetime import datetime
from .db import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(100), unique=True, nullable=False)  # 길이도 맞춤
    nickname = db.Column(db.String(100))
    profile_image = db.Column(db.String(255))  # ✅ 이름 통일
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.social_id}>"
