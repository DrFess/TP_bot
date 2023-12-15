import calendar
from datetime import date


class Employee:
    def __init__(self, surname: str, initials: str, ban_days: int):
        self.surname = surname
        self.initials = initials
        self.ban_days = ban_days
        self.wishes = []


class Duty:
    def __init__(self, day_week: str, shift_duration: int, first_doctor: str, second_doctor: str, third_doctor: str):
        self.day_week = day_week
        self.shift_duration = shift_duration
        self.first_doctor = first_doctor
        self.second_doctor = second_doctor
        self.third_doctor = third_doctor


schedule_duty = {}

week = {
    0: 'Понедельник',
    1: 'Вторник',
    2: 'Среда',
    3: 'Четверг',
    4: 'Пятница',
    5: 'Суббота',
    6: 'Воскресенье'
}

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

cal = calendar.Calendar()
current_month = date.today().month
current_year = date.today().year

month = cal.monthdayscalendar(current_year, current_month)
for days in month:
    for day in days:
        if day != 0:
            schedule_duty[day] = Duty()

