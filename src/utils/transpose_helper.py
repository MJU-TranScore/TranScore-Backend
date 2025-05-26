KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def transposeKey(currentKey: str, shift: int) -> str:
    keyUpper = currentKey.upper().replace('B♭', 'A#').replace('E♭', 'D#')  # 간단한 flat 처리 예시

    if keyUpper not in KEYS:
        raise ValueError(f"Invalid key: {currentKey}")

    index = KEYS.index(keyUpper)
    newIndex = (index + shift) % 12
    return KEYS[newIndex]
