import tkinter as tk
from tkinter import ttk, messagebox
from validation import validate_integer, validate_float
from mio import export_rows_to_csv
import data, docs

#Формат даты
DATE_FMT = data.DATE_FMT

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        data.init_db()
        self.title('Aeroflot')
        self.geometry('1100x700')
        self._build_menu()
        self._build_ui()
        data.init_db()
        self._refresh_flights()

    def _build_menu(self):
        '''Создание меню'''
        menubar = tk.Menu(self)
        rep = tk.Menu(menubar, tearoff=0)
        rep.add_command(label='Отчет: Рейсы за период', command=self._open_reports)
        rep.add_command(label='Отчет: Свободные места по пункту', command=self._open_reports)
        menubar.add_cascade(label='Отчёты', menu=rep)

        hm = tk.Menu(menubar, tearoff=0)
        hm.add_command(label='Справка', command=self._open_help)
        menubar.add_cascade(label='Справка', menu=hm)

        self.config(menu=menubar)

    def _build_ui(self):
        '''Создание интерфейса'''
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=6, pady=6)

        fram_crud = ttk.Frame(nb)
        nb.add(fram_crud, text='Flights')

        topf = ttk.Frame(fram_crud)
        topf.pack(side='left', fill='y', padx=6, pady=6)

        ttk.Label(topf, text='Номер рейса').pack(anchor='w')
        self.f_flight_no = tk.StringVar(); ttk.Entry(topf, textvariable=self.f_flight_no).pack(fill='x')

        ttk.Label(topf, text='Пункт назначения').pack(anchor='w')
        self.f_destination = tk.StringVar(); ttk.Entry(topf, textvariable=self.f_destination).pack(fill='x')

        ttk.Label(topf, text=f'Вылет после ({DATE_FMT})').pack(anchor='w')
        self.f_start = tk.StringVar(); ttk.Entry(topf, textvariable=self.f_start).pack(fill='x')

        ttk.Label(topf, text=f'Вылет до ({DATE_FMT})').pack(anchor='w')
        self.f_end = tk.StringVar(); ttk.Entry(topf, textvariable=self.f_end).pack(fill='x')

        ttk.Button(topf, text='Применить фильтр', command=self._refresh_flights).pack(pady=4)
        ttk.Button(topf, text='Сбросить фильтр', command=self._reset_filter).pack(pady=2)
        ttk.Button(topf, text='Добавить', command=self._open_add_flight).pack(pady=6)
        ttk.Button(topf, text='Редактировать', command=self._open_edit_flight).pack(pady=2)
        ttk.Button(topf, text='Удалить', command=self._delete_flight).pack(pady=2)
        ttk.Button(topf, text='Экспорт CSV (всё)', command=self._export_all).pack(pady=6)

        frame_tbl = ttk.Frame(fram_crud)
        frame_tbl.pack(side='left', fill='both', expand=True, padx=6, pady=6)
        cols = ('id','flight_no','destination','departure','arrival','free_seats', 'plane_type', 'notes')
        self.tree = ttk.Treeview(frame_tbl, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor='center')
        ysb = ttk.Scrollbar(frame_tbl, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=ysb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        ysb.grid(row=0, column=1, sticky='ns')
        frame_tbl.rowconfigure(0, weight=1); frame_tbl.columnconfigure(0, weight=1)

    def _refresh_flights(self):
        '''Обновление данных отображаемых в таблице при каком-то действии пользователя'''
        filters = {}
        if self.f_flight_no.get().strip(): filters['flight_no']=self.f_flight_no.get().strip()
        if self.f_destination.get().strip(): filters['destination']=self.f_destination.get().strip()
        if self.f_start.get().strip(): filters['start']=self.f_start.get().strip()
        if self.f_end.get().strip(): filters['end']=self.f_end.get().strip()
        rows = data.query_flights(filters)
        for iid in self.tree.get_children(): self.tree.delete(iid)
        for r in rows: self.tree.insert('', 'end', values=r)

    def _reset_filter(self):
        '''Сброс фильтров'''
        self.f_flight_no.set('')
        self.f_destination.set('')
        self.f_start.set('')
        self.f_end.set('')
        self._refresh_flights()

    def _open_add_flight(self):
        '''Открытие диалога с добавлением рейса'''
        AddEditFlight(self, title='Добавить рейс', on_save=self._refresh_flights)

    def _open_edit_flight(self):
        '''Открытие диалога с изменением рейса'''
        sel = self.tree.selection()
        if not sel: messagebox.showwarning('Внимание','Выберите запись'); return
        vals = self.tree.item(sel[0])['values']
        AddEditFlight(self, title='Редактировать рейс', values=vals, on_save=self._refresh_flights)

    def _delete_flight(self):
        '''Открытие диалога с удалением рейса'''
        sel = self.tree.selection()
        if not sel: messagebox.showwarning('Внимание','Выберите запись'); return
        vals = self.tree.item(sel[0])['values']
        import sqlite3
        if messagebox.askyesno('Удалить','Удалить выбранную запись?'):
            data.delete_flight(vals[0]); self._refresh_flights()

    def _export_all(self):
        '''Экспорт всех данных из БД'''
        rows = []
        for iid in self.tree.get_children(): rows.append(self.tree.item(iid)['values'])
        export_rows_to_csv(rows, ['id','flight_no','destination','departure','arrival','free_seats', 'plane_type', 'notes'])

    def _open_reports(self):
        '''Открытие окна с отчетами'''
        ReportsWindow(self)

    def _open_help(self):
        '''Открытие окна справки'''
        HelpWindow(self)

class AddEditFlight(tk.Toplevel):
    def __init__(self, parent, title='Add', values=None, on_save=None):
        '''Так как добавление и изменение имеют одинаковое взаимодействие, используется единый класс'''
        super().__init__(parent)
        self.transient(parent); self.grab_set()
        self.on_save = on_save; self.values = values
        self.title(title)
        labels = ['flight_no','destination','departure','arrival','free_seats','plane_type','notes']
        self.vars = {}
        for i,l in enumerate(labels):
            ttk.Label(self, text=l).grid(row=i, column=0, sticky='w', padx=4, pady=2)
            v = tk.StringVar(); ttk.Entry(self, textvariable=v, width=40).grid(row=i, column=1, padx=4, pady=2)
            self.vars[l]=v
        if values:
            for i,k in enumerate(labels):
                self.vars[k].set(values[i+1] if i+1 < len(values) else '')
        ttk.Button(self, text='Сохранить', command=self._save).grid(row=len(labels), column=0, columnspan=2, pady=6)

    def _save(self):
        '''Сохранение внесенных изменений'''
        rec = (self.vars['flight_no'].get().strip(),
               self.vars['destination'].get().strip(),
               self.vars['departure'].get().strip(),
               self.vars['arrival'].get().strip(),
               int(self.vars['free_seats'].get().strip() or '0'),
               self.vars['plane_type'].get().strip(),
               self.vars['notes'].get().strip())
        try:
            if self.values:
                data.update_flight(self.values[0], rec)
            else:
                data.insert_flight(rec)
            if self.on_save: self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))

class ReportsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent); self.title('Отчёты'); self.geometry('800x500')
        nb = ttk.Notebook(self); nb.pack(fill='both', expand=True)
        f1 = ttk.Frame(nb); f2 = ttk.Frame(nb)
        nb.add(f1, text='Рейсы за период'); nb.add(f2, text='Свободные места по пункту')

        # -------- Формирование отчета: Рейсы за период --------
        ttk.Label(f1, text=f'Вылет после ({DATE_FMT})').pack(anchor='w', padx=6, pady=4)
        self.r_start = tk.StringVar(); ttk.Entry(f1, textvariable=self.r_start).pack(fill='x', padx=6)
        ttk.Label(f1, text=f'Вылет до ({DATE_FMT})').pack(anchor='w', padx=6, pady=4)
        self.r_end = tk.StringVar(); ttk.Entry(f1, textvariable=self.r_end).pack(fill='x', padx=6)
        tree1 = ttk.Treeview(f1, columns=('flight_no','destination','departure','arrival','free_seats'), show='headings')
        for c,t in [('flight_no','Рейс'),('destination','Пункт'),('departure','Вылет'),('arrival','Прибытие'),('free_seats','Своб. места')]: tree1.heading(c,text=t); tree1.column(c,anchor='center')
        tree1.pack(fill='both', expand=True, padx=6, pady=6)
        ttk.Button(f1, text='Выполнить', command=lambda: self._run_period(tree1)).pack(padx=6, pady=4)
        ttk.Button(f1, text='Экспорт CSV', command=lambda: export_rows_to_csv([tree1.item(i)['values'] for i in tree1.get_children()], ['flight_no','destination','departure','arrival','free_seats'])).pack(padx=6,pady=4)

        # -------- Формирование отчета: Свободные места по пункту --------
        tree2 = ttk.Treeview(f2, columns=('destination','total_free'), show='headings'); tree2.heading('destination',text='Пункт'); tree2.heading('total_free',text='Свободные места'); tree2.pack(fill='both', expand=True, padx=6,pady=6)
        ttk.Button(f2, text='Выполнить', command=lambda: self._run_free_by_dest(tree2)).pack(padx=6,pady=4)
        ttk.Button(f2, text='Экспорт CSV', command=lambda: export_rows_to_csv([tree2.item(i)['values'] for i in tree2.get_children()], ['destination','total_free'])).pack(padx=6,pady=4)

    def _run_period(self, tree):
        '''Получения данных для отчета: Рейсы за период'''
        rows = data.query_flights({'start': self.r_start.get().strip() or None, 'end': self.r_end.get().strip() or None})
        tree.delete(*tree.get_children())
        for r in rows: tree.insert('', 'end', values=(r[1],r[2],r[3],r[4],r[5]))

    def _run_free_by_dest(self, tree):
        '''Получения данных для отчета: Свободные места по пункту'''
        import sqlite3
        conn = sqlite3.connect(data.DB); cur = conn.cursor()
        cur.execute('SELECT destination, SUM(free_seats) FROM flights GROUP BY destination ORDER BY SUM(free_seats) DESC')
        rows = cur.fetchall(); conn.close(); tree.delete(*tree.get_children())
        for r in rows: tree.insert('', 'end', values=r)

class HelpWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent); self.title('Справка'); self.geometry('800x600')
        nb = ttk.Notebook(self); nb.pack(fill='both', expand=True)
        t1 = tk.Text(nb, wrap='word'); t1.insert('1.0', docs.USER_DOC); t1.config(state='disabled'); t1.pack(fill='both', expand=True); nb.add(t1, text='Пользовательская')
        t2 = tk.Text(nb, wrap='word'); t2.insert('1.0', docs.DEV_DOC); t2.config(state='disabled'); t2.pack(fill='both', expand=True); nb.add(t2, text='Сопровождение')
