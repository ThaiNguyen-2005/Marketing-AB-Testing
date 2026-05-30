# 📊 Marketing A/B Testing & Production Analytics Dashboard

> **Hệ thống đánh giá hiệu suất chiến dịch quảng cáo, kiểm định giả thuyết thống kê tự động và ứng dụng mô hình máy học học máy (ML App).**  
> Dự án được phát triển trong khuôn khổ môn học **Statistical Learning** (Học thống kê).

---

## 📌 Tổng quan dự án

Dự án này tập trung vào việc phân tích và đánh giá kết quả một chiến dịch thử nghiệm A/B Testing trong Marketing để xác định xem cơ chế **Bidding tự động (Test)** có thực sự mang lại hiệu quả vượt trội hơn so với **Bidding truyền thống (Control)** hay không. 

Hệ thống bao gồm hai giao diện chính:
1. **Streamlit Production Dashboard (`app.py`)**: Ứng dụng phân tích dữ liệu chuyên sâu với các mô hình kiểm định thống kê tiên tiến (Welch's t-test, Bootstrap, OLS Regression, Power Analysis) và ứng dụng dự báo bằng Machine Learning.
2. **Static Web Dashboard (`dashboard/index.html`)**: Trang web tĩnh (HTML/CSS/JS) hiện đại, trực quan, phù hợp để trình bày báo cáo nhanh (Executive-level presentation).

---

## ⚡ Các tính năng chính (Key Features)

### 1. 🏠 Tổng quan KPI Cấp cao (Executive KPIs)
* So sánh tổng quan các chỉ số cốt lõi: Tổng đơn hàng (Total Purchases), Tỷ lệ chuyển đổi (Conversion Rate), Chi phí trung bình ngày (Average Spend), và Chi phí trên mỗi đơn hàng (CPA).
* Xác định tự động chiến dịch chiến thắng dựa trên mức tối ưu ROI/CPA.
* Thống kê chênh lệch phần trăm trung bình ngày.

### 2. 📈 Phân tích Chuỗi thời gian (Time-Series Analytics)
* Đồ thị trực quan biến động hàng ngày của chi tiêu, lượt click, số hiển thị và lượt mua.
* Biểu đồ hộp (Boxplot) thể hiện phân phối tần suất của từng chỉ số.
* Biểu đồ tương quan phân tán (Scatter Plot) kèm đường xu hướng OLS.
* Đồ thị tích lũy lũy kế (Cumulative Charts) giúp theo dõi xu hướng chênh lệch dài hạn.

### 3. 🎯 Phễu chuyển đổi (Conversion Funnel)
* Trực quan hóa phễu chuyển đổi qua 6 giai đoạn: `Impressions` → `Clicks` → `Searches` → `View Content` → `Add to Cart` → `Purchase`.
* Bảng thống kê chi tiết tỷ lệ chuyển đổi từng bước (Step-by-Step Conversion) và phân tích các điểm đứt gãy trong luồng trải nghiệm khách hàng.

### 4. 🧮 Kiểm định Welch's t-test & Giả định Thống kê
* Thực hiện kiểm định **Welch's t-test** (không giả định phương sai đồng nhất) kèm tính toán trị số t, p-value, khoảng tin cậy 95% và kích thước hiệu ứng **Cohen's d**.
* Kiểm tra giả định phân phối chuẩn bằng thuật toán **Shapiro-Wilk**.
* Cung cấp kiểm định phi tham số **Mann-Whitney U test** thay thế trong trường hợp dữ liệu lệch chuẩn nghiêm trọng.
* Đồ thị so sánh trị trung bình kèm sai số chuẩn 95% CI.

### 5. 🔄 Trình mô phỏng Tái mẫu Bootstrap (Bootstrap Resampling Simulator)
* Vectorized Bootstrap tái mẫu 1,000 lần trực tiếp trên trình duyệt để đánh giá khoảng tin cậy của hiệu số trung bình.
* Kiểm chứng sự hội tụ của Sai số chuẩn thực nghiệm (Bootstrap SE) so với lý thuyết (Welch SE).
* Đồ thị phân phối tần suất (Histogram) của phân phối Bootstrap mẫu.

### 6. 📊 Phân tích Hồi quy OLS & Chẩn đoán Đa cộng tuyến
* Hồi quy đơn biến và hồi quy đa biến OLS để dự đoán lượng đơn hàng.
* Tính toán **Hệ số phóng đại phương sai (VIF)** để chẩn đoán hiện tượng đa cộng tuyến (Multicollinearity).
* Chẩn đoán giả định OLS: Kiểm định phương sai thay đổi (Breusch-Pagan), tự tương quan (Durbin-Watson), biểu đồ Residuals vs Fitted và biểu đồ chuẩn Q-Q Plot.

### 7. 🤖 Mô hình Phân loại & ML App Dự báo tương tác
* Huấn luyện mô hình **Logistic Regression** và **Random Forest Classifier** để phân loại nhóm chiến dịch dựa trên hành vi tương tác.
* Đánh giá ma trận nhầm lẫn (Confusion Matrix), đường cong ROC (AUC) và độ quan trọng của đặc trưng (Feature Importance).
* Ứng dụng dự báo lượng đơn hàng tương tác (Interactive Prediction) thời gian thực bằng Random Forest Regressor dựa trên chi tiêu và lượt thêm giỏ hàng.

### 8. ⚡ Phân tích Lực lượng thống kê (Power Analysis)
* Công cụ tính toán lực lượng thống kê (Power) và **cỡ mẫu tối thiểu cần thiết** (N per group) tương ứng với kích thước hiệu ứng thực nghiệm.

---

## 🛠️ Công nghệ sử dụng (Tech Stack)

### Python Backend & Analytics
* **Streamlit**: Xây dựng web app dashboard tương tác.
* **Pandas & NumPy**: Xử lý và tính toán dữ liệu lớn.
* **Plotly**: Vẽ biểu đồ động chất lượng cao.
* **SciPy**: Tính toán kiểm định thống kê (`stats.ttest_ind`, `shapiro`, `mannwhitneyu`).
* **Statsmodels**: Xây dựng mô hình OLS, tính VIF, Breusch-Pagan.
* **Scikit-Learn**: Huấn luyện các mô hình học máy (Logistic Regression, Random Forest).

### Frontend Web tĩnh (HTML Dashboard)
* **HTML5 / CSS3 / JavaScript (Vanilla)**: Cấu trúc và thiết kế giao diện Glassmorphism cao cấp tương thích thiết bị.
* **Chart.js**: Thư viện vẽ biểu đồ phễu, đường và phân tán trên web.
* **FontAwesome**: Hệ thống icon vector.

---

## 📂 Cấu trúc thư mục dự án

```text
├── .streamlit/               # Cấu hình giao diện Streamlit
├── dashboard/                # Giao diện dashboard web tĩnh
│   ├── index.html            # File HTML chính
│   ├── style.css             # Định dạng phong cách Glassmorphism
│   ├── app.js                # Xử lý logic và biểu đồ Chart.js
│   └── data.js               # Dữ liệu xuất từ file csv sạch
├── data/
│   ├── raw/                  # Dữ liệu thô ban đầu
│   └── processed/            # Dữ liệu sạch đã qua tiền xử lý
│       └── cleaned_marketing.csv
├── notebooks/                # Các notebook phân tích dữ liệu (Jupyter)
├── thai.jpg                  # Ảnh chân dung tác giả
├── app.py                    # File chạy ứng dụng Streamlit Dashboard chính
├── requirements.txt          # Các thư viện Python cần thiết
└── README.md                 # Tài liệu giới thiệu dự án này
```

---

## 🚀 Hướng dẫn cài đặt và khởi chạy

> [!IMPORTANT]
> Khuyến nghị sử dụng Python phiên bản từ **3.9** trở lên.

### Giao diện Streamlit Dashboard (`app.py`)

1. **Clone repository về máy:**
   ```bash
   git clone https://github.com/ThaiNguyen-2005/Marketing-AB-Testing.git
   cd Marketing-AB-Testing
   ```

2. **Tạo và kích hoạt môi trường ảo (Virtual Environment):**
   * **Windows:**
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   * **macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Cài đặt các thư viện cần thiết:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Khởi chạy ứng dụng Streamlit:**
   ```bash
   streamlit run app.py
   ```

### Giao diện Báo cáo tĩnh (`dashboard/index.html`)

Chỉ cần truy cập vào thư mục `dashboard` và click đúp chuột vào file [index.html](file:///d:/Statistical%20Learning/Marketing-AB-Testing/dashboard/index.html) để mở trực tiếp trên trình duyệt Web (Chrome, Edge, Safari...).

---

## 👤 Tác giả (Author)

* **Nguyễn Trần Bảo Thái** (Sinh năm 2005)
* **Vai trò:** Student / Data Analyst
* **GitHub:** [@ThaiNguyen-2005](https://github.com/ThaiNguyen-2005)
