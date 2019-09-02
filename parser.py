import requests
import csv
from bs4 import BeautifulSoup as bs

headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0(X11;Linux x86_64...)Geco/20100101 Firefox/60.0'}

base_url = 'https://go.tpu.ru/JWQeqNnO'  # Url to parse

timetable = []
session = requests.Session()
request = session.get(base_url, headers=headers)
soup = bs(request.content, 'html.parser')

start_time = ['08:30 AM', '10:25 AM', '12:20 PM', '02:15 PM', '04:10 PM', '06:05 PM', '08:00 PM']
end_time = ['10:05 AM', '12:01 PM', '01:55 PM', '03:50 PM', '05:45 PM', '07:40 PM', '09:35 PM']


def rasp_append(subject, description, location, time, day):
    timetable.append({
        'subject': subject,
        'description': description,
        'location': location,
        'start_time': get_start_time(time),
        'end_time': get_end_time(time),
        'start_date': get_date(day),
        'end_date': get_date(day)
    })


def rasp_split(lst, n):
    lst[:] = (value for value in lst if value != '')
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def get_dates():
    dates = []
    ths = soup.find_all('th', {'width': '16%'})  # ths with Calendar dates
    for th in ths:
        date = th.text[17:25].replace('.', '/')
        tmp = date.split('/')
        tmp[0], tmp[1] = tmp[1], tmp[0]
        tmp = '/'.join(tmp)
        dates.append(tmp)
    return dates


dates_list = get_dates()


def get_date(number):
    return dates_list[number]


def get_start_time(number):
    return start_time[number]


def get_end_time(number):
    return end_time[number]


def rasp_parse():
    if request.status_code == 200:
        tds = soup.find_all('td', attrs={'class': 'cell'})  # tds with subjects
        time = 0
        day = 0
        row_counter = 1
        for td in tds:
            if td.text != "" and td.text.find('Военная подготовка', 0, len(td.text)) == -1:
                tmp = td.text[1:-1]
                tmp_list = tmp.split("\n")
                if len(tmp_list) > 3:
                    tmp_list = rasp_split(tmp_list, 3)
                    for t in tmp_list:
                        t.extend([time, day])
                        rasp_append(t[0], t[1], t[2], t[3], t[4])
                else:
                    tmp_list.extend([time, day])
                    if len(tmp_list) == 5:
                        rasp_append(tmp_list[0], tmp_list[1], tmp_list[2], tmp_list[3], tmp_list[4])
                    else:
                        rasp_append(tmp_list[1] + ' ' + tmp_list[0], '', '', tmp_list[2], tmp_list[3])
            day += 1
            if row_counter % 6 == 0:
                time += 1
                day = 0
            row_counter += 1
    else:
        print('NEOK')
    return timetable


def file_writer(timetable):
    with open('parsed_timetable.csv', 'w') as file:
        pen = csv.writer(file)
        pen.writerow(('Subject', 'Description', 'Location', 'Start Time', 'End Time', 'Start Date', 'End Date'))
        for t in timetable:
            pen.writerow((
                t['subject'], t['description'], t['location'], t['start_time'], t['end_time'], t['start_date'],
                t['end_date']))


timetable = rasp_parse()
file_writer(timetable)
