# producer.py
import pandas as pd
import requests
import json
import time
import random

# Đọc dữ liệu
try:
    df = pd.read_csv('data/customer_churn.csv')
except FileNotFoundError:
    print("Lỗi: Không tìm thấy file customer_churn.csv trong thư mục data/")
    exit()

# URL của consumer API
URL = "http://127.0.0.1:5000/predict"

print("Bắt đầu gửi dữ liệu khách hàng...")
print("Nhấn Ctrl+C để dừng.")

while True:
    try:
        # Lấy ngẫu nhiên một dòng dữ liệu
        random_index = random.randint(0, len(df) - 1)
        customer_data = df.iloc[[random_index]].to_dict(orient='records')[0]
        
        # Chuyển đổi sang JSON
        payload = json.dumps(customer_data)
        
        # Gửi request POST đến consumer
        response = requests.post(URL, data=payload, headers={'Content-Type': 'application/json'})
        
        # In kết quả
        print(f"Đã gửi: {customer_data['customerID']}")
        print(f"Phản hồi từ server: {response.json()}")
        
        # Chờ một khoảng thời gian ngẫu nhiên
        time.sleep(random.randint(2, 5))
        
    except requests.exceptions.ConnectionError:
        print("Lỗi: Không thể kết nối đến consumer. Hãy đảm bảo consumer.py đang chạy.")
        time.sleep(5)
    except KeyboardInterrupt:
        print("\nĐã dừng producer.")
        break