import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from plot_and_dataframe import ImprovingData, draw_model
from other_frames import create_scrollable_frame, create_table_frame, show_processing_popup

class ImprovementTab:
    def __init__(self, root, data: ImprovingData, initial_data = None):
        self.root = root
        self.data = data
        self.initial_data = initial_data

        # -------- Phần chính --------      
        self.frame, self.main_container, main_canvas = create_scrollable_frame(self.root)
        self.frame.pack(fill="both", expand=True)
        # main_canvas.bind("<Motion>", self.scroll_by_mouse_wheel)  # Thêm sự kiện cuộn chuột
        
        self.main_container.grid_rowconfigure(1, minsize=600, weight=1)  # Cho phép hàng thứ hai co giãn
        self.main_container.grid_rowconfigure(2, minsize=100, weight=1)
        self.main_container.grid_rowconfigure(4, minsize=400, weight=1)
        self.main_container.grid_rowconfigure(6, minsize=400, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1, minsize=590)  # Cho phép cột đầu tiên co giãn
        self.main_container.grid_columnconfigure(1, weight=1, minsize=590)  # Cho phép cột thứ hai co giãn
        
        tk.Label(self.main_container, text="CẢI TIẾN QUY TRÌNH", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Frame cho mô hình hiện tại
        left_frame = tk.Frame(self.main_container)
        left_frame.grid(row=1, column=0, sticky="nsew")
        left_frame.pack_propagate(False)
        
        # Tiêu đề cho Frame cho mô hình hiện tại
        model_title = tk.Frame(left_frame, bg="#ccc")
        model_title.pack(fill="x", side='top')
        tk.Label(model_title, text="Mô hình quy trình hiện tại", bg="#ccc", font=("Arial", 10, "bold")).pack(side="left", padx=5)

        self.dropdown_btn = ttk.Button(model_title, text="▼", command= lambda: self.show_model_options(frame_type='current'))
        self.dropdown_btn.pack(side="right", padx=2)
        
        current_model_frame, self.current_model_inner, _ = create_scrollable_frame(left_frame)
        current_model_frame.pack(fill="both", expand=True)
        
        # Frame cho mô hình cải tiến
        right_frame = tk.Frame(self.main_container)
        right_frame.grid(row=1, column=1, sticky="nsew")
        right_frame.pack_propagate(False)
        
        model_title_improve = tk.Frame(right_frame, bg="#ccc")
        model_title_improve.pack(fill="x", side='top')
        tk.Label(model_title_improve, text="Mô hình quy trình cải tiến", bg="#ccc", font=("Arial", 10, "bold")).pack(side="left", padx=5)

        self.dropdown_btn_improve = ttk.Button(model_title_improve, text="▼", command= lambda: self.show_model_options(frame_type= 'improve'))
        self.dropdown_btn_improve.pack(side="right", padx=2)
        
        improve_model_frame, self.improve_model_inner, _ = create_scrollable_frame(right_frame)
        improve_model_frame.pack(fill="both", expand=True)
        
        # Chỉ số mô hình
        metrics_frame = tk.Frame(self.main_container)
        metrics_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        metrics_frame.pack_propagate(False)
        
        tk.Label(metrics_frame, text="Các chỉ số", font=("Arial", 12, "bold"), bg="#ccc").grid(row=0, column=0, columnspan=5, pady=5, sticky="nsew")
        
        # Tạo bảng chỉ số
        self.metrics_label = ('Độ phù hợp tổng thế', 
                         'Độ phù hợp của các log lỗi', 
                         'Số lượng biến thể của mô hình', 
                         'Số lượng biến thể khớp với mô hình', 
                         'Trung bình Throughput Time')
        self.metrics_label_list = []
        
        for i, metric in enumerate(self.metrics_label):
            tk.Label(metrics_frame, text=metric, font=("Arial", 10, 'bold'), bg="#ccc").grid(row=1, column=i, sticky="nsew", padx=5)
            value = tk.Label(metrics_frame, text="N/A", font=("Arial", 15), bg="white")
            metrics_frame.grid_columnconfigure(i, weight=1)  # Cho phép cột co giãn
            value.grid(row=2, column=i, sticky="nsew", padx=5)
            self.metrics_label_list.append(value)
        
        tk.Label(self.main_container, text= 'Các luồng không xuất hiện trong mô hình và tần suất', font=("Arial", 12, "bold"), bg="#ccc").grid(row=3, column=0, columnspan=2, pady=5, sticky="nsew")
        tk.Label(self.main_container, text= 'Cycle Time các hoạt động kèm hoạt động trước', font=("Arial", 12, "bold"), bg="#ccc").grid(row=5, column=0, columnspan=2, pady=5, sticky="nsew")
        
    def show_model_options(self, frame_type: str):
        # Nếu đã mở popup rồi thì đóng lại
        if hasattr(self, "model_popup") and self.model_popup.winfo_exists():
            self.model_popup.destroy()
            return

        # Tạo cửa sổ phụ nhỏ
        self.model_popup = tk.Toplevel(self.root)
        self.model_popup.title("Tùy chọn")
        self.model_popup.geometry("200x200")
        self.model_popup.transient(self.root)
        self.model_popup.grab_set()

        # Lấy vị trí của nút ▼
        button_width = self.dropdown_btn.winfo_width() if frame_type == 'current' else self.dropdown_btn_improve.winfo_width()
        x = self.dropdown_btn.winfo_rootx() if frame_type == 'current' else self.dropdown_btn_improve.winfo_rootx()
        y = self.dropdown_btn.winfo_rooty() + self.dropdown_btn.winfo_height() if frame_type == 'current' else self.dropdown_btn_improve.winfo_rooty() + self.dropdown_btn_improve.winfo_height()
        self.model_popup.geometry(f"+{x-200+button_width}+{y}")

        # --- Áp dụng nút ---
        tk.Button(self.model_popup, text="Tạo mô hình", command= lambda: self.open_edit_model(model_type=frame_type, model_state="new"), font=('Arial', 12)).pack(pady=5, fill='x')
        tk.Button(self.model_popup, text="Thêm mô hình từ file", command= lambda: self.open_model_file(model_type=frame_type), font=('Arial', 12)).pack(pady=5, fill='x')
        tk.Button(self.model_popup, text="Chỉnh sửa mô hình", command= lambda: self.open_edit_model(model_type=frame_type, model_state="edit"), font=('Arial', 12)).pack(pady=5, fill='x')
        tk.Button(self.model_popup, text="Xuất mô hình thành file", command= lambda: self.export_model_file(model_type=frame_type), font=('Arial', 12)).pack(pady=5, fill='x')
        
        
    def open_edit_model(self, model_type: str, model_state: str):
        self.model_popup.destroy()
        
        self.edit_box = tk.Toplevel(self.root)
        self.edit_box.title("Chỉnh sửa mô hình" if model_state == "edit" else "Tạo mô hình")
        self.edit_box.geometry("1000x500")
        self.edit_box.transient(self.root)
        self.edit_box.grab_set()
        
        # Tạo Frame chính
        main_frame = tk.Frame(self.edit_box, bg="white")
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_rowconfigure(0, weight=0, minsize=30)
        main_frame.grid_rowconfigure(1, weight=0, minsize=50)
        main_frame.grid_rowconfigure(2, weight=1, minsize=300)
        main_frame.grid_rowconfigure(3, weight=0, minsize=50)
        
        for i in range(7):
            main_frame.grid_columnconfigure(i, weight=1)
        
        tk.Label(main_frame, text= "Hoạt động", font=("Arial", 12, 'bold'), bd=1).grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nesw")
        tk.Label(main_frame, text= "Kết nối", font=("Arial", 12, 'bold'), bd=1).grid(row=0, column=3, columnspan=2, padx=5, pady=5, sticky="nesw")
        tk.Label(main_frame, text= "Điểm", font=("Arial", 12, 'bold'), bd=1).grid(row=0, column=5, columnspan=2, padx=5, pady=5, sticky="nesw")
        
        tk.Button(main_frame, text="Tạo hoạt động", font=("Arial", 12, 'bold'), command= lambda: self.transition_frame(type="create")).grid(row=1, column=0, padx=5, pady=5, sticky="esw")
        tk.Button(main_frame, text="Chỉnh sửa hoạt động", font=("Arial", 12, 'bold'), command= lambda: self.transition_frame(type="edit")).grid(row=1, column=1, padx=5, pady=5, sticky="esw")
        tk.Button(main_frame, text="Xóa hoạt động", font=("Arial", 12, 'bold'), command= lambda: self.transition_frame(type="delete")).grid(row=1, column=2, padx=5, pady=5, sticky="esw")
        tk.Button(main_frame, text="Tạo kết nối", font=("Arial", 12, 'bold'), command=lambda: self.place_and_arc_frame(run_type="create", object_type="arc")).grid(row=1, column=3, padx=5, pady=5, sticky="esw")
        tk.Button(main_frame, text="Xóa kết nối", font=("Arial", 12, 'bold'), command=lambda: self.place_and_arc_frame(run_type="delete", object_type="arc")).grid(row=1, column=4, padx=5, pady=5, sticky="esw")
        tk.Button(main_frame, text="Tạo điểm", font=("Arial", 12, 'bold'), command=lambda: self.place_and_arc_frame(run_type="create", object_type="place")).grid(row=1, column=5, padx=5, pady=5, sticky="esw")
        tk.Button(main_frame, text="Xóa điểm", font=("Arial", 12, 'bold'), command=lambda: self.place_and_arc_frame(run_type="delete", object_type="place")).grid(row=1, column=6, padx=5, pady=5, sticky="esw")
        tk.Button(main_frame, text="Lưu", font=("Arial", 12, 'bold'), command=lambda: show_processing_popup(self.frame, lambda: self.save_model_changes(model_type=model_type), "Đang cập nhật, vui lòng chờ.\nCó thể mất khoảng một phút...")).grid(row=3, column=5, padx=5, pady=5, sticky="esw")
        tk.Button(main_frame, text="Hủy", font=("Arial", 12, 'bold'), command= self.edit_box.destroy).grid(row=3, column=6, padx=5, pady=5, sticky="esw")
        
        model_frame, self.model_inner, _ = create_scrollable_frame(main_frame)
        model_frame.grid(row=2, column=0, columnspan=7, sticky="nsew")

        self.data.get_temp_model(model_type=model_type, model_state=model_state)
        if model_state == "edit":
            net, im, fm = self.data.temp_model.get_petri_net()
            temp_model_img = draw_model(type='Petri Net', net=net, im=im, fm=fm, rankdir='LR')
            self.draw_model_from_img(temp_model_img, self.model_inner)
            
    def transition_frame(self, type: str):
        self.trans_box = tk.Toplevel(self.edit_box)
        self.trans_box.geometry("450x200")
        if type == "create":
            title = 'Tạo hoạt động'
        elif type == "edit":
            title = "Chỉnh sửa hoạt động"
        else:
            title = "Xóa hoạt động"
        self.trans_box.title(title)
        self.trans_box.transient(self.root)
        self.trans_box.grab_set()
        
        # Tạo Frame chính
        main_frame = tk.Frame(self.trans_box)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        
        def get_trans_to_edit(event):
            if type == "edit":
                self.trans_name_box.set(self.trans_in_net_box.get())
            self.cycle_time_entry.insert(0, str(self.data.temp_model_cycle_time[self.trans_name_box.get()]))
        
        def disable_cycle_time():
            self.cycle_time_entry.config(state="disabled") if self.vr_trans.get() else self.cycle_time_entry.config(state="normal")
        
        tk.Label(main_frame, text="Tên hoạt động").grid(row=1, column=0, padx=5, pady=5, sticky="esw")
        self.trans_name_box = ttk.Combobox(main_frame, state="normal")
        self.trans_name_box.grid(row=1, column=1, padx=5, pady=5, sticky="esw")
        self.trans_name_box.bind('<<ComboboxSelected>>', get_trans_to_edit)
        
        if type == "create":
            act_in_log = self.data.data[self.data.activity].unique()
            act_in_net = [trans.label for trans in self.data.temp_model.net.transitions]
            trans_name = list(set(act_in_log) - set(act_in_net))
            self.vr_trans = tk.BooleanVar(value=False)
            tk.Checkbutton(main_frame, text="Hoạt động ảo", variable=self.vr_trans, command=disable_cycle_time).grid(row=1, column=2, padx=5, pady=5, sticky="esw")
        elif type == "edit":
            trans_name = [trans.label for trans in self.data.temp_model.net.transitions]
        else:
            trans_name = [trans.name for trans in self.data.temp_model.net.transitions]
            
        self.trans_name_box.config(values=trans_name)
        
        if type != "delete":
            tk.Label(main_frame, text=f"Cycle Time ước tính ({self.data.analysis_data.time_unit})").grid(row=2, column=0, padx=5, pady=5, sticky="esw")
            self.cycle_time_entry = tk.Entry(main_frame)
            self.cycle_time_entry.grid(row=2, column=1, padx=5, pady=5, sticky="esw")
        
        if type == "edit":
            tk.Label(main_frame, text="Chọn hoạt động chỉnh sửa").grid(row=0, column=0, padx=5, pady=5, sticky="esw")
            self.trans_in_net_box = ttk.Combobox(main_frame, values=trans_name, state="readonly")
            self.trans_in_net_box.grid(row=0, column=1, padx=5, pady=5, sticky="esw")
            self.trans_in_net_box.bind('<<ComboboxSelected>>', get_trans_to_edit)
            
        tk.Button(main_frame, text="Xóa" if type == "delete" else "Lưu", font=("Arial", 10, 'bold'), command=lambda: self.run_command_for_edit_boxs(run_type=type, object_type='transition')).grid(row=3, column=2, padx=5, pady=5, sticky="es")
        
    def place_and_arc_frame(self, run_type: str, object_type: str):
        self.place_and_arc_box = tk.Toplevel(self.edit_box)
        
        type = "Thêm" if run_type == "create" else "Xóa"
        object = "kết nối" if object_type == "arc" else "điểm"
        title = f"{type} {object}"
        self.place_and_arc_box.title(title)
        
        self.place_and_arc_box.geometry("250x150")
        self.place_and_arc_box.transient(self.root)
        self.place_and_arc_box.grab_set()
        
        main_frame = tk.Frame(self.place_and_arc_box)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        
        trans_name = [trans.name for trans in self.data.temp_model.net.transitions]
        place_name = [place.name for place in self.data.temp_model.net.places]
        select_list = trans_name + place_name
        
        def get_destination(event):
            start_name = self.from_and_place_box.get()
            if run_type == "create":
                if start_name in place_name:
                    self.end_box.config(values=trans_name)
                elif start_name in trans_name:
                    self.end_box.config(values=place_name)
            else:
                start = self.data.temp_model.places.get(start_name) or self.data.temp_model.transitions.get(start_name)
                destination = [dest.target.name for dest in start.out_arcs]
                self.end_box.config(values=destination)
                        
        tk.Label(main_frame, text="Từ" if object_type == "arc" else "Tên điểm").grid(row=0, column=0, padx=5, pady=5, sticky="esw")
        
        if object_type == "place" and run_type == "create":
            self.place_entry = tk.Entry(main_frame)
            self.place_entry.grid(row=0, column=1, padx=5, pady=5, sticky="esw")
            self.place_type = tk.IntVar(value=0)
            tk.Radiobutton(main_frame, text="Điểm bắt đầu", value=1, variable=self.place_type).grid(row=1, column=1, padx=5, pady=5, sticky="esw")
            tk.Radiobutton(main_frame, text="Điểm kết thúc", value=2, variable=self.place_type).grid(row=2 , column=1, padx=5, pady=5, sticky="esw")
        else:
            self.from_and_place_box = ttk.Combobox(main_frame, values=select_list if object_type != "place" else place_name, state="readonly")
            self.from_and_place_box.grid(row=0, column=1, padx=5, pady=5, sticky="esw")
        
        if object_type == "arc":
            self.from_and_place_box.bind('<<ComboboxSelected>>', get_destination)
            tk.Label(main_frame, text="Đến").grid(row=1, column=0, padx=5, pady=5, sticky="esw")
            self.end_box = ttk.Combobox(main_frame, state="readonly")
            self.end_box.grid(row=1, column=1)
        
        tk.Button(main_frame, text="Xóa" if run_type == "delete" else "Lưu", font=("Arial", 10, 'bold'), command=lambda: self.run_command_for_edit_boxs(run_type=run_type, object_type=object_type)).grid(row=3, column=1, padx=5, pady=5, sticky="es")
        
    def run_command_for_edit_boxs(self, run_type: str, object_type: str):
        if object_type == "transition":
            name = self.trans_name_box.get()
            if name in [trans.name for trans in self.data.temp_model.net.transitions] and run_type != "delete":
                messagebox.showerror("Lỗi", "Đã có hoạt động mang tên này")
                return
            if run_type == "create":
                if not self.vr_trans.get():
                    cycle_time = self.cycle_time_entry.get()
                    self.data.temp_model.add_transition(name)
                    self.data.temp_model_cycle_time[name] = float(cycle_time)
                else:
                    self.data.temp_model.add_transition(name, vitural_transition=True)
                    self.vr_trans.set(False)
            elif run_type == "edit":
                cycle_time = self.cycle_time_entry.get()
                old_name = self.trans_in_net_box.get()
                self.data.temp_model.rename_transition(old_name, name)
                self.data.temp_model_cycle_time.pop(old_name, None)
                self.data.temp_model_cycle_time[name] = float(cycle_time)
            else:
                self.data.temp_model.remove_transition(name)
                self.data.temp_model_cycle_time.pop(name, None)
        elif object_type == "arc":
            source_name = self.from_and_place_box.get()
            target_name = self.end_box.get()
            
            if run_type == "create":
                try:
                    source = self.data.temp_model.places.get(source_name) or self.data.temp_model.transitions.get(source_name)
                    target = self.data.temp_model.places.get(target_name) or self.data.temp_model.transitions.get(target_name)
                    for arc in self.data.temp_model.net.arcs:
                        if arc.source == source and arc.target == target:
                            messagebox.showerror("Lỗi", "Kết nối đang tạo đã tồn tại")
                            return                       
                    self.data.temp_model.add_arc(source_name, target_name)
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể tạo kết nối: {e}")
            else:
                try:
                    self.data.temp_model.remove_arc(source_name, target_name)
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể xoá kết nối: {e}")
        else:
            if run_type == "create":
                name = self.place_entry.get()
                if self.data.temp_model.places.get(name) is not None:
                    messagebox.showerror("Lỗi", "Đã có điểm mang tên này. Vui lòng chọn tên khác")
                    return
                self.data.temp_model.add_place(name)
                if self.place_type.get() != 0:
                    self.data.temp_model.set_initial_marking(name) if self.place_type.get() == 1 else self.data.temp_model.set_final_marking(name)
                    self.place_type.set(value=0)
            else:
                name = self.from_and_place_box.get()
                self.data.temp_model.remove_place(name)
                
        self.trans_box.destroy() if object_type == "transition" else self.place_and_arc_box.destroy()
        
        net, im, fm = self.data.temp_model.get_petri_net()
        temp_model_img = draw_model(type='Petri Net', net=net, im=im, fm=fm, rankdir='LR')
        self.draw_model_from_img(temp_model_img, self.model_inner)
            
    def draw_model_from_img(self, img, frame: tk.Frame):
        """Vẽ mô hình dựa trên ảnh đã cho"""
        for widget in frame.winfo_children():
            widget.destroy()
        
        # Tạo canvas cho biểu đồ
        label = tk.Label(frame, image=img)
        label.image = img
        label.pack(fill="both", expand=True, anchor="center")
    
    def open_model_file(self, model_type: str):
        """
        Mở tệp mô hình PNML hoặc JSON.
        """
        file_path = tk.filedialog.askopenfilename(
            title="Chọn tệp mô hình",
            filetypes=[("PNML files", "*.pnml"), ("JSON files", "*.json")]
        )
        
        if file_path:
            self.model_popup.destroy() # Đóng cửa sổ popup nếu có
            # Xử lý mở tệp mô hình
            def process():
                self.data.get_petri_net_and_metrics(file_path=file_path, model_type= model_type)
            def next(_):    
                self.update_metric()
                self.update_tables(model_type=model_type)
            show_processing_popup(self.frame, process, "Đang cập nhật, vui lòng chờ.\nCó thể mất khoảng một phút...", on_done=next)
            
    def update_tables(self, model_type: str):
        if model_type == 'current':
            net, im, fm =self.data.current_model.get_petri_net()
            move_log_count = self.data.current_move_log_counts
            arc_time_df = self.data.current_arc_time
            model_frame = self.current_model_inner
            self.current_move_log_frame = create_table_frame(self.main_container, move_log_count)
            self.current_move_log_frame.grid(row=4, column=0, sticky="nsew")
            self.current_arc_time_frame = create_table_frame(self.main_container, arc_time_df)
            self.current_arc_time_frame.grid(row=6, column=0, sticky="nsew")
        elif model_type == 'improve':
            model_frame = self.improve_model_inner
            net, im, fm =self.data.improved_model.get_petri_net()
            move_log_count = self.data.improved_move_log_counts
            arc_time_df = self.data.improved_arc_time
            self.improved_move_log_frame = create_table_frame(self.main_container, move_log_count)
            self.improved_move_log_frame.grid(row=4, column=1, sticky="nsew")
            self.improved_arc_time_frame = create_table_frame(self.main_container, arc_time_df)
            self.improved_arc_time_frame.grid(row=6, column=1, sticky="nsew")
            
        petri_image = draw_model(type='Petri Net', net=net, im=im, fm=fm)
        self.draw_model_from_img(petri_image, model_frame)
                              
    def update_metric(self):       
        current_metrics = self.data.current_metrics 
        improved_metrics = self.data.improved_metrics
        for i, metric in enumerate(self.metrics_label):
            current_value = (
                current_metrics.loc[current_metrics['Chỉ số'] == metric, 'Giá trị'].values[0]
                if current_metrics is not None and not current_metrics.empty and metric in current_metrics['Chỉ số'].values
                else '--'
            )
            improved_value = (
                improved_metrics.loc[improved_metrics['Chỉ số'] == metric, 'Giá trị'].values[0]
                if improved_metrics is not None and not improved_metrics.empty and metric in improved_metrics['Chỉ số'].values
                else '--'
            )
            value = f"{current_value}  |  {improved_value}"
            self.metrics_label_list[i].config(text=value)
        
    def export_model_file(self, model_type: str):
        """
        Xuất mô hình thành tệp PNML.
        """
        file_path = tk.filedialog.asksaveasfilename(
            title="Lưu mô hình",
            defaultextension=".pnml",
            initialfile=f"{self.initial_data.process_name_entry.get()}_{model_type}_model.pnml",
            filetypes=[("PNML files", "*.pnml")]
        )
        
        if file_path:
            self.data.export_petri_net(file_path=file_path, model_type=model_type)
            messagebox.showinfo("Thông báo", "Mô hình đã được lưu thành công")
    
    def save_model_changes(self, model_type: str):
        # Lấy net sau khi sửa
        net, im, fm = self.data.temp_model.get_petri_net()
        self.data.get_petri_net_and_metrics(model_type=model_type, net=net, im=im, fm=fm)
            
        self.update_metric()
        self.update_tables(model_type=model_type)
        
        self.data.temp_model = None
        self.data.temp_model_arc_time = None
        self.data.temp_model_cycle_time = None

        self.edit_box.destroy()
                   
    def scroll_by_mouse_wheel(self, event):
        event.widget.bind_all("<MouseWheel>", lambda e: event.widget.yview_scroll(-1 * int(e.delta / 120), "units"))
        event.widget.bind_all("<Shift-MouseWheel>", lambda e: event.widget.xview_scroll(-1 * int(e.delta / 120), "units"))
    
