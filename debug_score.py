import cv2
from ML.src.makexml.MakeScore import MakeScore

# 1. 테스트 이미지 경로 설정
image_path = 'ML/testfiles/곰세마리.png'  # 실제 업로드된 악보 이미지 경로로 바꿔줘
img = cv2.imread(image_path, cv2.IMREAD_COLOR)
img_list = [img]

# 2. Score 객체 생성
score = MakeScore.make_score(img_list)

# 3. Score 객체 구조 출력
print(dir(score))
print(score.__dict__)
