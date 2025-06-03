import os
from src.models.db import db
from src.models.score_model import Score

def save_score_file_to_db(filename: str, title: str = None) -> int:
    new_score = Score(original_filename=filename, title=title)
    db.session.add(new_score)
    db.session.commit()
    return new_score.id

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

def get_score(score_id: int) -> dict:
    score = Score.query.get(score_id)
    if score:
        return {
            'score_id': score.id,
            'title': score.title,
            'original_filename': score.original_filename,
            'xml_path': score.xml_path,
            'pdf_path': score.pdf_path,
            'created_at': score.created_at.isoformat(),
            'key': score.key
        }
    else:
        print(f"⚠️ Score with id {score_id} not found for get_score.")
        return None

def delete_score(score_id: int) -> bool:
    score = Score.query.get(score_id)
    if score:
        db.session.delete(score)
        db.session.commit()
        return True
    else:
        print(f"⚠️ Score with id {score_id} not found for delete.")
        return False

# ✅ 가장 최신 인식된 악보 정보 (MelodyExtractPage에서 사용)
import cv2

def get_latest_score_info() -> dict:
    score = Score.query.order_by(Score.created_at.desc()).first()
    if not score:
        return None

    image_path = os.path.join('uploaded_scores', score.original_filename).replace('\\', '/')
    abs_path = os.path.join(os.getcwd(), image_path)
    image = cv2.imread(abs_path)
    h, w = image.shape[:2]

    return {
        'score_id': score.id,
        'title': score.title,
        'imageUrl': f"http://localhost:5000/{image_path}",
        'totalMeasures': 50,
        'imageWidth': w,
        'imageHeight': h
    }




