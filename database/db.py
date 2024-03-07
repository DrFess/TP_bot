import os
import sqlite3

from settings import PATH_TO_DB


def connection_to_DB(func):
    """Декоратор - подключение к базе данных"""
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(os.path.abspath(PATH_TO_DB), detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        result = func(cursor, *args, **kwargs)

        conn.commit()
        cursor.close()
        conn.close()

        return result
    return wrapper


@connection_to_DB
def create_tables(cursor):
    """Создание таблиц"""
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS doctor(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            telegram_id INTEGER,
                                            surname TEXT NOT NULL,
                                            name TEXT NOT NULL,
                                            patronymic TEXT NOT NULL
                                            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS weekday(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            day TEXT NOT NULL,
                                            alt_title TEXT NOT NULL
                                            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS const_forbidden_weekdays(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            doctor_id INTEGER,
                                            weekday_id INTEGER,
                                            FOREIGN KEY (doctor_id) REFERENCES doctor(id) ON DELETE CASCADE,
                                            FOREIGN KEY (weekday_id) REFERENCES weekday(id) ON DELETE CASCADE
                                            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS wish_weekday(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            doctor_id INTEGER,
                                            day_id INTEGER,
                                            wishes INTEGER,
                                            not_wishes INTEGER,
                                            FOREIGN KEY (doctor_id) REFERENCES doctor(id) ON DELETE CASCADE,
                                            FOREIGN KEY (day_id) REFERENCES weekday(id) ON DELETE CASCADE
                                            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS wish_date(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            doctor_id INTEGER,
                                            date TEXT,
                                            wishes INTEGER,
                                            not_wishes INTEGER,
                                            FOREIGN KEY (doctor_id) REFERENCES doctor(id) ON DELETE CASCADE
                                            )"""
    )


@connection_to_DB
def add_doctor(cursor, telegram_id: int, surname: str, name: str, patronymic: str):
    """Добавление врача в базу данных"""
    params = (telegram_id, surname, name, patronymic)
    query = """INSERT INTO doctor(telegram_id, surname, name, patronymic) VALUES (?, ?, ?, ?)"""
    cursor.execute(query, params)


@connection_to_DB
def edit_doctor_info(cursor, telegram_id, doc_id):
    """Обновление telegram_id врача по id"""
    params = (telegram_id, doc_id)
    query = """UPDATE doctor SET telegram_id = ? WHERE id = ?"""
    cursor.execute(query, params)


@connection_to_DB
def delete_doctor_info(cursor, doc_id):
    """Удаляет запись о враче по id"""
    params = (doc_id,)
    query = """DELETE FROM doctor WHERE id =?"""
    cursor.execute(query, params)


@connection_to_DB
def show_all_doctors(cursor):
    """Возвращает словарь с данными о всех врачах"""
    query = """SELECT * FROM doctor"""
    data = cursor.execute(query).fetchall()
    doctors_dict = {}
    for item in data:
        doctors_dict[item[0]] = {
            'идентификатор': item[1],
            'фамилия': item[2],
            'имя': item[3],
            'отчество': item[4]
        }
    return doctors_dict


@connection_to_DB
def get_doctor_telegram_id_by_surname(cursor, surname: str):
    """Возвращает id врача по фамилии"""
    params = (surname,)
    query = """SELECT telegram_id FROM doctor WHERE surname = ?"""
    data = cursor.execute(query, params).fetchone()
    return data[0]


@connection_to_DB
def show_all_doctors_id(cursor):
    """Возвращает список telegram_id всех врачей"""
    query = """SELECT telegram_id FROM doctor"""
    data = cursor.execute(query).fetchall()
    return [item[0] for item in data]


@connection_to_DB
def show_doctor_surname(cursor, telegram_id: str):
    """Возвращает telegram_id врача по фамилии"""
    query = """SELECT surname FROM doctor WHERE telegram_id = ?"""
    params = (telegram_id,)
    data = cursor.execute(query, params).fetchone()
    return data[0]


@connection_to_DB
def add_weekday(cursor, day: str, alt_title: str):
    """Добавление дня недели"""
    params = (day, alt_title)
    query = """INSERT INTO weekday(day, alt_title) VALUES (?, ?)"""
    cursor.execute(query, params)


@connection_to_DB
def show_all_weekdays(cursor):
    """Возвращает словарь с названиями дней недели"""
    query = """SELECT * FROM weekday"""
    data = cursor.execute(query).fetchall()
    weekdays_dict = {}
    for item in data:
        weekdays_dict[item[0]] = {
            'title': item[1],
            'alt_title': item[2]
        }
    return weekdays_dict


@connection_to_DB
def show_weekday_of_id(cursor, weekday_id: int):
    """Возвращает день недели по id"""
    params = (weekday_id,)
    query = """SELECT day FROM weekday WHERE id=?"""
    data = cursor.execute(query, params).fetchone()[0]
    return data


@connection_to_DB
def add_const_forbidden_weekday(cursor, doctor_id: int, weekday_id: int):
    """Добавляет запрещенный день недели к врачу"""
    params = (doctor_id, weekday_id)
    query = """INSERT INTO const_forbidden_weekdays(doctor_id, weekday_id) VALUES (?, ?)"""
    cursor.execute(query, params)


@connection_to_DB
def show_all_forbidden_weekdays(cursor):
    """Возвращает словарь всех запрещенных для смены дней"""
    query = """SELECT * FROM const_forbidden_weekdays"""
    data = cursor.execute(query).fetchall()
    forbidden_weekdays_dict = {}
    for item in data:
        forbidden_weekdays_dict[item[0]] = {
            'doctor_id': item[1],
            'weekday_id': item[2]
        }
    return forbidden_weekdays_dict


@connection_to_DB
def show_forbidden_weekdays_of_doctor(cursor, doctor_id):
    """Возвращает список id дней недели из таблицы запрещенных дней по id врача"""
    params = (doctor_id,)
    query = """SELECT * FROM const_forbidden_weekdays WHERE doctor_id=?"""
    data = cursor.execute(query, params).fetchall()
    forbidden_weekdays_list = []
    for item in data:
        forbidden_weekdays_list.append(item[2])
    return forbidden_weekdays_list


@connection_to_DB
def add_wish_date(cursor, doctor_id: int, date: str, switch: bool):
    """Добавляет дату пожелания врача по его id. Если switch == True - ставить смену, если False - не ставить"""
    if switch:
        params = (doctor_id, date, 1, 0)
    else:
        params = (doctor_id, date, 0, 1)
    query = """INSERT INTO wish_date(doctor_id, date, wishes, not_wishes) VALUES (?,?,?,?)"""
    cursor.execute(query, params)


@connection_to_DB
def show_all_wish_dates(cursor):
    """Возвращает словарь всех дат пожеланий врача"""
    query = """SELECT * FROM wish_date"""
    data = cursor.execute(query).fetchall()
    dates_dict = {}
    for item in data:
        dates_dict[item[0]] = [item[1], item[2], item[3], item[4]]
    return dates_dict


@connection_to_DB
def drop_table(cursor, table: str):
    """Удаляет указанную таблицу"""
    query = f"""DROP TABLE IF EXISTS {table}"""
    cursor.execute(query)
