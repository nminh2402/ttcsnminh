# PTIT ELIB - Hệ Thống Quản Lý Thư Viện Trực Tuyến

![PTIT ELIB](https://ptit.edu.vn/wp-content/uploads/2025/03/1958x745-1.png)

## Giới Thiệu

**PTIT ELIB** là hệ thống quản lý thư viện trực tuyến dành cho Học viện Công nghệ Bưu chính Viễn thông (PTIT). Hệ thống hỗ trợ sinh viên, giảng viên và cán bộ thư viện trong việc quản lý tài nguyên, mượn sách, trả sách và tìm kiếm thông tin một cách hiệu quả.

## Tính Năng

- **Quản lý sách**: Hiển thị danh sách sách, giáo trình và các tài liệu khác.
- **Tìm kiếm nâng cao**: Tìm kiếm theo từ khóa, danh mục hoặc hình ảnh bìa sách.
- **Mượn và trả sách**: Hỗ trợ mượn sách trực tuyến và cập nhật số lượng sách trong thư viện.
- **Gợi ý sách**: Đề xuất sách dựa trên lịch sử mượn của người dùng.
- **Quản lý người dùng**: Đăng ký, đăng nhập và quản lý tài khoản người dùng.
- **Giao diện thân thiện**: Thiết kế hiện đại, hỗ trợ đa ngôn ngữ (VI/EN).
- **Tin tức & Sự kiện**: Cập nhật các tin tức và sự kiện liên quan đến thư viện.
- **Tìm kiếm bằng ảnh**: Cho phép người dùng tìm kiếm sách bằng cách upload ảnh bìa.

## Công Nghệ Sử Dụng

- **Backend**: Django, Django ORM
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Cơ sở dữ liệu**: SQLite
- **OCR**: Tesseract OCR
- **Thư viện Python**: Pandas, Pillow, RapidFuzz

## Cấu Trúc Thư Mục

Dự án hiện tại được lưu trữ theo cấu trúc như sau:

```text
ttcsnminh/
├── .venv/                         # Môi trường ảo Python
├── .git/                          # Cấu hình Git
├── .gitignore                     # Các file/thư mục không đưa lên Git
├── README.md                      # File giới thiệu dự án này
└── lib-python/                    # Thư mục mã nguồn chính của Python
    ├── DOCS.md                    # Tài liệu tham khảo thêm
    ├── README.md                  # Tài liệu cũ
    └── mysite/                    # Thư mục gốc của dự án Django
        ├── manage.py              # Script thực thi các lệnh quản lý của Django
        ├── requirements.txt       # Danh sách thư viện Python cần thiết
        ├── db.sqlite3             # Database cục bộ
        ├── mysite/                # Thư mục chứa cấu hình gốc của Django (settings, urls)
        ├── myapp/                 # Ứng dụng quản lý thư viện chính (Models, Views, Templates, Static...)
        ├── media/                 # Thư mục chứa ảnh sách, ảnh người dùng upload...
        └── data/                  # Chứa dữ liệu data mẫu
```

## Hướng Dẫn Cài Đặt Và Chạy Local

1. Kích hoạt môi trường ảo:
   ```bash
   # Dành cho Windows
   .\.venv\Scripts\activate
   ```
2. Cài đặt thư viện:
   ```bash
   cd lib-python/mysite
   pip install -r requirements.txt
   ```
3. Chạy server:
   ```bash
   python manage.py runserver
   ```
4. Truy cập trang chủ tại `http://127.0.0.1:8000/`.

## Hướng Dẫn Sử Dụng
1. **Đăng ký/Đăng nhập**: Người dùng cần có tài khoản để sử dụng các tính năng mượn/trả sách.
2. **Tìm kiếm sách**: Sử dụng thanh tìm kiếm để tìm sách theo từ khóa hoặc danh mục. Hệ thống cũng hỗ trợ tìm kiếm bằng hình ảnh bìa sách thông qua tính năng OCR.
3. **Mượn/Trả sách**: Chọn sách từ danh sách hiển thị và nhấn nút "Mượn sách". Bạn có thể theo dõi và thực hiện trả sách tại danh sách sách đã mượn.
4. **Gợi ý sách**: Hệ thống tự động gợi ý sách phù hợp dựa trên lịch sử hoạt động và mượn sách của bạn.
