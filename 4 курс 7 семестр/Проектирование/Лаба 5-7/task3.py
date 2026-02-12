import tkinter as tk
from tkinter import ttk, messagebox
import re
from collections import deque


# ------------- Парсер / граф -------------
def extract_functions_and_bodies(text):
    """
    Находит определения функций в виде:
      def name(...):
          <тело>
    Возвращает dict name -> body_text
    (тело — всё до следующего 'def ' на уровне начала строки или до конца текста)
    """
    pattern = re.compile(
        r'^\s*def\s+([A-Za-zА-Яа-я_]\w*)\s*\([^)]*\)\s*:\s*', re.MULTILINE)
    funcs = {}
    matches = list(pattern.finditer(text))
    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.end()
        end = len(text)
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        body = text[start:end]
        funcs[name] = body
    return funcs


def find_calls_in_body(body, function_names):
    """
    Находит все вызовы вида name( в тексте body — простая эвристика.
    Возвращает множество найденных имён, пересекающихся с function_names.
    """
    calls = set()
    for m in re.finditer(r'([A-Za-z_]\w*)\s*\(', body):
        name = m.group(1)
        if name in function_names:
            calls.add(name)
    return calls


def build_call_graph(text):
    funcs = extract_functions_and_bodies(text)
    names = set(funcs.keys())
    graph = {name: set() for name in names}
    for name, body in funcs.items():
        calls = find_calls_in_body(body, names)
        graph[name].update(calls)
    return graph


def topo_sort_kahn(graph):
    indeg = {u: 0 for u in graph}
    for u in graph:
        for v in graph[u]:
            indeg[v] = indeg.get(v, 0) + 1
    q = deque([u for u in indeg if indeg[u] == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph.get(u, ()):
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    is_cycle = len(order) != len(indeg)
    return order, is_cycle


# ------------- Разметка и отрисовка -------------
def compute_levels(graph):
    """
    Возвращает mapping node -> level (целое), где level — минимальное расстояние
    от источников (вместо того чтобы пытаться делать строго топологические уровни).
    Для корректной топологической визуализации мы используем longest-path по DAG (если DAG),
    иначе используем BFS от источников.
    """
    order, is_cycle = topo_sort_kahn(graph)
    levels = {}
    if not is_cycle:
        for u in order:
            if u not in levels:
                levels[u] = 0
            for v in graph[u]:
                levels[v] = max(levels.get(v, 0), levels[u] + 1)
    else:
        indeg = {u: 0 for u in graph}
        for u in graph:
            for v in graph[u]:
                indeg[v] = indeg.get(v, 0)+1
        sources = [u for u, d in indeg.items() if d == 0]

        if not sources:
            sources = list(graph.keys())[:1]
        from collections import deque
        q = deque()
        for s in sources:
            levels[s] = 0
            q.append(s)
        while q:
            u = q.popleft()
            for v in graph[u]:
                if v not in levels or levels[v] > levels[u] + 1:
                    levels[v] = levels[u] + 1
                    q.append(v)
        for u in graph:
            levels.setdefault(u, 0)
    return levels


def layout_nodes_by_levels(levels, canvas_w, canvas_h, margin=50):
    from collections import defaultdict
    lvlmap = defaultdict(list)
    for n, l in levels.items():
        lvlmap[l].append(n)
    sorted_levels = sorted(lvlmap.keys())
    cols = len(sorted_levels)
    positions = {}
    if cols == 0:
        return positions
    xstep = (canvas_w - 2*margin) / max(1, cols-1) if cols > 1 else 0
    for i, l in enumerate(sorted_levels):
        nodes = lvlmap[l]
        ncount = len(nodes)
        ystep = (canvas_h - 2*margin) / max(1, ncount-1) if ncount > 1 else 0
        for j, node in enumerate(nodes):
            x = margin + i * xstep if cols > 1 else canvas_w/2
            y = margin + j * ystep if ncount > 1 else canvas_h/2
            positions[node] = (x, y)
    return positions


# ------------- GUI -------------
class CallGraphApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Анализ вызовов подпрограмм")
        self.geometry("1100x700")
        self._build_ui()
        self.graph = {}
        self.positions = {}
        self.node_items = {}
        self.edge_items = []

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(side='top', fill='x', padx=6, pady=6)

        ttk.Label(top, text="Вставьте текст программы (def ...):").pack(
            anchor='w')
        main = ttk.Frame(self)
        main.pack(fill='both', expand=True, padx=6, pady=6)

        left = ttk.Frame(main, width=400)
        left.pack(side='left', fill='y')

        self.text = tk.Text(left, width=60, height=30, wrap='none')
        self.text.pack(side='top', fill='both', expand=False)
        sample = (
            "def main():\n"
            "    f1()\n"
            "    f2()\n\n"
            "def f1():\n"
            "    f3()\n\n"
            "def f2():\n"
            "    f3()\n\n"
            "def f3():\n"
            "    pass\n"
        )
        self.text.insert('1.0', sample)

        btns = ttk.Frame(left)
        btns.pack(fill='x', pady=6)
        ttk.Button(btns, text="Анализировать и построить граф",
                   command=self.on_analyze).pack(side='left', padx=3)
        ttk.Button(btns, text="Топологическая сортировка",
                   command=self.on_topo).pack(side='left', padx=3)
        ttk.Button(btns, text="Сохранить холст...",
                   command=self.on_save_canvas).pack(side='left', padx=3)

        info_frame = ttk.LabelFrame(left, text="Функции и вызовы")
        info_frame.pack(fill='both', expand=True, pady=6)
        self.info_text = tk.Text(info_frame, height=12, wrap='word')
        self.info_text.pack(fill='both', expand=True)
        self.info_text.config(state='disabled')
        right = ttk.Frame(main)
        right.pack(side='left', fill='both', expand=True)
        cframe = ttk.Frame(right)
        cframe.pack(fill='both', expand=True)
        self.canvas = tk.Canvas(cframe, bg='white')
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.status = ttk.Label(self, text="Готово",
                                relief='sunken', anchor='w')
        self.status.pack(side='bottom', fill='x')
        self.bind("<Configure>", lambda e: None)

    def on_analyze(self):
        text = self.text.get("1.0", "end")
        self.status.config(text="Парсинг...")
        try:
            graph = build_call_graph(text)
            self.graph = {k: set(v) for k, v in graph.items()}
            self._render_graph()
            self._show_info()
            self.status.config(
                text=f"Готово — найдено {len(self.graph)} функций")
        except Exception as e:
            messagebox.showerror("Ошибка парсинга", str(e))
            self.status.config(text="Ошибка")

    def on_topo(self):
        if not self.graph:
            messagebox.showinfo(
                "Топо", "Сначала выполните анализ (кнопка 'Анализировать...').")
            return
        order, is_cycle = topo_sort_kahn(self.graph)
        if is_cycle:
            messagebox.showwarning(
                "Топологическая сортировка", "Граф содержит цикл — топологическая сортировка невозможна.")
            self.status.config(
                text="Цикл обнаружен; топологическая сортировка невозможна")
        else:
            messagebox.showinfo("Топологический порядок", " → ".join(order))
            self.status.config(text="Топологическая сортировка выполнена")

    def on_save_canvas(self):
        from tkinter import filedialog
        fname = filedialog.asksaveasfilename(
            defaultextension=".ps", filetypes=[("PostScript", "*.ps")])
        if not fname:
            return
        try:
            ps = self.canvas.postscript(colormode='color')
            with open(fname, 'w') as f:
                f.write(ps)
            messagebox.showinfo("Сохранено", f"Сохранено в {fname}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _show_info(self):
        self.info_text.config(state='normal')
        self.info_text.delete("1.0", "end")
        for u in sorted(self.graph.keys()):
            outs = sorted(self.graph[u])
            ins = sorted([v for v in self.graph if u in self.graph[v]])
            self.info_text.insert(
                "end", f"{u}:\n  вызывает: {', '.join(outs) or '-'}\n  вызывается из: {', '.join(ins) or '-'}\n\n")
        self.info_text.config(state='disabled')

    def _render_graph(self):
        self.canvas.delete('all')
        self.node_items.clear()
        self.edge_items.clear()
        self.positions.clear()
        if not self.graph:
            return
        w = max(600, self.canvas.winfo_width() or 800)
        h = max(400, self.canvas.winfo_height() or 600)
        levels = compute_levels(self.graph)
        self.positions = layout_nodes_by_levels(levels, w, h, margin=80)
        for u in self.graph:
            for v in self.graph[u]:
                if u in self.positions and v in self.positions:
                    x1, y1 = self.positions[u]
                    x2, y2 = self.positions[v]
                    line = self.canvas.create_line(
                        x1, y1, x2, y2, arrow='last', width=2, fill='#444')
                    self.edge_items.append(line)
        r = 26
        for node, (x, y) in self.positions.items():
            oval = self.canvas.create_oval(
                x-r, y-r, x+r, y+r, fill='lightyellow', outline='black', width=2)
            text = self.canvas.create_text(
                x, y, text=node, font=('Arial', 10), width=2*r)
            self.node_items[node] = (oval, text)
        for node, (oval, text) in self.node_items.items():
            self.canvas.tag_bind(oval, "<Button-1>", lambda e,
                                 n=node: self._on_node_click(n))
            self.canvas.tag_bind(text, "<Button-1>", lambda e,
                                 n=node: self._on_node_click(n))

    def on_canvas_click(self, event):
        self._clear_highlight()

    def _on_node_click(self, node):
        self._clear_highlight()
        if node not in self.node_items:
            return
        oval, text = self.node_items[node]
        self.canvas.itemconfig(oval, fill='#ffd27f')
        for u in self.graph:
            for v in self.graph[u]:
                if u == node or v == node:
                    pass
        x0, y0 = self.positions[node]
        for line in self.edge_items:
            coords = self.canvas.coords(line)
            if not coords or len(coords) < 4:
                continue
            x1, y1, x2, y2 = coords
            if (abs(x1-x0) < 5 and abs(y1-y0) < 5) or (abs(x2-x0) < 5 and abs(y2-y0) < 5):
                self.canvas.itemconfig(line, fill='red', width=3)
        self.info_text.config(state='normal')
        self.info_text.delete("1.0", "end")
        outs = sorted(self.graph[node])
        ins = sorted([v for v in self.graph if node in self.graph[v]])
        self.info_text.insert("end", f"Узел: {node}\n")
        self.info_text.insert(
            "end", f"  вызывает: {', '.join(outs) or '-'}\n")
        self.info_text.insert(
            "end", f"  вызывается из: {', '.join(ins) or '-'}\n")
        self.info_text.config(state='disabled')
        self.status.config(text=f"Выбран узел: {node}")

    def _clear_highlight(self):
        for node, (oval, text) in self.node_items.items():
            self.canvas.itemconfig(oval, fill='lightyellow')
        for line in self.edge_items:
            try:
                self.canvas.itemconfig(line, fill='#444', width=2)
            except:
                pass
        self.status.config(text="Готово")


# ------------- Запуск -------------
if __name__ == "__main__":
    app = CallGraphApp()
    app.mainloop()
