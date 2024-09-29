import tkinter as tk
from tkinter import messagebox
from pymodbus.client import ModbusSerialClient
import struct

def update_button_text():
    operation = operation_var.get()
    execute_button.config(text=operation)

def execute_modbus():
    port = port_entry.get()
    baudrate = int(baudrate_entry.get())
    address = int(address_entry.get())
    register = int(register_entry.get())
    value = int(value_entry.get()) if operation_var.get() == "Запись" else 0
    mode = mode_var.get()
    operation = operation_var.get()
    data_type = data_type_var.get()
    execute_button.config(text=operation)

    try:
        client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            timeout=3,
            stopbits=1,
            bytesize=8,
            parity='N'
        )

        if client.connect():
            if operation == "Запись":
                if mode == "Holding Register":
                    if data_type == "uint16":
                        response = client.write_register(register, value, slave=address)
                    elif data_type == "uint32":
                        response = client.write_registers(register, [value >> 16, value & 0xFFFF], slave=address)
                    elif data_type == "float32":
                        packed_value = struct.pack('>f', value)
                        high, low = struct.unpack('>HH', packed_value)
                        response = client.write_registers(register, [high, low], slave=address)
                elif mode == "Coil":
                    response = client.write_coil(register, value, slave=address)

                if response.isError():
                    messagebox.showerror("Ошибка", "Ошибка при записи: " + str(response))
                else:
                    messagebox.showinfo("Успех", "Запись прошла успешно")

            elif operation == "Чтение":
                if mode == "Holding Register":
                    if data_type == "uint16":
                        response = client.read_holding_registers(register, 1, slave=address)
                        result_value = response.registers[0] if response else None
                    elif data_type == "uint32":
                        response = client.read_holding_registers(register, 2, slave=address)
                        result_value = (response.registers[0] << 16) + response.registers[1] if response else None
                    elif data_type == "float32":
                        response = client.read_holding_registers(register, 2, slave=address)
                        if response:
                            packed_value = struct.pack('>HH', response.registers[0], response.registers[1])
                            result_value = struct.unpack('>f', packed_value)[0]
                elif mode == "Coil":
                    response = client.read_coils(register, 1, slave=address)
                    result_value = response.bits[0] if response else None

                if response.isError():
                    messagebox.showerror("Ошибка", "Ошибка при чтении: " + str(response))
                else:
                    messagebox.showinfo("Результат", f"Прочитанное значение: {result_value}")

            client.close()
        else:
            messagebox.showerror("Ошибка", "Не удалось подключиться к устройству")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


# Создаем графический интерфейс
window = tk.Tk()
window.title("Modbus RTU Чтение/Запись")
window.geometry("400x500")

# Поля для ввода порта, скорости и адреса устройства
tk.Label(window, text="COM-порт").pack()
port_entry = tk.Entry(window)
port_entry.pack()
port_entry.insert(0, "COM3")

tk.Label(window, text="Скорость (baudrate)").pack()
baudrate_entry = tk.Entry(window)
baudrate_entry.pack()
baudrate_entry.insert(0, "19200")

tk.Label(window, text="Адрес устройства").pack()
address_entry = tk.Entry(window)
address_entry.pack()
address_entry.insert(0, "1")

tk.Label(window, text="Адрес регистра/coil").pack()
register_entry = tk.Entry(window)
register_entry.pack()
register_entry.insert(0, "65010")

tk.Label(window, text="Значение для записи (игнорируется при чтении)").pack()
value_entry = tk.Entry(window)
value_entry.pack()
value_entry.insert(0, "1")

# Радиокнопки для выбора между Holding Register и Coil
mode_var = tk.StringVar(value="Holding Register")
tk.Radiobutton(window, text="Holding Register", variable=mode_var, value="Holding Register").pack(anchor=tk.W)
tk.Radiobutton(window, text="Coil", variable=mode_var, value="Coil").pack(anchor=tk.W)

# Радиокнопки для выбора операции: Чтение или Запись
operation_var = tk.StringVar(value="Запись")
tk.Radiobutton(window, text="Запись", variable=operation_var, value="Запись", command=update_button_text).pack(anchor=tk.W)
tk.Radiobutton(window, text="Чтение", variable=operation_var, value="Чтение", command=update_button_text).pack(anchor=tk.W)

# Выбор типа данных
tk.Label(window, text="Тип данных").pack()
data_type_var = tk.StringVar(value="uint16")
tk.Radiobutton(window, text="uint16", variable=data_type_var, value="uint16").pack(anchor=tk.W)
tk.Radiobutton(window, text="uint32", variable=data_type_var, value="uint32").pack(anchor=tk.W)
tk.Radiobutton(window, text="float32", variable=data_type_var, value="float32").pack(anchor=tk.W)
tk.Radiobutton(window, text="bool", variable=data_type_var, value="bool").pack(anchor=tk.W)

# Кнопка для выполнения операции
execute_button = tk.Button(window, text="Запись", command=execute_modbus)
execute_button.pack(pady=10)

# Запуск главного цикла программы
window.mainloop()
