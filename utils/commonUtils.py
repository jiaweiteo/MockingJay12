import re

def get_purpose_color_and_value(purpose):
    pattern = r':(\w+)\[(.*?)\]'
    match = re.match(pattern, purpose)
    
    if match:
        color = match.group(1)
        content = match.group(2)
        return color, content
    return None, None

def get_status_color(status):
    """
    Return the color code for the given status.
    """
    status_colors = {
        "Pending": "blue",
        "Registered": "green",
        "Waitlist": "yellow",
        "Rejected": "red",
    }
    return status_colors.get(status, "gray")  # Default to gray for unknown statuses
