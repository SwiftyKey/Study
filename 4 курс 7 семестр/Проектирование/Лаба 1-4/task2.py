import tkinter as tk
from tkinter import messagebox


def binomial_coefficient(m, n):
    if m < 0 or m > n:
        return 0
    if m == 0 or m == n:
        return 1

    m = min(m, n - m)
    result = 1
    for i in range(m):
        result = result * (n - i) // (i + 1)
    return result


def format_power(base, exp):
    if exp == 0:
        return ""
    elif exp == 1:
        return base
    else:
        return f"{base}^{exp}"


def format_term(m, n, a, b):
    coeff = binomial_coefficient(m, n)
    power_a = n - m
    power_b = m

    term_a = format_power(a, power_a)
    term_b = format_power(b, power_b)

    parts = []
    if coeff != 1 or (not term_a and not term_b):
        if coeff == 1 and n == 0:
            parts.append("1")
        elif coeff != 1:
            parts.append(str(coeff))
    if term_a:
        parts.append(term_a)
    if term_b:
        parts.append(term_b)

    return "·".join(parts)


def expand_binomial(a, b, n):
    if n == 0:
        return "1"
    terms = []
    for m in range(n + 1):
        term = format_term(m, n, a, b)
        if term:
            terms.append(term)
    return " + ".join(terms)


def on_expand():

    var_a = entry_a.get().strip()
    var_b = entry_b.get().strip()
    n_str = entry_n.get().strip()

    if not var_a:
        messagebox.showerror("Ошибка", "Введите переменную a.")
        return
    if not var_b:
        messagebox.showerror("Ошибка", "Введите переменную b.")
        return

    if not n_str.isdigit():
        messagebox.showerror(
            "Ошибка", "Степень n должна быть натуральным числом (целое ≥ 0).")
        return

    n = int(n_str)
    if n > 20:
        messagebox.showwarning(
            "Предупреждение", "Степень слишком высока (ограничение: ≤ 20).")
        return

    try:
        result = expand_binomial(var_a, var_b, n)
        expression = f"({var_a} + {var_b})^{n} = {result}"
        text_result.config(state='normal')
        text_result.delete(1.0, tk.END)
        text_result.insert(tk.END, expression)
        text_result.config(state='disabled')
    except Exception as e:
        messagebox.showerror(
            "Ошибка", f"Произошла ошибка при вычислении: {str(e)}")


root = tk.Tk()
root.title("Разложение бинома Ньютона")
root.geometry("600x400")
root.resizable(False, False)


title = tk.Label(root, text="Разложение бинома Ньютона",
                 font=("Arial", 16, "bold"))
title.pack(pady=10)


frame_input = tk.Frame(root)
frame_input.pack(pady=10)

tk.Label(frame_input, text="Переменная a:", font=("Arial", 12)).grid(
    row=0, column=0, padx=5, pady=5, sticky='e')
entry_a = tk.Entry(frame_input, font=("Arial", 12), width=10)
entry_a.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_input, text="Переменная b:", font=("Arial", 12)).grid(
    row=1, column=0, padx=5, pady=5, sticky='e')
entry_b = tk.Entry(frame_input, font=("Arial", 12), width=10)
entry_b.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_input, text="Степень n:", font=("Arial", 12)).grid(
    row=2, column=0, padx=5, pady=5, sticky='e')
entry_n = tk.Entry(frame_input, font=("Arial", 12), width=10)
entry_n.grid(row=2, column=1, padx=5, pady=5)


btn_expand = tk.Button(root, text="Разложить",
                       font=("Arial", 12), command=on_expand)
btn_expand.pack(pady=10)


text_result = tk.Text(root, font=("Courier", 12),
                      wrap=tk.WORD, height=6, width=70, state='disabled')
text_result.pack(padx=20, pady=10)


footer = tk.Label(root, text="Формат: (a + b)^n",
                  font=("Arial", 10), fg="gray")
footer.pack(pady=5)


root.mainloop()
