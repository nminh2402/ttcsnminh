import os, re, uuid, logging, pytesseract, json
import pandas as pd

from PIL import Image, ImageEnhance, ImageFilter
from urllib.parse import urljoin
from rapidfuzz import process

from django.conf import settings
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Q, Case, When
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import Book, Giaotrinh, UserHistory, BorrowRecord
from .forms import BookCoverForm, UserUpdateForm, BookForm
from .recommend import recommend_books
from myapp.models import CreateRegister



pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

logger = logging.getLogger(__name__)



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

from django.db.models import Case, When


def home(request):
    user = request.user
    books = Book.objects.all()
    recommended = []

    if user.is_authenticated:
        history = UserHistory.objects.filter(user=user).values_list('book_id', flat=True)
        books_df = pd.DataFrame(list(books.values('id', 'title', 'author')))
        books_df['combined'] = books_df['title'] + ' ' + books_df['author']

        history_dict = {user.id: list(history)}
        recommended_df = recommend_books(user.id, books_df, history_dict)

        # Lấy danh sách Book theo thứ tự ID trong recommended
        recommended_ids = list(recommended_df['id'])
        preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(recommended_ids)])
        recommended = list(Book.objects.filter(id__in=recommended_ids).order_by(preserved_order))

    return render(request, 'home.html', {
        'books': books,
        'recommended_books': recommended
    })


def intro_ptit(request):
    return render(request, 'intro.html')

@login_required(login_url='/login/')
def search_page(request):
    user = request.user
    query = request.GET.get('q', '')
    category = request.GET.get('category', 'all')

    books = []
    giaotrinhs = []
    recommended_books = []

    if query:
        if category == 'book':
            books = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
        elif category == 'giaotrinh':
            giaotrinhs = Giaotrinh.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
        elif category == 'all':
            books = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
            giaotrinhs = Giaotrinh.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))


    if user.is_authenticated:
        history = UserHistory.objects.filter(user=user).values_list('book_id', flat=True)
        books_df = pd.DataFrame(list(Book.objects.values('id', 'title', 'author')))
        books_df['combined'] = books_df['title'] + ' ' + books_df['author']

        history_dict = {user.id: list(history)}
        recommended_df = recommend_books(user.id, books_df, history_dict)

        if not recommended_df.empty:
            recommended_ids = list(recommended_df['id'])
            preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(recommended_ids)])
            recommended_books = list(Book.objects.filter(id__in=recommended_ids).order_by(preserved_order))

    return render(request, 'search.html', {
        'query': query,
        'category': category,
        'books': books,
        'giaotrinhs': giaotrinhs,
        'recommended_books': recommended_books
    })


def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Thêm remember me functionality
            if request.POST.get('remember_me'):
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 ngày
            else:
                request.session.set_expiry(0)  # Khi trình duyệt đóng
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
        if user is None:
             print("Authentication failed")

    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def profile_view(request):
    user = request.user
    borrowed_books = BorrowRecord.objects.filter(user=user)
    returned_books = borrowed_books.exclude(returned_at=None)
    viewed_books = UserHistory.objects.filter(user=user).select_related('book').order_by('-viewed_at')

    return render(request, 'user/profile.html', {
        'user': user,
        'borrowed_books': borrowed_books,
        'returned_books': returned_books,
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


# ─── CRUD Quản lý sách (chỉ staff/superuser) ───────────────────────────────

def staff_required(view_func):
    """Decorator kiểm tra is_staff; redirect về home nếu không có quyền."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'Bạn không có quyền truy cập trang này.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@staff_required
def manage_books(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query) | Q(publisher__icontains=query)
    ) if query else Book.objects.all().order_by('title')
    form = BookForm()
    return render(request, 'admin/manage_books.html', {
        'books': books,
        'form': form,
        'query': query,
    })


@login_required
@staff_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã thêm sách "{form.cleaned_data["title"]}" thành công!')
            return redirect('manage_books')
        else:
            # Trả về lỗi dạng JSON để modal xử lý
            errors = {field: list(errs) for field, errs in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    return redirect('manage_books')


@login_required
@staff_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'GET':
        # Trả về dữ liệu JSON cho modal
        data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'publisher': book.publisher,
            'uri': book.uri or '',
            'quantity': book.quantity,
            'image_url': book.image.url if book.image else '',
            'pdf_url': book.pdf_file.url if book.pdf_file else '',
        }
        return JsonResponse(data)
    elif request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
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
            error = 'Mật khẩu mới và xác nhận mật khẩu không khớp.'
        else:
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Giữ đăng nhập sau khi đổi mật khẩu
            success = 'Đổi mật khẩu thành công!'

    return render(request, 'user/change_password.html', {'error': error, 'success': success})

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    is_borrowed = False
    if request.user.is_authenticated:
        is_borrowed = BorrowRecord.objects.filter(
            user=request.user, book=book, returned_at__isnull=True
        ).exists()
    return render(request, 'book.html', {'book': book, 'is_borrowed': is_borrowed})

def giaotrinh_detail(request, giaotrinh_id):
    giaotrinh = get_object_or_404(Giaotrinh, id=giaotrinh_id)
    return render(request, 'giaotrinh.html', {'giaotrinh': giaotrinh})



def recommended_books(request):
    user = request.user
    books = Book.objects.all()
    history = UserHistory.objects.filter(user=user).values_list('book_id', flat=True)

    books_df = pd.DataFrame(list(books.values('id', 'title', 'description')))
    history_dict = {user.id: list(history)}

    recommendations = recommend_books(user.id, books_df, history_dict)
    return render(request, 'home.html', {'home': home})

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
                books_data = [{'title': b.title, 'author': b.author, 'id': b.id} for b in books]

                return render(request, 'result.html', {
                    'books': books,
                    'title': cleaned_title
                })

            except Exception as e:
                logger.error(f"Lỗi xử lý ảnh: {str(e)}", exc_info=True)
                return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Yêu cầu không hợp lệ.'})



@require_POST
@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if BorrowRecord.objects.filter(user=request.user, book=book, returned_at__isnull=True).exists():
        return JsonResponse({'success': False, 'message': f"Bạn đã mượn sách '{book.title}' rồi."})

    data = {}
    if request.body:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            pass
            
    expected_return_date = data.get('expected_return_date')
    note = data.get('note')

    BorrowRecord.objects.create(
        user=request.user,
        book=book,
        borrowed_at=timezone.now(),
        expected_return_date=expected_return_date,
        note=note
    )

    return JsonResponse({'success': True, 'message': f"Bạn đã mượn sách '{book.title}' thành công!"})
# View để liệt kê sách đã mượn
@login_required
def list_borrowed_books(request):
    borrowed_books = BorrowRecord.objects.filter(user=request.user, returned_at__isnull=True)
    return render(request, "borrowed_books.html", {"borrowed_books": borrowed_books})

# View để trả sách
@login_required
def return_book(request, borrow_id):
    borrow_record = get_object_or_404(BorrowRecord, id=borrow_id, user=request.user)

    if borrow_record.returned_at is None:
        borrow_record.returned_at = timezone.now()
        borrow_record.save()

        book = borrow_record.book
        book.quantity += 1
        book.save()

        messages.success(request, f"Bạn đã trả sách '{book.title}' thành công!")
    else:
        messages.warning(request, "Sách này đã được trả trước đó.")

    return redirect("borrowed_books")