import os, re, uuid, logging, pytesseract, json
import pandas as pd

from PIL import Image, ImageEnhance, ImageFilter
from urllib.parse import urljoin
from rapidfuzz import process
from functools import wraps

from django.conf import settings
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Q, Case, When, Count, Avg
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Book, UserHistory, BorrowRecord, BookReview, CATEGORY_CHOICES, BORROW_STATUS_CHOICES
from .forms import BookCoverForm, UserUpdateForm, BookForm, BookReviewForm
from .recommend import recommend_books
from myapp.models import CreateRegister

# ─── Cấu hình thanh toán ────────────────────────────────────────────────────────────────
BORROW_FEE_PER_DAY = 3000          # VND / ngày
BANK_CODE       = 'MB'
BANK_ACCOUNT    = '0774504240205'
ACCOUNT_NAME    = 'LE NGUYEN NHAT MINH'


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

logger = logging.getLogger(__name__)


# ─── Decorators ─────────────────────────────────────────────────────────────

def staff_required(view_func):
    """Decorator kiểm tra is_staff; redirect về home nếu không có quyền."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'Bạn không có quyền truy cập trang này.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Auth Views ──────────────────────────────────────────────────────────────

def register_view(request):
    form = CreateRegister()
    if request.method == "POST":
        form = CreateRegister(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Đăng ký thành công! Vui lòng đăng nhập.")
            return redirect("login")

    context = {'form': form}
    return render(request, 'register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if request.POST.get('remember_me'):
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 ngày
            else:
                request.session.set_expiry(0)
            return redirect('home')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ─── Home & Static Pages ─────────────────────────────────────────────────────

def home(request):
    user = request.user
    books = Book.objects.all()
    recommended = []

    if user.is_authenticated:
        history = UserHistory.objects.filter(user=user).values_list('book_id', flat=True)
        books_df = pd.DataFrame(list(books.values('id', 'title', 'author')))
        if not books_df.empty:
            books_df['combined'] = books_df['title'] + ' ' + books_df['author']
            history_dict = {user.id: list(history)}
            recommended_df = recommend_books(user.id, books_df, history_dict)
            recommended_ids = list(recommended_df['id'])
            preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(recommended_ids)])
            recommended = list(Book.objects.filter(id__in=recommended_ids).order_by(preserved_order))

    return render(request, 'home.html', {
        'books': books,
        'recommended_books': recommended
    })


def intro_ptit(request):
    return render(request, 'intro.html')


# ─── Search ──────────────────────────────────────────────────────────────────

@login_required(login_url='/login/')
def search_page(request):
    user = request.user
    query = request.GET.get('q', '')
    book_category = request.GET.get('book_category', '')  # thể loại sách

    books = []
    recommended_books = []

    if query:
        book_qs = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))

        # Lọc theo thể loại nếu có
        if book_category:
            book_qs = book_qs.filter(category=book_category)

        books = book_qs

    if user.is_authenticated:
        history = UserHistory.objects.filter(user=user).values_list('book_id', flat=True)
        all_books = Book.objects.all()
        books_df = pd.DataFrame(list(all_books.values('id', 'title', 'author')))
        if not books_df.empty:
            books_df['combined'] = books_df['title'] + ' ' + books_df['author']
            history_dict = {user.id: list(history)}
            recommended_df = recommend_books(user.id, books_df, history_dict)

            if not recommended_df.empty:
                recommended_ids = list(recommended_df['id'])
                preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(recommended_ids)])
                recommended_books = list(Book.objects.filter(id__in=recommended_ids).order_by(preserved_order))

    return render(request, 'search.html', {
        'query': query,
        'book_category': book_category,
        'books': books,
        'recommended_books': recommended_books,
        'category_choices': CATEGORY_CHOICES,
    })


# ─── Book Views ───────────────────────────────────────────────────────────────

def book_list(request):
    book_qs = Book.objects.all().order_by('title')
    category_filter = request.GET.get('category', '')
    if category_filter:
        book_qs = book_qs.filter(category=category_filter)

    paginator = Paginator(book_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'book_list.html', {
        'page_obj': page_obj,
        'category_filter': category_filter,
        'category_choices': CATEGORY_CHOICES,
    })


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    borrow_status = None
    is_borrowed = False
    if request.user.is_authenticated:
        borrow_record = BorrowRecord.objects.filter(
            user=request.user, book=book, returned_at__isnull=True
        ).exclude(status='rejected').first()
        if borrow_record:
            is_borrowed = True
            borrow_status = borrow_record.status
        # Lưu vào UserHistory (tránh trùng lặp quá nhiều: chỉ ghi nếu chưa xem trong 24h)
        from datetime import timedelta
        recent_view = UserHistory.objects.filter(
            user=request.user,
            book=book,
            viewed_at__gte=timezone.now() - timedelta(hours=24)
        ).exists()
        if not recent_view:
            UserHistory.objects.create(user=request.user, book=book)

    # Đánh giá
    reviews = BookReview.objects.filter(book=book).select_related('user')
    user_review = None
    review_form = None
    if request.user.is_authenticated:
        user_review = BookReview.objects.filter(user=request.user, book=book).first()
        if not user_review:
            review_form = BookReviewForm()

    avg_rating = book.average_rating()
    review_count = book.review_count()

    return render(request, 'book.html', {
        'book': book,
        'is_borrowed': is_borrowed,
        'borrow_status': borrow_status,
        'reviews': reviews,
        'user_review': user_review,
        'review_form': review_form,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'rating_range': range(1, 6),
    })





# ─── Review Views ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def submit_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Kiểm tra đã đánh giá chưa
    existing = BookReview.objects.filter(user=request.user, book=book).first()
    if existing:
        messages.warning(request, 'Bạn đã đánh giá cuốn sách này rồi.')
        return redirect('book_detail', book_id=book_id)

    form = BookReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.book = book
        review.save()
        messages.success(request, 'Cảm ơn bạn đã đánh giá!')
    else:
        messages.error(request, 'Vui lòng chọn số sao và nhập nhận xét.')

    return redirect('book_detail', book_id=book_id)


# ─── Profile Views ────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    user = request.user
    borrowed_books = BorrowRecord.objects.filter(user=user).exclude(status='rejected')
    viewed_books = UserHistory.objects.filter(user=user).select_related('book').order_by('-viewed_at')[:10]

    return render(request, 'user/profile.html', {
        'user': user,
        'borrowed_books': borrowed_books,
        'viewed_books': viewed_books,
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật thông tin thành công.")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'user/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    error = None
    success = None
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(old_password):
            error = 'Mật khẩu hiện tại không đúng.'
        elif len(new_password1) < 8:
            error = 'Mật khẩu mới phải có ít nhất 8 ký tự.'
        elif new_password1 != new_password2:
            error = 'Mật khẩu mới và xác nhận không khớp.'
        else:
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            success = 'Đổi mật khẩu thành công!'

    return render(request, 'user/change_password.html', {'error': error, 'success': success})


# ─── Borrow / Return Views ────────────────────────────────────────────────────

@require_POST
@login_required
def borrow_book(request, book_id):
    from urllib.parse import quote
    from datetime import date as date_cls

    book = get_object_or_404(Book, id=book_id)

    # Kiểm tra đã có yêu cầu pending/approved chưa trả
    if BorrowRecord.objects.filter(
        user=request.user, book=book,
        returned_at__isnull=True,
        status__in=['pending', 'approved']
    ).exists():
        return JsonResponse({'success': False, 'message': f"Bạn đã có yêu cầu mượn sách '{book.title}'."} )

    data = {}
    if request.body:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            pass

    expected_return_date = data.get('expected_return_date')
    note = data.get('note')

    # Tạo BorrowRecord với status='pending' (chưa trừ quantity)
    BorrowRecord.objects.create(
        user=request.user,
        book=book,
        borrowed_at=timezone.now(),
        expected_return_date=expected_return_date,
        note=note,
        status='pending'
    )

    # Tính tiền theo ngày
    total_fee = 0
    days = 0
    if expected_return_date:
        try:
            return_date = date_cls.fromisoformat(expected_return_date)
            days = (return_date - timezone.now().date()).days
            if days > 0:
                total_fee = days * BORROW_FEE_PER_DAY
        except Exception:
            pass

    # Tạo QR URL qua VietQR API
    add_info = quote(f'Muon sach {book.title}'[:30])
    qr_url = (
        f'https://img.vietqr.io/image/{BANK_CODE}-{BANK_ACCOUNT}-compact2.png'
        f'?amount={total_fee}'
        f'&addInfo={add_info}'
        f'&accountName={quote(ACCOUNT_NAME)}'
    )

    return JsonResponse({
        'success': True,
        'message': f"Yêu cầu mượn sách '{book.title}' đã được gửi!",
        'qr_url': qr_url,
        'total_fee': f"{total_fee:,}".replace(',', '.'),
        'fee_per_day': f"{BORROW_FEE_PER_DAY:,}".replace(',', '.'),
        'days': days,
        'book_title': book.title,
        'bank_account': BANK_ACCOUNT,
        'account_name': ACCOUNT_NAME,
        'bank_name': 'MB Bank',
    })


@login_required
def list_borrowed_books(request):
    borrowed_books = BorrowRecord.objects.filter(
        user=request.user, returned_at__isnull=True
    ).exclude(status='rejected').select_related('book').order_by('-borrowed_at')
    return render(request, 'borrowed_books.html', {'borrowed_books': borrowed_books})



# ─── Admin: Duyệt / Từ chối yêu cầu mượn ───────────────────────────────────────────

@login_required
@staff_required
def pending_borrows(request):
    pending_list = BorrowRecord.objects.filter(
        status='pending'
    ).select_related('user', 'book').order_by('borrowed_at')
    pending_count = pending_list.count()
    return render(request, 'admin/manage_borrows.html', {
        'pending_list': pending_list,
        'pending_count': pending_count,
    })


@login_required
@staff_required
@require_POST
def approve_borrow(request, borrow_id):
    record = get_object_or_404(BorrowRecord, id=borrow_id)
    if record.status != 'pending':
        messages.warning(request, 'Yêu cầu này không còn ở trạng thái chờ.')
        return redirect('pending_borrows')

    record.status = 'approved'
    record.save()

    messages.success(request, f'Đã duyệt yêu cầu mượn “{record.book.title}” của {record.user.username}.')
    return redirect('pending_borrows')


@login_required
@staff_required
@require_POST
def reject_borrow(request, borrow_id):
    record = get_object_or_404(BorrowRecord, id=borrow_id)
    if record.status != 'pending':
        messages.warning(request, 'Yêu cầu này không còn ở trạng thái chờ.')
        return redirect('pending_borrows')

    record.status = 'rejected'
    record.save()
    messages.success(request, f'Đã từ chối yêu cầu mượn “{record.book.title}” của {record.user.username}.')
    return redirect('pending_borrows')


@login_required
@staff_required
@require_POST
def approve_all_borrows(request):
    records = BorrowRecord.objects.filter(status='pending')
    count = records.update(status='approved')
    messages.success(request, f'Đã duyệt thành công {count} yêu cầu mượn.')
    return redirect('pending_borrows')


@login_required
@staff_required
@require_POST
def reject_all_borrows(request):
    records = BorrowRecord.objects.filter(status='pending')
    count = records.update(status='rejected')
    messages.success(request, f'Đã từ chối {count} yêu cầu mượn.')
    return redirect('pending_borrows')


# ─── Admin CRUD – Sách ───────────────────────────────────────────────────────

@login_required
@staff_required
def manage_books(request):
    query = request.GET.get('q', '')
    book_qs = Book.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query) | Q(publisher__icontains=query)
    ) if query else Book.objects.all().order_by('title')

    paginator = Paginator(book_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = BookForm()
    return render(request, 'admin/manage_books.html', {
        'page_obj': page_obj,
        'form': form,
        'query': query,
    })


@login_required
@staff_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            pdf_source = request.POST.get('pdf_source')
            if pdf_source == 'url':
                book.pdf_file = None
            elif pdf_source == 'file':
                book.uri = ''
            book.save()
            messages.success(request, f'Đã thêm sách "{form.cleaned_data["title"]}" thành công!')
            return redirect('manage_books')
        else:
            errors = {field: list(errs) for field, errs in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    return redirect('manage_books')


@login_required
@staff_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'GET':
        data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'publisher': book.publisher,
            'category': book.category,
            'description': book.description or '',
            'uri': book.uri or '',
            'image_url': book.image.url if book.image else '',
            'pdf_url': book.pdf_file.url if book.pdf_file else '',
        }
        return JsonResponse(data)
    elif request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            pdf_source = request.POST.get('pdf_source')
            if pdf_source == 'url':
                if book.pdf_file:
                    book.pdf_file.delete(save=False)
                book.pdf_file = None
            elif pdf_source == 'file':
                book.uri = ''
            book.save()
            messages.success(request, f'Đã cập nhật sách "{book.title}" thành công!')
            return redirect('manage_books')
        else:
            errors = {field: list(errs) for field, errs in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    return redirect('manage_books')


@login_required
@staff_required
@require_POST
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    title = book.title
    book.delete()
    messages.success(request, f'Đã xóa sách "{title}" thành công!')
    return redirect('manage_books')





# ─── Admin Dashboard & User Management ───────────────────────────────────────

@login_required
@staff_required
def admin_dashboard(request):
    from django.db.models.functions import TruncMonth

    total_books = Book.objects.count()
    total_users = User.objects.count()
    active_borrows = BorrowRecord.objects.filter(status='approved', returned_at__isnull=True).count()
    total_borrows = BorrowRecord.objects.count()

    # Top 5 sách được mượn nhiều nhất
    top_books = (
        BorrowRecord.objects.values('book__id', 'book__title', 'book__author')
        .annotate(borrow_count=Count('id'))
        .order_by('-borrow_count')[:5]
    )

    # Top 5 user mượn nhiều nhất
    top_users = (
        BorrowRecord.objects.values('user__id', 'user__username', 'user__first_name', 'user__last_name')
        .annotate(borrow_count=Count('id'))
        .order_by('-borrow_count')[:5]
    )



    pending_count = BorrowRecord.objects.filter(status='pending').count()

    # Lượt mượn theo tháng (6 tháng gần nhất)
    monthly_borrows = (
        BorrowRecord.objects
        .annotate(month=TruncMonth('borrowed_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    monthly_labels = [item['month'].strftime('%m/%Y') for item in monthly_borrows if item['month']]
    monthly_data = [item['count'] for item in monthly_borrows if item['month']]

    # Sách mới thêm gần đây (không có created_at, dùng ID desc)
    recent_books = Book.objects.order_by('-id')[:5]

    return render(request, 'admin/dashboard.html', {
        'total_books': total_books,
        'total_users': total_users,
        'active_borrows': active_borrows,
        'total_borrows': total_borrows,
        'top_books': top_books,
        'top_users': top_users,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
        'recent_books': recent_books,
    })


@login_required
@staff_required
def manage_users(request):
    query = request.GET.get('q', '')
    user_qs = User.objects.all().order_by('username')
    if query:
        user_qs = user_qs.filter(
            Q(username__icontains=query) | Q(email__icontains=query) |
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

    # Annotate số sách đang mượn
    user_qs = user_qs.annotate(
        active_borrows=Count('borrowrecord', filter=Q(borrowrecord__status='approved', borrowrecord__returned_at__isnull=True)),
        total_borrows=Count('borrowrecord'),
    )

    paginator = Paginator(user_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/manage_users.html', {
        'page_obj': page_obj,
        'query': query,
    })


# ─── OCR Image Search ─────────────────────────────────────────────────────────

def preprocess_image(image):
    try:
        image = image.convert('L')
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.8)
        image = ImageEnhance.Sharpness(image).enhance(1.5)
        return image
    except Exception as e:
        logger.error(f"Lỗi tiền xử lý ảnh: {str(e)}")
        raise


def optimize_ocr_for_vietnamese(image):
    """Optimized OCR configuration for mixed English/Vietnamese text"""
    try:
        config = r'''
        -l eng+vie
        --oem 3
        --psm 6
        --dpi 300
        -c preserve_interword_spaces=1
        -c tessedit_char_blacklist=|\\`~_@
        -c textord_space_size_is_variable=1
        '''
        text = pytesseract.image_to_string(image, config=config)
        logger.info(f"OCR Raw Output: {text}")

        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
        text = re.sub(r'([a-zA-Z])\1{2,}', r'\1', text)

        return text.strip()
    except Exception as e:
        logger.error(f"OCR error: {str(e)}", exc_info=True)
        raise


def clean_text(text):
    """Enhanced text cleaning with line preservation"""
    text = re.sub(r'\s*-\s*', '-', text)
    text = re.sub(r'\b([A-Z])([A-Z]+)\b', lambda m: m.group(1) + m.group(2).lower(), text)
    text = re.sub(r'[^\wÀ-ỹ\s.,;:\-\n]', '', text, flags=re.UNICODE)
    text = '\n'.join([' '.join(line.split()) for line in text.split('\n')])
    return text.strip()


@login_required(login_url='/login/')
def upload_cover(request):
    if request.method == 'POST':
        form = BookCoverForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            try:
                img = Image.open(image)
                img = preprocess_image(img)
                raw_text = optimize_ocr_for_vietnamese(img)
                cleaned_title = clean_text(raw_text)

                if not cleaned_title:
                    return JsonResponse({'success': False, 'message': "Không thể nhận diện văn bản từ ảnh."})

                all_titles = list(Book.objects.values_list('title', flat=True))
                match = process.extractOne(cleaned_title, all_titles)

                if not match:
                    return JsonResponse({'success': False, 'message': "Không tìm thấy tiêu đề phù hợp."})

                best_match, _, _ = match
                books = Book.objects.filter(title__icontains=best_match)

                return render(request, 'result.html', {
                    'books': books,
                    'title': cleaned_title
                })

            except Exception as e:
                logger.error(f"Lỗi xử lý ảnh: {str(e)}", exc_info=True)
                return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Yêu cầu không hợp lệ.'})