from typing import List


def weekdays() -> List[str]:
    """The function should return a list of lines with weekdays"""

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return (weekdays)


def get_time_intervals() -> List[str]:
    """The function should return a list of lines with learning intervals"""

    time_intervals = ['8:00 - 9:30',
                      '9:50 - 11:20',
                      '11:40 - 13:10',
                      '13:40 - 15:10',
                      '15:30 - 17:00',
                      '17:20 - 18:50']
    return (time_intervals)


def room_types() -> List[str]:
    """The function should return a list of room types"""

    room_type = ['lecture', 'lab', 'practice', 'mixed']
    return (room_type)


def eng_room_type():
    """The function should return a dictionary
    with key = russian room type and
    with value = english room type"""

    dictionary = {
        'пр.': 'practice',
        'лек.': 'lecture',
        'лаб.': 'lab',
        'mixed': 'mixed',
        'кр.': 'practice'
    }
    return dictionary


def create_groups():
    """The function should return a list of integer group's values"""

    groups = [9491, 9492, 9493, 9494]
    return groups
