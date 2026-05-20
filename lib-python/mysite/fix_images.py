import django, os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
sys.stdout.reconfigure(encoding='utf-8')
django.setup()
from myapp.models import Book

# Mapping: book_id -> filename in book_images/
image_mapping = {
    3:  'De-The-Gioi-Biet-Ban-La-Ai.jpg',
    4:  'Tu-Duy-Nguoc-Nguyen-Anh-Dung.jpg',
    6:  'Diem-Tinh-Va-Nong-Gian.jpg',
    8:  'Ky-Luat-Tu-Do.jpg',
    10: 'tam-ly-hoc-ve-tien.jpg',
    11: 'Flow-Dong-Chay-Mihaly-Csikszentmihalyi.png',
    13: 'Me-Lam-Gi-Co-Uoc-Mo.jpg',
    15: 'Hieu-Ve-Trai-Tim-Minh-Niem.jpg',
    17: 'dam-tha-thu-edward-m-hallowell-xuan-khanh-dich.jpg',
}

for book_id, filename in image_mapping.items():
    full_path = os.path.join('C:/Users/nminh/ttcsnminh/lib-python/mysite/media/book_images', filename)
    if os.path.exists(full_path):
        try:
            book = Book.objects.get(id=book_id)
            book.image = f'book_images/{filename}'
            book.save()
            print(f'✓ Updated book id={book_id} -> {filename}')
        except Book.DoesNotExist:
            print(f'✗ Book id={book_id} not found')
    else:
        print(f'✗ File not found: {filename}')
