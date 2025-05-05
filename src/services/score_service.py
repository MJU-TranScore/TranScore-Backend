import os
from werkzeug.utils import secure_filename
from src.config import SCORE_UPLOAD_DIR

# 임시 DB 시뮬레이션
score_storage = {}
score_id_counter = 1

def upload_score(file):
    global score_id_counter
    filename = secure_filename(file.filename)
    file_path = os.path.join(SCORE_UPLOAD_DIR, filename)
    file.save(file_path)

    score_data = {
        'id': score_id_counter,
        'filename': filename,
        'path': file_path
    }

    score_storage[score_id_counter] = score_data
    score_id_counter += 1

    return score_data

def get_score(score_id):
    return score_storage.get(score_id)

def delete_score(score_id):
    score = score_storage.pop(score_id, None)
    if score:
        os.remove(score['path'])
        return True
    return False
