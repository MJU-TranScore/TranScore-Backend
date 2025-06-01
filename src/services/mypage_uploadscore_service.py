from src.models.db import db
from src.models.uploadscore_save_model import UploadScoreSave

def save_upload_score(user_id, score_id):
    exists = UploadScoreSave.query.filter_by(user_id=user_id, score_id=score_id).first()
    if exists:
        return False  # 이미 저장됨

    save = UploadScoreSave(user_id=user_id, score_id=score_id)
    db.session.add(save)
    db.session.commit()
    return True

def get_saved_upload_scores(user_id):
    return UploadScoreSave.query.filter_by(user_id=user_id).all()

def delete_upload_score(user_id, score_id):
    save = UploadScoreSave.query.filter_by(user_id=user_id, score_id=score_id).first()
    if not save:
        return False
    db.session.delete(save)
    db.session.commit()
    return True
