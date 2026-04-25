HƯỚNG DẪN CHẠY ỨNG DỤNG

1. Mục đích
Thư mục này chứa source code và các file hỗ trợ để chạy Ứng dụng Kiểm soát Quy trình.

2. Thành phần chính
- main.py: file khởi chạy ứng dụng.
- analysis_tab.py: xử lý tab Phân tích quy trình.
- improvement_tab.py: xử lý tab Cải tiến quy trình.
- build_petri_net.py: hỗ trợ tạo và xử lý mô hình Petri Net.
- main_screens.py: giao diện chính của ứng dụng.
- other_frames.py: các khung giao diện phụ.
- plot_and_dataframe.py: xử lý biểu đồ và bảng dữ liệu.
- install_required_libraries.bat: file hỗ trợ cài thư viện.
- run_app.bat: file hỗ trợ chạy ứng dụng.
- required_libraries.txt: danh sách thư viện cần thiết.
- app_data/: dữ liệu và mô hình mẫu đi kèm.

3. Môi trường cần có
- Python đã được cài đặt.
- Graphviz đã được cài đặt và kiểm tra được bằng lệnh `dot -V`.

4. Cách chạy được khuyến nghị
Mở CMD tại thư mục này và chạy:

py main.py

5. Ghi chú
Có thể sử dụng `install_required_libraries.bat` và `run_app.bat` như các file hỗ trợ. Tuy nhiên, trong môi trường kiểm thử, cách chạy ổn định nhất là mở CMD và chạy trực tiếp `py main.py`.
