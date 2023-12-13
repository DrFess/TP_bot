from itertools import zip_longest

import gspread


def daily_summary():
    gs = gspread.service_account(filename='access.json')
    sh = gs.open_by_key('1feNhDOpE41gwPwuvtW_V5kZH2hFSt9qc8gZvmoH2UIE')

    data = sh.worksheet('Отчёт за сутки')

    if len(data.col_values(5)) > 2:
        hospitalization = list(zip_longest(data.col_values(7), data.col_values(6), data.col_values(8), fillvalue='нет данных'))[2::]
    else:
        hospitalization = 'не было'

    daily_report = {
        'экстренных госпитализаций': data.col_values(2)[8],
        'всего обратилось': data.col_values(2)[9],
        'госпитализации': hospitalization
    }
    return daily_report
