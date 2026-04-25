import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import analysis_tab
import improvement_tab
from plot_and_dataframe import AnalysisData, ImprovingData
import json
from other_frames import show_processing_popup

class InitialSetupScreen:
    def __init__(self, root, file_path, initial_data=None, start_screen = None):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        self.start_screen = start_screen
        self.file_path = file_path
        self.initial_data = initial_data
        
        # Nút TIẾP TỤC góc phải trên
        self.continue_button = tk.Button(self.frame, text="TIẾP TỤC", bg="#4CAF50", fg="white",
                                        command=self.on_continue, font=("Arial", 15, "bold")) 
        self.continue_button.grid(row=1, column=4, sticky='e', padx=5, pady=5)
        
        # Nút lưu thiết lập 
        self.save_initial_button = tk.Button(self.frame, text="LƯU THIẾT LẬP", bg="#2196F3", fg="white",
                                    command=self.on_initial_save, font=("Arial", 15, "bold"))
        self.save_initial_button.grid(row=0, column=4, sticky='e', padx=5, pady=5)
        
        #TIÊU ĐỀ
        self.title_label = tk.Label(self.frame, text="THIẾT LẬP QUY TRÌNH", font=("Arial", 20, "bold"))
        self.title_label.grid(row=0, column=1, pady=(10, 20))
        
        #Nút quay lại
        tk.Button(self.frame, text="QUAY LẠI", font=("Arial", 15, "bold"), bg="red", fg="white", command=self.back_to_start).grid(row=0, column=0, sticky='w', padx=5, pady=5)

        # TÊN QUY TRÌNH
        tk.Label(self.frame, text="TÊN QUY TRÌNH", font=("Arial", 20, "bold")).grid(row=1, column=0, sticky='w')
        self.process_name_entry = tk.Entry(self.frame, width=40, bg="lightgrey", font=("Arial", 20))
        self.process_name_entry.grid(row=1, column=1, padx=10, pady=5)

        # ĐƯỜNG DẪN FILE
        tk.Label(self.frame, text="ĐƯỜNG DẪN FILE DATA", font=("Arial", 20, "bold")).grid(row=2, column=0, sticky='w')
        self.file_entry = tk.Entry(self.frame, width=40, bg="lightgrey", font=("Arial", 20))
        self.file_entry.insert(0, file_path)
        self.file_entry.config(state='disabled')
        self.file_entry.grid(row=2, column=1, padx=10, pady=5)

        # CÁC CỘT YÊU CẦU
        tk.Label(self.frame, text="CÁC CỘT YÊU CẦU", font=("Arial", 17, "bold")).grid(row=3, column=0, columnspan=5, pady=(20, 5))
        
        tk.Label(self.frame, text="CỘT CHỨA MÃ TRƯỜNG HỢP (CASE ID)").grid(row=4, column=0, pady=1)
        self.case_id_cb = ttk.Combobox(self.frame, state="readonly", width=30)
        self.case_id_cb.grid(row=5, column=0)
        
        tk.Label(self.frame, text="CỘT CHỨA TÊN HOẠT ĐỘNG (ACTIVITY)").grid(row=4, column=1, pady=1)
        self.activity_cb = ttk.Combobox(self.frame, state="readonly", width=30)
        self.activity_cb.grid(row=5, column=1)
        
        tk.Label(self.frame, text="CỘT CHỨA THỜI GIAN (TIMESTAMP)").grid(row=4, column=2, pady=1)
        self.timestamp_cb = ttk.Combobox(self.frame, state="readonly", width=20)
        self.timestamp_cb.grid(row=5, column=2)
        
        tk.Label(self.frame, text="GHI NHẬN LÚC").grid(row=4, column=3, pady=1)
        self.recorded_cb = ttk.Combobox(self.frame, values= ["start", "end"], state="readonly", width=20)
        self.recorded_cb.grid(row=5, column=3)
        
        tk.Label(self.frame, text="ĐƠN VỊ TÍNH").grid(row=4, column=4, pady=1)
        self.time_unit_cb = ttk.Combobox(self.frame, values= ["Năm", "Tháng", "Ngày", "Giờ", "Phút", "Giây"], state="readonly", width=20)
        self.time_unit_cb.grid(row=5, column=4)
        
        tk.Label(self.frame, text="DATA MẪU", font=("Arial", 12, "bold")).grid(row=6, column=0, columnspan=5, pady=(20, 5), sticky="we")
        
        show_processing_popup(self.frame, self._process, message="Đang xử lý. Vui lòng chờ...", on_done=self._next)
        
    def _process(self):
        df = pd.read_excel(self.file_path) if self.file_path.endswith(".xlsx") else pd.read_csv(self.file_path)
        return df
        # self.df.columns = self.df.columns.str.lower().str.replace(" ", "_")
        
    def _next(self, result):
        self.df = result
        columns = list(self.df.columns)

        self.case_id_cb.config(values=columns)
        self.activity_cb.config(values=columns)
        self.timestamp_cb.config(values=columns)
        
        if self.initial_data:
            # Nếu có dữ liệu ban đầu, điền vào các trường
            self.process_name_entry.insert(0, self.initial_data["process_name"])
            self.case_id_cb.set(self.initial_data["columns"]["case_id"])
            self.activity_cb.set(self.initial_data["columns"]["activity"])
            self.timestamp_cb.set(self.initial_data["columns"]["timestamp"])
            self.recorded_cb.set(self.initial_data["recorded_at"])
            self.time_unit_cb.set(self.initial_data["time_unit"])

        # DATA MẪU
        self.create_table_preview()
        

    def create_table_preview(self):
        preview_frame = tk.Frame(self.frame)
        preview_frame.grid(row=7, column=0, columnspan=5, sticky="nsew", pady=10, rowspan=4)

        # Cho phép co giãn khung chứa table
        self.frame.rowconfigure(7, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, weight=1)

        # Scrollbar dọc và ngang
        vsb = ttk.Scrollbar(preview_frame, orient="vertical")
        hsb = ttk.Scrollbar(preview_frame, orient="horizontal")

        # Tạo Treeview
        table = ttk.Treeview(
            preview_frame,
            columns=list(self.df.columns),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=table.yview)
        hsb.config(command=table.xview)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        table.pack(expand=True, fill="both")

        # Định nghĩa cột và dữ liệu
        for col in self.df.columns:
            table.heading(col, text=col)
            table.column(col, width=150, anchor="w", stretch=False)  # bạn có thể tăng giảm width

        for _, row in self.df.head(30).iterrows():
            table.insert("", "end", values=list(row))


    def on_continue(self):
        ''' Xử lý khi bấm TIẾP TỤC '''
        # Kiểm tra xem các trường đã được chọn chưa
        if not all([self.case_id_cb.get(), self.activity_cb.get(), self.timestamp_cb.get(), self.recorded_cb.get()]):
            messagebox.showerror("Lỗi", "Vui lòng chọn tất cả các trường yêu cầu.")
            return

        self.frame.pack_forget()
        self.sidebar = SidebarMenu(self.root, self.df, start_screen=self.start_screen, initial_screen=self)
        self.sidebar.process_name_label.config(text=f"Tên quy trình:\n{self.process_name_entry.get()}")
            
    def on_initial_save(self):
        ''' Xử lý khi bấm LƯU THIẾT LẬP '''
        if not all([self.case_id_cb.get(), self.activity_cb.get(), self.timestamp_cb.get(), self.recorded_cb.get()]):
            messagebox.showerror("Lỗi", "Vui lòng chọn tất cả các trường yêu cầu.")
            return
        data = {
        "process_name": self.process_name_entry.get(),
        "log_path": self.file_path,
        "columns": {
            "case_id": self.case_id_cb.get(),
            "activity": self.activity_cb.get(),
            "timestamp": self.timestamp_cb.get(),
            },
        "recorded_at": self.recorded_cb.get(),
        "time_unit": self.time_unit_cb.get()
        }
        # Lưu vào file JSON
        file_save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Chọn nơi lưu file JSON",
            initialfile=f"{self.process_name_entry.get()}_initial_setup.json"
        )
        if file_save_path:
            with open(file_save_path, 'w') as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
            messagebox.showinfo("Thành công", "Thiết lập đã được lưu thành công!")
            
    def back_to_start(self):
        if hasattr(self, "sidebar"):
            self.frame.pack_forget()
            self.sidebar.frame.pack(side="left", fill="y")
            self.sidebar.main_content.pack(side="right", fill="both", expand=True)
            self.sidebar.frame.pack_propagate(False)
        else:
            self.frame.pack_forget()
            self.start_screen.main_frame.pack(fill="both", expand=True)
        
        
class SidebarMenu:
    def __init__(self, parent, analysis_data, start_screen, initial_screen: InitialSetupScreen):
        """
        parent: Frame hoặc root để gắn sidebar vào
        on_menu_select: callback nhận tên mục menu được chọn (tùy chọn)
        """
        self.start_screen = start_screen
        self.initial_screen = initial_screen
        self.data = analysis_data
        
        self.frame = tk.Frame(parent, width=350, bg="#444")
        self.frame.pack(side="left", fill="y")
        self.frame.pack_propagate(False)  # Ngăn không cho frame tự động co giãn
        
        # Frame cho phần còn lại bên phải
        self.main_content = tk.Frame(parent, bg="white")
        self.main_content.pack(side="right", fill="both", expand=True)

        # Tiêu đề quy trình (placeholder)
        self.process_name_label = tk.Label(self.frame, text="Tên quy trình:", fg="white", bg="#444", font=("Arial", 20, "bold"))
        self.process_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="wne")

        # Nút menu
        self.analysis_btn = tk.Button(self.frame, text="Phân tích quy trình", command=lambda: self.show_tab("analysis"), font=("Arial", 15))
        self.analysis_btn.grid(row=1, column=0, padx=5, pady=5, sticky="wne")

        self.improve_btn = tk.Button(self.frame, text="Cải tiến quy trình", command=lambda: self.show_tab("improvement"), font=("Arial", 15))
        self.improve_btn.grid(row=2, column=0, padx=5, pady=5, sticky="wne")
        
        tk.Button(self.frame, text="Thoát", font=("Arial", 15), command=lambda: self.back_to(type="start")).grid(row=4, column=0, padx=5, pady=5, sticky="wne")
        tk.Button(self.frame, text="Thiết lập", font=("Arial", 15), command=lambda: self.back_to(type="initial")).grid(row=3, column=0, padx=5, pady=5, sticky="wne")
        
        show_processing_popup(self.frame, self._process, message="Đang tạo báo cáo, vui lòng chờ.\n Có thể mất một vài phút...", on_done=self._next)
        
    def _process(self):
        try:  
            analysis_data = AnalysisData(self.data,
                                            self.initial_screen.case_id_cb.get(),
                                            self.initial_screen.activity_cb.get(),
                                            self.initial_screen.timestamp_cb.get(),
                                            self.initial_screen.recorded_cb.get(),
                                            self.initial_screen.time_unit_cb.get())
            improving_data = ImprovingData(analysis_data)
            return analysis_data, improving_data
        except Exception as e:
            messagebox.showerror("Lỗi", f"{e}")
        
    def _next(self, result):
        self.analysis_data, self.improving_data = result   
        self.screens = {
            "analysis": analysis_tab.AnalysisTab(self.main_content, self.analysis_data),
            "improvement": improvement_tab.ImprovementTab(self.main_content, self.improving_data, initial_data=self.initial_screen)
        }
        
        self.tab_name = "analysis"
        self.show_tab(self.tab_name)
        
    def show_tab(self, tab_name):
        """Hiển thị tab phân tích hoặc cải tiến quy trình"""
        for widget in self.main_content.winfo_children():
            widget.pack_forget()
        
        self.tab_name = tab_name    
        self.screens[tab_name].frame.pack(fill="both", expand=True)
    
    def back_to(self, type: str):
        if type == "initial":
            self.frame.pack_forget()
            self.main_content.pack_forget()
            self.initial_screen.frame.pack(fill="both", expand=True)
        else:
            self.frame.destroy()
            self.main_content.destroy()
            self.start_screen.main_frame.pack(fill="both", expand=True)
            
        
