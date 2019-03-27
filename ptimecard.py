import sys
import re
import datetime as dt
from argparse import ArgumentParser, SUPPRESS
import pandas as pd
from math import modf
from numpy import float64
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# Project file name
PROJECT_FILE = 'projects.txt'

# Column names
COL_PROJECT_PATH = 'Project Path'
COL_PROJECT_CODE = 'Project Code'
COL_BILLABLE = 'Billable'
COL_BILLABLE_AMOUNT = 'Billable Amount'
COL_TOTAL_HOURS = 'Total Hours'  # original name of the column, renamed at run-time as COL_TOTALS
COL_TOTALS = 'Totals'
COL_ERRORS = 'Errors'
COL_FORMULAS = 'Formulas'

# Row names
ROW_TOTALS = 'Totals'
ROW_FORMULAS = 'Formulas'

# Column types
UNNEEDED_COLUMNS = [COL_PROJECT_CODE, COL_BILLABLE, COL_BILLABLE_AMOUNT]
NON_INPUT_DATA_COLUMNS = [COL_PROJECT_PATH, COL_TOTAL_HOURS, COL_TOTALS, COL_ERRORS]

# Font name used to format cells
FONT_NAME = 'Liberation Sans'


def dump_data(df, label='', print_types=False):
    """
    Print the contents of a pandas DataFrame on the screen.
    Used for testing purposes.
    :param df: pandas data frame
    :type df: pd.DataFrame
    :param label: label to print in output header
    :type label: str
    :param print_types: print data types along with values
    :type print_types: bool
    :return: None
    """
    assert (isinstance(df, pd.DataFrame))
    aux = '-- ' + label + ' ' if label else ''
    delimiter = aux + '-' * 100
    print(delimiter)
    print('+ ', end='')
    for col in df.keys():
        print('[' + str(col) + ']', end=' ')
    print('\n')
    for row in list(df.index.values):
        for col in df.keys():
            value = df.at[row, col]
            if print_types:
                print('[' + str(value) + ' ' + str(type(value)) + ']', end=' ')
            else:
                print('[' + str(value) + ']', end=' ')
        print()
    print()


def closest_number(x):
    """
    Return the closest real to a given number whose fractional part is either 0, 0.25, 0.5 or 0.75.
    :param x: number to approximate
    :return: tuple with closest number and difference between the two
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


def read_project_list(file_name):
    lst = []
    f = open(file_name, 'r')
    for line in f:
        line = line.strip()
        if not re.search('^#', line) or len(line) == 0:
            # print(line)
            lst.append(line)
    # print(lst)
    return lst


def check_projects(df, project_list):
    """
    Make sure that all the projects in the data frame are named in the master project list.
    :param df: data frame
    :type df: pd.DataFrame
    :param project_list: list of valid projects
    :type project_list: list
    :return: False if a project is not in the master list, False otherwise
    :rtype: bool
    """
    assert (isinstance(df, pd.DataFrame))
    ok = True
    for _, row in df.iterrows():
        project_name = row[COL_PROJECT_PATH]
        if project_name not in project_list and project_name != ROW_TOTALS:
            print(project_name + ' not in project list')
            ok = False
    return ok


def read_excel_file(file_name):
    """
    Read Excel spreadsheet into a Pandas data frame
    :param file_name: spreadsheet file name
    :return: pandas data frame
    :rtype: pd.DataFrame
    """
    df = pd.read_excel(file_name)

    # Drop unused columns
    df_out = df.drop(columns=UNNEEDED_COLUMNS)

    # Look for the row containing the column totals
    lst = df_out.index[df_out[COL_PROJECT_PATH] == ROW_TOTALS].tolist()
    if len(lst) == 1:
        index = lst[0]
    else:
        raise (ValueError, 'No totals')

    # Only return rows up to the totals
    return df_out[0:index + 1]


def convert_values(df):
    """
    Convert hh:mm data to decimal, making sure that times bigger than 24 hours are handled correctly.
    Convert all numeric cells to float data.
    :param df: data frame
    :type df: pd.DataFrame
    :return: converted data frame
    :rtype: pd.DataFrame
    """
    assert (isinstance(df, pd.DataFrame))

    # Make a copy of the data frame so the original is left untouched
    df_out = df.copy(deep=True)

    # First convert datetime objects to decimal time
    for row_index, _ in df_out.iterrows():
        for col_name in df_out.keys():
            value = df_out.at[row_index, col_name]
            if isinstance(value, dt.time):
                # print('found time', value, value.hour)
                result = value.hour + value.minute / 60.0 + value.second / 3600.0
                df_out.at[row_index, col_name] = result
            elif isinstance(value, dt.datetime):  # times greater than 24 hours
                # print('found datetime', value)
                result = value.day * 24 + value.hour + value.minute / 60.0 + value.second / 3600.0
                # print('----', result)
                df_out.at[row_index, col_name] = result

    # Then convert all columns (except for the project name/path) to the same data type
    # (should be numpy.float64)
    for col_name in df_out.keys():
        if col_name != COL_PROJECT_PATH:
            df_out[col_name] = pd.to_numeric(df_out[col_name])

    return df_out


def rename_columns(df):
    """
    Rename date of the week, which originally are of the form 'dow yyyy-mm-dd', to just the day.
    Also rename the column 'Total Hours' to 'Totals'
    :param df: input data frame
    :type df: pd.DataFrame
    :return: converted data frame
    :rtype: pd.DataFrame
    """
    assert (isinstance(df, pd.DataFrame))
    d = {COL_TOTAL_HOURS: COL_TOTALS}
    for col in df.keys():
        # print(col)
        if col not in NON_INPUT_DATA_COLUMNS:
            d[col] = re.sub('... ....-..-', '', col)
    df_out = df.rename(columns=d)
    return df_out


def round_data(df):
    """
    Round time data to the nearest 15 minute boundary (x.0 x.25, xx.5, x.75).
    The rounding errors are recorded into the (new) 'Errors' column.
    The row and column totals become inconsistent after this point.
    :param df: input data frame
    :type df: pd.DataFrame
    :return: converted data frame
    :rtype: pd.DataFrame
    """
    assert (isinstance(df, pd.DataFrame))

    # Make a copy of the data frame so the original is left untouched
    df_out = df.copy(deep=True)

    # First round out every data cell to the nearest number.
    # Keep track of the errors for the row in the errors column.
    for row_index, _ in df_out.iterrows():
        total_error = 0
        for col_name in df_out.keys():
            if col_name not in NON_INPUT_DATA_COLUMNS:
                # value = df_out.at[row, col]
                new_value, error = closest_number(df_out.at[row_index, col_name])
                df_out.at[row_index, col_name] = new_value
                total_error += error
                # print(row, col, value, new_value, error, total_error)
        df_out.at[row_index, COL_ERRORS] = total_error

    return df_out


def recalculate_totals(df):
    """
    Round time data to the nearest 15 minute boundary (x.0 x.25, xx.5, x.75).
    The rounding errors are recorded into the (new) 'Errors' column.
    The row and column totals become inconsistent after this point.
    :param df: input data frame
    :type df: pd.DataFrame
    :return: converted data frame
    :rtype: pd.DataFrame
    """
    assert (isinstance(df, pd.DataFrame))

    # Make a copy of the data frame so the original is left untouched
    df_out = df.copy(deep=True)

    # Include the errors in the recalculations
    column_list = NON_INPUT_DATA_COLUMNS.copy()
    column_list.remove(COL_ERRORS)
    # print(column_list)

    # Calculate the row totals
    col_total = {col_name: 0.0 for col_name in df_out.keys()}
    # print(col_total)
    big_total = 0.0
    for row_index, row in df_out.iterrows():
        if row[COL_PROJECT_PATH] == ROW_TOTALS:  # it doesn't make sense to update this row yet
            continue
        row_total = 0.0
        for col_name in df_out.keys():
            # if col_name not in NON_INPUT_DATA_COLUMNS:
            if col_name not in column_list:
                # print(col_name)
                row_total += df_out.at[row_index, col_name]
                col_total[col_name] += df_out.at[row_index, col_name]
        big_total += row_total
        # print(row_total)

        df_out.at[row_index, COL_TOTALS] = row_total

    # Update column totals
    row = df_out.loc[df_out[COL_PROJECT_PATH] == ROW_TOTALS]
    row_index = row.index[0]
    # print(row)
    # print('--', row.index)
    for col_name in df_out.keys():
        # if col_name not in NON_INPUT_DATA_COLUMNS:
        if col_name not in column_list:
            df_out.at[row_index, col_name] = col_total[col_name]

    # Update total hours for period
    df_out.at[row_index, COL_TOTALS] = big_total

    # print(big_total)
    # print(col_total)

    return df_out


def convert_value(value):
    """
    Converts numpy.float64 values to float and replaces zero data with a '-'.
    All other data types are left unchanged.
    :param value: input value
    :return: converted value
    """
    if isinstance(value, float64):
        output_value = float(value)
        if abs(output_value) < 0.0001:
            output_value = '-'
        # print('found float64')
    else:
        output_value = value
    return output_value


def get_row_and_index(df, name):
    """
    Auxiliary funtion that returns the row and the row index for the row where COL_PROJECT_PATH matches a given name.
    Provided to prevent code redundancy in the program.
    :param df: data frame
    :type df: pd.DataFrame
    :param name: name to match
    :type name: str
    :return: row and row index
    :rtype: tuple
    """
    assert (isinstance(df, pd.DataFrame))
    row = df.loc[df[COL_PROJECT_PATH] == name]
    row_index = row.index[0]
    return row, row_index


def get_row_columns(df, row_index, column_names):
    """
    :param df: data frame
    :type df: pd.DataFrame
    :param column_names: list of column names
    :param row_index: row index (zero indexed)
    :type row_index: int
    :return: list of column values for the row
    :rtype: list
    """
    n = 0
    column_values = []
    for col_name in column_names:
        if col_name == COL_FORMULAS:
            value = '=sum(B' + str(row_index + 2) + ':' + excel_column_name(n - 2) + str(row_index + 2) + ')'
            # print(value)
        else:
            value = convert_value(df.at[row_index, col_name])
        column_values.append(value)
        n += 1
    return column_values


def excel_column_name(column_number):
    """
    Convert a zero-indexed column number into an Excel column name.
    :param column_number: column number (zero indexed)
    :type column_number: int
    :return: column name
    :rtype: str
    """
    assert (isinstance(column_number, int))
    column_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                   'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                   'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    max_columns = len(column_list)

    if column_number < max_columns:
        col_name = column_list[column_number]
    else:
        r = column_number // max_columns
        if r > max_columns:
            raise ValueError('column number too large')
        col_name = column_list[r - 1] + column_list[column_number - max_columns * r]

    return col_name


def write_excel_file(df, project_list, file_name):
    """
    Write data to spreadsheet file
    :param df: data frame
    :type df: pd.DataFrame
    :param project_list: list of valid projects
    :type project_list: list
    :param file_name: output file name
    :type file_name: str
    :return: None
    """
    assert (isinstance(df, pd.DataFrame))

    # Create workbook and define basic attributes
    wb = Workbook()
    ws = wb.active
    ws.title = 'Timecard'

    # Get spreadsheet dimensions
    # Allocate two additional rows (column titles, and formulas)
    # Allocate an additional column for the formulas
    # row = df.loc[df[COL_PROJECT_PATH] == ROW_TOTALS]
    row, _ = get_row_and_index(df, ROW_TOTALS)
    n_rows = row.index[0] + 3  # row.index[0] is zero indexed
    n_cols = len(df.keys()) + 1
    # print(n_rows, n_cols)

    # Prepare the spreadsheet heading (column titles)
    heading = list(df.keys()).copy()
    heading = heading[:-1] + [COL_FORMULAS, COL_ERRORS]
    # print(heading)
    ws.append(heading)

    # Append the time data
    for project in project_list:
        try:
            row, row_index = get_row_and_index(df, project)
        except IndexError:
            continue
        row_list = get_row_columns(df, row_index, heading)
        ws.append(row_list)

    # Append the column totals
    row, row_index = get_row_and_index(df, ROW_TOTALS)
    row_list = get_row_columns(df, row_index, heading)
    ws.append(row_list)

    # Append the column formulas
    column_list = list(df.keys()).copy()
    column_list = column_list[1:-2]  # remove project name, totals and errors
    # print(column_list)
    row_list = ['Formulas']
    for col_number in range(1, len(column_list) + 1):
        # print(col_number, excel_column_name(col_number))
        row_list.append('=sum(' + excel_column_name(col_number) + '2:' +
                        excel_column_name(col_number) + str(n_rows - 2))
    # print(row_list)
    ws.append(row_list)

    # -- Font definitions start here

    # Change the font in all relevant cells
    ft = Font(name=FONT_NAME)
    for row_number in range(1, n_rows + 1):
        for col_number in range(0, n_cols):
            # print(excel_column_name(col_number) + str(row_number))
            ws[excel_column_name(col_number) + str(row_number)].font = ft

    # Format titles in bold
    ft = Font(name=FONT_NAME, bold=True)
    for col_number in range(0, n_cols):
        # print(excel_column_name(col_number) + '1')
        ws[excel_column_name(col_number) + '1'].font = ft

    # Format totals in bold. Use the same font definition used for the titles.
    for col_number in range(1, n_cols - 1):
        # print(excel_column_name(col_number) + str(n_rows - 1))
        ws[excel_column_name(col_number) + str(n_rows - 1)].font = ft
    for row_number in range(1, n_rows):
        # print(excel_column_name(n_cols - 3) + str(row_number))
        ws[excel_column_name(n_cols - 3) + str(row_number)].font = ft

    # Change format and color in the formulas
    ft = Font(name=FONT_NAME, bold=True, italic=True, color="FF0000")
    for col_number in range(1, len(column_list) + 1):
        # print(excel_column_name(col_number))
        ws[excel_column_name(col_number) + str(n_rows)].font = ft
    for row_number in range(2, n_rows):
        # print(row_number)
        ws[excel_column_name(n_cols - 2) + str(row_number)].font = ft

    # -- Alignment and numeric format start here

    # Align numeric cells to the right
    for row_number in range(1, n_rows):
        for col_number in range(1, n_cols):
            # print(excel_column_name(col_number) + str(row_number))
            ws[excel_column_name(col_number) + str(row_number)].alignment = Alignment(horizontal='right')

    # Make numbers display with two decimals
    for row_number in range(1, n_rows + 1):
        for col_number in range(1, n_cols - 1):
            # print(excel_column_name(col_number) + str(row_number))
            ws[excel_column_name(col_number) + str(row_number)].number_format = '0.00'

    # Make errors display with four decimals
    for row_number in range(1, n_rows):
        # print(excel_column_name(n_cols - 1) + str(row_number))
        ws[excel_column_name(n_cols - 1) + str(row_number)].number_format = '0.0000'

    wb.save(file_name)


def get_args(argv):
    """
    Process command line arguments
    :param argv: command line arguments from sys.argv
    :type argv: list
    :return: arguments
    :rtype: argparse.Namespace
    """

    parser = ArgumentParser()

    parser.add_argument(action='store',
                        dest='file',
                        default='')

    parser.add_argument('--debug',
                        action='store_true',
                        dest='debug',
                        default=False,
                        help=SUPPRESS)

    return parser.parse_args(argv[1:])


if __name__ == '__main__':

    # Get command line arguments
    args = get_args(sys.argv)
    input_file = args.file
    output_file = 'Output_' + input_file
    debug = args.debug

    try:
        master_project_list = read_project_list(PROJECT_FILE)
    except FileNotFoundError as e:
        print('Project file not found', e)
        exit(0)
    if debug:
        print(master_project_list)

    data_frame_excel = None  # to make PyCharm happy
    try:
        data_frame_excel = read_excel_file(input_file)
    except Exception as e:
        print('Cannot open spreadsheet', e)
        exit(0)

    if debug:
        dump_data(data_frame_excel, label='read_excel', print_types=True)

    if not check_projects(data_frame_excel, master_project_list):
        exit(0)

    data_frame_convert = convert_values(data_frame_excel)
    if debug:
        dump_data(data_frame_convert, 'convert_values', print_types=True)

    data_frame_rename = rename_columns(data_frame_convert)
    if debug:
        dump_data(data_frame_rename, label='rename_columns')

    data_frame_round = round_data(data_frame_rename)
    if debug:
        dump_data(data_frame_round, label='round_data')

    data_frame_recalculate = recalculate_totals(data_frame_round)
    if debug:
        dump_data(data_frame_recalculate, label='recalculate_totals')

    try:
        write_excel_file(data_frame_recalculate, master_project_list, output_file)
    except Exception as e:
        print('Cannot write spreadsheet', e)
