def int_or_none(value):                      # Define a function that converts a value to integer or returns None
    return int(value) if value and value.strip() else None   # If value exists and is not whitespace, convert to int; otherwise return None

def float_or_zero(value):                    # Define a function that converts a value to float or returns 0
    try:                                     # Attempt to convert the value
        return float(value)                  # Return the float conversion if successful
    except:                                  # Catch any conversion error (ValueError, TypeError, etc.)
        return 0                             # Return 0 if conversion fails