from tkinter import filedialog, messagebox
import csv

def export_rows_to_csv(rows, columns):
    '''
    Экспорт данных в csv
    '''
    fname = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
    if not fname:
        return
    try:
        with open(fname, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(columns)
            for r in rows:
                w.writerow(r)
        messagebox.showinfo('Экспорт', f'Экспортировано в {fname}')
    except Exception as e:
        messagebox.showerror('Ошибка', str(e))
