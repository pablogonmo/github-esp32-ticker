import utime

def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def days_in_year(year):
    return 366 if is_leap_year(year) else 365

def days_in_month(year, month):
    if month == 2:  # February
        return 29 if is_leap_year(year) else 28
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        return 31

def get_current_timestamp():
    current_time = utime.localtime()
    year, month, mday, hour, minute, second, _, _ = current_time

    days_since_epoch = 0
    for y in range(1970, year):
        days_since_epoch += days_in_year(y)

    for m in range(1, month):
        days_since_epoch += days_in_month(year, m)

    days_since_epoch += mday - 1

    total_seconds = (days_since_epoch * 86400) + (hour * 3600) + (minute * 60) + second

    return total_seconds