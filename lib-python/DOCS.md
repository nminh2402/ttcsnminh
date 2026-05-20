# 📚 Tài Liệu Dự Án - Hệ Thống Quản Lý Thư Viện PTIT

> **Công nghệ:** Django 5.1 · MySQL · Python 3.x  
> **Mục đích:** Hệ thống quản lý thư viện trực tuyến cho phép người dùng tìm kiếm, mượn/trả sách, xem giáo trình và quản lý tài khoản cá nhân. Staff có thể quản lý sách trực tiếp trên web.

---

## 📁 Cấu Trúc Thư Mục Tổng Quan

```
lib-python/
├── mysite/                         # Thư mục gốc của dự án Django
│   ├── manage.py                   # Công cụ quản lý Django
│   ├── check_books.py              # Script kiểm tra dữ liệu sách
│   ├── fix_images.py               # Script sửa đường dẫn ảnh bìa
│   ├── requirements.txt            # Danh sách thư viện Python
│   ├── db.sqlite3                  # (dự phòng) SQLite database
│   ├── data/
│   │   └── Book1-version-1.xlsx    # File Excel dữ liệu sách mẫu
│   ├── media/                      # File upload (ảnh bìa, PDF)
│   ├── mysite/                     # Package cấu hình Django
│   │   ├── settings.py             # Cấu hình toàn dự án
│   │   ├── urls.py                 # URL gốc của toàn site
│   │   ├── wsgi.py                 # Điểm vào WSGI (deploy production)
│   │   └── asgi.py                 # Điểm vào ASGI (async support)
│   └── myapp/                      # Ứng dụng chính
│       ├── models.py               # Định nghĩa cơ sở dữ liệu
│       ├── views.py                # Xử lý logic các trang
│       ├── urls.py                 # Định tuyến URL của app
│       ├── forms.py                # Form nhập liệu
│       ├── admin.py                # Cấu hình trang Django Admin
│       ├── apps.py                 # Cấu hình ứng dụng
│       ├── recommend.py            # Thuật toán gợi ý sách
│       ├── tests.py                # File test
│       ├── management/
│       │   └── commands/
│       │       └── import_books.py # Lệnh import sách từ Excel
│       ├── migrations/             # Lịch sử thay đổi database
│       ├── static/
│       │   ├── css/                # File CSS cho từng trang
│       │   └── js/                 # File JavaScript
│       └── templates/              # File HTML giao diện
│           ├── base.html
│           ├── home.html
│           ├── ... (các trang khác)
│           ├── admin/
│           │   └── manage_books.html
│           └── user/
│               ├── profile.html
│               ├── edit_profile.html
│               └── change_password.html
```

---

## 🔧 CẤU HÌNH DỰ ÁN

### `mysite/mysite/settings.py`
File cấu hình trung tâm của toàn bộ dự án Django.

| Cài đặt | Giá trị | Mô tả |
|---|---|---|
| `DATABASE` | MySQL (`library_db`) | Kết nối đến MySQL, host `localhost:3306` |
| `MEDIA_ROOT` | `mysite/media/` | Nơi lưu file upload (ảnh, PDF) |
| `STATIC_URL` | `/static/` | Đường dẫn file tĩnh (CSS, JS, ảnh) |
| `ALLOWED_HOSTS` | `hoangmelinh.io.vn`, `127.0.0.1`, v.v. | Các host được phép truy cập |
| `DEBUG` | `True` | Chế độ phát triển (tắt khi deploy thật) |

---

### `mysite/mysite/urls.py`
**URL gốc** của toàn site. Phân phối request đến:
- `/admin/` → Trang Django Admin tích hợp sẵn
- `/` (tất cả còn lại) → `myapp.urls` (xử lý bởi ứng dụng chính)
- Phục vụ file media (ảnh, PDF) khi `DEBUG=True`

---

### `mysite/mysite/wsgi.py` & `asgi.py`
Các điểm vào để deploy lên server thật (Nginx, Gunicorn, v.v.). Không cần chỉnh sửa trong quá trình phát triển.

---

### `mysite/requirements.txt`
Danh sách tất cả các thư viện Python cần cài đặt. Cài bằng lệnh:
```bash
pip install -r requirements.txt
```

---

## 🗄️ DATABASE - MODELS

### `myapp/models.py`
Định nghĩa **4 bảng dữ liệu** chính:

#### `Book` — Bảng Sách
| Trường | Kiểu | Mô tả |
|---|---|---|
| `title` | CharField | Tên sách |
| `author` | CharField | Tác giả |
| `publisher` | CharField | Nhà xuất bản |
| `uri` | URLField | Link đọc online (tùy chọn) |
| `image` | ImageField | Ảnh bìa, lưu tại `media/book_images/` |
| `pdf_file` | FileField | File PDF, lưu tại `media/book_pdfs/` |
| `quantity` | PositiveIntegerField | Số lượng sách còn lại (mặc định: 1) |

#### `Giaotrinh` — Bảng Giáo Trình
Lưu giáo trình học thuật. Tương tự `Book` nhưng không có `quantity` và `pdf_file`.
Trường: `title`, `author`, `uri`, `image`.

#### `CreateRegister` — Form Đăng Ký (kế thừa `UserCreationForm`)
Mở rộng form đăng ký mặc định của Django:
- Thêm trường `full_name` (Họ và Tên)
- Tự động tách `full_name` thành `first_name` + `last_name` khi lưu

#### `UserHistory` — Lịch Sử Xem Sách
Ghi lại sách nào người dùng đã xem để phục vụ gợi ý.
| Trường | Mô tả |
|---|---|
| `user` | Liên kết đến User (Django Auth) |
| `book` | Liên kết đến Book |
| `viewed_at` | Thời điểm xem (tự động ghi) |

#### `BorrowRecord` — Lịch Sử Mượn/Trả Sách
| Trường | Mô tả |
|---|---|
| `user` | Người mượn |
| `book` | Sách được mượn |
| `borrowed_at` | Ngày mượn (tự động) |
| `expected_return_date` | Ngày dự kiến trả |
| `note` | Ghi chú của người mượn |
| `returned_at` | Ngày trả thực tế (`NULL` = chưa trả) |
- Method `is_borrowed()`: Trả về `True` nếu `returned_at` là `NULL`

---

## 🧩 FORMS

### `myapp/forms.py`
Định nghĩa **3 form** nhập liệu:

| Form | Mục đích |
|---|---|
| `BookCoverForm` | Upload ảnh bìa sách để nhận dạng OCR |
| `UserUpdateForm` | Cập nhật thông tin cá nhân (`first_name`, `last_name`, `email`) |
| `BookForm` | Thêm/sửa sách (dành cho staff): tên, tác giả, NXB, URL, ảnh, PDF, số lượng |

---

## 🌐 VIEWS & URLS

### `myapp/urls.py`
Ánh xạ URL → View function:

| URL | View | Tên | Mô tả |
|---|---|---|---|
| `/` | `home` | `home` | Trang chủ |
| `/home/` | `home` | `home` | Alias trang chủ |
| `/intro/` | `intro_ptit` | `intro` | Trang giới thiệu trường PTIT |
| `/search/` | `search_page` | `search` | Tìm kiếm sách/giáo trình |
| `/search-image/` | `upload_cover` | `upload_cover` | Tìm kiếm bằng ảnh bìa (OCR) |
| `/book/` | `book_list` | `book` | Danh sách tất cả sách |
| `/book/<id>/` | `book_detail` | `book_detail` | Chi tiết 1 cuốn sách |
| `/book/<id>/borrow/` | `borrow_book` | `borrow_book` | API mượn sách |
| `/borrow_book/` | `list_borrowed_books` | `borrowed_books` | Danh sách sách đang mượn |
| `/return/<id>/` | `return_book` | `return_book` | Trả sách |
| `/giaotrinh/<id>/` | `giaotrinh_detail` | `giaotrinh_detail` | Chi tiết giáo trình |
| `/login/` | `login_view` | `login` | Đăng nhập |
| `/register/` | `register_view` | `register` | Đăng ký tài khoản |
| `/logout/` | `logout_view` | `logout` | Đăng xuất |
| `/profile/` | `profile_view` | `profile` | Trang cá nhân |
| `/profile/edit/` | `edit_profile` | `edit_profile` | Sửa thông tin cá nhân |
| `/profile/change-password/` | `change_password` | `change_password` | Đổi mật khẩu |
| `/manage/books/` | `manage_books` | `manage_books` | Quản lý sách (chỉ staff) |
| `/manage/books/add/` | `add_book` | `add_book` | Thêm sách mới (staff) |
| `/manage/books/<id>/edit/` | `edit_book` | `edit_book` | Sửa thông tin sách (staff) |
| `/manage/books/<id>/delete/` | `delete_book` | `delete_book` | Xóa sách (staff) |

---

### `myapp/views.py`
File xử lý logic lớn nhất (~464 dòng). Bao gồm các nhóm chức năng:

#### 🔐 Xác Thực Người Dùng
- **`register_view`**: Xử lý đăng ký tài khoản mới với `CreateRegister` form
- **`login_view`**: Đăng nhập, hỗ trợ "Remember Me" (session 30 ngày)
- **`logout_view`**: Đăng xuất và chuyển về trang login

#### 🏠 Trang Chính
- **`home`**: Trang chủ, hiển thị tất cả sách + gợi ý sách cá nhân hóa (nếu đã đăng nhập)
- **`intro_ptit`**: Render trang giới thiệu tĩnh

#### 🔍 Tìm Kiếm
- **`search_page`**: Tìm kiếm theo từ khóa, lọc theo loại (`book`/`giaotrinh`/`all`). Yêu cầu đăng nhập.
- **`upload_cover`**: Nhận ảnh bìa → xử lý OCR → tìm sách phù hợp trong database

#### 📖 Sách & Giáo Trình
- **`book_list`**: Liệt kê toàn bộ sách
- **`book_detail`**: Chi tiết sách, kiểm tra người dùng đang mượn hay chưa
- **`giaotrinh_detail`**: Chi tiết giáo trình

#### 📋 Mượn/Trả Sách
- **`borrow_book`**: API POST mượn sách; kiểm tra không mượn trùng; nhận `expected_return_date` và `note` từ JSON body
- **`list_borrowed_books`**: Danh sách sách đang mượn (chưa trả)
- **`return_book`**: Trả sách, cập nhật `returned_at` và tăng `quantity`

#### 👤 Quản Lý Tài Khoản
- **`profile_view`**: Trang cá nhân: sách đã mượn, đã trả, lịch sử xem
- **`edit_profile`**: Cập nhật `first_name`, `last_name`, `email`
- **`change_password`**: Đổi mật khẩu với 3 bước kiểm tra (mật khẩu cũ, độ dài, xác nhận). Dùng `update_session_auth_hash` để giữ đăng nhập sau khi đổi.

#### 🛠️ Quản Lý Sách (Staff Only)
- **`staff_required`**: Decorator tùy chỉnh, chặn user không phải staff
- **`manage_books`**: Giao diện CRUD sách, hỗ trợ tìm kiếm theo tên/tác giả/NXB
- **`add_book`**: Thêm sách mới qua modal, trả lỗi dạng JSON nếu form không hợp lệ
- **`edit_book`**: GET → trả JSON dữ liệu sách cho modal; POST → cập nhật sách
- **`delete_book`**: Xóa sách (chỉ nhận POST request)

#### 🤖 OCR - Nhận Dạng Ảnh
- **`preprocess_image`**: Tiền xử lý ảnh (grayscale, tăng contrast/sharpness)
- **`optimize_ocr_for_vietnamese`**: Chạy Tesseract OCR cho tiếng Việt + tiếng Anh
- **`clean_text`**: Làm sạch văn bản OCR (chuẩn hóa khoảng trắng, ký tự đặc biệt)

---

## 🤖 THUẬT TOÁN GỢI Ý

### `myapp/recommend.py`
Gợi ý sách dựa trên lịch sử xem của người dùng.

**Thuật toán:**
1. Ghép `title + author` thành cột `combined`
2. Dùng **TF-IDF Vectorizer** để vector hóa tất cả sách
3. Lấy các sách trong lịch sử của user, tính vector trung bình
4. Tính **Cosine Similarity** giữa vector user và tất cả sách
5. Trả về top-10 sách tương đồng nhất

> ⚠️ **Lưu ý:** Nếu user chưa có lịch sử, trả về 10 sách đầu tiên trong database.

---

## 🖥️ ADMIN PANEL

### `myapp/admin.py`
Đăng ký 4 model vào trang Django Admin (`/admin/`):

| Model | Cột hiển thị | Tìm kiếm | Lọc |
|---|---|---|---|
| `Book` | title, author, publisher, quantity, uri, **Có PDF?** | title, author, publisher | author, publisher |
| `Giaotrinh` | title, author, uri | title, author | — |
| `UserHistory` | user, book, viewed_at | — | viewed_at, user |
| `BorrowRecord` | user, book, borrowed_at, expected_return_date, returned_at, is_borrowed | username, book title, note | borrowed_at, returned_at, user |

---

## 🗃️ DATABASE MIGRATIONS

### `myapp/migrations/`
Lịch sử thay đổi cấu trúc database theo thứ tự:

| File | Nội dung thay đổi |
|---|---|
| `0001_initial.py` | Tạo bảng `Book` và `Giaotrinh` ban đầu |
| `0002_remove_book_collection.py` | Xóa trường `collection` khỏi `Book` |
| `0003_giaotrinh.py` | Cập nhật model `Giaotrinh` |
| `0004_userhistory.py` | Tạo bảng `UserHistory` (lịch sử xem) |
| `0005_borrowrecord.py` | Tạo bảng `BorrowRecord` (mượn/trả sách) |
| `0006_book_available.py` | Thêm trường `available` vào `Book` |
| `0007_remove_book_available_book_quantity.py` | Đổi `available` thành `quantity` |
| `0008_borrowrecord_expected_return_date_note.py` | Thêm `expected_return_date` và `note` vào `BorrowRecord` |
| `0009_book_pdf_file.py` | Thêm trường `pdf_file` vào `Book` |

---

## 🎨 TEMPLATES (Giao Diện HTML)

### `myapp/templates/base.html`
Template gốc, các trang khác kế thừa từ đây. Chứa:
- Navigation bar (logo, menu điều hướng, nút đăng nhập/đăng xuất)
- Link CSS và JS chung
- Block `content` để các trang con chèn nội dung

### `myapp/templates/home.html`
Trang chủ. Hiển thị:
- Banner/Hero section giới thiệu
- Danh sách sách gợi ý cá nhân hóa (nếu đã đăng nhập)
- Toàn bộ danh sách sách có ảnh bìa
- Thanh tìm kiếm bằng ảnh (OCR)

### `myapp/templates/search.html`
Trang tìm kiếm. Hiển thị:
- Ô tìm kiếm và bộ lọc loại (Sách / Giáo trình / Tất cả)
- Kết quả tìm kiếm sách và giáo trình
- Sách gợi ý liên quan

### `myapp/templates/book.html`
Trang chi tiết sách. Hiển thị:
- Ảnh bìa, tên, tác giả, nhà xuất bản
- Nút **Mượn sách** (hiện modal nhập ngày trả + ghi chú)
- Link đọc online và tải PDF (nếu có)
- Trạng thái đang mượn

### `myapp/templates/borrowed_books.html`
Danh sách sách đang mượn của người dùng hiện tại. Có nút **Trả sách**.

### `myapp/templates/giaotrinh.html`
Chi tiết một giáo trình: tên, tác giả, ảnh, link đọc online.

### `myapp/templates/intro.html`
Trang giới thiệu về trường PTIT (nội dung tĩnh).

### `myapp/templates/login.html`
Form đăng nhập: username, password, checkbox "Remember Me".

### `myapp/templates/register.html`
Form đăng ký: Họ tên, username, email, mật khẩu, xác nhận mật khẩu.

### `myapp/templates/result.html`
Trang kết quả tìm kiếm bằng ảnh OCR, hiển thị các sách phù hợp tìm được.

### `myapp/templates/admin/manage_books.html`
Giao diện quản lý sách dành riêng cho **Staff**:
- Bảng danh sách toàn bộ sách
- Thanh tìm kiếm
- Nút thêm, sửa, xóa sách qua modal (không cần chuyển trang)

### `myapp/templates/user/profile.html`
Trang cá nhân người dùng. Hiển thị:
- Thông tin tài khoản (tên, email)
- Tab "Đang mượn": sách chưa trả, có link PDF nếu có
- Tab "Đã trả": lịch sử các sách đã trả
- Tab "Lịch sử xem"
- Nút chuyển đến sửa thông tin và đổi mật khẩu

### `myapp/templates/user/edit_profile.html`
Form sửa thông tin cá nhân (họ tên, email).

### `myapp/templates/user/change_password.html`
Form đổi mật khẩu với:
- Ô nhập mật khẩu cũ, mới, xác nhận
- Hiển thị lỗi/thành công
- Thanh kiểm tra độ mạnh mật khẩu theo thời gian thực (realtime)

---

## 🎨 STATIC FILES

### CSS (`myapp/static/css/`)

| File | Phụ trách trang |
|---|---|
| `base.css` | Styles chung, navigation |
| `home.css` | Trang chủ |
| `search.css` | Trang tìm kiếm |
| `book.css` | Trang chi tiết sách |
| `borrowed_book.css` | Trang sách đang mượn |
| `profile.css` | Trang cá nhân |
| `edit_profile.css` | Form sửa thông tin / đổi mật khẩu |
| `login.css` | Trang đăng nhập |
| `register.css` | Trang đăng ký |
| `result.css` | Trang kết quả OCR |
| `intro.css` | Trang giới thiệu |
| `style.css` | Styles tổng hợp dùng chung |

### JavaScript (`myapp/static/js/`)

| File | Chức năng |
|---|---|
| `style.js` | Xử lý tương tác chung: upload ảnh OCR, modal mượn sách, nút trả sách, hiệu ứng động |
| `profile.js` | Xử lý tab chuyển đổi trên trang cá nhân, kiểm tra độ mạnh mật khẩu realtime |

---

## 🛠️ SCRIPTS TIỆN ÍCH

### `mysite/check_books.py`
Script chạy ngoài Django để **kiểm tra nhanh** dữ liệu sách trong database:
```bash
python check_books.py
```
In ra danh sách tất cả sách kèm `id`, tên ảnh và tiêu đề.

### `mysite/fix_images.py`
Script **sửa đường dẫn ảnh** cho các sách có ảnh bị mất liên kết. Chứa mapping cứng `book_id → tên_file_ảnh`, dùng để cập nhật lại trường `image` trong database khi cần.

---

## 📋 LỆNH MANAGEMENT

### `myapp/management/commands/import_books.py`
Custom Django management command để **import sách hàng loạt từ file Excel**:
```bash
python manage.py import_books data/Book1-version-1.xlsx
```
**Quy trình:**
1. Đọc file `.xlsx` bằng `pandas`
2. Chuẩn hóa tên cột (Title, Author, Publisher, Url, Image)
3. Với mỗi dòng: tạo đối tượng `Book`, tải ảnh từ URL và lưu vào `ImageField`
4. Báo lỗi từng dòng nếu thất bại, không dừng toàn bộ

### `mysite/data/Book1-version-1.xlsx`
File Excel chứa dữ liệu sách mẫu. Các cột cần có: `Title`, `Author`, `Publisher`, `Url`, `Image` (URL ảnh).

---

## 🗂️ APPS CONFIG

### `myapp/apps.py`
Khai báo cấu hình ứng dụng `myapp` với Django. Tên ứng dụng: `myapp`.

### `myapp/__init__.py`, `mysite/__init__.py`
File trống, đánh dấu thư mục là Python package.

### `myapp/tests.py`
File test mặc định (chưa có test case nào được viết).

---

## 🚀 HƯỚNG DẪN CHẠY DỰ ÁN

```bash
# 1. Cài thư viện
pip install -r requirements.txt

# 2. Áp dụng migrations
python manage.py migrate

# 3. Tạo tài khoản admin (lần đầu)
python manage.py createsuperuser

# 4. Import dữ liệu sách mẫu
python manage.py import_books data/Book1-version-1.xlsx

# 5. Chạy server
python manage.py runserver
```

Truy cập: `http://127.0.0.1:8000/`  
Trang Admin: `http://127.0.0.1:8000/admin/`  
Quản lý sách (staff): `http://127.0.0.1:8000/manage/books/`
