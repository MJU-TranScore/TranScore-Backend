from src.models.db import db
from src.models.uploadScore_save import UploadScoreSave
from src.models.score import Score
from src.models.user import User

def saveUploadScore(userId, scoreId):
    exists = UploadScoreSave.query.filter_by(user_id=userId, score_id=scoreId).first()
    if exists:
        return False  # 이미 저장됨

    save = UploadScoreSave(user_id=userId, score_id=scoreId)
    db.session.add(save)
    db.session.commit()
    return True


def getSavedUploadScores(userId):
    return UploadScoreSave.query.filter_by(user_id=userId).all()


def deleteUploadScore(userId, scoreId):
    save = UploadScoreSave.query.filter_by(user_id=userId, score_id=scoreId).first()
    if not save:
        return False
    db.session.delete(save)
    db.session.commit()
    return True
