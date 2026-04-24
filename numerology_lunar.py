import ephem
from datetime import datetime, timedelta

def get_chaldean_number(name):
    chaldean_map = {
        'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
        'B': 2, 'K': 2, 'R': 2,
        'C': 3, 'G': 3, 'L': 3, 'S': 3,
        'D': 4, 'M': 4, 'T': 4,
        'E': 5, 'H': 5, 'N': 5, 'X': 5,
        'U': 6, 'V': 6, 'W': 6,
        'O': 7, 'Z': 7,
        'F': 8, 'P': 8
    }

    total = 0
    name = name.upper().replace(" ", "")
    for char in name:
        if char in chaldean_map:
            total += chaldean_map[char]

    while total > 9:
        total = sum(int(digit) for digit in str(total))

    if total == 9:
        total = 8
    elif total == 0:
        total = 1

    return total

def calculate_moon_phase(target_date):
    date_ephem = ephem.Date(target_date)

    next_fm = ephem.next_full_moon(date_ephem)
    prev_fm = ephem.previous_full_moon(date_ephem)

    next_nm = ephem.next_new_moon(date_ephem)
    prev_nm = ephem.previous_new_moon(date_ephem)

    date_dt = date_ephem.datetime()

    if abs((date_dt - next_fm.datetime()).total_seconds()) <= 86400 or \
       abs((date_dt - prev_fm.datetime()).total_seconds()) <= 86400:
        return 'FULL_MOON_WINDOW'

    if abs((date_dt - next_nm.datetime()).total_seconds()) <= 86400 or \
       abs((date_dt - prev_nm.datetime()).total_seconds()) <= 86400:
        return 'SKIP_NEW_MOON'

    return 'NORMAL'
