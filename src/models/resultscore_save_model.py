from .db import db

class ResultScoreSave(db.Model):
    __tablename__ = 'result_score_save'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('results.id'), primary_key=True)
    saved_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', back_populates='saved_result_scores')
    result = db.relationship('Result', back_populates='saved_by_users')
