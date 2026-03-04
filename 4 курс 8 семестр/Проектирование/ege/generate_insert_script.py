import csv
from pathlib import Path

query = """INSERT INTO t_student (c_school, c_class, c_fio, c_number) VALUES"""

with open(Path('C:\\Users\\Swifty\\Downloads\\ВУЗ\\Учеба\\4 курс 8 семестр\\Проектирование\\ege\\data\\students2.csv'), 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        query += f"""\n("{row['c_school']}", "{row['c_class']}", "{row['c_fio']}", "{row['c_number']}"),"""
    query = query[:-1] + ';'
print(query)
