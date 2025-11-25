import sqlite3, os
DB = './aeroflot.db'
DATE_FMT = '%Y-%m-%d %H:%M'

def init_db():
    '''
    Инициализация БД. Если она не создана, будет сделана таблица и добавлены в нее данные
    '''
    need_seed = not os.path.exists(DB)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_no TEXT UNIQUE,
        destination TEXT,
        departure TEXT,
        arrival TEXT,
        free_seats INTEGER,
        plane_type TEXT,
        notes TEXT
    )''')
    conn.commit()
    if need_seed:
        seed = [
            ('SU100','Moscow','2025-10-01 08:00','2025-10-01 10:30',25,'A320',''),
            ('SU200','SPb','2025-10-02 12:00','2025-10-02 13:30',10,'737',''),
            ('SU300','Sochi','2025-10-03 06:00','2025-10-03 07:40',5,'A319',''),
            ('SU400','Novosib','2025-10-04 14:15','2025-10-04 18:00',50,'A330',''),
            ('SU500','Kazan','2025-10-05 09:20','2025-10-05 10:50',12,'737',''),
        ]
        for r in seed:
            try:
                cur.execute('INSERT INTO flights (flight_no,destination,departure,arrival,free_seats,plane_type,notes) VALUES (?,?,?,?,?,?,?)', r)
            except:
                pass
        conn.commit()
    conn.close()

def insert_flight(rec):
    '''Добавление строки в БД'''
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('INSERT INTO flights (flight_no,destination,departure,arrival,free_seats,plane_type,notes) VALUES (?,?,?,?,?,?,?)', rec)
    conn.commit(); conn.close()


def update_flight(fid, rec):
    '''Изменение строки в БД'''
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute('UPDATE flights SET flight_no=?,destination=?,departure=?,arrival=?,free_seats=?,plane_type=?,notes=? WHERE id=?', (*rec, fid))
    conn.commit(); conn.close()


def delete_flight(fid):
    '''Удаление строки из БД'''
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute('DELETE FROM flights WHERE id=?', (fid,))
    conn.commit(); conn.close()


def query_flights(filters=None):
    '''Получение строк из БД с применением фильтрации'''
    sql = 'SELECT id,flight_no,destination,departure,arrival,free_seats,plane_type,notes FROM flights'
    params = {}
    if filters:
        clauses = []
        if 'flight_no' in filters and filters['flight_no']:
            clauses.append('flight_no LIKE :flight_no')
            params['flight_no']='%'+filters['flight_no']+'%'
        if 'destination' in filters and filters['destination']:
            clauses.append('destination LIKE :destination')
            params['destination']='%'+filters['destination']+'%'
        if 'start' in filters and filters['start']:
            clauses.append('departure >= :start'); params['start']=filters['start']
        if 'end' in filters and filters['end']:
            clauses.append('departure <= :end'); params['end']=filters['end']
        if clauses:
            sql += ' WHERE ' + ' AND '.join(clauses)
    sql += ' ORDER BY departure'
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall(); conn.close(); return rows
