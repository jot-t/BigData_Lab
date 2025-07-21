Dự đoán Khách hàng Rời bỏ Dịch vụ (Customer Churn Prediction)
Mô phỏng hệ thống thu thập và xử lý dữ liệu theo thời gian thực để huấn luyện mô hình học máy. Hệ thống có khả năng dự đoán liệu một khách hàng có rời bỏ dịch vụ (churn) hay không dựa trên thông tin sử dụng của họ.

Dự án này được xây dựng theo mô hình Producer-Consumer, trong đó một server chịu trách nhiệm gửi dữ liệu liên tục và một server khác nhận, xử lý và huấn luyện mô hình. Cụ thể:
- producer.py: Giả lập một nguồn dữ liệu, liên tục đọc thông tin khách hàng từ file CSV và gửi đến Consumer qua API.
- consumer.py: Một server web xây dựng bằng Flask, có khả năng nhận dữ liệu, lưu vào bộ đệm (buffer).
- Tự động Huấn luyện: Khi bộ đệm đạt đến một ngưỡng dữ liệu nhất định (ví dụ: 50 mẫu), Consumer sẽ tự động tiền xử lý dữ liệu và huấn luyện một mô hình học máy (Random Forest).
- Dự đoán Real-time: Sau khi đã có mô hình, Consumer có thể nhận dữ liệu của khách hàng mới và trả về dự đoán về khả năng rời bỏ dịch vụ theo thời gian thực.

Dataset: https://www.kaggle.com/datasets/blastchar/telco-customer-churn 

Thư viện chính:
- Flask (để xây dựng server API)
- Pandas (để đọc và xử lý dữ liệu)
- Scikit-learn (để xây dựng và huấn luyện mô hình học máy)
- Requests (để gửi request từ producer)

Cấu trúc Thư mục
.
├── data/
│   └── customer_churn.csv    # Bộ dữ liệu đầu vào
├── producer.py               # Script gửi dữ liệu
├── consumer.py               # Script nhận dữ liệu và huấn luyện
├── notebook.ipynb            # Notebook để kiểm thử API
└── requirements.txt          # Các thư viện cần thiết

Cài đặt 
- Clone repository này về máy (hoặc tải về dưới dạng zip).
- Tải bộ dữ liệu "Telco Customer Churn" từ Kaggle và lưu vào thư mục data/ với tên customer_churn.csv.
- Tạo môi trường ảo để quản lý các thư viện một cách độc lập. Mở terminal trong thư mục dự án và chạy: py -m venv venv
- Kích hoạt môi trường ảo:
    + Trên Windows (PowerShell): .\venv\Scripts\Activate.ps1
    + Trên macOS/Linux: source venv/bin/activate
- Cài đặt các thư viện cần thiết từ file requirements.txt: pip install -r requirements.txt

Hướng dẫn sử dụng 
- Mở hai cửa sổ terminal riêng biệt.
- Mở Terminal thứ nhất và khởi động Consumer Server (Đảm bảo môi trường ảo đã được kích hoạt): python consumer.py
Server sẽ khởi động và lắng nghe các yêu cầu tại địa chỉ http://1227.0.0.1:5000.
- Mở Terminal thứ hai và khởi động Producer để bắt đầu gửi dữ liệu (Đảm bảo môi trường ảo đã được kích hoạt): python producer.py

Quan sát:
- Theo dõi log trên cả hai cửa sổ terminal. Ban đầu, Consumer sẽ chỉ nhận và lưu dữ liệu.
- Sau khi nhận đủ 50 mẫu, nó sẽ tự động bắt đầu quá trình huấn luyện mô hình.
- Khi huấn luyện xong, Producer sẽ bắt đầu nhận được kết quả dự đoán (prediction, confidence) cho các dữ liệu mới mà nó gửi đi.

Kiểm thử bằng Notebook:
- Mở và chạy các ô code trong file notebook.ipynb để gửi một yêu cầu đơn lẻ đến Consumer và xem kết quả dự đoán trả về.