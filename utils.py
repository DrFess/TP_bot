from itertools import zip_longest
import time
import calendar
import json

import gspread


def get_dates_you_need(year: int, month: int) -> list:
    """Получает календарь на необходимый месяц в виде списка кортежей.
    Кортеж: 0 элемент - день месяца, 1 элемент - день недели (неделя начинается с 0)"""
    cal = calendar.Calendar()
    date_raw = cal.monthdays2calendar(year, month)
    result = []
    for days in date_raw:
        for day in days:
            result.append(day)
    return result


def connect_to_google_sheets():
    """Подключение в гугл таблице"""
    gs = gspread.service_account(filename='access.json')
    sh = gs.open_by_key('1feNhDOpE41gwPwuvtW_V5kZH2hFSt9qc8gZvmoH2UIE')
    return sh


def daily_summary():
    """Формирует данные для отчета за сутки в телеграм боте"""
    sh = connect_to_google_sheets()
    data = sh.worksheet('Отчёт за сутки')

    if len(data.col_values(5)) > 2:
        hospitalization = list(
            zip_longest(data.col_values(7), data.col_values(6), data.col_values(8), fillvalue='нет данных'))[2::]
    else:
        hospitalization = 'не было'

    daily_report = {
        'экстренных госпитализаций': data.col_values(2)[8],
        'всего обратилось': data.col_values(2)[9],
        'госпитализации': hospitalization
    }
    return daily_report


def add_days_duty_schedule(month_example):
    """Добавляет числа и дни недели в гугл таблицу графика дежурств (duty schedule)"""
    sh = connect_to_google_sheets()
    worksheet = sh.get_worksheet(5)

    week = {
        0: 'Пн',
        1: 'Вт',
        2: 'Ср',
        3: 'Чт',
        4: 'Пт',
        5: 'Сб',
        6: 'Вс'
    }

    for day in month_example:
        if day[0] != 0:
            worksheet.update_cell(1, day[0] + 1, week[day[1]])
            worksheet.update_cell(2, day[0] + 1, day[0])
            time.sleep(1)


def formatting_duty_schedule():
    """Форматирует график дежурств"""
    sh = connect_to_google_sheets()
    worksheet = sh.get_worksheet(5)

    worksheet.format('A1:AF2', {"horizontalAlignment": "CENTER"})
    weekend = []
    saturday = worksheet.findall('Сб', 1)
    sunday = worksheet.findall('Вс', 1)
    weekend.extend(saturday)
    weekend.extend(sunday)
    for item in weekend:
        column_letter = item.address[0:len(item.address) - 1]
        worksheet.format(
            f'{column_letter}1:{column_letter}18',
            {"backgroundColor":
                {
                    "red": 300.0,
                    "green": 300.0,
                    "blue": 300.0
                },
            }
        )


def set_restricted_cells(doctor: str, day_of_week: str, mark: str):
    """Добавляет метки смен из списков
    X - не ставить смены
    * - пожелания
    о - отпуск
    8, 16, 24 - количество часов"""
    sh = connect_to_google_sheets()
    worksheet = sh.get_worksheet(5)
    find_row = worksheet.find(doctor, in_column=1).row
    restricted_cells = worksheet.findall(day_of_week, 1)
    for cell in restricted_cells:
        cell_address = cell.col
        worksheet.update_cell(find_row, cell_address, mark)


def clear_duty_schedule():
    """Очищает заданный диапазон таблицы"""
    sh = connect_to_google_sheets()
    worksheet = sh.get_worksheet(5)
    worksheet.batch_clear(['B1:AF18'])
    worksheet.format(
        'B1:AF18',
        {'backgroundColor':
            {
                "red": -255.0,
                "green": -255.0,
                "blue": -255.0
            }
        }
    )


def open_data_file(path_to_file: str):
    """Открывает указанный JSON файл"""
    with open(f'database/{path_to_file}', 'r') as file:
        data = json.load(file)
    return data


def write_doctors_wishes_str(doctor: str, wish: str):
    """Записывает пожелания врача"""
    data = open_data_file('wish_days.json')
    doc = data[doctor]
    doc.append(wish)

    with open('database/wish_days.json', 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def write_doctors_ban_days(doctor: str, ban_day: list, choice: str):
    """Записывает числа или дни в которые ставить смены нежелательно"""
    data = open_data_file('wish_ban_days.json')
    data[doctor][choice] = ban_day

    with open('database/wish_ban_days.json', 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def write_doctors_wish_days(doctor: str, ban_day: list, choice: str):
    """Записывает числа или дни в которые ставить смены желательно"""
    data = open_data_file('wish_days.json')
    data[doctor][choice] = ban_day

    with open('database/wish_ban_days.json', 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def write_doctors_wishes(doctor: str, ban_day: list, choice: str, file_name: str):
    """Записывает числа или дни в которые ставить смены нельзя"""
    data = open_data_file(f'{file_name}.json')
    data[doctor][choice] = ban_day

    with open(f'database/{file_name}.json', 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_wishes_data():
    answer_bans = {}
    data_bans = open_data_file('wish_ban_days.json')
    for doctor in data_bans:
        for days in data_bans[doctor]:
            if len(data_bans[doctor][days]) > 0:
                answer_bans[doctor] = data_bans[doctor]
    answer_wishes = {}
    data_wishes = open_data_file('wish_days.json')
    for doctor in data_wishes:
        for days in data_wishes[doctor]:
            if len(data_wishes[doctor][days]) > 0:
                answer_wishes[doctor] = data_wishes[doctor]
    return answer_bans, answer_wishes


def validate_date(dates: str):
    valid = dates.split(', ')
    return valid
