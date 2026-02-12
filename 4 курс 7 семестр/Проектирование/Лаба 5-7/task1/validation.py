def validate_integer(value: str, minimum: int = 3) -> int:
    '''Валидация целочисленных значений'''
    if not value.strip().isdigit():
        raise ValueError('Значение должно быть целым числом')
    n = int(value)
    if n < minimum:
        raise ValueError(f'Значение должно быть >= {minimum}')
    return n


def validate_float(value: str, minimum: float = 0.0) -> float:
    '''Валидация вещественных значений'''
    try:
        num = float(value)
    except Exception:
        raise ValueError('Значение должно быть числом')
    if num <= minimum:
        raise ValueError(f'Значение должно быть > {minimum}')
    return num
