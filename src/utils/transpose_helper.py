KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def transpose_key(current_key: str, shift: int) -> str:
    key_upper = current_key.upper().replace('B♭', 'A#').replace('E♭', 'D#')  # 간단한 flat 처리 예시

    if key_upper not in KEYS:
        raise ValueError(f"Invalid key: {current_key}")

    index = KEYS.index(key_upper)
    new_index = (index + shift) % 12
    return KEYS[new_index]
