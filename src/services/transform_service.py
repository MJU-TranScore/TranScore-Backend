import uuid
import os
import platform
import subprocess
import cv2

from music21 import midi, stream
from src.models.db import db
from src.models.score import Score
from src.models.result import Result  # ✅ 통합된 Result 모델
from ML.src.makexml.MakeScore import MakeScore

# OS별 실행 경로 설정
if platform.system() == "Windows":
    FFMPEG_CMD = r"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe"
    TIMIDITY_CMD = "timidity"
else:
    FFMPEG_CMD = "ffmpeg"
    TIMIDITY_CMD = "timidity"

def perform_transpose(score: Score, shift: int) -> int:
    """
    키 변경을 수행하고 결과 PDF를 생성해 Result 테이블에 저장
    """
    image_path = os.path.join('uploaded_scores', score.original_filename)
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    img_list = [img]

    score_obj = MakeScore.make_score(img_list)
    transposed_score = MakeScore.change_key(score_obj, shift)

    result_id = str(uuid.uuid4())
    convert_dir = 'convert_result'
    os.makedirs(convert_dir, exist_ok=True)

    xml_path = os.path.join(convert_dir, f"{result_id}.xml")
    pdf_path = os.path.join(convert_dir, f"{result_id}.pdf")

    MakeScore.score_to_xml(transposed_score, result_id)

    mscore_path = "../squashfs-root/bin/mscore4portable"
    subprocess.run([mscore_path, xml_path, "-o", pdf_path])

    result = Result(
        score_id=score.id,
        type='transpose',
        download_path=pdf_path
    )
    db.session.add(result)
    db.session.commit()

    return result.id

def extract_melody(score: Score, start_measure: int, end_measure: int) -> int:
    """
    악보에서 특정 마디 범위의 멜로디를 추출하여 MP3 파일로 저장 후 Result 테이블에 저장
    """
    image_path = os.path.join('uploaded_scores', score.original_filename)
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    img_list = [img]
    score_obj = MakeScore.make_score(img_list)

    extracted_score = stream.Score()
    for part in score_obj.parts:
        part_extract = stream.Part()
        for m in part.measures(start_measure, end_measure):
            part_extract.append(m)
        extracted_score.append(part_extract)

    result_id = str(uuid.uuid4())
    convert_dir = 'convert_result'
    os.makedirs(convert_dir, exist_ok=True)

    midi_path = os.path.join(convert_dir, f"{result_id}.mid")
    mp3_path = os.path.join(convert_dir, f"{result_id}.mp3")
    wav_path = midi_path.replace('.mid', '.wav')

    mf = midi.translate.music21ObjectToMidiFile(extracted_score)
    mf.open(midi_path, 'wb')
    mf.write()
    mf.close()

    subprocess.run([TIMIDITY_CMD, midi_path, "-Ow", "-o", wav_path])
    subprocess.run([FFMPEG_CMD, "-i", wav_path, mp3_path])
    os.remove(wav_path)

    result = Result(
        score_id=score.id,
        type='melody',
        audio_path=mp3_path
    )
    db.session.add(result)
    db.session.commit()

    return result.id
