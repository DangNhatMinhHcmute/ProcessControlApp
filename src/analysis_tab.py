import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from plot_and_dataframe import AnalysisData, draw_model
from other_frames import create_scrollable_frame, create_table_frame, show_processing_popup

class AnalysisTab:
    def __init__(self, root, data: AnalysisData):
        self.root = root
        self.data = data

        # -------- Phần chính --------      
        self.frame, main_container, main_canvas = create_scrollable_frame(self.root)
        self.frame.pack(fill="both", expand=True)
        # main_canvas.bind("<Motion>", self.scroll_by_mouse_wheel)  # Thêm sự kiện cuộn chuột
        
        main_container.grid_rowconfigure(0, weight=0)  # Hàng đầu tiên không co giãn
        main_container.grid_rowconfigure(1, minsize=700, weight=1)  # Cho phép hàng thứ hai co giãn
        main_container.grid_rowconfigure(2, minsize=500, weight=1)
        main_container.grid_rowconfigure(3, minsize=500, weight=1)
        main_container.grid_rowconfigure(4, minsize=500, weight=1)
        main_container.grid_rowconfigure(5, minsize=500, weight=1)
        main_container.grid_rowconfigure(6, minsize=500, weight=1)
        main_container.grid_columnconfigure(0, weight=0, minsize=600)
        main_container.grid_columnconfigure(1, weight=0, minsize=590)

        tk.Label(main_container, text="PHÂN TÍCH QUY TRÌNH", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # ------ Mô hình ------
        left_frame = tk.Frame(main_container)
        left_frame.grid(row=1, column=0, sticky="nsew")
        left_frame.pack_propagate(False)

        # Tiêu đề
        model_title = tk.Frame(left_frame, bg="#ccc")
        model_title.pack(fill="x", side='top')
        tk.Label(model_title, text="Mô hình quy trình", bg="#ccc", font=("Arial", 10, "bold")).pack(side="left", padx=5)

        self.dropdown_btn = ttk.Button(model_title, text="▼", command=self.show_model_options)
        self.dropdown_btn.pack(side="right", padx=2)

        # Scrollable canvas cho biểu đồ mô hình
        canvas_container, self.model_canvas_inner, model_canvas = create_scrollable_frame(left_frame)
        canvas_container.pack(fill="both", expand=True)

        # -------- Thống kê bên phải --------
        right_frame = tk.Frame(main_container)
        right_frame.grid(row=1, column=1, sticky="nsew")
        right_frame.pack_propagate(False)
        
        stat_frame = tk.Frame(right_frame, height=400, bg="white", relief="solid")
        stat_frame.pack(fill="x", expand=True, padx=5, pady=5, side='top')
        
        headers = {"Số lượng trường hợp": self.data.case_count, 
                   "Số lượng hoạt động": self.data.activity_count, 
                   "Số lượng biến thể": self.data.variant_count,
                   f"Trung bình\nthời gian thực hiện\n({self.data.time_unit})": round(self.data.mean_throughput_time, 2),
                   f"Trung vị\nthời gian thực hiện\n({self.data.time_unit})": round(self.data.median_throughput_time, 2)}
        self.stat_labels = []
        
       
        for i, (metric, value) in enumerate(headers.items()):
            row_frame = tk.Frame(stat_frame, bd=1)
            row_frame.grid(row= i // 3, column= i % 3, padx=5, pady=5, sticky="nwes")
            tk.Label(row_frame, text=metric, bg="#eee", font=("Arial", 10, "bold")).pack(side='top', fill='x')
            value = tk.Label(row_frame, text=str(value), font=('Arial', 20))  # <-- cập nhật dữ liệu tại đây
            value.pack(fill='both')
            self.stat_labels.append(value)
            
        # Thiết lập bộ lọc theo tần suất luồng tối thiểu cho toàn bộ phân tích 
        filter_frame = tk.Frame(stat_frame, bg='white')
        filter_frame.grid(row=0, column=3, rowspan=2, padx=5, pady=5, sticky="nsew")  # Tạo khoảng trống cho nút lọc
        tk.Label(filter_frame, text="Tần suất biến thể\ntối thiểu", bg="#ccc", font=("Arial", 10, "bold")).pack(fill="x")
        self.freq_analysis_entry = tk.Entry(filter_frame)
        self.freq_analysis_entry.insert(0, '0')  # Đặt giá trị mặc định là 0
        self.freq_analysis_entry.pack(padx=5, pady=5)
        ttk.Button(filter_frame, text="Lọc", command=lambda: show_processing_popup(self.frame, lambda: self.update_analysis(min_freq=int(self.freq_analysis_entry.get())), "Đang tạo báo cáo, vui lòng chờ.\nCó thể mất một vài phút...")).pack(pady=5)
        
        # ------ Phân phối thời gian thực hiện ------
        throughput_frame = tk.Frame(right_frame, relief="solid")
        throughput_frame.pack(fill="both", expand=True, padx=5, pady=5, side='top')  # Đặt sau phần thống kê 

        tk.Label(throughput_frame, text=f"Phân phối thời gian thực hiện ({self.data.time_unit})", bg="#ccc", font=("Arial", 10, "bold")).pack(side="top", fill="x")
        
        canvas_container_freq, self.throughput_chart_inner, _ = create_scrollable_frame(throughput_frame)
        canvas_container_freq.pack(fill="both", expand=True, side='top')
        # Tạo biểu đồ Phân phối thời gian thực hiện
        throughput_dist = self.data.throughput_time_distribution()
        self.draw_chart(throughput_dist, self.throughput_chart_inner, height_size=400, width_size=600)
        
        # ------ Tần suất biến thể ------
        # Tần suất biến thể
        self.variant_freq_container = tk.Frame(main_container)
        self.variant_freq_container.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        tk.Label(self.variant_freq_container, text="Tần suất các biến thể", bg="#ccc", font=("Arial", 10, "bold")).pack(fill="x", padx=5, pady=5)
        
        variant_freq_df = self.data.variant_frequency()
        self.variant_freq_inner = create_table_frame(self.variant_freq_container, variant_freq_df)
        self.variant_freq_inner.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tan suất theo các yếu tố
        self.freq_container = tk.Frame(main_container)
        self.freq_container.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.freq_container.pack_propagate(False)# Ngăn không cho frame tự động co giãn
        # Thiết lập cấu hình cho các hàng và cột
        self.freq_container.grid_rowconfigure(0, weight=0)  # Hàng đầu tiên không co giãn
        self.freq_container.grid_rowconfigure(1, weight=1, minsize=500) # Cho phép hàng thứ hai co giãn
        self.freq_container.grid_columnconfigure(0, weight=1, minsize=650)  # Cho phép cột đầu tiên co giãn
        
        freq_header = tk.Frame(self.freq_container, bg="#ccc")
        freq_header.grid(row=0, column=0, columnspan=2, sticky="ew")  # Dòng tiêu đề
        self.freq_options_but = ttk.Button(freq_header, text="▼", command=lambda: self.show_options(type='freq'))
        self.freq_options_but.pack(side="right", padx=2)
        tk.Label(freq_header, text="Tần suất theo các yếu tố", bg="#ccc", font=("Arial", 10, "bold")).pack(padx=5,fill="x")
        self.freq_popup_initial_setup = {'by': self.data.activity, 'top': '10', 'sort_by': 'lớn nhất'}
        
        freq_fig, freq_df = self.data.frequency_by(column=self.data.activity)
        # Tạo canvas và frame cho biểu đồ tần suất theo các yếu tố
        freq_frame, self.freq_inner, _ = create_scrollable_frame(self.freq_container)
        freq_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.draw_chart(freq_fig, self.freq_inner, width_size=800)
        # Tạo DataFrame cho tần suất theo các yếu tố
        self.freq_df_inner = create_table_frame(self.freq_container, freq_df)
        self.freq_df_inner.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # ------ Bảng thống kê lần thực hiện công việc ------
        self.work_count_container = tk.Frame(main_container)
        self.work_count_container.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.work_count_container.pack_propagate(False)  # Ngăn không cho frame tự động co giãn
        
        tk.Label(self.work_count_container, text="Bảng thống kê lần thực hiện công việc", bg="#ccc", font=("Arial", 10, "bold")).pack(fill="x", padx=5, pady=5)
        
        self.current_model_type = "Petri Net"  # Loại mô hình mặc định

        self.update_model(type=self.current_model_type, min_freq= self.data.freq_model)  # Vẽ Petri Net mặc định
        
        
        # ------ Thời gian chu kỳ ------
        self.cycle_time_container = tk.Frame(main_container)
        self.cycle_time_container.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.cycle_time_container.pack_propagate(False)
        
        self.cycle_time_container.grid_rowconfigure(0, weight=0)  # Hàng đầu tiên không co giãn
        self.cycle_time_container.grid_rowconfigure(1, weight=1, minsize=500)
        self.cycle_time_container.grid_columnconfigure(0, weight=1, minsize=650)  # Cho phép cột đầu tiên co giãn
        
        cycle_time_header = tk.Frame(self.cycle_time_container, bg="#ccc")
        cycle_time_header.grid(row=0, column=0, columnspan=2, sticky="ew")  # Dòng tiêu đề
        self.cycle_time_options_but = ttk.Button(cycle_time_header, text="▼", command=lambda: self.show_options(type='cycle'))
        self.cycle_time_options_but.pack(side="right", padx=2)
        tk.Label(cycle_time_header, text=f"Thời gian chu kỳ (Cycle Time) theo các yếu tố ({self.data.time_unit})", bg="#ccc", font=("Arial", 10, "bold")).pack(padx=5,fill="x")
        self.cycle_time_popup_initial_setup = {'by': self.data.activity, 'top': '10', 'sort_by': 'lớn nhất'}
        
        cycle_time_fig, cycle_time_df = self.data.cycle_time_by(column=self.data.activity)
        # Tạo canvas và frame cho biểu đồ tần suất theo các yếu tố
        cycle_time_frame, self.cycle_time_inner, _ = create_scrollable_frame(self.cycle_time_container)
        cycle_time_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.draw_chart(cycle_time_fig, self.cycle_time_inner, width_size=800)
        # Tạo DataFrame cho tần suất theo các yếu tố
        self.cycle_time_df_inner = create_table_frame(self.cycle_time_container, cycle_time_df)
        self.cycle_time_df_inner.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # ------ Throughput Time------
        self.throughput_time_container = tk.Frame(main_container)
        self.throughput_time_container.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.throughput_time_container.pack_propagate(False)
        
        self.throughput_time_container.grid_rowconfigure(0, weight=0)  # Hàng đầu tiên không co giãn
        self.throughput_time_container.grid_rowconfigure(1, weight=1, minsize=500)
        self.throughput_time_container.grid_columnconfigure(0, weight=1, minsize=650)  # Cho phép cột đầu tiên co giãn
        
        throughput_time_header = tk.Frame(self.throughput_time_container, bg="#ccc")
        throughput_time_header.grid(row=0, column=0, columnspan=2, sticky="ew")  # Dòng tiêu đề
        self.throughput_time_options_but = ttk.Button(throughput_time_header, text="▼", command=lambda: self.show_options(type='throughput'))
        self.throughput_time_options_but.pack(side="right", padx=2)
        tk.Label(throughput_time_header, text=f"Thời gian thông lượng (Throughput Time) theo các yếu tố ({self.data.time_unit})", bg="#ccc", font=("Arial", 10, "bold")).pack(padx=5,fill="x")
        self.throughput_time_popup_initial_setup = {'by': self.data.trace_columns[0], 'top': '10', 'sort_by': 'lớn nhất'}
        
        throughput_time_fig, throughput_time_df = self.data.throughput_time_by(column=self.data.trace_columns[0])
        # Tạo canvas và frame cho biểu đồ tần suất theo các yếu tố
        throughput_time_frame, self.throughput_time_inner, _ = create_scrollable_frame(self.throughput_time_container)
        throughput_time_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.draw_chart(throughput_time_fig, self.throughput_time_inner, width_size=800)
        # Tạo DataFrame cho tần suất theo các yếu tố
        self.throughput_time_df_inner = create_table_frame(self.throughput_time_container, throughput_time_df)
        self.throughput_time_df_inner.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
    # ====== HÀM HÀNH ĐỘNG (chèn tại đây) ======
    def draw_chart(self, fig, frame, width_size=None, height_size=None):
        """Vẽ biểu đồ từ Figure vào frame đã cho"""
        for widget in frame.winfo_children():
            widget.destroy()

        if width_size or height_size:
            new_fig_width = fig.get_figwidth()
            new_fig_height = fig.get_figheight()
            
            if width_size:
                new_fig_width = width_size / fig.dpi
            if height_size:
                new_fig_height = height_size / fig.dpi

            fig.set_size_inches(new_fig_width, new_fig_height)
        fig.tight_layout()    
            
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)
        
    def draw_model_from_img(self, img):
        """Vẽ mô hình dựa trên ảnh đã cho"""
        for widget in self.model_canvas_inner.winfo_children():
            widget.destroy()
        
        # Tạo canvas cho biểu đồ
        label = tk.Label(self.model_canvas_inner, image=img)
        label.image = img
        label.pack(fill="both", anchor="center", expand=True)
    
    def update_model(self, type: str, min_freq: int):
        """Cập nhật mô hình dựa trên tần suất tối thiểu và loại mô hình"""
        if min_freq != self.data.freq_model:
            self.data.freq_model = min_freq
            self.data.get_model(min_freq)
        if type == "Petri Net":
            img = draw_model(type=type, 
                             net=self.data.net, 
                             im=self.data.im, 
                             fm=self.data.fm)
        elif type == "BPMN":
            img = draw_model(type=type, 
                             bpmn_model=self.data.bpmn_model)
            
        self.draw_model_from_img(img)
        
        work_count_df = self.data.work_count_df()
        
        self.work_count_inner.destroy() if hasattr(self, 'work_count_inner') else None
        self.work_count_inner = create_table_frame(self.work_count_container, work_count_df)
        self.work_count_inner.pack(fill="both", expand=True, padx=5, pady=5)
        
    def update_statistics(self, case_count, activity_count, variant_count, mean_throughput_time, median_throughput_time):
        self.stat_labels[0].config(text=str(case_count))
        self.stat_labels[1].config(text=str(activity_count))
        self.stat_labels[2].config(text=f"{variant_count}")
        self.stat_labels[3].config(text=f"{mean_throughput_time:.2f}")
        self.stat_labels[4].config(text=f"{median_throughput_time:.2f}")
    
    def show_model_options(self):
        # Nếu đã mở popup rồi thì đóng lại
        if hasattr(self, "model_popup") and self.model_popup.winfo_exists():
            self.model_popup.destroy()
            return

        # Tạo cửa sổ phụ nhỏ
        self.model_popup = tk.Toplevel(self.root)
        self.model_popup.title("Tùy chọn mô hình")
        self.model_popup.geometry("200x120")
        self.model_popup.transient(self.root)
        self.model_popup.grab_set()

        # Lấy vị trí của nút ▼
        button_width = self.dropdown_btn.winfo_width()
        x = self.dropdown_btn.winfo_rootx()
        y = self.dropdown_btn.winfo_rooty() + self.dropdown_btn.winfo_height()
        self.model_popup.geometry(f"+{x-200+button_width}+{y}")

        # --- Dạng biểu đồ ---
        tk.Label(self.model_popup, text="Dạng biểu đồ").pack(pady=(5, 0))
        self.model_type = ttk.Combobox(self.model_popup, values=["Petri Net", "BPMN"])
        self.model_type.set(self.current_model_type)  # Đặt giá trị mặc định
        self.model_type.pack()

        # --- Tần suất tối thiểu ---
        tk.Label(self.model_popup, text="Tần suất biến thể tối thiểu").pack(pady=(5, 0))
        self.min_freq_entry = tk.Entry(self.model_popup)
        self.min_freq_entry.insert(0, str(self.data.freq_model))  # Sử dụng tần suất mặc định từ dữ liệu
        self.min_freq_entry.pack()

        # --- Áp dụng nút ---
        tk.Button(self.model_popup, text="Áp dụng", command=lambda: show_processing_popup(self.frame, self.apply_model_options, "Đang tạo báo cáo, vui lòng chờ.\nCó thể mất một vài phút...")).pack(pady=5)
        
    def show_options(self, type: str):
        # Nếu đã mở popup rồi thì đóng lại
        if hasattr(self, "model_popup") and self.model_popup.winfo_exists():
            self.model_popup.destroy()
            return
        if type == 'cycle':
            title = "Tùy chọn thời gian chu kỳ"
            initial_setup = self.cycle_time_popup_initial_setup
            first_label = "Thời gian chu kỳ theo"
            button = self.cycle_time_options_but
            values = self.data.data.columns.tolist()

            for col in values:
                if col in[self.data.case_id, self.data.timestamp, 'start_time', 'end_time', 'cycle_time']:
                    values.remove(col)
                
        elif type == 'throughput':
            title = "Tùy chọn thời gian thông lượng"
            initial_setup = self.throughput_time_popup_initial_setup
            first_label = "Thời gian thông lượng theo"
            button = self.throughput_time_options_but
            values = self.data.trace_columns

            for col in values:
                if col in[self.data.case_id, self.data.timestamp, 'start_time', 'end_time', 'cycle_time']:
                    values.remove(col)
        elif type == 'freq':
            title = "Tùy chọn tần suất"
            initial_setup = self.freq_popup_initial_setup
            first_label = "Tần suất theo"
            button = self.freq_options_but
            values = self.data.data.columns.tolist()
            for col in values:
                if col in [self.data.case_id, self.data.timestamp, 'start_time', 'end_time', 'cycle_time']:
                    values.remove(col)
                    
        # Tạo cửa sổ phụ nhỏ
        self.model_popup = tk.Toplevel(self.root)
        self.model_popup.title(title)
        self.model_popup.geometry("200x200")
        self.model_popup.transient(self.root)
        self.model_popup.grab_set()

        # Lấy vị trí của nút ▼
        button_width = button.winfo_width()
        x = button.winfo_rootx()
        y = button.winfo_rooty() + button.winfo_height()
        self.model_popup.geometry(f"+{x-200+button_width}+{y}")
        
        # --- Tần suất theo ---
        tk.Label(self.model_popup, text=first_label).pack(pady=(5, 0))
        self.freq_by = ttk.Combobox(self.model_popup, values= values)
        self.freq_by.set(initial_setup['by'])  # Đặt giá trị mặc định
        self.freq_by.pack()
        
        # --- Top ---
        tk.Label(self.model_popup, text="Top").pack(pady=(5, 0))
        self.top_entry = tk.Entry(self.model_popup)
        self.top_entry.insert(0, initial_setup['top'])  # Đặt giá trị mặc định là 10
        self.top_entry.pack()
        
        # --- Xếp theo---
        tk.Label(self.model_popup, text="Xếp theo").pack(pady=(5, 0))
        self.sort_by = ttk.Combobox(self.model_popup, values= ['lớn nhất', 'nhỏ nhất'])
        self.sort_by.set(initial_setup['sort_by'])  # Đặt giá trị mặc định là lớn nhất
        self.sort_by.pack()
        
        # --- Áp dụng nút ---
        tk.Button(self.model_popup, text="Áp dụng", command= lambda: self.apply_options(type=type)).pack(pady=5)

    def apply_model_options(self):
        model_type = self.model_type.get()
        min_freq = self.min_freq_entry.get()

        self.update_model(model_type, int(min_freq))
        self.current_model_type = model_type # Cập nhật lại giá trị trong dropdown

        self.model_popup.destroy()
        
    def apply_options(self, type: str):
        by = self.freq_by.get() if hasattr(self, 'model_popup') and self.model_popup.winfo_exists() else ""  # Nếu không có giá trị thì mặc định là rỗng
        top = self.top_entry.get() if hasattr(self, 'model_popup') and self.model_popup.winfo_exists() else ""
        sort_by = self.sort_by.get() if hasattr(self, 'model_popup') and self.model_popup.winfo_exists() else ""  

        
        if type == 'freq':
            if by == "":
                by = self.freq_popup_initial_setup['by']
            if top == "":
                top = self.freq_popup_initial_setup['top']
            if sort_by == "":
                sort_by = self.freq_popup_initial_setup['sort_by']
            freq_chart, freq_df = self.data.frequency_by(column=by, top=int(top), biggest_or_smallest= 'biggest' if sort_by == 'lớn nhất' else 'smallest')
            self.draw_chart(freq_chart, self.freq_inner)
            
            self.freq_df_inner.destroy() if hasattr(self, 'freq_df_inner') else None  # Xóa DataFrame cũ nếu có
            self.freq_df_inner = create_table_frame(self.freq_container, freq_df)
            self.freq_df_inner.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
            
            self.freq_popup_initial_setup = {'by': by, 'top': top, 'sort_by': sort_by}
            
        elif type == 'cycle':
            if by == "":
                by = self.cycle_time_popup_initial_setup['by']
            if top == "":
                top = self.cycle_time_popup_initial_setup['top']
            if sort_by == "":
                sort_by = self.cycle_time_popup_initial_setup['sort_by']
            cycle_time_chart, cycle_time_df = self.data.cycle_time_by(column=by, top=int(top), biggest_or_smallest= 'biggest' if sort_by == 'lớn nhất' else 'smallest')
            self.draw_chart(cycle_time_chart, self.cycle_time_inner)
            
            self.cycle_time_df_inner.destroy() if hasattr(self, 'cycle_time_df_inner') else None  # Xóa DataFrame cũ nếu có
            self.cycle_time_df_inner = create_table_frame(self.cycle_time_container, cycle_time_df)
            self.cycle_time_df_inner.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
            
            self.cycle_time_popup_initial_setup = {'by': by, 'top': top, 'sort_by': sort_by}
            
        elif type == 'throughput':
            if by == "":
                by = self.throughput_time_popup_initial_setup['by']
            if top == "":
                top = self.throughput_time_popup_initial_setup['top']
            if sort_by == "":
                sort_by = self.throughput_time_popup_initial_setup['sort_by']
            throughput_time_chart, throughput_time_df = self.data.throughput_time_by(column=by, top=int(top), biggest_or_smallest= 'biggest' if sort_by == 'lớn nhất' else 'smallest')
            self.draw_chart(throughput_time_chart, self.throughput_time_inner)
            
            self.throughput_time_df_inner.destroy() if hasattr(self, 'throughput_time_df_inner') else None  # Xóa DataFrame cũ nếu có
            self.throughput_time_df_inner = create_table_frame(self.throughput_time_container, throughput_time_df)
            self.throughput_time_df_inner.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
            
            self.throughput_time_popup_initial_setup = {'by': by, 'top': top, 'sort_by': sort_by}
            
        self.model_popup.destroy() if hasattr(self, 'model_popup') and self.model_popup.winfo_exists() else None  # Đóng popup nếu có
            
    def update_analysis(self, min_freq: int):
        self.data.update_data(min_freq= min_freq)
        self.update_model(type=self.current_model_type, min_freq=min_freq)
        self.update_statistics(
            case_count=self.data.case_count,
            activity_count=self.data.activity_count,
            variant_count=self.data.variant_count,
            mean_throughput_time=self.data.mean_throughput_time,
            median_throughput_time=self.data.median_throughput_time
        )
        # Cập nhật biểu đồ phân phối thời gian thực hiện
        throughput_dist = self.data.throughput_time_distribution()
        self.draw_chart(throughput_dist, self.throughput_chart_inner, height_size=400, width_size=600)
        
        variant_freq_df = self.data.variant_frequency()
        
        self.variant_freq_inner.destroy() if hasattr(self, 'variant_freq_inner') else None  # Xóa DataFrame cũ nếu có
        self.variant_freq_inner = create_table_frame(self.variant_freq_container, variant_freq_df)
        self.variant_freq_inner.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.apply_options(type='freq')
        self.apply_options(type='cycle')
        self.apply_options(type='throughput')
        
    def scroll_by_mouse_wheel(self, event):
        event.widget.bind_all("<MouseWheel>", lambda e: event.widget.yview_scroll(-1 * int(e.delta / 120), "units"))
        event.widget.bind_all("<Shift-MouseWheel>", lambda e: event.widget.xview_scroll(-1 * int(e.delta / 120), "units"))

