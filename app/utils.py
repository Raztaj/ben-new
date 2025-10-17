# --- START OF FILE app/utils.py ---

def calculate_age_group(age):
    """Categorizes an age into a predefined group."""
    if age <= 18:
        return '0-18'
    elif 19 <= age <= 35:
        return '19-35'
    elif 36 <= age <= 50:
        return '36-50'
    elif 51 <= age <= 65:
        return '51-65'
    else:
        return '65+'
