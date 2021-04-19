from datetime import datetime
import pytz


def datetime_string_to_utc(datetime_string):
    tz_utc = pytz.utc
    try:
        dt = datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S.%f%z')
    except ValueError:
        return None
    dt_utc = dt.astimezone(tz_utc)
    return dt_utc


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
