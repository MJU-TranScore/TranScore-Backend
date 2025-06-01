from src.models.db import db
from src.models.resultscore_save_model import ResultScoreSave
from src.models.result_model import Result

def save_result_score(user_id, result_id):
    exists = ResultScoreSave.query.filter_by(user_id=user_id, result_id=result_id).first()
    if exists:
        return False  # 이미 저장됨

    save = ResultScoreSave(user_id=user_id, result_id=result_id)
    db.session.add(save)
    db.session.commit()
    return True

def get_saved_result_scores(user_id, result_type=None):
    query = ResultScoreSave.query.join(Result).filter(ResultScoreSave.user_id == user_id)
    if result_type:
        query = query.filter(Result.type == result_type)
    return query.all()

def delete_result_score(user_id, result_id):
    save = ResultScoreSave.query.filter_by(user_id=user_id, result_id=result_id).first()
    if not save:
        return False
    db.session.delete(save)
    db.session.commit()
    return True
