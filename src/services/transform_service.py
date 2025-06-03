import uuid
import os
import platform
import subprocess
import cv2

from music21 import midi, stream, note
from src.models.db import db
from src.models.score_model import Score
from src.models.result_model import Result
from src.models.transform_model import TransformMelody
from ML.src.makexml.MakeScore import MakeScore

# 플랫폼별 경로 설정
if platform.system() == "Windows":
    ffmpeg_cmd = r"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe"
    timidity_cmd = "timidity"
    mscore_cmd = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
else:
    ffmpeg_cmd = "ffmpeg"
    timidity_cmd = "timidity"
    mscore_cmd = os.path.join("squashfs-root", "mscore4portable")


def perform_transpose(score: Score, shift: int) -> int:
    image_path = os.path.join('uploaded_scores', score.original_filename)
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    img_list = [img]

    score_obj = MakeScore.make_score(img_list)
    if isinstance(score_obj, tuple):
        score_obj = score_obj[0]

    transposed_score = MakeScore.change_key(score_obj, shift)

    result_id = str(uuid.uuid4())
    convert_dir = 'convert_result'
    os.makedirs(convert_dir, exist_ok=True)

    xml_path = os.path.join(convert_dir, f"{result_id}.xml")
    pdf_path = os.path.join(convert_dir, f"{result_id}.pdf")
    image_copy_path = os.path.join(convert_dir, f"{result_id}-1.png")

    MakeScore.score_to_xml(transposed_score, result_id)

    subprocess.run([mscore_cmd, xml_path, "-o", pdf_path], check=True)
    subprocess.run([mscore_cmd, xml_path, "-o", image_copy_path], check=True)

    result = Result(
        score_id=score.id,
        type='transpose',
        download_path=pdf_path,
        image_path=image_copy_path
    )
    db.session.add(result)
    db.session.commit()

    return result.id


def extract_melody(score: Score, start_measure: int, end_measure: int) -> int:
    try:
        image_path = os.path.join('uploaded_scores', score.original_filename)
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        img_list = [img]

        score_obj = MakeScore.make_score(img_list)
        if isinstance(score_obj, tuple):
            score_obj = score_obj[0]

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

        subprocess.run(
            [timidity_cmd, "-c", "C:\\Users\\funjm\\timidity.cfg", os.path.abspath(midi_path), "-Ow", "-o", os.path.abspath(wav_path)],
            check=True
        )
        subprocess.run([ffmpeg_cmd, "-i", wav_path, mp3_path], check=True)
        os.remove(wav_path)

        melody_result = TransformMelody(
            score_id=score.id,
            mp3_path=mp3_path,
            start_measure=start_measure,
            end_measure=end_measure
        )
        db.session.add(melody_result)

        result = Result(
            score_id=score.id,
            type='melody',
            audio_path=mp3_path,
            title=score.title,
            original_filename=score.original_filename,
            key=score.key
        )
        db.session.add(result)
        db.session.commit()

        return result.id

    except Exception as e:
        print("🔥 extract_melody 중 에러 발생:", e)
        raise RuntimeError(f"멜로디 추출 실패: {str(e)}")


def extract_lyrics(score: Score) -> int:
    image_path = os.path.join('uploaded_scores', score.original_filename)
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError("이미지를 불러올 수 없습니다")

    img_list = [img]

    score_obj = MakeScore.make_score(img_list)
    if isinstance(score_obj, tuple):
        score_obj = score_obj[0]

    lyrics = []
    for el in score_obj.recurse():
        if isinstance(el, note.Note) and el.lyric:
            lyrics.append(el.lyric.strip())

    lyrics_text = "\n".join(filter(None, lyrics)).strip()

    result_id = str(uuid.uuid4())
    convert_dir = 'convert_result'
    os.makedirs(convert_dir, exist_ok=True)

    text_path = os.path.join(convert_dir, f"{result_id}.txt")
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(lyrics_text)

    result = Result(
        score_id=score.id,
        type='lyrics',
        download_path=text_path,
        text_content=lyrics_text
    )
    db.session.add(result)
    db.session.commit()

    return result.id
