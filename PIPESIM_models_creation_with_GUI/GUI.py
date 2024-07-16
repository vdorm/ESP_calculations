import tkinter as tk
from tkinter import font
from tkinter import ttk
import os

import subprocess
import threading

current_directory = os.getcwd()

def execute_script(script_name, status_label):
    def run_script():
        status_label.config(text=f"Выполняется создание модели '{script_name}'")
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
            subprocess.run(["python", script_path], check=True)
            status_label.config(text=f"Модель '{script_name}' создана.")
        except subprocess.CalledProcessError:
            status_label.config(text=f"Ошибка при создании модели '{script_name}'")

    threading.Thread(target=run_script).start()

root = tk.Tk()
root.title("Расчетный модуль")
root.geometry("400x250") # Устанавливаем размер основного окна

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

main_tab = ttk.Frame(notebook)
notebook.add(main_tab, text='Создание моделей PIPESIM')

custom_font = font.Font(family="Arial", size=12)

# Label для отображения статуса
status_label1 = tk.Label(main_tab, text="")
status_label2 = tk.Label(main_tab, text="")
status_label3 = tk.Label(main_tab, text="")

# Модель 1
script_1_name = "ESP_P_DIS_water_model_creation_PTK.py"
script_1_full_path = current_directory + "\\" + script_1_name
button1 = tk.Button(main_tab, text="Создать модель ESP_P_DIS_water", 
                    command=lambda: execute_script(script_1_name, status_label1))
button1.pack(pady=10)
status_label1.pack()

# Модель 2
script_2_name = "ESP_P_DIS_oil_model_creation_PTK.py"
script_2_full_path = current_directory + "\\" + script_2_name
button2 = tk.Button(main_tab, text="Создать модель ESP_P_DIS_oil", 
                    command=lambda: execute_script(script_2_name, status_label2))
button2.pack(pady=10)
status_label2.pack()

# Модель 3
script_3_name = "pipesim_model_creation_PTK.py"
script_3_full_path = current_directory + "\\" + script_3_name
button3 = tk.Button(main_tab, text="Создать модель PIPESIM для анализа свойств флюида", 
                    command=lambda: execute_script(script_3_name, status_label3))
button3.pack(pady=10)
status_label3.pack()

root.mainloop()