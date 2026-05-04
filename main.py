import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

# --- Настройки ---
DATA_FILE = "data.json"
CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Быт", "Здоровье", "Другое"]
DATE_FORMAT = "%Y-%m-%d"

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")
        
        # Загрузка данных из файла
        self.expenses = self.load_data()
        
        # Создание виджетов
        self.create_widgets()
        
        # Заполнение таблицы начальными данными
        self.update_table()

    def create_widgets(self):
        # --- Рамка для ввода ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить расход", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w", pady=2)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=15)
        self.amount_entry.grid(row=0, column=1, sticky="w", pady=2)

        # Категория
        ttk.Label(input_frame, text="Категория:").grid(row=1, column=0, sticky="w", pady=2)
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.category_combobox = ttk.Combobox(
            input_frame, textvariable=self.category_var, 
            values=CATEGORIES, state="readonly", width=13
        )
        self.category_combobox.grid(row=1, column=1, sticky="w", pady=2)

        # Дата
        ttk.Label(input_frame, text="Дата:").grid(row=2, column=0, sticky="w", pady=2)
        self.date_entry = DateEntry(input_frame, date_pattern='yyyy-MM-dd', width=12)
        self.date_entry.grid(row=2, column=1, sticky="w", pady=2)

        # Кнопка Добавить
        ttk.Button(input_frame, text="Добавить расход", command=self.add_expense).grid(
            row=3, column=0, columnspan=2, pady=10)

        # --- Рамка для фильтрации и подсчета ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры и отчет", padding="10")
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по категории
        ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, sticky="w", pady=2)
        self.filter_category_var = tk.StringVar(value="Все")
        
        filter_cats = CATEGORIES + ["Все"]
        
        self.filter_category_combobox = ttk.Combobox(
            filter_frame, textvariable=self.filter_category_var,
            values=filter_cats, state="readonly", width=13
        )
        self.filter_category_combobox.grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(
            row=0, column=2, padx=5)

        # Период для подсчета суммы
        ttk.Label(filter_frame, text="Период для суммы:").grid(row=1, column=0, sticky="w", pady=2)
        
        self.start_date_entry = DateEntry(filter_frame, date_pattern='yyyy-MM-dd', width=12)
        self.start_date_entry.grid(row=1, column=1, sticky="w", pady=2)
        
        self.end_date_entry = DateEntry(filter_frame, date_pattern='yyyy-MM-dd', width=12)
        self.end_date_entry.grid(row=1, column=2, sticky="w", pady=2)

        ttk.Button(filter_frame, text="Подсчитать сумму", command=self.calculate_sum).grid(
            row=1, column=3, padx=5)

         # Поле для вывода суммы
         self.sum_result_var = tk.StringVar()
         ttk.Label(filter_frame, textvariable=self.sum_result_var).grid(
             row=2, column=0, columnspan=4, pady=5)
         
         # Кнопки сохранения/загрузки (для демонстрации работы с JSON)
         ttk.Button(filter_frame, text="Сохранить данные (JSON)", command=self.save_data).grid(
             row=3, columnspan=4, pady=5)

    def add_expense(self):
        """Добавляет новый расход после проверки данных."""
        amount_str = self.amount_var.get()
        category = self.category_var.get()
        
        # Валидация суммы
        try:
            amount = float(amount_str.replace(',', '.'))
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной.")
            if len(str(amount).split('.')[1]) > 2: # Проверка на копейки (не более 2 знаков)
                raise ValueError("Слишком много знаков после запятой.")
            amount = round(amount, 2) # Округляем до 2 знаков
            self.amount_var.set(f"{amount:.2f}") # Обновляем поле для красоты
            
            # Валидация даты (DateEntry сам по себе не дает ввести неверную дату)
            date_str = self.date_entry.get_date().strftime(DATE_FORMAT)
            
            # Добавление в список и таблицу
            self.expenses.append({"date": date_str, "category": category, "amount": amount})
            self.update_table()
            
            # Очистка полей после успешного добавления
            self.amount_var.set("")
            
            # Сохраняем автоматически после каждого добавления
            self.save_data()
            
            messagebox.showinfo("Успех", "Расход добавлен!")
            
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))

    def update_table(self):
        """Обновляет данные в таблице с учетом текущего фильтра."""
        
        # Очистка таблицы
        for i in self.tree.get_children():
            self.tree.delete(i)
            
         # Применение фильтра по категории
         filter_cat = self.filter_category_var.get()
         filtered_expenses = self.expenses if filter_cat == "Все" else [
             exp for exp in self.expenses if exp["category"] == filter_cat
         ]
         
         # Вставка данных в таблицу
         for exp in filtered_expenses:
             self.tree.insert("", "end", values=(exp["date"], exp["category"], f"{exp['amount']:.2f}"))
         
    def apply_filter(self):
         """Применяет фильтр к таблице."""
         self.update_table()
         
    def calculate_sum(self):
         """Подсчитывает сумму расходов за указанный период."""
         try:
             start_date_str = self.start_date_entry.get_date().strftime(DATE_FORMAT)
             end_date_str = self.end_date_entry.get_date().strftime(DATE_FORMAT)
             
             start_date = datetime.strptime(start_date_str, DATE_FORMAT)
             end_date = datetime.strptime(end_date_str, DATE_FORMAT) + \
                        datetime.timedelta(days=1) # Чтобы включить последний день

             total_sum = sum(
                 exp["amount"] for exp in self.expenses 
                 if start_date <= datetime.strptime(exp["date"], DATE_FORMAT) < end_date
             )
             
             self.sum_result_var.set(f"Сумма за период: {total_sum:.2f} ₽")
             
         except Exception as e:
             messagebox.showerror("Ошибка", "Проверьте правильность введенных дат.")
             
    def create_table(self):
         """Создает таблицу для отображения расходов."""
         columns = ("date", "category", "amount")
         self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
         
         self.tree.heading("date", text="Дата")
         self.tree.heading("category", text="Категория")
         self.tree.heading("amount", text="Сумма")
         
         self.tree.column("date", width=120)
         self.tree.column("category", width=150)
         self.tree.column("amount", width=100)
         
         self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
         
    def load_data(self):
         """Загружает данные из JSON файла."""
         if os.path.exists(DATA_FILE):
             with open(DATA_FILE, 'r', encoding='utf-8') as f:
                 try:
                     data = json.load(f)
                     # Проверка структуры данных на случай ручного редактирования JSON
                     for item in data:
                         if not all(k in item for k in ("date", "category", "amount")):
                             raise ValueError("Неверная структура данных в JSON.")
                     return data
                 except json.JSONDecodeError:
                     messagebox.showwarning("Файл данных",
                         f"Файл {DATA_FILE} поврежден или пуст. Будет создан новый.")
                     return []
                 except ValueError as e:
                     messagebox.showerror("Ошибка данных", str(e))
                     return []
         return []
         
    def save_data(self):
         """Сохраняет данные в JSON файл."""
         with open(DATA_FILE, 'w', encoding='utf-8') as f:
             json.dump(self.expenses, f, ensure_ascii=False, indent=4)
             
    def run(self):
         """Запускает главный цикл приложения."""
         self.create_table() # Создаем таблицу после инициализации всех данных
         self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    app.run()