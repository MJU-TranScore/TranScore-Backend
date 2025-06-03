from src.models.db import db
from src.models.resultscore_save_model import ResultScoreSave
from src.models.result_model import Result
from src.models.score_model import Score

def save_result_score(user_id, result_id, title=None):
    exists = ResultScoreSave.query.filter_by(user_id=user_id, result_id=result_id).first()
    if exists:
        print("⚠️ 이미 저장된 결과입니다:", result_id)
        return False  # 이미 저장됨

    save = ResultScoreSave(user_id=user_id, result_id=result_id)
    db.session.add(save)

    if title:
        print("🎯 전달받은 title:", title)
        result = Result.query.filter_by(id=result_id).first()
        if result:
            print("📌 커밋 전 기존 DB title:", result.title)
            result.title = title
            print("✅ 변경 후 result.title:", result.title)
        else:
            print("❌ 해당 result_id를 가진 결과가 없습니다:", result_id)
    else:
        print("⚠️ title이 전달되지 않음")

    db.session.commit()
    print("🧾 커밋 완료")

    return True




def get_saved_result_scores(user_id, result_type=None):
    """
    유저가 저장한 변환 결과 목록을 Result 및 Score와 함께 반환
    반환값: [(ResultScoreSave, Result, Score), ...]
    """
    query = (
        db.session.query(ResultScoreSave, Result, Score)
        .select_from(ResultScoreSave)
        .join(Result, ResultScoreSave.result_id == Result.id)
        .join(Score, Result.score_id == Score.id)
        .filter(ResultScoreSave.user_id == user_id)
    )
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
