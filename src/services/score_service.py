from src.models.db import db
from src.models.score_model import Score

# ✅ 파일 업로드 시 DB에 저장 (xml/pdf 경로는 null)
def save_score_file_to_db(filename: str) -> int:
    new_score = Score(original_filename=filename)
    db.session.add(new_score)
    db.session.commit()
    return new_score.id

# ✅ xml/pdf 변환 결과를 DB에 업데이트
def update_score_with_recognized_data(score_id: int, xml_path: str, pdf_path: str) -> int:
    score = Score.query.get(score_id)
    if score:
        score.xml_path = xml_path
        score.pdf_path = pdf_path
        db.session.commit()
        return score.id
    else:
        print(f"⚠️ Score with id {score_id} not found for update.")
        return -1

# ✅ 악보 정보 조회
def get_score(score_id: int) -> dict:
    score = Score.query.get(score_id)
    if score:
        return {
            'score_id': score.id,
            'original_filename': score.original_filename,
            'xml_path': score.xml_path,
            'pdf_path': score.pdf_path,
            'created_at': score.created_at.isoformat()
        }
    else:
        print(f"⚠️ Score with id {score_id} not found for get_score.")
        return None

# ✅ 악보 삭제
def delete_score(score_id: int) -> bool:
    score = Score.query.get(score_id)
    if score:
        db.session.delete(score)
        db.session.commit()
        return True
    else:
        print(f"⚠️ Score with id {score_id} not found for delete.")
        return False
