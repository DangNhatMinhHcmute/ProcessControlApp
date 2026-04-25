import tkinter as tk
from tkinter import ttk
import pandas as pd
import threading

def create_scrollable_frame(parent):
    # Khung chính chứa canvas và scrollbar
    outer = ttk.Frame(parent)

    canvas = tk.Canvas(outer)
    v_scroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    h_scroll = ttk.Scrollbar(outer, orient="horizontal", command=canvas.xview)

    canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    v_scroll.grid(row=0, column=1, sticky="ns")
    h_scroll.grid(row=1, column=0, sticky="ew")

    outer.grid_rowconfigure(0, weight=1)
    outer.grid_columnconfigure(0, weight=1)

    # Frame bên trong canvas để chứa nội dung
    inner = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=inner, anchor="nw")

    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    return outer, inner, canvas  # outer là frame chứa (bạn pack nó), inner là nơi bạn gắn widget con

def create_table_frame(parent, df: pd.DataFrame) -> tk.Frame:
    """
    Tạo một Frame chứa bảng dữ liệu từ DataFrame với thanh cuộn ngang và dọc.
    
    Args:
        parent: Frame cha nơi bạn sẽ đặt bảng vào.
        df (pd.DataFrame): Bảng dữ liệu đầu vào.

    Returns:
        tk.Frame: Frame chứa Treeview có scrollbar.
    """
    # Tạo frame chứa bảng
    outer_frame = tk.Frame(parent)

    # Scrollbars
    vsb = ttk.Scrollbar(outer_frame, orient="vertical")
    hsb = ttk.Scrollbar(outer_frame, orient="horizontal")

    # Tạo Treeview
    table = ttk.Treeview(
        outer_frame,
        columns=list(df.columns),
        show="headings",
        yscrollcommand=vsb.set,
        xscrollcommand=hsb.set
    )

    vsb.config(command=table.yview)
    hsb.config(command=table.xview)

    # Đặt vị trí
    table.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    # Cho phép giãn đều khi phóng to
    outer_frame.grid_rowconfigure(0, weight=1)
    outer_frame.grid_columnconfigure(0, weight=1)

    # Định nghĩa các cột
    for col in df.columns:
        table.heading(col, text=col)
        table.column(col, width=150, anchor="w")

    # Thêm dữ liệu (giới hạn nếu cần)
    for _, row in df.iterrows():
        table.insert("", "end", values=list(row))

    return outer_frame

def show_processing_popup(master, task_func, message: str, on_done=None):
    # Tạo cửa sổ popup
    popup = tk.Toplevel(master)
    popup.title("Đang xử lý...")
    
    width = 250
    height = 80
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    popup.geometry(f"{width}x{height}+{x}+{y}")
    popup.resizable(False, False)
    popup.transient(master)
    popup.grab_set()

    tk.Label(popup, text=message).pack(pady=10)
    ttk.Progressbar(popup, mode="indeterminate").pack(fill="x", padx=20)
    
    # Hàm bao ngoài task, sẽ tự hủy popup khi xong
    def task_wrapper():
        result = task_func()             # Chạy tác vụ thật
        popup.after(0, popup.destroy)  # Quay về main thread để hủy popup
        
        if on_done:  # nếu có hàm hậu xử lý
            popup.after(0, on_done(result))  # chạy trong GUI thread

    # Chạy tác vụ trong thread để không làm đơ GUI
    threading.Thread(target=task_wrapper, daemon=True).start()