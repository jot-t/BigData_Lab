# consumer.py
from flask import Flask, request, jsonify
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import threading
import atexit

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# --- Phần lưu trữ và mô hình ---
DATA_BUFFER = [] # Lưu dữ liệu nhận được
MODEL = None # Biến toàn cục để lưu mô hình đã huấn luyện
COLUMNS = [] # Lưu tên các cột
TRAINING_THRESHOLD = 50 # Huấn luyện lại mô hình sau mỗi 50 mẫu mới
IS_TRAINING = False # Cờ để tránh huấn luyện đồng thời

def train_model():
    """Hàm huấn luyện mô hình từ dữ liệu trong buffer."""
    global MODEL, DATA_BUFFER, COLUMNS, IS_TRAINING
    
    if len(DATA_BUFFER) < TRAINING_THRESHOLD:
        print(f"Chưa đủ dữ liệu để huấn luyện. Cần {TRAINING_THRESHOLD}, hiện có {len(DATA_BUFFER)}.")
        IS_TRAINING = False
        return

    print(f"\nBắt đầu huấn luyện mô hình với {len(DATA_BUFFER)} mẫu dữ liệu...")
    IS_TRAINING = True
    
    # Tạo DataFrame từ buffer
    df = pd.DataFrame(DATA_BUFFER)
    
    # --- Tiền xử lý dữ liệu ---
    # Chuyển đổi các cột object sang số
    df_processed = df.copy()
    encoders = {}
    for col in df_processed.select_dtypes(include='object').columns:
        if col != 'customerID':
            encoders[col] = LabelEncoder()
            df_processed[col] = encoders[col].fit_transform(df_processed[col])
            
    # Xử lý giá trị số bị lỗi
    df_processed['TotalCharges'] = pd.to_numeric(df_processed['TotalCharges'], errors='coerce')
    df_processed.fillna(0, inplace=True)
    
    # Xác định biến mục tiêu và biến độc lập
    X = df_processed.drop(columns=['customerID', 'Churn'])
    y = df_processed['Churn']
    
    # Lưu lại tên cột để dùng cho việc dự đoán sau này
    COLUMNS = X.columns
    
    # Huấn luyện mô hình
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Cập nhật mô hình toàn cục
    MODEL = model
    print("Huấn luyện thành công! Mô hình đã được cập nhật.\n")
    
    # Xóa buffer để chuẩn bị cho lần huấn luyện tiếp theo
    DATA_BUFFER.clear()
    IS_TRAINING = False

# --- Định nghĩa API endpoint ---
@app.route('/predict', methods=['POST'])
def handle_predict():
    global DATA_BUFFER, MODEL, IS_TRAINING
    
    # Nhận dữ liệu JSON từ request
    data = request.get_json()
    DATA_BUFFER.append(data)
    
    # Kiểm tra nếu cần huấn luyện lại
    if len(DATA_BUFFER) >= TRAINING_THRESHOLD and not IS_TRAINING:
        # Chạy huấn luyện trong một luồng riêng để không chặn request
        training_thread = threading.Thread(target=train_model)
        training_thread.start()
    
    # Nếu chưa có mô hình, trả về thông báo
    if MODEL is None:
        return jsonify({"message": f"Dữ liệu đã được nhận. Đang chờ đủ dữ liệu để huấn luyện. ({len(DATA_BUFFER)}/{TRAINING_THRESHOLD})"})
    
    # --- Nếu đã có mô hình, thực hiện dự đoán ---
    try:
        # Chuẩn bị dữ liệu đầu vào cho dự đoán
        df_predict = pd.DataFrame([data])
        
        # Tiền xử lý tương tự như lúc huấn luyện
        for col in df_predict.select_dtypes(include='object').columns:
            if col != 'customerID':
                 # Dùng LabelEncoder đã fit trước đó hoặc fit mới nếu cần
                le = LabelEncoder().fit(df_predict[col]) 
                df_predict[col] = le.transform(df_predict[col])

        df_predict['TotalCharges'] = pd.to_numeric(df_predict['TotalCharges'], errors='coerce')
        df_predict.fillna(0, inplace=True)
        
        # Sắp xếp lại cột để khớp với lúc huấn luyện
        df_predict = df_predict[COLUMNS]
        
        # Dự đoán
        prediction = MODEL.predict(df_predict)[0]
        prediction_proba = MODEL.predict_proba(df_predict)[0]
        
        churn_status = "Yes" if prediction == 1 else "No"
        confidence = prediction_proba[prediction] * 100
        
        return jsonify({
            "customerID": data.get("customerID", "N/A"),
            "prediction": churn_status,
            "confidence": f"{confidence:.2f}%"
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    # Chạy Flask server
    app.run(debug=True, host='127.0.0.1', port=5000)