from src.models.db import db
from src.models.uploadscore_save_model import UploadScoreSave
from src.models.score_model import Score

# ✅ 업로드 악보 저장
def save_upload_score(user_id, score_id):
    exists = UploadScoreSave.query.filter_by(user_id=user_id, score_id=score_id).first()
    if exists:
        return False  # 이미 저장됨

    save = UploadScoreSave(user_id=user_id, score_id=score_id)
    db.session.add(save)
    db.session.commit()
    return True

# ✅ 업로드 악보 목록 조회 (Score 정보 함께 join)
def get_saved_upload_scores(user_id):
    return (
        db.session.query(UploadScoreSave, Score)
        .join(Score, UploadScoreSave.score_id == Score.id)
        .filter(UploadScoreSave.user_id == user_id)
        .all()
    )

# ✅ 업로드 악보 삭제
def delete_upload_score(user_id, score_id):
    save = UploadScoreSave.query.filter_by(user_id=user_id, score_id=score_id).first()
    if not save:
        return False
    db.session.delete(save)
    db.session.commit()
    return True
