# src/utils/transpose_helper.py

# 키 목록 (샾/플랫 병행 포함)
NOTE_LIST = [
    "C", "C#", "Db", "D", "D#", "Eb", "E", "F",
    "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"
]

# Enharmonic mapping (같은 음이지만 표기 다른 것)
ENHARMONIC_EQUIVS = {
    "C#": "Db", "Db": "C#",
    "D#": "Eb", "Eb": "D#",
    "F#": "Gb", "Gb": "F#",
    "G#": "Ab", "Ab": "G#",
    "A#": "Bb", "Bb": "A#"
}

def normalize_key(key: str) -> str:
    """
    사용자 입력 키를 정규화 (예: E- → Eb)
    """
    return key.replace("-", "b").strip().capitalize()

def transpose_key(current_key: str, shift: int) -> str:
    """
    키를 주어진 반음 수만큼 이동시켜 새로운 키 반환
    """
    key = normalize_key(current_key)

    if key not in NOTE_LIST:
        raise ValueError(f"지원하지 않는 키입니다: {key}")

    index = NOTE_LIST.index(key)
    transposed_index = (index + shift) % len(NOTE_LIST)
    transposed_key = NOTE_LIST[transposed_index]

    # enharmonic 처리 예시 (Eb 대신 D# 원하면 변경 가능)
    return transposed_key
