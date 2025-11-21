# Project TODO App (Nhóm 10)

Đây là dự án full-stack Web Todo List được xây dựng cho môn học Lập trình Python.

## 🛠️ Công nghệ sử dụng

- **Backend:** Django, Django Rest Framework, dj-rest-auth

  - **Thư viện (Python):** Được quản lý bởi `pip`. Xem chi tiết trong `backend/requirements.txt`.
  - **AI/ML:** Scikit-learn, Joblib, Numpy - Dự đoán khả năng hoàn thành task đúng hạn

- **Frontend:** React, React Router, Axios, Tailwind CSS

  - **Thư viện (JavaScript):** Được quản lý bởi `npm` (Node.js) qua file `frontend/package.json`. Các thư viện chính bao gồm `react`, `react-dom`, **`react-router-dom`**, `axios`, và `react-scripts`.

- **Database:** Supabase (PostgreSQL).

## 📂 Cấu trúc Thư mục

```
/TODOLIST/
├── backend/     (Django REST API + AI)
├── frontend/    (React App)
└── supabase/    (Supabase local config)
```

---

## 📋 Yêu cầu Cài đặt (Prerequisites)

Trước khi bắt đầu, hãy đảm bảo bạn đã cài đặt các công cụ sau trên máy:

1.  **Python** (phiên bản 3.9+).
2.  **Node.js** (phiên bản LTS 18+).
3.  **Docker Desktop** (Tải về và **khởi động** Docker Desktop. Nó phải luôn chạy ở chế độ nền).
4.  **Supabase CLI** (Cài đặt bằng cách mở terminal và gõ: `npm install -g supabase`).

---

## ⚙️ Cấu hình Môi trường (File `.env`)

Project Backend (Django) yêu cầu một file `.env` để biết cách kết nối với database. Bạn **PHẢI** tạo file này và đặt nó trong thư mục `backend/` (ngang hàng với `manage.py`).

Bạn có 2 lựa chọn cho nội dung file này. Hãy chọn một trong hai:

### Lựa chọn 1: Dùng Supabase Local (Khuyến nghị để code)

Đây là cách nhanh nhất để phát triển, không bị trễ mạng và không bị "ngủ".

1.  Đảm bảo bạn đã chạy `npx supabase start` (ở Terminal 1).
2.  Lệnh này sẽ cung cấp cho bạn thông tin `DB URL` (thường là port `54322`) và `Secret key`.
3.  Tạo file `backend/.env` và dán nội dung mẫu sau, sau đó **điền các giá trị bạn nhận được từ terminal**:

    ```ini
    # File .env này trỏ về Supabase LOCAL (chạy trên Docker)
    # Lấy các giá trị này từ output của lệnh 'npx supabase start'

    SECRET_KEY='[DÁN_SECRET_KEY_TỪ_TERMINAL_VÀO_ĐÂY]'

    DB_NAME='postgres'
    DB_USER='postgres'
    DB_PASSWORD='postgres'
    DB_HOST='127.0.0.1'
    DB_PORT='[DÁN_PORT_DATABASE_VÀO_ĐÂY (ví dụ: 54322)]'
    ```

### Lựa chọn 2: Dùng Supabase Cloud (Dùng chung database)

Nếu nhóm của bạn muốn dùng chung 1 database trên mạng (sẽ bị chậm nếu dùng gói miễn phí).

1.  Đăng nhập vào [Supabase.com](https://supabase.com/).
2.  Tạo file `backend/.env` và điền các thông tin sau:

        ```ini
        # File .env này trỏ về Supabase CLOUD (trên mạng)

        # Lấy từ Project Settings -> API -> Project API Keys -> service_role
        SECRET_KEY='[DÁN_SERVICE_ROLE_KEY_CỦA_BẠN_VÀO_ĐÂY]'

        # --- Lấy thông tin DB từ Project Settings -> Database -> Connection String (chọn "Pooler") ---
        DB_NAME='postgres'
        DB_USER='[DÁN_USER_CỦA_POOLER_VÀO_ĐÂY (ví dụ: postgres.abc)]'
        DB_PASSWORD='[NHẬP_MẬT_KHẨU_DATABASE_CỦA_BẠN]'
        DB_HOST='[DÁN_HOST_CỦA_POOLER_VÀO_ĐÂY (ví dụ: aws-0-....)]'
        DB_PORT='5432'
        ```

    _(Lưu ý: File `.gitignore` đã được cấu hình để bỏ qua file `.env` này, đảm bảo mật khẩu của bạn an toàn và không bị đẩy lên Git)._

---

## 🚀 Hướng dẫn Khởi chạy (Local)

Để chạy dự án, bạn sẽ cần mở **3 terminal** riêng biệt.

### 1. Khởi động Database (Supabase Local)

_(Nếu bạn dùng Lựa chọn 2 (Cloud), bạn có thể bỏ qua bước này)._

1.  Mở terminal 1.
2.  Di chuyển (cd) vào thư mục `supabase` của dự án:
    ```bash
    cd supabase
    ```
3.  Khởi động Supabase:
    ```bash
    npx supabase start
    ```
4.  Đợi cho đến khi nó hiển thị `Started supabase local development setup.`.
5.  **Giữ terminal này chạy.**

### 2. Khởi động Backend (Django API)

1.  Mở terminal 2.
2.  Di chuyển (cd) vào thư mục `backend`:
    ```bash
    cd backend
    ```
3.  Tạo môi trường ảo (virtual environment):
    ```bash
    python -m venv .venv
    ```
4.  Kích hoạt môi trường ảo:
    - Trên Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
    - Trên macOS/Linux: `source .venv/bin/activate`
5.  **Cài đặt thư viện Python:** (Lệnh này đọc file `requirements.txt`)
    ```bash
    pip install -r requirements.txt
    ```
6.  (Đảm bảo bạn đã tạo file `backend/.env` như hướng dẫn ở mục "Cấu hình Môi trường").
7.  **Quan trọng:** Áp dụng cấu trúc database (tạo bảng) lên database của bạn:
    ```bash
    python manage.py migrate
    ```
8.  (Tùy chọn) Tạo một tài khoản Admin để test (chỉ cần cho Lựa chọn 1):
    ```bash
    python manage.py createsuperuser
    ```
9.  Khởi động server Django (mặc định chạy ở port 8000):
    ```bash
    python manage.py runserver
    ```
10. **Giữ terminal này chạy.**

### 3. Khởi động Frontend (React UI)

1.  Mở terminal 3.
2.  Di chuyển (cd) vào thư mục `frontend`:
    ```bash
    cd frontend
    ```
3.  **Cài đặt thư viện Node:** (Lệnh này sẽ đọc file `package.json` và cài `react`, `axios`, `react-router-dom`, v.v.)
    ```bash
    npm install
    ```
4.  Khởi động server React (mặc định chạy ở port 3000):
    ```bash
    npm start
    ```
5.  Trình duyệt của bạn sẽ tự động mở `http://localhost:3000`.

---

## 🔐 Sử dụng Ứng dụng

- **Trang chủ:** `http://localhost:3000/` (Landing Page)
- **Đăng ký:** `http://localhost:3000/register` (Tạo tài khoản mới)
- **Đăng nhập:** `http://localhost:3000/login` (Dùng tài khoản vừa tạo)
- **Dashboard:** `http://localhost:3000/home` (Trang chính của ứng dụng)

---

## 🤖 Tính năng AI

1. **AI Prediction**: Dự đoán khả năng hoàn thành task đúng hạn
2. **AI Chatbot**: Tạo task tự động từ chat (VD: "Thêm task học Python 2 tiếng chiều mai")

Chi tiết: `AI_FEATURES.md`
