from .db import db

class UploadScoreSave(db.Model):
    __tablename__ = 'upload_score_save'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    score_id = db.Column(db.Integer, db.ForeignKey('scores.id'), primary_key=True)
    saved_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', back_populates='saved_upload_scores')
    score = db.relationship('Score', back_populates='saved_by_users')
