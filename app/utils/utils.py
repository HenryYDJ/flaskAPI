from datetime import datetime
import pytz


def datetime_string_to_utc(datetime_string):
    """
    This function converts ISO 8601 time string with timezone info to a datetime object in UTC timezone.
    """
    tz_utc = pytz.utc
    try:
        dt = datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        return None
    dt_utc = dt.astimezone(tz_utc)
    return dt_utc


def datetime_string_to_naive(datetime_string):
    """
    This function converts ISO 8601 time string without timezone info to a naive datetime object.
    Main usage is for date of birth and other places where timezon is not required.
    """
    try:
        dt = datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')
        return dt
    except ValueError:
        return None


def datetime_string_to_datetime(datetime_string):
    """
    This function converts ISO 8601 time string with timezone info to a datetime object
    preserving the original timezone.
    """
    try:
        dt = datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S%z')
        return dt
    except ValueError:
        return None


def convert_to_UTC(dt):
    """
    This function converts a datetime object with timezone information to a datetime object in UTC.
    """
    tz_utc = pytz.utc
    dt_utc = dt.astimezone(tz_utc)
    return dt_utc


def dt_list_to_UTC_list(dt_list):
    """
    This function converts a list of datetime objects to a list of UTC datetime objects.
    """
    result = []
    for dt in dt_list:
        result.append(convert_to_UTC(dt))
    return result


class Roles:
    """
    This class serves as the enum for roles.
    """
    EVERYBODY = 0
    STUDENT = 1
    PARENT = 2
    TEACHER = 4
    PRINCIPLE = 8
    ADMIN = 16


Relationship = {
    "FATHER": 1,
    "MOTHER": 2,
    "GRANDPA": 3,
    "GRANDMA": 4,
    "BROTHER": 5,
    "SISTER": 6,
    "UNCLE": 7,
    "AUNT": 8
}
