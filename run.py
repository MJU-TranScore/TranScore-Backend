from flask import Flask, send_from_directory
from src import create_app
from src.models import db
import os

app = create_app()

# ✅ uploaded_scores 정적 경로 추가!
@app.route('/uploaded_scores/<path:filename>')
def uploaded_scores(filename):
    # 현재 경로를 기준으로 uploaded_scores 폴더 경로 지정
    return send_from_directory(os.path.join(os.getcwd(), 'uploaded_scores'), filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
