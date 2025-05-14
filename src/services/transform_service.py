import uuid
import os
import platform
import subprocess
import cv2

from music21 import midi, stream, converter
from src.models.db import db
from src.models.score import Score
from src.models.transform import TransformTranspose, TransformMelody
from ML.src.makexml.MakeScore import MakeScore

# OS에 따라 실행 경로 설정
if platform.system() == "Windows":
    FFMPEG_CMD = r"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe"
    TIMIDITY_CMD = "timidity"
else:
    FFMPEG_CMD = "ffmpeg"
    TIMIDITY_CMD = "timidity"

def perform_transpose(score: Score, shift: int) -> str:
    # 이미지 경로
    upload_dir = 'uploaded_scores'
    image_path = os.path.join(upload_dir, score.original_filename)
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    img_list = [img]

    # 악보 객체 → 키 변경
    score_obj = MakeScore.make_score(img_list)
    transposed_score = MakeScore.change_key(score_obj, shift)

    # 저장 경로
    result_id = str(uuid.uuid4())
    convert_dir = 'convert_result'
    os.makedirs(convert_dir, exist_ok=True)

    xml_path = os.path.join(convert_dir, result_id + '.xml')
    pdf_path = os.path.join(convert_dir, result_id + '.pdf')

    # XML → PDF
    MakeScore.score_to_xml(transposed_score, result_id)
    mscore_path = "../squashfs-root/bin/mscore4portable"
    subprocess.run([mscore_path, xml_path, "-o", pdf_path])

    # DB 저장
    result = TransformTranspose(
        id=result_id,
        score_id=score.id,
        pdf_path=pdf_path
    )
    db.session.add(result)
    db.session.commit()

    return result_id

def extract_melody(score: Score, start_measure: int, end_measure: int) -> str:
    # 이미지 로딩
    image_path = os.path.join('uploaded_scores', score.original_filename)
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    img_list = [img]
    score_obj = MakeScore.make_score(img_list)

    # 멜로디 범위 추출
    extracted_score = stream.Score()
    for part in score_obj.parts:
        part_extract = stream.Part()
        measures = part.measures(start_measure, end_measure)
        for m in measures:
            part_extract.append(m)
        extracted_score.append(part_extract)

    # 파일 경로
    convert_dir = 'convert_result'
    os.makedirs(convert_dir, exist_ok=True)
    result_id = str(uuid.uuid4())

    midi_path = os.path.join(convert_dir, f"{result_id}.mid")
    mp3_path = os.path.join(convert_dir, f"{result_id}.mp3")
    wav_path = midi_path.replace('.mid', '.wav')

    # MIDI 저장
    mf = midi.translate.music21ObjectToMidiFile(extracted_score)
    mf.open(midi_path, 'wb')
    mf.write()
    mf.close()

    # 변환: MIDI → WAV → MP3
    subprocess.run([TIMIDITY_CMD, midi_path, "-Ow", "-o", wav_path])
    subprocess.run([FFMPEG_CMD, "-i", wav_path, mp3_path])
    os.remove(wav_path)

    # DB 저장
    result = TransformMelody(
        id=result_id,
        score_id=score.id,
        mp3_path=mp3_path
    )
    db.session.add(result)
    db.session.commit()

    return result_id
