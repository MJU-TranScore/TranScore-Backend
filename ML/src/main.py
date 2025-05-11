import subprocess
import os
import sys
import cv2

# 경로 추가 (TranScore-Backend 루트를 sys.path에 포함)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ML.src.FilePath import BASE_DIR
from ML.src.makexml.MakeScore import MakeScore
# 로직엔 문제가 없는 것 같지만 객체탐지 성능이 떨어져 제대로된 악보가 나오지 않는다

def main():
    print("메인 실행")

    
    # 악보 만들기
    img_path = os.path.join(BASE_DIR, 'testfiles', '곰세마리.png') # 테스트용 이미지 경로
    img = cv2.imread(img_path)

    # 사용자로부터 파일을 받아 png 형식으로 변환하는 부분. 현재 없음 

    # ⚠ YOLO는 RGB 또는 BGR 3채널 이미지 필요 → 확인
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img_list = []
    img_list.append(img)

    score = MakeScore.make_score(img_list) # 실제 악보를 이용해 시도
    

    # 악보이름
    # score = MakeScore.make_score(None) # 현재는 미리 만들어진 데이터셋을 이용해 변환
    name = "곰세마리_테스트"
    
    # score 객체를 musicxml로 변환
    MakeScore.score_to_xml(score, name)
    
    # 만들어진 xml을 pdf로 변환환
    input_path = os.path.join(BASE_DIR, 'convert_result', name+".xml")
    # 출력 PDF 경로
    output_path = os.path.join(BASE_DIR, 'convert_result', name+".pdf")
    # MuseScore 실행 파일 경로
    mscore_path = "../squashfs-root/bin/mscore4portable" # 이게 변환하는거. squashfs-root 이게 리눅스용 musescore4를 cli에서 실행할 수 있도록 변환?시킨거

    # 출력 mp3 경로
    #output_path_mp3 = os.path.join(BASE_DIR, 'convert_result', name+".mp3")

    """ 성공적으로 됨. 현재는 다른것을테스트하기 위해 잠시 막아놓기
    # 키 변환
    diff = -2 # 변환시킬 만큼
    new_score_name = name+"키변환"+str(diff)
    new_score = MakeScore.change_key(score, diff) # 두번째 파라미터가 변경할 key. 현재 -2 ~ 2까지만만
    MakeScore.score_to_xml(new_score,new_score_name)
    input_path2 = os.path.join(BASE_DIR, 'convert_result', new_score_name+".xml")
    output_path2 = os.path.join(BASE_DIR, 'convert_result', new_score_name+".pdf")
    mscore_path2 = "../squashfs-root/bin/mscore4portable" 

    result2 = subprocess.run(
        [mscore_path2, input_path2, "-o", output_path2],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    """

    #정상적으로 잘 되었는지 확인
    result = subprocess.run(
        [mscore_path, input_path, "-o", output_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode == 0:
        print("PDF 변환 완료:", output_path)
    else:
        print("오류 발생:")
        print(result.stderr.decode())




if __name__ == "__main__":
    main()