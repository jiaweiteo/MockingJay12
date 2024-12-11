from datetime import datetime

def format_date(date_string):
    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%b %d, %Y")
    return formatted_date

def combine_date_and_time(date_str, time_str, date_format="%Y-%m-%d", time_format="%H:%M"):
    # Parse the date and time strings
    date_part = datetime.strptime(date_str, date_format)
    time_part = datetime.strptime(time_str, time_format).time()

    # Combine date and time
    return datetime.combine(date_part, time_part).strftime("%Y-%m-%d %H:%M:%S")

def datetime_string_to_date_and_time_object(date_time_string):
    datetime_object = datetime.fromisoformat(date_time_string)
    print(datetime_object)
    # Extract the date object
    date_object = datetime_object.date()
    time_object = datetime_object.time
    print(date_object, time_object)
    return date_object,time_object()