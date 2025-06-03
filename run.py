from flask import send_from_directory
from src import create_app
from src.models import db
import os

app = create_app()

# ✅ uploaded_scores 정적 경로
@app.route('/uploaded_scores/<path:filename>')
def uploaded_scores(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'uploaded_scores'), filename)

# ✅ convert_result 정적 경로
@app.route('/convert_result/<path:filename>')
def convert_result(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'convert_result'), filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
