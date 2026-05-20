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
- **Triển khai**: Hỗ trợ triển khai trên các nền tảng như Heroku hoặc máy chủ nội bộ.

## Cấu Trúc Thư Mục
```
mysite/
├── db.sqlite3                     # File cơ sở dữ liệu SQLite
├── manage.py                      # File quản lý dự án Django
├── requirements.txt               # Danh sách các thư viện cần thiết
├── mysite/                        # Thư mục chính của dự án Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                # File cấu hình dự án
│   ├── urls.py                    # File định tuyến URL
│   └── wsgi.py
├── myapp/                         # Ứng dụng chính của dự án
│   ├── migrations/                # Thư mục chứa các file migration
│   │   ├── __init__.py
│   │   └── ...                    # Các file migration khác
│   ├── static/                    # Thư mục chứa các file tĩnh
│   │   ├── css/
│   │   │   └── style.css          # File CSS chính
│   │   ├── js/
│   │   │   └── style.js           # File JavaScript chính
│   │   └── images/                # Thư mục chứa hình ảnh
│   │       ├── logo.jpg           # Logo của dự án
│   │       ├── default-book-cover.jpg
│   │       └── ...                # Các hình ảnh khác
│   ├── templates/                 # Thư mục chứa các template HTML
│   │   ├── home.html              # Trang chủ
│   │   ├── upload.html            # Trang upload ảnh
│   │   ├── search.html            # Trang tìm kiếm
│   │   ├── base.html              # Template cơ bản
│   │   └── ...                    # Các template khác
│   ├── __init__.py
│   ├── admin.py                   # File cấu hình admin
│   ├── apps.py                    # File cấu hình ứng dụng
│   ├── models.py                  # File định nghĩa các model
│   ├── tests.py                   # File chứa các test case
│   ├── views.py                   # File xử lý logic của ứng dụng
│   └── urls.py                    # File định tuyến URL cho ứng dụng
├── media/                         # Thư mục chứa các file upload
│   └── uploads/                   # Thư mục chứa ảnh được upload
│       └── example.jpg
└── data/                          # Thư mục chứa dữ liệu mẫu
    └── books.xlsx                 # File Excel chứa danh sách sách
```

## Hướng Dẫn Sử Dụng
1. Đăng nhập/Đăng ký:

2. Người dùng cần đăng ký tài khoản hoặc đăng nhập để sử dụng các tính năng như mượn sách, trả sách.
Tìm kiếm sách:

3. Sử dụng thanh tìm kiếm để tìm sách theo từ khóa hoặc danh mục.
Tìm kiếm bằng hình ảnh bìa sách thông qua tính năng OCR.

4. Mượn và trả sách:

Chọn sách từ danh sách hiển thị và nhấn nút "Mượn sách".
Truy cập danh sách sách đã mượn để trả sách.
Xem gợi ý sách:

5. Hệ thống tự động gợi ý sách dựa trên lịch sử mượn của bạn.

