def validate_float(value):
    if value == "":
        return True

    try:
        float(value)
        return True
    except ValueError:
        return False


def validate_int(value):
    if value == "":
        return True

    try:
        int(value)
        return True
    except ValueError:
        return False
