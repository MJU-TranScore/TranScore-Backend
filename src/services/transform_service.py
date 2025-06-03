import uuid
import os
import platform
import subprocess
import cv2
from pdf2image import convert_from_path


from music21 import midi, stream, note, metadata 
from src.models.db import db
from src.models.score_model import Score
from src.models.result_model import Result
from src.models.transform_model import TransformMelody
from ML.src.makexml.MakeScore import MakeScore

# 플랫폼별 명령어
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

    # ✅ 제목 설정 추가
    transposed_score.metadata = transposed_score.metadata or metadata.Metadata()
    transposed_score.metadata.title = score.title or "Untitled"

    # 🔍 변환된 조성 분석
    analyzed_key = transposed_score.analyze('key')
    converted_key = f"{analyzed_key.tonic.name} {analyzed_key.mode.capitalize()}"

    result_id = str(uuid.uuid4())
    convert_dir = 'convert_result'
    os.makedirs(convert_dir, exist_ok=True)

    xml_path = os.path.join(convert_dir, f"{result_id}.xml")
    pdf_path = os.path.join(convert_dir, f"{result_id}.pdf")
    png_path = os.path.join(convert_dir, f"{result_id}-1.png")

    MakeScore.score_to_xml(transposed_score, result_id)

    try:
        subprocess.run([mscore_cmd, os.path.abspath(xml_path), "-o", os.path.abspath(pdf_path)], check=True)
    except subprocess.CalledProcessError as e:
        print("🛑 PDF 변환 실패:", e)
        raise RuntimeError("MuseScore PDF 변환 실패")

    # ✅ PDF → PNG 변환 (poppler path 지정)
    try:
        pages = convert_from_path(
            pdf_path,
            dpi=300,
            poppler_path=r"C:\Program Files\poppler-24.08.0\Library\bin"
        )
        if pages:
            pages[0].save(png_path, "PNG")
            print("✅ PNG 생성 완료:", png_path)
        else:
            print("⚠️ PDF 변환은 되었으나 PNG로 추출 실패")
            png_path = None
    except Exception as e:
        print("⚠️ PDF to PNG 변환 실패:", e)
        png_path = None

    result = Result(
        score_id=score.id,
        type='transpose',
        download_path=pdf_path.replace('\\', '/'),
        image_path=png_path.replace('\\', '/') if png_path else None,
        title=score.title,
        original_filename=score.original_filename,
        key=converted_key  # ✅ 변환된 조성 저장
    )

    db.session.add(result)
    db.session.commit()

    return result.id



def extract_melody(score: Score, start_measure: int, end_measure: int) -> dict:
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

        print("🎧 mp3_path =", mp3_path)
        print("🎧 mp3 존재 여부 =", os.path.exists(mp3_path))

        # ✅ 제목 추출 로직 개선
        original_filename = score.original_filename or "untitled.png"
        base_title = os.path.splitext(os.path.basename(original_filename))[0]
        title = score.title or base_title

        # ✅ 조성 분석
        try:
            analyzed_key = extracted_score.analyze('key')
            key = f"{analyzed_key.tonic.name} {analyzed_key.mode.capitalize()}"
        except:
            key = "Unknown"

        # ✅ MIDI 파일명 기준
        midi_filename = os.path.basename(midi_path)

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
            title=title,
            original_filename=midi_filename,
            key=key
        )
        db.session.add(result)
        db.session.commit()

        return {
            "result_id": result.id,
            "mp3_path": mp3_path.replace('\\', '/'),
            "midi_path": midi_path.replace('\\', '/'),
            "title": result.title,
            "key_signature": result.key
        }

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
