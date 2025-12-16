def to_int_or_none(value):
    return int(value) if value not in (None, "", " ") else None
