from itertools import zip_longest
import time
import calendar

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


current_month = get_dates_you_need(2024, 1)

employees_ban_weekdays = {
        'Преториус Т.Л.': [],
        'Решетова Ю.В.': [],
        'Докучаев М.А.': ['Сб'],
        'Колганов И.В.': [],
        'Цыренов Ж.Э.': ['Пн', 'Ср', 'Сб'],
        'Остапенко В.Г.': ['Пн', 'Ср', 'Сб', 'Вс'],
        'Зеленин И.В.': ['Вт'],
        'Решетов А.В.': [],
        'Дегтярев А.А.': [],
        'Забинов В.К.': [],
        'Шпагин Д.Е.': [],
        'Ипатьева Е.Л.': ['Пн', 'Чт'],
        'Казанцев А.В.': [],
        'Гуфайзин И.В.': [],
        'Негрей М.К': [],
        'Черноусова Е.Л.': [],
    }

employees_wishes_weekdays = {
        'Преториус Т.Л.': [],
        'Решетова Ю.В.': [],
        'Докучаев М.А.': [],
        'Колганов И.В.': ['Пн', 'Чт'],
        'Цыренов Ж.Э.': [],
        'Остапенко В.Г.': [],
        'Зеленин И.В.': [],
        'Решетов А.В.': ['Вс'],
        'Дегтярев А.А.': [],
        'Забинов В.К.': ['Пт'],
        'Шпагин Д.Е.': [],
        'Ипатьева Е.Л.': [],
        'Казанцев А.В.': [],
        'Гуфайзин И.В.': [],
        'Негрей М.К': [],
        'Черноусова Е.Л.': ['Пт'],
    }

# add_days_duty_schedule(current_month)
# formatting_duty_schedule()
# time.sleep(60)
# for doc in employees_ban_weekdays:
#     for item in employees_ban_weekdays[doc]:
#         set_restricted_cells(doc, item, 'X')


for doc in employees_wishes_weekdays:
    for item in employees_wishes_weekdays[doc]:
        set_restricted_cells(doc, item, '*')


# clear_duty_schedule()
