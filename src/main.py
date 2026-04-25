import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from main_screens import InitialSetupScreen
# from other_frames import show_processing_popup
import json

class ProcessControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng Kiểm soát Quy trình")
        # self.root.attributes("-fullscreen", True)
        self.root.geometry("1200x600")  # Kích thước cửa sổ mặc định
        
        # Tạo Frame chính
        self.main_frame = tk.Frame(self.root, bg="lightgray")
        self.main_frame.pack(fill="both", expand=True)
        # Tiêu đề ứng dụng
        self.title_label = tk.Label(
            self.main_frame,
            text="ỨNG DỤNG KIỂM SOÁT\nQUY TRÌNH",
            font=("Times New Roman", 55, "bold"),
            justify="center",
            bg="lightgray",
        )
        self.title_label.pack(pady=50)

        # Khung chứa nút
        self.button_frame = tk.Frame(self.main_frame, bg="lightgray")
        self.button_frame.pack(pady=20, side="bottom")

        # Nút New
        self.new_button = tk.Button(
            self.button_frame,
            text="New",
            font=("Times New Roman", 20),
            width=40,
            height=3,
            bg="gray",
            fg="black",
            command= self.handle_new_file_selection
        )
        self.new_button.pack(side="left", padx=20, pady=20)

        # Nút Open
        self.open_button = tk.Button(
            self.button_frame,
            text="Open",
            font=("Times New Roman", 20),
            width=40,
            height=3,
            bg="gray",
            fg="black",
            command= self.handle_open_setup
        )
        self.open_button.pack(side="right", padx=20, pady=20)

    def handle_new_file_selection(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file dữ liệu quy trình",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls")]
        )

        if file_path:
            # def process():
            self.main_frame.pack_forget()
            InitialSetupScreen(self.root, file_path, start_screen=self)
            
    def handle_open_setup(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file thiết lập quy trình",
            filetypes=[("JSON files", "*.json")]
        )

        if file_path:
            # def process():
            self.main_frame.pack_forget()
            with open(file_path, 'r') as json_file:
                initial_data = json.load(json_file)
                process_name = initial_data.get("process_name")
                log_path = initial_data.get("log_path")
                columns = initial_data.get("columns")
                recorded_at = initial_data.get("recorded_at")
                time_unit = initial_data.get("time_unit")
            InitialSetupScreen(
                self.root,
                start_screen=self,
                file_path=log_path,
                initial_data={
                    "process_name": process_name,
                    "columns": columns,
                    "recorded_at": recorded_at,
                    "time_unit": time_unit
                }
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessControlApp(root)
    root.mainloop()