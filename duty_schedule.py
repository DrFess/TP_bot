import calendar
from datetime import date


class Employee:
    employees = {
        0: 'Преториус Т.Л.',
        1: 'Решетова Ю.В.',
        2: 'Докучаев М.А.',
        3: 'Колганов И.В.',
        4: 'Цыренов Ж.Э.',
        5: 'Остапенко В.Г.',
        6: 'Зеленин И.В.',
        7: 'Решетов А.В.',
        8: 'Дегтярев А.А.',
        9: 'Забинов В.К.',
        10: 'Шпагин Д.Е.',
        11: 'Ипатьева Е.Л.',
        12: 'Казанцев А.В.',
        13: 'Гуфайзин И.В.',
        14: 'Негрей М.К',
    }

    def __init__(self, doc_id: int, ban_days: list):
        self.doc_id = doc_id
        self.ban_days = ban_days
        self.wishes = []

    def add_wishes(self, wish_day: int):
        self.wishes.append(wish_day)


class Duty:
    week = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье'
    }

    def __init__(self, day_week: str, shift_duration: int, first_doctor: str, second_doctor: str, third_doctor: str):
        self.day_week = day_week
        self.shift_duration = shift_duration # длительность смены (8, 16 или 24)
        self.first_doctor = first_doctor
        self.second_doctor = second_doctor
        self.third_doctor = third_doctor

    def set_day_week(self, day_number: int):
        self.day_week = []


schedule_duty = {}

cal = calendar.Calendar()
current_month = date.today().month
current_year = date.today().year

month_raw = cal.monthdays2calendar(current_year, current_month)
month = []
for days in month_raw:
    for day in days:
        month.append(day)
