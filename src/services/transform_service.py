import uuid
import os
import platform
import subprocess
import cv2

from music21 import midi, stream, note
from src.models.db import db
from src.models.score import Score
from src.models.result import Result
from ML.src.makexml.MakeScore import MakeScore

if platform.system() == "Windows":
    ffmpegCmd = r"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe"
    timidityCmd = "timidity"
    mscoreCmd = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
else:
    ffmpegCmd = "ffmpeg"
    timidityCmd = "timidity"
    mscoreCmd = os.path.join("squashfs-root", "mscore4portable")


def performTranspose(score: Score, shift: int) -> int:
    imagePath = os.path.join('uploaded_scores', score.original_filename)
    img = cv2.imread(imagePath, cv2.IMREAD_COLOR)
    imgList = [img]

    scoreObj = MakeScore.make_score(imgList)
    transposedScore = MakeScore.change_key(scoreObj, shift)

    resultId = str(uuid.uuid4())
    convertDir = 'convert_result'
    os.makedirs(convertDir, exist_ok=True)

    xmlPath = os.path.join(convertDir, f"{resultId}.xml")
    pdfPath = os.path.join(convertDir, f"{resultId}.pdf")

    MakeScore.score_to_xml(transposedScore, resultId)
    subprocess.run([mscoreCmd, xmlPath, "-o", pdfPath], check=True)

    result = Result(
        score_id=score.id,
        type='transpose',
        download_path=pdfPath
    )
    db.session.add(result)
    db.session.commit()

    return result.id


def extractMelody(score: Score, startMeasure: int, endMeasure: int) -> int:
    imagePath = os.path.join('uploaded_scores', score.original_filename)
    img = cv2.imread(imagePath, cv2.IMREAD_COLOR)
    imgList = [img]

    scoreObj = MakeScore.make_score(imgList)

    extractedScore = stream.Score()
    for part in scoreObj.parts:
        partExtract = stream.Part()
        for m in part.measures(startMeasure, endMeasure):
            partExtract.append(m)
        extractedScore.append(partExtract)

    resultId = str(uuid.uuid4())
    convertDir = 'convert_result'
    os.makedirs(convertDir, exist_ok=True)

    midiPath = os.path.join(convertDir, f"{resultId}.mid")
    mp3Path = os.path.join(convertDir, f"{resultId}.mp3")
    wavPath = midiPath.replace('.mid', '.wav')

    mf = midi.translate.music21ObjectToMidiFile(extractedScore)
    mf.open(midiPath, 'wb')
    mf.write()
    mf.close()

    subprocess.run([timidityCmd, midiPath, "-Ow", "-o", wavPath], check=True)
    subprocess.run([ffmpegCmd, "-i", wavPath, mp3Path], check=True)
    os.remove(wavPath)

    result = Result(
        score_id=score.id,
        type='melody',
        audio_path=mp3Path
    )
    db.session.add(result)
    db.session.commit()

    return result.id


def extractLyrics(score: Score) -> int:
    imagePath = os.path.join('uploaded_scores', score.original_filename)
    img = cv2.imread(imagePath, cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError("이미지를 불러올 수 없습니다")

    imgList = [img]
    scoreObj = MakeScore.make_score(imgList)

    lyrics = []
    for el in scoreObj.recurse():
        if isinstance(el, note.Note) and el.lyric:
            lyrics.append(el.lyric.strip())

    lyricsText = "\n".join(filter(None, lyrics)).strip()

    resultId = str(uuid.uuid4())
    convertDir = 'convert_result'
    os.makedirs(convertDir, exist_ok=True)

    textPath = os.path.join(convertDir, f"{resultId}.txt")
    with open(textPath, 'w', encoding='utf-8') as f:
        f.write(lyricsText)

    result = Result(
        score_id=score.id,
        type='lyrics',
        download_path=textPath,
        text_content=lyricsText
    )
    db.session.add(result)
    db.session.commit()

    return result.id
