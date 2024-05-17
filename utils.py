from datetime import datetime
from itertools import zip_longest
import time
import calendar
import json

import gspread
import requests
from bs4 import BeautifulSoup

from database.db import show_all_doctors, show_doctor_surname


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

    patients_in_department = sh.worksheet('Цифры')
    total_patients = patients_in_department.acell('L2').value
    patients_in_stock = patients_in_department.acell('B2').value

    daily_report = {
        'экстренных госпитализаций': data.col_values(2)[8],
        'всего обратилось': data.col_values(2)[9],
        'госпитализации': hospitalization,
        'пациентов в травматологии всего/присутствует': f'{total_patients}/{patients_in_stock}'
    }
    return daily_report


def add_days_duty_schedule(month_example):
    """Добавляет числа и дни недели в гугл таблицу графика дежурств (duty schedule)"""
    sh = connect_to_google_sheets()
    worksheet = sh.get_worksheet_by_id(735128125)

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
            worksheet.update_cell(1, day[0] + 2, week[day[1]])
            worksheet.update_cell(2, day[0] + 2, day[0])
            time.sleep(1)


def get_weekend_and_holidays(year) -> dict:
    """Парсит с сайта Консультант (производственный календарь) выходные и праздничные числа по месяцам"""
    data = requests.get(f'https://www.consultant.ru/law/ref/calendar/proizvodstvennye/{year}/').text

    soup = BeautifulSoup(data, 'html.parser')

    days = soup.findAll('table', class_='cal')
    month = 0
    weekends_and_holidays = {}
    for day in days:
        month += 1
        item = day.find_all('td', class_='weekend')
        list_days = []
        for i in item:
            list_days.append(i.text)
        weekends_and_holidays[month] = list_days

    return weekends_and_holidays


def formatting_duty_schedule():
    """Форматирует график дежурств"""
    sh = connect_to_google_sheets()
    worksheet = sh.get_worksheet_by_id(735128125)

    worksheet.format('A1:AF2', {"horizontalAlignment": "CENTER"})
    month = datetime.now().month
    if month == 12:
        year = datetime.now().year
        year += 1
        month = 0
    else:
        year = datetime.now().year

    weekend_and_holidays = get_weekend_and_holidays(year)

    gray_columns = []
    for day in weekend_and_holidays.get(month + 1):
        gray_columns.append(worksheet.find(query=day, in_row=2))
    for item in gray_columns:
        column_letter = item.address[0:len(item.address) - 1]
        worksheet.format(
            f'{column_letter}1:{column_letter}40',
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
    worksheet = sh.get_worksheet_by_id(735128125)
    find_row = worksheet.find(doctor, in_column=2).row
    restricted_cells = worksheet.findall(day_of_week, 1)
    for cell in restricted_cells:
        cell_address = cell.col
        worksheet.update_cell(find_row, cell_address, mark)


def clear_duty_schedule():
    """Очищает заданный диапазон таблицы"""
    sh = connect_to_google_sheets()
    worksheet = sh.get_worksheet_by_id(735128125)
    worksheet.batch_clear(['C1:AG24'])
    worksheet.format(
        'C1:AG24',
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


def create_date(day: str):
    current_date = datetime.now()
    date_with_next_month = datetime(current_date.year, current_date.month + 1, int(day))
    return date_with_next_month.strftime('%d.%m.%Y')


def get_all_patients_in_ward(interval):
    """Получает данные из таблицы по указанному диапазону"""
    sh = connect_to_google_sheets()
    worksheet = sh.get_worksheet_by_id(0)

    result = []
    for item in worksheet.get(interval):
        if len(item) > 0:
            result.append([item[0], item[1].split(' ')[0], item[2]])
    return result


def get_patients_info():
    """Формирует словарь, ключ - фамилия врача, значение - данные о пациенте"""
    wards = ('A3:F8', 'A9:F14', 'A15:F20', 'A21:F26', 'A27:F32', 'A33:F38', 'A39:F40', 'A41:F42')
    doctors_patients = {
        'Большаков': [],
        'Дегтярев': [],
        'Зеленин': [],
        'Остапенко': [],
        'Казанцев': [],
        'Яковлев': [],
    }
    count = 0
    for ward in wards:
        count += 1
        data = get_all_patients_in_ward(ward)
        for item in data:
            if len(item[0]) > 0:
                doctors_patients[item[0]].append(f'{count} {item[1]} {item[2]}')

    return doctors_patients


def length_doctors_list():
    doctors = show_all_doctors()
    return len(doctors)


def create_text_report(message_from_user_id: int) -> str:
    all_data = get_patients_info()
    doctor = show_doctor_surname(message_from_user_id)
    data_for_doctor = all_data.get(doctor)
    ward = 0
    text = ''
    for item in data_for_doctor:
        patient = item.split(' ')
        if ward != patient[0]:
            ward = patient[0]
            text += ward + '\n' + '----------\n'
        patient_surname = patient[1]
        text += patient_surname + '\n'
        history_number = patient[2]
        text += history_number + '\n\n'
    return text
