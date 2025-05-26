from src.models.score import db, Score

def saveScoreToDb(filename, xmlPath, pdfPath):
    newScore = Score(
        original_filename=filename,
        xml_path=xmlPath,
        pdf_path=pdfPath
    )
    db.session.add(newScore)
    db.session.commit()
    return newScore.id  # 새로 생성된 정수 ID를 반환

def getScore(scoreId):
    score = Score.query.get(scoreId)
    if score:
        return {
            'scoreId': score.id,
            'originalFilename': score.original_filename,
            'xmlPath': score.xml_path,
            'pdfPath': score.pdf_path,
            'createdAt': score.created_at.isoformat()
        }
    return None

def deleteScore(scoreId):
    score = Score.query.get(scoreId)
    if score:
        db.session.delete(score)
        db.session.commit()
        return True
    return False
