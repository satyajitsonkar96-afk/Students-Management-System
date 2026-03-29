def int_or_none(value):
    return int(value) if value and value.strip() else None

def float_or_zero(value):
    try:
        return float(value)
    except:
        return 0
