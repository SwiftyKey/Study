import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import traceback

import task2 as parser_module


class TestManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Менеджер тестов парсера")
        self.geometry("1100x700")
        self.tests = []
        self.results = []
        self._load_initial_tests()
        self._build_ui()

    def _load_initial_tests(self):
        try:
            for t in getattr(parser_module, 'tests', []):
                name, src, expected = t
                self.tests.append(
                    {'name': name, 'input': src, 'expected': bool(expected)})
        except Exception as e:
            print("Ошибка загрузки тестов из task2.py:", e)

    def _build_ui(self):
        left = ttk.Frame(self)
        left.pack(side='left', fill='y', padx=6, pady=6)

        ttk.Label(left, text="Тесты").pack(anchor='w')
        cols = ('name', 'expected')
        self.tree_tests = ttk.Treeview(
            left, columns=cols, show='headings', height=24)
        self.tree_tests.heading('name', text='Имя')
        self.tree_tests.heading('expected', text='Ожидаемый результат')
        self.tree_tests.column('name', width=280)
        self.tree_tests.column('expected', width=200, anchor='center')
        self.tree_tests.pack(side='left', fill='y')

        vs = ttk.Scrollbar(left, orient='vertical',
                           command=self.tree_tests.yview)
        self.tree_tests.configure(yscrollcommand=vs.set)
        vs.pack(side='left', fill='y')

        btnf = ttk.Frame(left)
        btnf.pack(fill='x', pady=6)
        ttk.Button(btnf, text="Добавить", command=self.on_add).pack(
            side='left', padx=3)
        ttk.Button(btnf, text="Изменить", command=self.on_edit).pack(
            side='left', padx=3)
        ttk.Button(btnf, text="Удалить", command=self.on_delete).pack(
            side='left', padx=3)
        ttk.Button(btnf, text="Запустить",
                   command=self.on_run_selected).pack(side='left', padx=3)
        ttk.Button(btnf, text="Запустить все", command=self.on_run_all).pack(
            side='left', padx=3)
        ttk.Button(btnf, text="Сохранить...",
                   command=self.on_save_tests).pack(side='left', padx=3)
        ttk.Button(btnf, text="Загрузить...",
                   command=self.on_load_tests).pack(side='left', padx=3)

        self._refresh_tests_tree()

        right = ttk.Frame(self)
        right.pack(side='left', fill='both', expand=True, padx=6, pady=6)

        ttk.Label(right, text="Результаты").pack(anchor='w')
        rcols = ('test', 'status')
        self.tree_results = ttk.Treeview(
            right, columns=rcols, show='headings', height=14)
        self.tree_results.heading('test', text='Тест')
        self.tree_results.heading('status', text='Статус')
        self.tree_results.column('test', width=240, anchor='w')
        self.tree_results.column('status', width=80, anchor='center')
        self.tree_results.pack(fill='both', expand=True)

        rbtnf = ttk.Frame(right)
        rbtnf.pack(fill='x', pady=6)
        ttk.Button(rbtnf, text="Сохранить отчет (JSON)",
                   command=self.on_save_report_json).pack(side='left', padx=4)
        ttk.Button(rbtnf, text="Сохранить отчет (CSV)",
                   command=self.on_save_report_csv).pack(side='left', padx=4)
        ttk.Button(rbtnf, text="Очистить",
                   command=self.on_clear_results).pack(side='left', padx=4)

        ttk.Label(
            right, text="Отчет о тестировании").pack(anchor='w', pady=(8, 0))
        self.txt_detail = tk.Text(right, height=12)
        self.txt_detail.pack(fill='both', expand=False)

        self.tree_tests.bind('<<TreeviewSelect>>', self.on_test_select)
        self.tree_results.bind('<<TreeviewSelect>>', self.on_result_select)

    def _refresh_tests_tree(self):
        self.tree_tests.delete(*self.tree_tests.get_children())
        for i, t in enumerate(self.tests):
            self.tree_tests.insert('', 'end', iid=str(i), values=(
                t['name'], 'OK' if t['expected'] else 'ОШИБКА'))

    def on_add(self):
        dlg = TestEditDialog(self, title="Новый тест")
        self.wait_window(dlg)
        if dlg.result:
            self.tests.append(dlg.result)
            self._refresh_tests_tree()

    def on_edit(self):
        sel = self.tree_tests.selection()
        if not sel:
            messagebox.showwarning("Ошибка редактирования", "Выберите тест для редактирования")
            return
        idx = int(sel[0])
        dlg = TestEditDialog(self, title="Редактирование теста", test=self.tests[idx])
        self.wait_window(dlg)
        if dlg.result:
            self.tests[idx] = dlg.result
            self._refresh_tests_tree()

    def on_delete(self):
        sel = self.tree_tests.selection()
        if not sel:
            messagebox.showwarning("Ошибка удаление", "Выберите тест для удаления")
            return
        idx = int(sel[0])
        if messagebox.askyesno("Удаление", f"Вы действительно хотите удалить тест '{self.tests[idx]['name']}'?"):
            del self.tests[idx]
            self._refresh_tests_tree()

    def on_test_select(self, event):
        sel = self.tree_tests.selection()
        if not sel:
            return
        idx = int(sel[0])
        t = self.tests[idx]
        self.txt_detail.delete('1.0', 'end')
        self.txt_detail.insert('1.0', t['input'])

    def run_test_case(self, test):
        """
        Запускает тест парсера.
        Возвращает (ok:bool, message:str).
        """
        try:
            toks = parser_module.lex(test['input'])
            p = parser_module.Parser(toks)
            ast = p.parse()
            ok = True
            message = "Успешный парсинг"

            if not isinstance(ast, parser_module.ParseResult):
                ok = False
                message = "Выражение спарсилось, но дерево имеет недействительный тип"
        except Exception as e:
            ok = False
            message = f"{e}\n{traceback.format_exc(limit=1)}"
        return ok == test['expected'], message

    def on_run_selected(self):
        sel = self.tree_tests.selection()
        if not sel:
            messagebox.showwarning("Запуск", "Для запуска выберите тест")
            return
        idx = int(sel[0])
        test = self.tests[idx]
        ok, msg = self.run_test_case(test)
        self._append_result(test['name'], ok, msg)
        self._refresh_results_table()

    def on_run_all(self):
        self.results.clear()
        for t in self.tests:
            ok, msg = self.run_test_case(t)
            self._append_result(t['name'], ok, msg)
        self._refresh_results_table()
        messagebox.showinfo("Запуск всех тестов", f"Запущено {len(self.tests)} тестов")

    def _append_result(self, name, ok, message):
        self.results.append({'test': name, 'ok': ok, 'message': message})

    def _refresh_results_table(self):
        self.tree_results.delete(*self.tree_results.get_children())
        for i, r in enumerate(self.results):
            status = "УСПЕШНО" if r['ok'] else "ОШИБКА"
            self.tree_results.insert('', 'end', iid=str(i), values=(
                r['test'], status, (r['message'] or '')[:250]))

    def on_result_select(self, event):
        sel = self.tree_results.selection()
        if not sel:
            return
        idx = int(sel[0])
        r = self.results[idx]
        self.txt_detail.delete('1.0', 'end')
        self.txt_detail.insert(
            '1.0', f"Тест: {r['test']}\nСтатус: {'УСПЕШНО' if r['ok'] else 'ОШИБКА'}\nСообщение:\n{r['message']}")

    def on_save_report_json(self):
        if not self.results:
            messagebox.showinfo("Сохранение отчета", "Нет результатов для сохранения")
            return
        f = filedialog.asksaveasfilename(
            defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not f:
            return
        with open(f, 'w', encoding='utf-8') as fh:
            json.dump(self.results, fh, ensure_ascii=False, indent=2)
        messagebox.showinfo(
            "Сохранение отчета", f"Сохранено {len(self.results)} результатов в {f}")

    def on_save_report_csv(self):
        if not self.results:
            messagebox.showinfo("Сохранение отчета", "Нет результатов для сохранения")
            return
        f = filedialog.asksaveasfilename(
            defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        if not f:
            return
        with open(f, 'w', encoding='utf-8', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(['test', 'status', 'message'])
            for r in self.results:
                w.writerow([r['test'], 'УСПЕШНО' if r['ok']
                           else 'ОШИБКА', r['message']])
        messagebox.showinfo(
            "Сохранение отчета", f"Сохранено {len(self.results)} результатов в {f}")

    def on_clear_results(self):
        self.results.clear()
        self._refresh_results_table()
        self.txt_detail.delete('1.0', 'end')

    def on_save_tests(self):
        f = filedialog.asksaveasfilename(
            defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not f:
            return
        with open(f, 'w', encoding='utf-8') as fh:
            json.dump(self.tests, fh, ensure_ascii=False, indent=2)
        messagebox.showinfo(
            "Сохранение тестов", f"Сохранено {len(self.tests)} тестов в {f}")

    def on_load_tests(self):
        f = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
        if not f:
            return
        with open(f, 'r', encoding='utf-8') as fh:
            loaded = json.load(fh)
        if isinstance(loaded, list):
            self.tests = loaded
            self._refresh_tests_tree()
            messagebox.showinfo(
                "Загрузка тестов", f"Загружено {len(self.tests)} тестов из {f}")
        else:
            messagebox.showerror("Загрузка тестов", "Неверный формат")


class TestEditDialog(tk.Toplevel):
    def __init__(self, parent, title="Редактирование теста", test=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.geometry("780x480")
        ttk.Label(self, text="Имя").pack(anchor='w', padx=6, pady=3)
        self.en_name = ttk.Entry(self)
        self.en_name.pack(fill='x', padx=6)
        self.var_expected = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Ожидает: OK",
                        variable=self.var_expected).pack(anchor='w', padx=6)
        ttk.Label(self, text="Тело теста").pack(
            anchor='w', padx=6, pady=3)
        self.txt_input = tk.Text(self, height=20)
        self.txt_input.pack(fill='both', expand=True, padx=6, pady=3)
        frame = ttk.Frame(self)
        frame.pack(fill='x', pady=6)
        ttk.Button(frame, text="Сохранить", command=self.on_save).pack(
            side='left', padx=6)
        ttk.Button(frame, text="Отменить", command=self.on_cancel).pack(
            side='left', padx=6)

        if test:
            self.en_name.insert(0, test.get('name', ''))
            self.var_expected.set(bool(test.get('expected', True)))
            self.txt_input.insert('1.0', test.get('input', ''))

    def on_save(self):
        name = self.en_name.get().strip() or "unnamed"
        expected = bool(self.var_expected.get())
        inp = self.txt_input.get('1.0', 'end').strip()
        if not inp:
            messagebox.showwarning("Ошибка ввода", "Введите тело теста")
            return
        self.result = {'name': name, 'input': inp, 'expected': expected}
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


if __name__ == "__main__":
    app = TestManagerApp()
    app.mainloop()
