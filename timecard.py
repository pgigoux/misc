"""
Auxiliary routines used in the time card programs
"""
import re
from math import modf
from calendar import monthrange
from datetime import datetime


class Totals:

    def __init__(self):
        self.data = {}
        self.day_totals = {}
        self.project_totals = {}
        self.reference_date = None

    def add(self, project: str, date: str, time: str, first_half: bool):
        """
        Add time data for a given project and time of the day
        :param project: project name
        :param date: date
        :param time: time
        :param first_half: first of second part of the month?
        """

        dt = datetime.strptime(date, '%d/%m/%Y')
        if self.reference_date is None:
            self.reference_date = dt
        if dt.day > 15 and first_half:
            return

        hours, new_error = closest_fraction(convert_time(time))
        # print(project, date, time, hours, new_error)

        if self.get_project_totals(project)[1] + new_error > 0.25:
            hours += 0.25
            new_error -= 0.25

        if project in self.project_totals:
            old_hours = self.project_totals[project][0]
            old_error = self.project_totals[project][1]
            self.project_totals[project] = (old_hours + hours, old_error + new_error)
            # print('+', project, hours, old_hours, self.project_totals[project])
        else:
            self.project_totals[project] = (hours, new_error)

        if dt.day in self.day_totals:
            self.day_totals[dt.day] += hours
        else:
            self.day_totals[dt.day] = hours

        key = (project, dt.day)
        if key in self.data:
            self.data[key] += hours
        else:
            self.data[key] = hours

    def get_hours(self, project: str, day: int):
        """
        Get the hours spent of a given project and day
        :param project: project name
        :param day: day of the month
        :return:
        """
        key = (project, day)
        if key in self.data:
            return self.data[key]
        else:
            return 0

    def get_project_list(self):
        """
        Get the list of projects where time was charged
        """
        return list(self.project_totals.keys())

    def get_project_totals(self, project: str) -> tuple:
        """
        Get the total number of hours spent in a given project
        The rounding error is returned because the data is rounded to 15-minute intervals
        :param project: project name
        :return: tuple with the number of hours and the rounding error
        """
        if project in self.project_totals:
            return self.project_totals[project]
        else:
            return 0, 0

    def get_day_totals(self, day: int) -> int:
        """
        Get the total number of hours spent in a given day of the month
        :param day: day of the month
        :return: number of hours
        """
        if day in self.day_totals:
            return self.day_totals[day]
        else:
            return 0

    def get_total_time(self) -> int:
        """
        Get the total time spent in all projects and all days
        :return: total time in decimal hours
        """
        return sum(self.day_totals.values())

    def get_number_of_days(self) -> int:
        """
        Return the number of days in the month being processed
        :return: number of days
        """
        if self.reference_date is not None:
            return days_in_month(self.reference_date)[1]
        else:
            return 0

    def dump(self):
        """
        Dump data (debugging)
        :return:
        """
        print('-' * 40)
        print(self.get_project_list())
        print(self.project_totals)
        print(self.day_totals)
        for key in self.data:
            print(key, self.data[key])
        print('-' * 40)


def closest_fraction(x: int | float):
    """
    Return the closest real to a given number whose fractional part is either 0, 0.25, 0.5 or 0.75.
    :param x: number to approximate
    :return: tuple with the closest number and difference between the two
    """
    xf, xi = modf(x)
    if xf > 0.875:
        xi += 1
        xf = 0
    elif xf > 0.675:
        xf = 0.75
    elif xf > 0.375:
        xf = 0.5
    elif xf > 0.125:
        xf = 0.25
    else:
        xf = 0
    xt = xi + xf
    dx = x - xt if abs(x - xt) > 1.0E-4 else 0
    return xt, dx


def read_project_list(file_name: str) -> list:
    """
    Read the contents of the file with the list of valid projects.
    :param file_name: project list file name
    :return: list of projects
    """
    output_list = []
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip()
            if not re.search('^#', line) or len(line) == 0:
                output_list.append(line)
    return output_list


def convert_time(time: str) -> float:
    """
    Convert time in hh:mm:ss to a floating point number
    :param time: time in hh:mm:ss
    :return: time in decimal format
    """
    try:
        h, m, s = map(int, str(time).split(':'))
        return h + m / 60.0 + s / 3600.0
    except ValueError:
        return 0


def days_in_month(date: datetime):
    """
    Return the days in a month for a given data
    :param date: datetime object
    :return: number of days in the month
    """
    return monthrange(date.year, date.month)


def column_name(column_number: int) -> str:
    """
    Convert a zero-indexed column number into a spreadsheet column name.
    :param column_number: column number (zero indexed)
    :return: column name
    """
    column_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                   'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                   'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    if column_number < len(column_list):
        # index = day - 1 if day < 16 else day - 16
        return column_list[column_number]
    else:
        raise ValueError(f'Bad column number {column_number}')
