import tkinter as tk
from tkinter import messagebox
import math
from functools import lru_cache



def is_prime(num):
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(num)) + 1, 2):
        if num % i == 0:
            return False
    return True


def find_primes(n):
    return [num for num in range(2, n + 1) if is_prime(num)]


def on_find_primes():
    input_text = entry_n.get().strip()

    if not input_text:
        entry_n.delete(0, tk.END)
        messagebox.showerror("Ошибка ввода", "Поле не должно быть пустым.")

        return

    if not input_text.isdigit():
        entry_n.delete(0, tk.END)
        messagebox.showerror(
            "Ошибка ввода", "Введите натуральное число (целое положительное).")

        return

    n = int(input_text)

    if n > 100000:
        messagebox.showerror("Переполнение", "Введите число до 100000")
        return

    if n < 1:
        entry_n.delete(0, tk.END)
        messagebox.showerror(
            "Ошибка ввода", "Число должно быть натуральным (≥ 1).")

        return

    primes = find_primes(n)

    if primes:
        result = ", ".join(map(str, primes))
    else:
        result = "Простых чисел нет."

    text_output.config(state='normal')
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, f"Простые числа от 1 до {n}:\n\n{result}")
    text_output.config(state='disabled')


root = tk.Tk()
root.title("Поиск простых чисел")
root.geometry("500x400")
root.resizable(False, False)


label_title = tk.Label(root, text="Поиск простых чисел",
                       font=("Arial", 16, "bold"))
label_title.pack(pady=10)


label_prompt = tk.Label(
    root, text="Введите натуральное число n:", font=("Arial", 12))
label_prompt.pack(pady=5)


entry_n = tk.Entry(root, font=("Arial", 12), width=20)
entry_n.pack(pady=5)


button_find = tk.Button(root, text="Найти простые числа",
                        font=("Arial", 12), command=on_find_primes)
button_find.pack(pady=10)


text_output = tk.Text(root, font=("Arial", 10), wrap=tk.WORD,
                      height=12, width=60, state='disabled')
text_output.pack(padx=20, pady=10)


root.mainloop()
