from src.models.score import db, Score

def save_score_to_db(filename, xml_path, pdf_path):
    new_score = Score(
        original_filename=filename,
        xml_path=xml_path,
        pdf_path=pdf_path
    )
    db.session.add(new_score)
    db.session.commit()
    return new_score.id  # 새로 생성된 정수 ID를 반환

def get_score(score_id):
    score = Score.query.get(score_id)
    if score:
        return {
            'score_id': score.id,
            'original_filename': score.original_filename,
            'xml_path': score.xml_path,
            'pdf_path': score.pdf_path,
            'created_at': score.created_at.isoformat()
        }
    return None

def delete_score(score_id):
    score = Score.query.get(score_id)
    if score:
        db.session.delete(score)
        db.session.commit()
        return True
    return False
