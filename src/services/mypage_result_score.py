from src.models.db import db
from src.models.resultScore_save import ResultScoreSave
from src.models.result import Result
from src.models.user import User

def saveResultScore(userId, resultId):
    exists = ResultScoreSave.query.filter_by(user_id=userId, result_id=resultId).first()
    if exists:
        return False  # 이미 저장됨

    save = ResultScoreSave(user_id=userId, result_id=resultId)
    db.session.add(save)
    db.session.commit()
    return True


def getSavedResultScores(userId, resultType=None):
    query = ResultScoreSave.query.join(Result).filter(ResultScoreSave.user_id == userId)
    if resultType:
        query = query.filter(Result.type == resultType)
    return query.all()


def deleteResultScore(userId, resultId):
    save = ResultScoreSave.query.filter_by(user_id=userId, result_id=resultId).first()
    if not save:
        return False
    db.session.delete(save)
    db.session.commit()
    return True
